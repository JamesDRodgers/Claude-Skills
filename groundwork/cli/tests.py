"""Phase 1 tests: control flow only, no real model, no real network. Every
client here is a scripted double so these run deterministically and prove
the harness's guarantees hold regardless of what a real model does.
"""

import copy

from agent.consistency import check_budget_alignment, check_public_record_alignment
from agent.documents import Filing, FakeProPublicaClient, parse_budget_csv
from agent.draft import assemble_section, build_criteria_table
from agent.harness import InterviewHarness
from agent.models import InterviewState, Resolution, ResolutionType
from agent.resolution import apply_resolution
from agent.sections import SECTIONS

# SECTIONS is a shared, module-level list that several tests mutate in place
# (trimming .probes to exercise a single probe in isolation). Snapshotted here,
# before any test runs, so a test needing a guaranteed-fresh, unmutated set of
# probes can pull from this instead of accidentally reading another test's
# leftover mutation -- copy.deepcopy(ORIGINAL_SECTIONS) gives an independent copy.
ORIGINAL_SECTIONS = copy.deepcopy(SECTIONS)


# ---------- scripted doubles ----------


class ScriptedEvalClient:
    """Returns one scripted action per call, in order. Each action is a dict
    matching what harness.step() expects from a real model's tool call."""

    def __init__(self, script):
        self.script = list(script)
        self.calls = 0

    def evaluate(self, *, section, probe, reply, known_metrics=None):
        action = self.script[self.calls]
        self.calls += 1
        return action


class AlwaysMissClient:
    def evaluate(self, *, section, probe, reply, known_metrics=None):
        return {"type": "miss"}


class FakeDraftClient:
    """canned: {section_key: prose_string}"""

    def __init__(self, canned):
        self.canned = canned

    def transform(self, facts):
        section = facts[0].section
        return self.canned[section]


# ---------- follow-up ladder ----------


def test_ladder_walks_miss_reask_rephrase_gap():
    h = InterviewHarness(client=AlwaysMissClient(), sections=SECTIONS[:1])  # funder_fit, 1 probe
    r0 = h.step()
    assert r0.role == "question"

    r1 = h.step("vague answer")
    assert r1.role == "question", "miss 1 should just re-ask"

    r2 = h.step("still vague")
    assert r2.role == "rephrase", f"miss 2 should force a rephrase, got {r2.role}"

    r3 = h.step("still nothing")
    assert r3.role == "warning", f"funder_fit gap should be severity=warning, got {r3.role}"
    assert h.state.gaps, "gap should be logged"
    print("PASS: ladder walks miss -> reask -> rephrase -> gap, harness-enforced")


def test_ladder_records_fact_and_advances():
    script = [
        {
            "type": "fact",
            "summary": "130 youth enrolled Jan-June per intake database",
            "verbatim_quote": "130 youth enrolled between January and June, per our intake database",
            "structured_fields": {"metric_name": "youth_enrolled", "value": 130, "source_name": "intake database"},
        }
    ]
    h = InterviewHarness(client=ScriptedEvalClient(script), sections=SECTIONS[:1])
    h.step()
    result = h.step("130 youth enrolled between January and June, per our intake database")
    assert result.role == "recorded"
    assert len(h.state.facts) == 1
    assert h.section_idx == 1, "should advance past the only section"
    print("PASS: a concrete answer records a fact and advances immediately")


def test_non_funder_fit_gap_is_plain_gap_not_warning():
    problem_section = [s for s in SECTIONS if s.key == "problem_evidence"]
    h = InterviewHarness(client=AlwaysMissClient(), sections=problem_section)
    h.step()
    h.step("a")
    h.step("b")
    result = h.step("c")
    assert result.role == "gap", f"non-funder-fit section should log a plain gap, got {result.role}"
    print("PASS: gap severity is section-specific (warning only for funder_fit)")


# ---------- consistency checks ----------


def test_internal_consistency_catches_contradiction():
    script = [
        {
            "type": "fact",
            "summary": "130 youth served",
            "verbatim_quote": "we served 130 youth",
            "structured_fields": {"metric_name": "youth_served", "value": 130},
        },
        {
            "type": "fact",
            "summary": "80 youth in baseline",
            "verbatim_quote": "baseline was 80 youth",
            "structured_fields": {"metric_name": "youth_served", "value": 80},
        },
    ]
    sections = [s for s in SECTIONS if s.key in ("team_capacity", "measurable_outcomes")]
    # collapse to one probe each so two `step` calls each record a fact
    sections[0].probes = sections[0].probes[:1]
    sections[1].probes = sections[1].probes[:1]
    h = InterviewHarness(client=ScriptedEvalClient(script), sections=sections)
    h.step()
    h.step("we served 130 youth")
    h.step("baseline was 80 youth")
    assert len(h.state.inconsistencies) == 1, "same metric_name, divergent values should flag"
    print("PASS: internal consistency check catches a same-metric contradiction across sections")


