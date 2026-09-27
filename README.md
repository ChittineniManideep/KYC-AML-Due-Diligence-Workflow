# KYC/AML Due Diligence Workflow
### CDD/EDD risk tiering, UBO ownership chain resolution, sanctions/PEP screening, and periodic review scheduling — built on the FATF risk-based approach

## What's here

| Component | Description |
|---|---|
| `data/` | Simulated entity onboarding records with ownership structures and jurisdiction/risk attributes |
| `risk_tiering/cdd_edd_risk_scoring.py` | FATF-aligned risk scoring, tiering entities into Standard (CDD) vs. Enhanced (EDD) due diligence |
| `ubo_mapping/ubo_ownership_chain.py` | Recursive ownership chain resolution to identify Ultimate Beneficial Owners above the 25% threshold |
| `screening/sanctions_watchlist_screening.py` | Fuzzy name matching against a simulated sanctions/PEP list |
| `review_workflow/periodic_review_scheduler.py` | KYC refresh cadence by risk tier, overdue review detection |
| `docs/fatf_kyc_framework.md` | FATF Recommendations reference — CDD/EDD, PEP, beneficial ownership thresholds |

## Risk tiering

`risk_tiering/cdd_edd_risk_scoring.py` scores each entity across jurisdiction risk, ownership complexity, industry risk, and PEP exposure, producing a Low/Medium/High risk tier that determines whether Standard (CDD) or Enhanced (EDD) due diligence applies — the FATF risk-based approach in practice, not a flat checklist applied identically to every customer.

Run:
```bash
python data/generate_entity_onboarding_data.py
python risk_tiering/cdd_edd_risk_scoring.py
```

## UBO ownership chain resolution

`ubo_mapping/ubo_ownership_chain.py` recursively resolves multi-layer corporate ownership structures to identify natural persons holding, directly or indirectly, above the 25% ownership threshold — the actual mechanical problem UBO identification is, once you get past a single-layer example.

Run:
```bash
python ubo_mapping/ubo_ownership_chain.py
```

## Sanctions/PEP screening

`screening/sanctions_watchlist_screening.py` performs fuzzy name matching (not just exact string match, which real screening never relies on) against a simulated sanctions/PEP list, scoring and ranking potential matches for analyst review.

Run:
```bash
python screening/sanctions_watchlist_screening.py
```

## Periodic review scheduling

`review_workflow/periodic_review_scheduler.py` schedules KYC refresh cadence by risk tier (annual for High risk, longer intervals for Low) and flags entities overdue for review.

Run:
```bash
python review_workflow/periodic_review_scheduler.py
```

## Repo structure

```
kyc-aml-due-diligence-workflow/
├── README.md
├── data/
│   └── generate_entity_onboarding_data.py
├── risk_tiering/
│   └── cdd_edd_risk_scoring.py
├── ubo_mapping/
│   └── ubo_ownership_chain.py
├── screening/
│   └── sanctions_watchlist_screening.py
├── review_workflow/
│   └── periodic_review_scheduler.py
└── docs/
    └── fatf_kyc_framework.md
```
