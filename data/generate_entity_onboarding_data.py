"""
Synthetic entity onboarding data — corporate customers (lessees, SPVs)
with jurisdiction, industry, and multi-layer ownership structure, the
kind of data a leasing company's KYC function actually works with.
"""
import numpy as np
import pandas as pd

np.random.seed(20)

HIGH_RISK_JURISDICTIONS = ["Jurisdiction-X", "Jurisdiction-Y"]  # placeholder for FATF grey/black list style flagging
STANDARD_JURISDICTIONS = ["Ireland", "United States", "United Kingdom", "Germany", "Singapore", "UAE", "Cayman Islands"]

N_ENTITIES = 25
entities = pd.DataFrame({
    "entity_id": [f"ENT-{3000+i}" for i in range(N_ENTITIES)],
    "entity_name": [f"Client Entity {i+1} Ltd" for i in range(N_ENTITIES)],
    "jurisdiction": np.random.choice(STANDARD_JURISDICTIONS + HIGH_RISK_JURISDICTIONS, N_ENTITIES,
                                       p=[0.20, 0.15, 0.12, 0.10, 0.13, 0.10, 0.10, 0.05, 0.05]),
    "industry": np.random.choice(["Airline Operator", "Leasing SPV", "Investment Holding", "Aviation Services"],
                                  N_ENTITIES, p=[0.35, 0.30, 0.20, 0.15]),
    "entity_type": np.random.choice(["Operating Company", "Special Purpose Vehicle", "Holding Company"],
                                     N_ENTITIES, p=[0.40, 0.35, 0.25]),
})
entities.to_csv("data/entities.csv", index=False)

# --- Ownership structure: some entities are owned by other entities in
# the dataset (multi-layer), some ultimately by named natural persons ---
NATURAL_PERSON_OWNERS = [
    "James Callahan", "Fiona Bergstrom", "Marcus Whitfield", "Elena Kovacs",
    "Rashid Al-Mansoori", "Julia Nakamura", "Declan O'Sullivan", "Priya Ramaswamy",
    "Tobias Lindqvist", "Camille Dubois",
]

ownership_rows = []
for _, e in entities.iterrows():
    n_owners = np.random.choice([1, 2, 3], p=[0.5, 0.35, 0.15])
    remaining_pct = 100.0
    for i in range(n_owners):
        is_corporate_owner = np.random.rand() < 0.4 and len(entities) > 1
        pct = round(remaining_pct if i == n_owners - 1 else remaining_pct * np.random.uniform(0.3, 0.7), 1)
        remaining_pct -= pct

        if is_corporate_owner:
            owner_id = np.random.choice(entities.entity_id[entities.entity_id != e.entity_id])
            owner_name = entities[entities.entity_id == owner_id].entity_name.iloc[0]
            owner_type = "Corporate"
        else:
            owner_name = np.random.choice(NATURAL_PERSON_OWNERS)
            owner_id = owner_name
            owner_type = "Natural Person"

        ownership_rows.append({
            "entity_id": e.entity_id,
            "owner_id": owner_id,
            "owner_name": owner_name,
            "owner_type": owner_type,
            "ownership_pct": max(pct, 0.1),
        })

ownership = pd.DataFrame(ownership_rows)
ownership.to_csv("data/ownership_structure.csv", index=False)

# PEP flags — a small number of natural person owners flagged as PEP
pep_flags = pd.DataFrame({
    "person_name": NATURAL_PERSON_OWNERS,
    "is_pep": [True if i in [2, 7] else False for i in range(len(NATURAL_PERSON_OWNERS))],  # Marcus Whitfield, Priya Ramaswamy
})
pep_flags.to_csv("data/pep_flags.csv", index=False)

print(f"Entities: {len(entities)}, ownership records: {len(ownership)}, natural persons: {len(NATURAL_PERSON_OWNERS)}")