def test_internal_consistency_allows_rounding_tolerance():
    script = [
        {"type": "fact", "summary": "130", "verbatim_quote": "130", "structured_fields": {"metric_name": "x", "value": 130}},
        {"type": "fact", "summary": "131", "verbatim_quote": "131", "structured_fields": {"metric_name": "x", "value": 131}},
    ]
    sections = [s for s in SECTIONS if s.key in ("team_capacity", "measurable_outcomes")]
    sections[0].probes = sections[0].probes[:1]
    sections[1].probes = sections[1].probes[:1]
    h = InterviewHarness(client=ScriptedEvalClient(script), sections=sections)
    h.step()
    h.step("130")
    h.step("131")
    assert len(h.state.inconsistencies) == 0, "130 vs 131 is within rounding tolerance, should not flag"
    print("PASS: trivial rounding differences don't trigger a false inconsistency")


class FakeMetricMatcher:
    """canned: {new_metric: matched_candidate_name_or_None}"""

    def __init__(self, canned):
        self.canned = canned

    def find_same_metric(self, new_metric, new_value, candidates):
        return self.canned.get(new_metric)


def test_semantic_matcher_wiring_catches_synonym_when_matcher_says_match():
    """Proves the harness wiring itself is correct, independent of whether a
    real model's judgment is good -- with a matcher that DOES recognize the
    synonym, the previously-confirmed gap now gets caught."""
    script = [
        {"type": "fact", "summary": "130 youth served", "verbatim_quote": "we served 130 youth",
         "structured_fields": {"metric_name": "youth_served", "value": 130}},
        {"type": "fact", "summary": "80 young people served", "verbatim_quote": "80 young people came through the program",
         "structured_fields": {"metric_name": "young_people_served", "value": 80}},
    ]
    sections = [s for s in SECTIONS if s.key in ("team_capacity", "measurable_outcomes")]
    sections[0].probes = sections[0].probes[:1]
    sections[1].probes = sections[1].probes[:1]
    matcher = FakeMetricMatcher({"young_people_served": "youth_served"})
    h = InterviewHarness(client=ScriptedEvalClient(script), sections=sections, metric_matcher=matcher)
    h.step()
    h.step("we served 130 youth")
    h.step("80 young people came through the program")
    assert len(h.state.inconsistencies) == 1, "with a matcher configured, the synonym case should now be caught"
    assert "semantic match" in list(h.state.inconsistencies.values())[0].description
    print("PASS: with a metric_matcher configured, a synonym contradiction is caught via semantic match")


def test_semantic_matcher_no_friction_when_values_actually_agree():
    """The workflow-friction concern: if the matcher correctly recognizes two
    labels as the same quantity and the VALUES agree, nothing should flag --
    no unnecessary interruption for something that isn't actually wrong."""
    script = [
        {"type": "fact", "summary": "130 youth served", "verbatim_quote": "we served 130 youth",
         "structured_fields": {"metric_name": "youth_served", "value": 130}},
        {"type": "fact", "summary": "131 young people served", "verbatim_quote": "about 131 young people",
         "structured_fields": {"metric_name": "young_people_served", "value": 131}},
    ]
    sections = [s for s in SECTIONS if s.key in ("team_capacity", "measurable_outcomes")]
    sections[0].probes = sections[0].probes[:1]
    sections[1].probes = sections[1].probes[:1]
    matcher = FakeMetricMatcher({"young_people_served": "youth_served"})
    h = InterviewHarness(client=ScriptedEvalClient(script), sections=sections, metric_matcher=matcher)
    h.step()
    h.step("we served 130 youth")
    h.step("about 131 young people")
    assert len(h.state.inconsistencies) == 0, "matched quantity + agreeing values (within tolerance) must not create friction"
    print("PASS: recognizing a synonym match does not itself create friction when the values already agree")


def test_semantic_matcher_correctly_does_not_match_genuinely_different_quantities():
    """The other side of the friction concern: 'enrolled' and 'completed' are
    both about program participation but are NOT the same quantity -- a
    matcher (real or fake here) that correctly declines to match them must
    not produce a false-positive flag."""
    script = [
        {"type": "fact", "summary": "162 students enrolled", "verbatim_quote": "162 students enrolled",
         "structured_fields": {"metric_name": "students_enrolled", "value": 162}},
        {"type": "fact", "summary": "148 students completed", "verbatim_quote": "148 students completed the program",
         "structured_fields": {"metric_name": "students_completed", "value": 148}},
    ]
    sections = [s for s in SECTIONS if s.key in ("team_capacity", "measurable_outcomes")]
    sections[0].probes = sections[0].probes[:1]
    sections[1].probes = sections[1].probes[:1]
    matcher = FakeMetricMatcher({"students_completed": None})  # correctly declines to match
    h = InterviewHarness(client=ScriptedEvalClient(script), sections=sections, metric_matcher=matcher)
    h.step()
    h.step("162 students enrolled")
    h.step("148 students completed the program")
    assert len(h.state.inconsistencies) == 0, "enrolled vs completed are genuinely different quantities -- must not be flagged as contradictory"
    print("PASS: a matcher that correctly distinguishes enrolled-vs-completed produces no false-positive flag")


