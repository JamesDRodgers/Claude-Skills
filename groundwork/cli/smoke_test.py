"""Manual smoke test against the REAL Anthropic API. Not part of tests.py on
purpose — this costs real tokens and isn't deterministic, so it doesn't
belong in the automated suite. Run once before trusting the live client."""

from dotenv import load_dotenv
load_dotenv()

from agent.live_clients import AnthropicEvalClient, AnthropicDraftClient
from agent.sections import SECTIONS
from agent.models import Fact, Tier

client = AnthropicEvalClient()

problem_probe = SECTIONS[1].probes[0]  # problem_evidence
team_probe = SECTIONS[4].probes[0]     # team_capacity

cases = [
    ("problem_evidence — concrete", problem_probe,
     "412 households faced food insecurity last year according to our intake database, and the nearest food pantry closed in March."),
    ("problem_evidence — clearly vague", problem_probe,
     "Hunger is a really big problem in our community."),
    ("problem_evidence — fluent but empty (adversarial)", problem_probe,
     "This aligns strongly with the deep community needs we've identified through extensive stakeholder engagement and ongoing dialogue with residents."),
    ("team_capacity — concrete", team_probe,
     "We've run this program at 12 sites over 5 years with 85% participant retention."),
    ("team_capacity — vague", team_probe,
     "Our staff are highly experienced and uniquely qualified."),
]

print("=== Classifier smoke test ===")
for label, probe, reply in cases:
    result = client.evaluate(section=SECTIONS[1], probe=probe, reply=reply)
    print(f"\n[{label}]")
    print(f"  reply: {reply[:80]}...")
    print(f"  -> {result}")

print("\n=== Draft transformer smoke test ===")
draft_client = AnthropicDraftClient()
facts = [
    Fact(id="f1", section="team_capacity", criterion="TEAM", probe_key="track_record",
         summary="delivered at 12 sites over 5 years with 85% retention", verbatim_quote="12 sites, 5 years, 85% retention",
         structured_fields={"sites": 12, "years": 5, "retention": 85}, tier=Tier.ATTRIBUTED),
]
prose = draft_client.transform(facts)
print(f"Generated prose: {prose}")

from agent.draft import _numbers_in
allowed = {12.0, 5.0, 85.0}
drafted = _numbers_in(prose)
print(f"Numbers in prose: {drafted}")
print(f"Allowed numbers: {allowed}")
print(f"Grounded (subset check): {drafted.issubset(allowed)}")
