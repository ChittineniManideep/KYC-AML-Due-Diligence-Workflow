"""
Recursive UBO (Ultimate Beneficial Owner) resolution — walks a multi-layer
corporate ownership structure to find the natural persons who, directly
or indirectly, own above the 25% threshold (the standard FATF/EU AMLD
threshold). This is the actual mechanical problem UBO identification is:
a single-layer "who owns this company" lookup is trivial; the real
problem is multiplying ownership percentages down a chain that may be
several corporate layers deep, and correctly aggregating a person's
total indirect stake when they appear via more than one path.
"""
import pandas as pd
from collections import defaultdict

entities = pd.read_csv("data/entities.csv")
ownership = pd.read_csv("data/ownership_structure.csv")

UBO_THRESHOLD_PCT = 25.0

# Build owner lookup: entity_id -> list of (owner_id, owner_type, pct)
ownership_map = defaultdict(list)
for _, row in ownership.iterrows():
    ownership_map[row.entity_id].append((row.owner_id, row.owner_type, row.ownership_pct))

entity_ids = set(entities.entity_id)


def resolve_ubos(entity_id: str, cumulative_pct: float = 100.0, path: tuple = (), max_depth: int = 6) -> list:
    """Recursively walk the ownership chain. Returns a list of
    (natural_person_name, effective_pct, ownership_path) for every
    natural person reached, at their EFFECTIVE (multiplied-through)
    ownership percentage — not their stated percentage at whatever layer
    they appear."""
    if len(path) >= max_depth:
        return []  # guard against a data error creating an unbounded/circular chain

    results = []
    for owner_id, owner_type, pct in ownership_map.get(entity_id, []):
        effective_pct = cumulative_pct * (pct / 100.0)
        new_path = path + (f"{entity_id} ({pct}%)",)

        if owner_type == "Natural Person":
            results.append((owner_id, round(effective_pct, 2), new_path))
        elif owner_id in entity_ids:
            # corporate owner — recurse further up the chain
            results.extend(resolve_ubos(owner_id, effective_pct, new_path, max_depth))
    return results


def get_ubos_above_threshold(entity_id: str) -> pd.DataFrame:
    all_natural_person_stakes = resolve_ubos(entity_id)

    # A person may reach ownership via multiple paths (e.g. owns two
    # intermediate holding companies that both hold stakes) — their TOTAL
    # effective stake must be aggregated across all paths before testing
    # against the threshold, or a real UBO could be missed by looking at
    # any single path in isolation
    aggregated = defaultdict(float)
    paths_by_person = defaultdict(list)
    for person, pct, path in all_natural_person_stakes:
        aggregated[person] += pct
        paths_by_person[person].append(f"{' -> '.join(path)} -> {person}")

    rows = [
        {"person": person, "total_effective_ownership_pct": round(pct, 2),
         "is_ubo": pct >= UBO_THRESHOLD_PCT, "ownership_paths": paths_by_person[person]}
        for person, pct in aggregated.items()
    ]
    return pd.DataFrame(rows).sort_values("total_effective_ownership_pct", ascending=False) if rows else pd.DataFrame()


if __name__ == "__main__":
    all_results = []
    for entity_id in entities.entity_id:
        ubo_df = get_ubos_above_threshold(entity_id)
        if len(ubo_df) > 0:
            for _, r in ubo_df.iterrows():
                all_results.append({
                    "entity_id": entity_id, "person": r.person,
                    "total_effective_ownership_pct": r.total_effective_ownership_pct,
                    "is_ubo": r.is_ubo,
                })

    results_df = pd.DataFrame(all_results)
    results_df.to_csv("ubo_mapping/ubo_resolution_results.csv", index=False)

    ubos_only = results_df[results_df.is_ubo]
    print(f"Total natural-person ownership stakes resolved: {len(results_df)}")
    print(f"Stakes reaching UBO threshold (>= {UBO_THRESHOLD_PCT}%): {len(ubos_only)}\n")
    print(ubos_only.sort_values(["entity_id", "total_effective_ownership_pct"], ascending=[True, False]).to_string(index=False))

    # Worked example: show the full path for one multi-layer case
    multi_layer_entities = ownership[ownership.owner_type == "Corporate"].entity_id.unique()
    if len(multi_layer_entities) > 0:
        example_id = multi_layer_entities[0]
        print(f"\nWorked example — full UBO resolution for {example_id}:")
        example_ubos = get_ubos_above_threshold(example_id)
        for _, r in example_ubos.iterrows():
            print(f"  {r.person}: {r.total_effective_ownership_pct}% effective — {'UBO' if r.is_ubo else 'below threshold'}")
            for path in r.ownership_paths:
                print(f"    via: {path}")