# ---------- edge cases: metric_name exact-match brittleness (KNOWN GAP) ----------
# These document a real limitation surfaced during review, not desired behavior.
# check_internal_consistency requires metric_name to match character-for-character.
# None of these are false POSITIVES (it never wrongly flags) -- all three are false
# NEGATIVES: real contradictions the checker silently misses because the live
# classifier has no strong reason to name the same quantity identically twice
# across an 8-section interview.


def test_edge_case_synonym_metric_names_defeat_consistency_check():
    """check_internal_consistency ALONE (no matcher) still can't do this --
    deterministic string comparison has no way to know two different words
    mean the same thing, and that's not something normalization can fix
    either. MITIGATED, not contradicted, by check_semantic_consistency +
    AnthropicMetricMatcher (see test_semantic_matcher_* above and
    smoke_test_metric_matcher.py) -- a real model call, live-verified to
    correctly match this exact synonym case, correctly decline to match
    "enrolled" vs "completed", and only fire when values actually disagree.
    This test still documents what the free, always-on, deterministic layer
    alone cannot do; it is not testing the full system, which now catches
    this when metric_matcher is configured."""
    script = [
        {"type": "fact", "summary": "130 youth served", "verbatim_quote": "we served 130 youth",
         "structured_fields": {"metric_name": "youth_served", "value": 130}},
        {"type": "fact", "summary": "80 young people served", "verbatim_quote": "80 young people came through the program",
         "structured_fields": {"metric_name": "young_people_served", "value": 80}},
    ]
    sections = [s for s in SECTIONS if s.key in ("team_capacity", "measurable_outcomes")]
    sections[0].probes = sections[0].probes[:1]
    sections[1].probes = sections[1].probes[:1]
    h = InterviewHarness(client=ScriptedEvalClient(script), sections=sections)
    h.step()
    h.step("we served 130 youth")
    h.step("80 young people came through the program")
    assert len(h.state.inconsistencies) == 0, (
        "a real 130-vs-80 contradiction should have gone undetected here -- "
        "'youth_served' != 'young_people_served' as exact strings"
    )
    print("CONFIRMED GAP: synonym metric_name strings ('youth_served' vs 'young_people_served') defeat the consistency check entirely")


def test_edge_case_formatting_variation_now_caught_after_normalization_fix():
    """FIXED (was a confirmed gap): case and separator differences on the same
    label. _normalize_metric() now collapses 'Households Served' and
    'households-served' to the same comparison key -- pure code fix, no
    model dependency, so it's provable deterministically."""
    script = [
        {"type": "fact", "summary": "130 households", "verbatim_quote": "130 households",
         "structured_fields": {"metric_name": "Households Served", "value": 130}},
        {"type": "fact", "summary": "80 households", "verbatim_quote": "80 households",
         "structured_fields": {"metric_name": "households-served", "value": 80}},
    ]
    sections = [s for s in SECTIONS if s.key in ("team_capacity", "measurable_outcomes")]
    sections[0].probes = sections[0].probes[:1]
    sections[1].probes = sections[1].probes[:1]
    h = InterviewHarness(client=ScriptedEvalClient(script), sections=sections)
    h.step()
    h.step("130 households")
    h.step("80 households")
    assert len(h.state.inconsistencies) == 1, (
        "'Households Served' vs 'households-served' should now be recognized as the same metric"
    )
    print("FIXED: normalization now catches case/punctuation-only metric_name differences")


