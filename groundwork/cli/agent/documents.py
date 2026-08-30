"""Document-grounded facts. Deliberately narrow: a two-column CSV for budget
(not arbitrary PDFs — that parsing is fragile enough to produce false
inconsistencies, which are worse than not checking at all), and an injectable
ProPublica client for the 990 cross-check so Phase 1 could prove the control
flow without a network call. The real HTTP client is wired below in Phase 3.

Field names (filings_with_data, tax_prd, tax_prd_yr, totrevenue,
totfuncexpns) were verified against a real response fetched outside this
session (this session's own network policy blocks projects.propublica.org —
confirmed via both curl and WebFetch, both rejected by the egress proxy) and
replayed through this exact client code. Also confirmed: a filing can exist
in filings_without_data (structured data not yet extracted by ProPublica)
without appearing in filings_with_data — get_most_recent_filing correctly
ignores those and falls through to the most recent filing that actually has
usable data, which is the right behavior given missing data stays neutral.
"""

from __future__ import annotations

import csv
import io
import re
from dataclasses import dataclass

import requests


def parse_budget_csv(csv_text: str) -> dict[str, float]:
    """Two columns: category, amount. Returns {category: amount}."""
    reader = csv.reader(io.StringIO(csv_text))
    lines: dict[str, float] = {}
    for row in reader:
        if len(row) < 2:
            continue
        category, amount = row[0].strip(), row[1].strip()
        if category.lower() == "category":
            continue  # header row
        try:
            lines[category] = float(amount.replace("$", "").replace(",", ""))
        except ValueError:
            continue
    return lines


@dataclass
class Filing:
    ein: str
    tax_year: int
    total_revenue: float | None = None
    total_expenses: float | None = None
    """Both figures are optional on purpose: a filing can exist without a
    usable revenue field (different Form 990 variants expose different
    fields), and that's a distinct state from no filing existing at all.
    check_public_record_alignment() already treats a None figure as neutral,
    never a flag — this dataclass just needs to be able to say "found the
    org, no usable number" instead of collapsing that into "not found."""


class ProPublicaClient:
    BASE_URL = "https://projects.propublica.org/nonprofits/api/v2"

    def get_most_recent_filing(self, ein: str) -> Filing | None:
        """Verified against a real response (EIN 14-2007220, ProPublica's own
        organization record) fetched outside this session and replayed
        through this exact code — see the module docstring.

        Raises requests.RequestException on a real network/HTTP failure —
        deliberately NOT caught here, so a service outage can never look
        identical to "no filing found" (returns None) to the caller. The CLI
        (Phase 3 item 4) must catch this distinctly and report "couldn't
        check" rather than silently treating it as neutral.
        """
        clean_ein = re.sub(r"\D", "", ein)
        if len(clean_ein) != 9:
            raise ValueError(f"EIN must contain 9 digits, got {ein!r}")

        url = f"{self.BASE_URL}/organizations/{int(clean_ein)}.json"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        filings = data.get("filings_with_data", [])
        if not filings:
            return None

        latest = max(filings, key=lambda f: int(f.get("tax_prd", 0)))

        revenue = latest.get("totrevenue")
        expenses = latest.get("totfuncexpns")
        return Filing(
            ein=clean_ein,
            tax_year=int(latest.get("tax_prd_yr", 0)),
            total_revenue=float(revenue) if revenue is not None else None,
            total_expenses=float(expenses) if expenses is not None else None,
        )


class FakeProPublicaClient(ProPublicaClient):
    """Test double: returns whatever was scripted for a given EIN."""

    def __init__(self, filings: dict[str, Filing | None]):
        self.filings = filings

    def get_most_recent_filing(self, ein: str) -> Filing | None:
        return self.filings.get(ein)
