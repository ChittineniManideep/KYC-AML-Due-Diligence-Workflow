# FATF KYC/AML Framework Reference

| Term | Definition | Where it shows up |
|---|---|---|
| **FATF (Financial Action Task Force)** | The global standard-setter for AML/CFT policy — its 40 Recommendations underpin virtually every jurisdiction's KYC regulation, including Ireland's Criminal Justice (Money Laundering and Terrorist Financing) Act | Whole project's methodology basis |
| **Risk-Based Approach (RBA)** | FATF's core principle: due diligence intensity should match the assessed risk of the customer, not be applied uniformly — a Low risk customer and a High risk customer are not run through the same checklist | `risk_tiering/cdd_edd_risk_scoring.py` |
| **CDD (Customer Due Diligence)** | The standard baseline checks required for every customer: identity verification, understanding the nature of the business relationship, ongoing monitoring | Default tier for Low/Medium risk entities |
| **EDD (Enhanced Due Diligence)** | Additional scrutiny required for higher-risk customers — more extensive source-of-funds/source-of-wealth checks, senior management sign-off, more frequent review | Applied to High risk tier entities |
| **UBO (Ultimate Beneficial Owner)** | The natural person(s) who ultimately own or control a legal entity, directly or through a chain of intermediaries — identifying them is required specifically because corporate structures can otherwise obscure who's really behind a transaction | `ubo_mapping/ubo_ownership_chain.py` |
| **25% ownership threshold** | The standard (FATF/EU AMLD) threshold above which a person is treated as a beneficial owner requiring identification — chosen as a workable line, not because ownership below it is risk-free, which is why entities with no single person crossing 25% still require identifying whoever exercises control by other means | `UBO_THRESHOLD_PCT` |
| **PEP (Politically Exposed Person)** | An individual who holds or has held a prominent public function, or their close associates/family — inherently higher corruption/bribery risk, requiring EDD regardless of other risk factors | `data/pep_flags.csv`, PEP scoring in risk tiering |
| **Sanctions screening** | Checking customers and beneficial owners against government/international sanctions lists (OFAC, EU consolidated list, UN) — a genuine hit blocks the relationship outright, distinct from a PEP flag which triggers EDD rather than automatic refusal | `screening/sanctions_watchlist_screening.py` |
| **Source of Funds / Source of Wealth** | SoF is where the specific funds in a transaction came from; SoW is the broader picture of how the customer accumulated their overall wealth — EDD requires establishing both, not just one | Referenced as part of EDD scope, not separately modelled in this project |
| **Ongoing monitoring / periodic review** | KYC is not a one-time onboarding exercise — FATF requires ongoing monitoring and periodic refresh of customer information, at a frequency proportional to risk | `review_workflow/periodic_review_scheduler.py` |

## Why aircraft leasing specifically has elevated KYC complexity

Aircraft lessees and SPV counterparties are frequently structured through multiple holding layers across jurisdictions (often for legitimate tax/financing reasons — this is standard aviation finance structuring, not inherently suspicious) — which means the UBO resolution problem this project solves (multi-layer ownership, aggregating a person's stake across multiple paths) is not a hypothetical exercise for a leasing company's compliance function. It's close to the actual daily mechanics.