def test_edge_case_missing_metric_name_now_caught_via_harness_fallback():
    """FIXED (was a confirmed gap): a fact recorded with empty structured_fields
    now gets a deterministic fallback metric_name (section:probe_key) derived
    by the harness itself when numeric_values() finds a number in the text --
    no longer invisible to check_internal_consistency."""
    script = [
        {"type": "fact", "summary": "130 households served", "verbatim_quote": "130 households",
         "structured_fields": {"metric_name": "households_served", "value": 130}},
        {"type": "fact", "summary": "we actually only reached about 80 households",
         "verbatim_quote": "we actually only reached about 80 households",
         "structured_fields": {}},  # classifier didn't populate metric_name/value this time
    ]
    sections = [s for s in SECTIONS if s.key in ("team_capacity", "measurable_outcomes")]
    sections[0].probes = sections[0].probes[:1]
    sections[1].probes = sections[1].probes[:1]
    h = InterviewHarness(client=ScriptedEvalClient(script), sections=sections)
    h.step()
    h.step("130 households")
    h.step("we actually only reached about 80 households")
    second_fact = list(h.state.facts.values())[1]
    # the second fact is recorded in measurable_outcomes/indicator (the 2nd section's
    # first probe) -- NOT the same probe as the first fact -- which is exactly why
    # this fallback doesn't (and shouldn't) make the two facts match each other below
    assert second_fact.structured_fields.get("metric_name") == "measurable_outcomes:indicator", (
        "harness should derive a deterministic fallback metric_name from section:probe_key"
    )
    assert second_fact.structured_fields.get("value") == 80.0
    assert len(h.state.inconsistencies) == 0, (
        "the two facts are about different probes, so the fallback correctly does NOT "
        "make them match each other -- this fix stops a fact from being totally invisible, "
        "it doesn't solve the cross-probe synonym problem (that's still test 1's confirmed gap)"
    )
    print("FIXED: a fact with no metric_name now gets a harness-derived fallback instead of being invisible")
    print("  (still limited: this fallback is scoped per probe_key, so it does NOT solve the cross-probe synonym problem)")


def test_budget_alignment_flags_missing_and_zero_lines():
    lines = {"Personnel": 40000, "Supplies": 0}
    missing = check_budget_alignment("Community Engagement", lines)
    assert missing is not None and "no budget line matches" in missing.description
    zero = check_budget_alignment("Supplies", lines)
    assert zero is not None and "$0.00" in zero.description
    present = check_budget_alignment("Personnel", lines)
    assert present is None
    print("PASS: budget alignment flags missing and near-zero categories, passes real ones")


def test_public_record_alignment_matching_mismatching_and_missing():
    assert check_public_record_alignment(100_000, 105_000) is None, "close figures should pass"
    assert check_public_record_alignment(2_000_000, 200_000) is not None, "5x divergence should flag"
    assert check_public_record_alignment(100_000, None) is None, "no filing on record is neutral, not a flag"
    print("PASS: public-record check flags real divergence, passes close figures, treats missing filing as neutral")


def test_budget_csv_parsing():
    csv_text = "category,amount\nPersonnel,40000\nSupplies,\"1,250.50\"\n"
    lines = parse_budget_csv(csv_text)
    assert lines == {"Personnel": 40000.0, "Supplies": 1250.50}
    print("PASS: budget CSV parses category/amount pairs, header row skipped")


def test_real_propublica_client_logic_via_mocked_response():
    """These test the client's own logic — EIN normalization, deterministic
    filing selection, missing-field handling — by mocking requests.get, since
    this environment's network policy blocks the real API. Field names in
    the payloads below (filings_with_data, tax_prd, tax_prd_yr, totrevenue,
    totfuncexpns) were confirmed against a real response fetched outside
    this session — see documents.py's module docstring."""
    from unittest.mock import patch, MagicMock
    from agent.documents import ProPublicaClient

    class FakeResponse:
        def __init__(self, payload):
            self._payload = payload

        def raise_for_status(self):
            pass

        def json(self):
            return self._payload

    client = ProPublicaClient()

    # deterministic selection: out-of-order filings, must pick the true latest by tax_prd
    payload = {
        "filings_with_data": [
            {"tax_prd": 202012, "tax_prd_yr": 2020, "totrevenue": 100000, "totfuncexpns": 90000},
            {"tax_prd": 202212, "tax_prd_yr": 2022, "totrevenue": 150000, "totfuncexpns": 130000},
            {"tax_prd": 202112, "tax_prd_yr": 2021, "totrevenue": 120000, "totfuncexpns": 110000},
        ]
    }
    with patch("agent.documents.requests.get", return_value=FakeResponse(payload)):
        filing = client.get_most_recent_filing("12-3456789")
    assert filing.tax_year == 2022 and filing.total_revenue == 150000.0, "must pick latest by tax_prd, not array order"

    # EIN normalization: hyphens stripped before building the URL
    captured = {}

    def capture_get(url, timeout):
        captured["url"] = url
        return FakeResponse({"filings_with_data": []})

    with patch("agent.documents.requests.get", side_effect=capture_get):
        client.get_most_recent_filing("12-3456789")
    assert "123456789" in captured["url"], f"EIN should be normalized in the URL, got {captured['url']}"

    # malformed EIN raises loudly instead of silently mis-querying
    try:
        client.get_most_recent_filing("not-an-ein")
        assert False, "should have raised ValueError"
    except ValueError:
        pass

    # no filings at all -> None (neutral, not a flag)
    with patch("agent.documents.requests.get", return_value=FakeResponse({"filings_with_data": []})):
        assert client.get_most_recent_filing("12-3456789") is None

    # a filing exists but has no revenue field -> a Filing with total_revenue=None,
    # NOT None outright -- "found the org, no usable number" is a different state
    # than "no filing found"
    payload_no_revenue = {"filings_with_data": [{"tax_prd": 202312, "tax_prd_yr": 2023}]}
    with patch("agent.documents.requests.get", return_value=FakeResponse(payload_no_revenue)):
        filing = client.get_most_recent_filing("12-3456789")
    assert filing is not None and filing.total_revenue is None
    assert check_public_record_alignment(1_000_000, filing.total_revenue) is None, "None revenue must stay neutral"

    print("PASS: real ProPublica client logic (selection, normalization, missing-field handling) verified via mocked responses")


