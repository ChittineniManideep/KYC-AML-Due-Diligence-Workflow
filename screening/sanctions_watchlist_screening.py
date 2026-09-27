"""
Sanctions/PEP watchlist screening via fuzzy name matching — real screening
never relies on exact string match, since names transliterate differently,
have typos, or use different name orderings. This uses a Levenshtein-
distance-based similarity score to rank potential matches for analyst
review, rather than returning a binary match/no-match.
"""
import pandas as pd
from difflib import SequenceMatcher

# Simulated sanctions/PEP watchlist — deliberately includes near-miss
# variants of names in the onboarding dataset, to prove the fuzzy matcher
# catches what an exact-match screen would miss
WATCHLIST = [
    {"listed_name": "Priya Ramaswamy", "list_type": "PEP", "reason": "Senior government official, Jurisdiction-X"},
    {"listed_name": "Marcus Whitfield", "list_type": "PEP", "reason": "Politically exposed — immediate family of former head of state"},
    {"listed_name": "Dmitri Volkov", "list_type": "Sanctions", "reason": "OFAC SDN list — asset freeze"},
    {"listed_name": "Rashid Al-Mansuri", "list_type": "Sanctions", "reason": "EU consolidated list — travel ban (deliberate near-miss spelling to test fuzzy matching against 'Rashid Al-Mansoori')"},
]
watchlist_df = pd.DataFrame(WATCHLIST)

ownership = pd.read_csv("data/ownership_structure.csv")
names_to_screen = ownership[ownership.owner_type == "Natural Person"].owner_name.unique()


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


MATCH_THRESHOLD = 0.75  # below this, treated as no match — tunable based on false-positive tolerance

results = []
for name in names_to_screen:
    for _, w in watchlist_df.iterrows():
        score = similarity(name, w.listed_name)
        if score >= MATCH_THRESHOLD:
            results.append({
                "screened_name": name,
                "watchlist_name": w.listed_name,
                "list_type": w.list_type,
                "reason": w.reason,
                "match_score": round(score, 3),
                "match_type": "Exact" if score == 1.0 else "Fuzzy — requires analyst review",
            })

results_df = pd.DataFrame(results).sort_values("match_score", ascending=False)
results_df.to_csv("screening/screening_hits.csv", index=False)

print(f"Names screened: {len(names_to_screen)}")
print(f"Watchlist entries: {len(watchlist_df)}")
print(f"\nPotential matches (threshold >= {MATCH_THRESHOLD}):")
print(results_df.to_string(index=False))

fuzzy_only = results_df[results_df.match_type.str.startswith("Fuzzy")]
print(f"\n{len(fuzzy_only)} fuzzy match(es) found that an EXACT string match screen would have missed entirely — "
      f"this is why sanctions screening tools use fuzzy matching as standard, not exact match.")
