"""Manual smoke test against the REAL Anthropic API for AnthropicMetricMatcher.
Not part of tests.py — this costs real tokens and depends on live model
judgment, not deterministic logic. Run this after any change to the matcher's
prompt to confirm it still gets these three cases right."""

from dotenv import load_dotenv
load_dotenv()

from agent.live_clients import AnthropicMetricMatcher

matcher = AnthropicMetricMatcher()

cases = [
    ("genuine synonym -- should MATCH", "young_people_served", 80, [("youth_served", 130)], "youth_served"),
    ("enrolled vs completed -- should NOT match (different quantities)", "students_completed", 148,
     [("students_enrolled", 162)], None),
    ("unrelated metrics -- should NOT match", "annual_revenue", 900_000,
     [("youth_served", 130), ("total_expenses", 44_000)], None),
]

for label, new_metric, new_value, candidates, expected in cases:
    result = matcher.find_same_metric(new_metric, new_value, candidates)
    status = "PASS" if result == expected else "FAIL"
    print(f"[{status}] {label}")
    print(f"  {new_metric}={new_value} vs {candidates} -> matched: {result} (expected: {expected})")