def test_propublica_fake_client_returns_scripted_filing():
    client = FakeProPublicaClient({"12-3456789": Filing(ein="12-3456789", tax_year=2025, total_revenue=500_000)})
    assert client.get_most_recent_filing("12-3456789").total_revenue == 500_000
    assert client.get_most_recent_filing("00-0000000") is None
    print("PASS: fake ProPublica client returns scripted filings, missing EIN returns None")


# ---------- resolution pass ----------


def test_resolution_pass_correcting_a_gap_creates_a_fact_not_silence():
    from agent.models import Gap

    state = InterviewState()
    gap = Gap(id="gap-1", section="problem_evidence", criterion="SIGNIFICANCE", probe_key="problem_scale",
              reason="no data given")
    state.gaps[gap.id] = gap

    apply_resolution(state, Resolution(flag_id="gap-1", resolution=ResolutionType.CORRECTED,
                                        updated_value="412 households per intake data"))

    assert len(state.facts) == 1, "correcting a gap must create a fact, not just a resolution record"
    new_fact = list(state.facts.values())[0]
    assert new_fact.summary == "412 households per intake data"
    assert new_fact.section == "problem_evidence"

    draft_client = FakeDraftClient({"problem_evidence": "412 households, per intake data, face this problem."})
    section_draft = assemble_section("problem_evidence", state, draft_client)
    assert "[GAP:" not in section_draft.text, "a corrected gap must not still render as an unresolved placeholder"
    assert "412" in section_draft.text
    print("PASS: correcting a gap creates a real fact and the placeholder is replaced, not duplicated or dropped")


def test_resolution_pass_explaining_a_gap_keeps_placeholder_with_note():
    from agent.models import Gap

    state = InterviewState()
    gap = Gap(id="gap-1", section="problem_evidence", criterion="SIGNIFICANCE", probe_key="problem_scale",
              reason="no data given")
    state.gaps[gap.id] = gap

    apply_resolution(state, Resolution(flag_id="gap-1", resolution=ResolutionType.EXPLAINED,
                                        note="we're pre-launch, no intake data exists yet"))

    assert len(state.facts) == 0, "an explanation is not a fact"
    section_draft = assemble_section("problem_evidence", state, FakeDraftClient({}))
    assert "[GAP:" in section_draft.text
    assert "pre-launch" in section_draft.text
    print("PASS: explaining a gap keeps the placeholder but attaches the leader's note instead of hiding it")


def test_resolution_pass_override_marks_fact_and_never_erases_flag():
    state = InterviewState()
    from agent.models import Fact, Inconsistency, Tier

    fact = Fact(id="fact-1", section="budget_congruence", criterion="BUDGET", probe_key="allocation",
                summary="$0 allocated to community engagement", verbatim_quote="we didn't budget for that separately",
                structured_fields={"metric_name": "engagement_budget", "value": 0}, tier=Tier.ATTRIBUTED)
    state.facts[fact.id] = fact
    inc = Inconsistency(id="inc-1", criterion="BUDGET", description="engagement is central but $0 budgeted",
                         related_fact_ids=[fact.id], kind="budget")
    state.inconsistencies[inc.id] = inc

    apply_resolution(state, Resolution(flag_id="inc-1", resolution=ResolutionType.OVERRIDDEN,
                                        note="we fold it into personnel time, not a separate line"))

    assert "inc-1" in state.resolutions, "flag must stay on record, never erased"
    assert fact.structured_fields["overridden"] is True
    print("PASS: override marks the fact and preserves the flag record instead of erasing it")


def test_resolution_pass_can_target_either_side_of_a_two_fact_inconsistency():
    from agent.models import Fact, Inconsistency, Tier

    def make_state():
        state = InterviewState()
        older = Fact(id="fact-old", section="team_capacity", criterion="TEAM", probe_key="track_record",
                     summary="130 swimmers", verbatim_quote="130 swimmers",
                     structured_fields={"metric_name": "x", "value": 130}, tier=Tier.ATTRIBUTED)
        newer = Fact(id="fact-new", section="measurable_outcomes", criterion="OUTCOMES", probe_key="baseline",
                     summary="80 swimmers", verbatim_quote="80 swimmers",
                     structured_fields={"metric_name": "x", "value": 80}, tier=Tier.ATTRIBUTED)
        state.facts[older.id] = older
        state.facts[newer.id] = newer
        inc = Inconsistency(id="inc-1", criterion="TEAM", description="mismatch",
                             related_fact_ids=[older.id, newer.id])
        state.inconsistencies[inc.id] = inc
        return state, older, newer

    # leader says the OLDER fact was the typo -- must be able to target it explicitly
    state, older, newer = make_state()
    apply_resolution(state, Resolution(flag_id="inc-1", resolution=ResolutionType.CORRECTED,
                                        updated_value="118", target_fact_id="fact-old"))
    assert older.summary == "118", "explicit target_fact_id must let the leader correct either side"
    assert newer.summary == "80 swimmers", "the untargeted fact must be left alone"

    # naming a fact_id that isn't actually part of this flag should fail loudly, not silently misapply
    state, older, newer = make_state()
    try:
        apply_resolution(state, Resolution(flag_id="inc-1", resolution=ResolutionType.CORRECTED,
                                            updated_value="118", target_fact_id="fact-not-related"))
        assert False, "should have raised"
    except ValueError:
        pass
    print("PASS: a two-fact inconsistency can be resolved against either named fact, not just a hardcoded default")


def test_resolution_pass_all_four_types_apply_expected_effect():
    from agent.models import Fact, Inconsistency, Tier

    def make_state():
        state = InterviewState()
        fact = Fact(id="fact-1", section="team_capacity", criterion="TEAM", probe_key="track_record",
                    summary="original", verbatim_quote="original", structured_fields={"value": 5}, tier=Tier.ATTRIBUTED)
        state.facts[fact.id] = fact
        inc = Inconsistency(id="inc-1", criterion="TEAM", description="test", related_fact_ids=[fact.id])
        state.inconsistencies[inc.id] = inc
        return state, fact

    s, f = make_state()
    apply_resolution(s, Resolution(flag_id="inc-1", resolution=ResolutionType.CORRECTED, updated_value="8"))
    assert f.summary == "8"

    s, f = make_state()
    apply_resolution(s, Resolution(flag_id="inc-1", resolution=ResolutionType.EXPLAINED, note="context here"))
    assert f.structured_fields["resolution_note"] == "context here"

    s, f = make_state()
    apply_resolution(s, Resolution(flag_id="inc-1", resolution=ResolutionType.ACCEPTED))
    assert "overridden" not in f.structured_fields and "resolution_note" not in f.structured_fields

    s, f = make_state()
    apply_resolution(s, Resolution(flag_id="inc-1", resolution=ResolutionType.OVERRIDDEN))
    assert f.structured_fields["overridden"] is True

    print("PASS: all four resolution types apply their distinct, correct effect")


# ---------- draft assembly ----------


def test_draft_uses_model_prose_when_grounded():
    state = InterviewState()
    from agent.models import Fact, Tier

    f = Fact(id="fact-1", section="team_capacity", criterion="TEAM", probe_key="track_record",
             summary="delivered at 23 sites, 91% retention", verbatim_quote="23 sites, 91% retention",
             structured_fields={"sites": 23, "retention": 91}, tier=Tier.ATTRIBUTED)
    state.facts[f.id] = f

    draft_client = FakeDraftClient({"team_capacity": "Our team has delivered this program at 23 sites with 91% retention."})
    section_draft = assemble_section("team_capacity", state, draft_client)
    assert not section_draft.used_fallback
    assert "23" in section_draft.text and "91" in section_draft.text
    print("PASS: grounded model prose (numbers all trace to facts) is used as-is")


def test_draft_falls_back_when_model_invents_a_number():
    state = InterviewState()
    from agent.models import Fact, Tier

    f = Fact(id="fact-1", section="team_capacity", criterion="TEAM", probe_key="track_record",
             summary="delivered at 23 sites", verbatim_quote="23 sites",
             structured_fields={"sites": 23}, tier=Tier.ATTRIBUTED)
    state.facts[f.id] = f

    # the fake model slips in a number (500) that was never logged as a fact
    draft_client = FakeDraftClient({"team_capacity": "Our team has reached over 500 people across 23 sites."})
    section_draft = assemble_section("team_capacity", state, draft_client)
    assert section_draft.used_fallback, "an ungrounded number must trigger the template fallback, never pass through"
    assert "500" not in section_draft.text
    assert "23" in section_draft.text  # the honest template version still says what's real
    print("PASS: an ungrounded number in model prose is caught and the section falls back to template phrasing")


def test_overridden_fact_never_sent_to_model_renders_verbatim():
    state = InterviewState()
    from agent.models import Fact, Tier

    f = Fact(id="fact-1", section="budget_congruence", criterion="BUDGET", probe_key="allocation",
             summary="we fold it into personnel time", verbatim_quote="we fold it into personnel time, not a separate line",
             structured_fields={"overridden": True}, tier=Tier.ATTRIBUTED)
    state.facts[f.id] = f

    class ExplodingDraftClient:
        def transform(self, facts):
            raise AssertionError("overridden facts must never be sent to the model for transformation")

    section_draft = assemble_section("budget_congruence", state, ExplodingDraftClient())
    assert section_draft.text == "we fold it into personnel time, not a separate line"
    print("PASS: an overridden fact bypasses the model entirely and renders exactly as the leader wrote it")


def test_criteria_table_flags_override_status_not_erased():
    state = InterviewState()
    from agent.models import Fact, Tier

    f = Fact(id="fact-1", section="budget_congruence", criterion="BUDGET", probe_key="allocation",
             summary="kept despite flag", verbatim_quote="kept despite flag",
             structured_fields={"overridden": True}, tier=Tier.ATTRIBUTED)
    state.facts[f.id] = f
    table = build_criteria_table(state)
    assert table[0]["status"] == "confirmed despite flag"
    print("PASS: criteria table discloses an override rather than hiding it")


def test_baseline_vs_target_no_longer_false_positives():
    """Charlene test, Defect 2. Reproduces exactly what broke: the outcomes
    section's own baseline and target probes, for the same indicator, sharing
    a metric_name (correctly, per the reuse-known-metrics instruction) --
    which used to get flagged as a contradiction even though a baseline and
    target are SUPPOSED to differ."""
    outcomes_section = copy.deepcopy([s for s in ORIGINAL_SECTIONS if s.key == "measurable_outcomes"])
    script = [
        {"type": "fact", "summary": "baseline 38%", "verbatim_quote": "38%",
         "structured_fields": {"metric_name": "stress_mgmt_pct", "value": 38}},
        {"type": "fact", "summary": "target 65%", "verbatim_quote": "65% by month 12",
         "structured_fields": {"metric_name": "stress_mgmt_pct", "value": 65}},
    ]
    # collapse to just the baseline and target_timing probes, in that order
    outcomes_section[0].probes = [p for p in outcomes_section[0].probes if p.key in ("baseline", "target_timing")]
    h = InterviewHarness(client=ScriptedEvalClient(script), sections=outcomes_section)
    h.step()
    h.step("38%")
    h.step("65% by month 12")
    assert len(h.state.inconsistencies) == 0, (
        "a baseline and its target sharing a metric_name must NOT be flagged as contradictory"
    )
    facts = list(h.state.facts.values())
    assert facts[0].structured_fields["metric_role"] == "baseline"
    assert facts[1].structured_fields["metric_role"] == "target"
    print("FIXED: baseline vs. target for the same indicator no longer false-positives (Charlene test, Defect 2)")


def test_baseline_vs_target_fix_does_not_suppress_real_cross_section_contradictions():
    """The fix must be narrow: it should NOT suppress the original, legitimate
    cross-section contradiction case (different probes entirely, no
    metric_role tagged on either side) -- that's still test_internal_
    consistency_catches_contradiction above, re-affirmed here for the record."""
    sections = copy.deepcopy([s for s in ORIGINAL_SECTIONS if s.key in ("team_capacity", "measurable_outcomes")])
    sections[0].probes = sections[0].probes[:1]
    sections[1].probes = sections[1].probes[:1]  # "indicator" probe, not baseline/target -- no role tag applies
    script = [
        {"type": "fact", "summary": "130 youth served", "verbatim_quote": "130 youth",
         "structured_fields": {"metric_name": "youth_served", "value": 130}},
        {"type": "fact", "summary": "80 youth served", "verbatim_quote": "80 youth",
         "structured_fields": {"metric_name": "youth_served", "value": 80}},
    ]
    h = InterviewHarness(client=ScriptedEvalClient(script), sections=sections)
    h.step()
    h.step("130 youth")
    h.step("80 youth")
    assert len(h.state.inconsistencies) == 1, "a real same-role contradiction must still be caught after the role-tag fix"
    print("PASS: the baseline/target fix does not suppress genuine cross-section contradictions")


def test_semantic_matcher_respects_metric_role_for_baseline_vs_target():
    """Follow-up to Charlene Defect 2, found in code review: the metric_role
    guard was added to the DETERMINISTIC check only. If the live classifier
    tags baseline and target with DIFFERENT metric names (the reuse
    instruction makes identical names likely, not guaranteed), the
    deterministic pass skips them and the semantic matcher -- correctly
    recognizing they describe the same indicator -- would raise the very same
    false positive through the second door. Both facts already carry the
    harness-set metric_role; the semantic check must honor it too."""
    outcomes_section = copy.deepcopy([s for s in ORIGINAL_SECTIONS if s.key == "measurable_outcomes"])
    outcomes_section[0].probes = [p for p in outcomes_section[0].probes if p.key in ("baseline", "target_timing")]
    script = [
        {"type": "fact", "summary": "baseline 38%", "verbatim_quote": "38%",
         "structured_fields": {"metric_name": "stress_pct_baseline", "value": 38}},
        {"type": "fact", "summary": "target 65%", "verbatim_quote": "65% by month 12",
         "structured_fields": {"metric_name": "stress_pct_target", "value": 65}},
    ]
    # a matcher that (correctly!) recognizes the two labels describe the same indicator
    matcher = FakeMetricMatcher({"stress_pct_target": "stress_pct_baseline"})
    h = InterviewHarness(client=ScriptedEvalClient(script), sections=outcomes_section, metric_matcher=matcher)
    h.step()
    h.step("38%")
    h.step("65% by month 12")
    assert len(h.state.inconsistencies) == 0, (
        "baseline vs target must not be flagged even when the semantic matcher links their differing metric names"
    )
    print("FIXED: the semantic-match path now honors metric_role, closing the second door on the baseline/target false positive")


def test_criteria_table_includes_inconsistencies_and_their_resolution():
    """Charlene test, Defect 1. The table previously only iterated state.facts
    and state.gaps -- a resolved inconsistency (the one flag type that
    actually fired in the live persona run) vanished from the table with no
    trace, contradicting its own "shows what's covered" premise."""
    from agent.models import Fact, Inconsistency, Tier

    state = InterviewState()
    f1 = Fact(id="fact-1", section="measurable_outcomes", criterion="OUTCOMES", probe_key="baseline",
              summary="38%", verbatim_quote="38%", structured_fields={"metric_name": "x", "value": 38}, tier=Tier.ATTRIBUTED)
    f2 = Fact(id="fact-2", section="measurable_outcomes", criterion="OUTCOMES", probe_key="target_timing",
              summary="65%", verbatim_quote="65%", structured_fields={"metric_name": "x", "value": 65}, tier=Tier.ATTRIBUTED)
    state.facts[f1.id] = f1
    state.facts[f2.id] = f2
    inc = Inconsistency(id="inc-1", criterion="OUTCOMES", description="test inconsistency",
                         related_fact_ids=[f1.id, f2.id])
    state.inconsistencies[inc.id] = inc
    apply_resolution(state, Resolution(flag_id="inc-1", resolution=ResolutionType.ACCEPTED))

    table = build_criteria_table(state)
    inc_rows = [r for r in table if "inconsistency" in r["status"]]
    assert len(inc_rows) == 1, "the resolved inconsistency must appear as its own row"
    assert inc_rows[0]["status"] == "inconsistency (accepted)"
    assert inc_rows[0]["section"] == "measurable_outcomes"
    print("FIXED: the criteria table now shows resolved inconsistencies instead of silently dropping them (Charlene test, Defect 1)")


def test_session_save_and_resume_continues_from_the_right_probe():
    """The highest-priority fix from the three-persona pressure test: an
    interruption mid-interview must not lose progress. Proves save -> load
    -> a FRESH harness instance correctly resumes at the next unanswered
    probe, with prior facts intact -- not a restart from probe 0."""
    import os
    import tempfile

    from agent.persistence import load_session, save_session

    script = [
        {"type": "fact", "summary": "130 households", "verbatim_quote": "130 households",
         "structured_fields": {"metric_name": "households_served", "value": 130}},
    ]
    sections = [s for s in SECTIONS if s.key in ("team_capacity", "measurable_outcomes")]
    sections[0].probes = sections[0].probes[:1]
    h1 = InterviewHarness(client=ScriptedEvalClient(script), sections=sections)
    h1.step()
    h1.step("130 households")  # records the one team_capacity fact, advances into measurable_outcomes

    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "session.json")
        save_session(path, h1)

        payload = load_session(path)
        h2 = InterviewHarness(client=AlwaysMissClient(), sections=sections)  # simulates a fresh process
        h2.state = payload["state"]
        h2.section_idx = payload["section_idx"]
        h2.probe_idx = payload["probe_idx"]
        h2.attempts = payload["attempts"]

        assert len(h2.state.facts) == 1, "the fact recorded before saving must survive the round trip"
        assert list(h2.state.facts.values())[0].summary == "130 households"

        result = h2.step()
        assert result.role == "question", f"resumed harness should ask the next probe's question, got {result.role}"
        assert result.text == sections[1].probes[0].question, (
            "resumed harness must continue at measurable_outcomes, not restart at team_capacity"
        )
    print("PASS: a saved session, loaded into a fresh harness, resumes at the correct next probe with prior facts intact")


if __name__ == "__main__":
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
    print(f"\nAll {len(tests)} Phase 1 tests passed.")
