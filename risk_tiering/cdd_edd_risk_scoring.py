"""
FATF risk-based approach: score each entity across the standard risk
factors (jurisdiction, ownership complexity, industry, PEP exposure) and
tier into Low/Medium/High risk, which determines whether Standard (CDD)
or Enhanced (EDD) due diligence applies. This is the actual mechanism
behind "risk-based" KYC — not every customer gets the same checklist.
"""
import pandas as pd

entities = pd.read_csv("data/entities.csv")
ownership = pd.read_csv("data/ownership_structure.csv")
pep_flags = pd.read_csv("data/pep_flags.csv")

HIGH_RISK_JURISDICTIONS = {"Jurisdiction-X", "Jurisdiction-Y"}
MEDIUM_RISK_JURISDICTIONS = {"Cayman Islands", "UAE", "Singapore"}  # offshore/complex structuring jurisdictions, not inherently high-risk but warrant closer review
HIGH_RISK_INDUSTRIES = {"Investment Holding"}  # opaque holding structures carry more layering risk than an operating airline

def jurisdiction_risk(jurisdiction):
    if jurisdiction in HIGH_RISK_JURISDICTIONS:
        return 40
    elif jurisdiction in MEDIUM_RISK_JURISDICTIONS:
        return 20
    return 5

def industry_risk(industry):
    return 15 if industry in HIGH_RISK_INDUSTRIES else 5

ownership_complexity = ownership.groupby("entity_id").agg(
    owner_count=("owner_id", "count"),
    has_corporate_owner=("owner_type", lambda x: (x == "Corporate").any()),
).reset_index()

pep_exposure = ownership.merge(pep_flags, left_on="owner_name", right_on="person_name", how="left")
pep_exposure["is_pep"] = pep_exposure.is_pep.fillna(False)
pep_by_entity = pep_exposure.groupby("entity_id").is_pep.any().reset_index()
pep_by_entity.columns = ["entity_id", "has_pep_owner"]

scored = entities.merge(ownership_complexity, on="entity_id").merge(pep_by_entity, on="entity_id")

scored["score_jurisdiction"] = scored.jurisdiction.apply(jurisdiction_risk)
scored["score_industry"] = scored.industry.apply(industry_risk)
scored["score_ownership_complexity"] = scored.owner_count.apply(lambda n: min(n * 8, 25)) + scored.has_corporate_owner.map({True: 15, False: 0})
scored["score_pep"] = scored.has_pep_owner.map({True: 30, False: 0})

scored["total_risk_score"] = (
    scored.score_jurisdiction + scored.score_industry
    + scored.score_ownership_complexity + scored.score_pep
)

def tier(score):
    if score >= 50:
        return "High Risk"
    elif score >= 25:
        return "Medium Risk"
    return "Low Risk"

scored["risk_tier"] = scored.total_risk_score.apply(tier)
scored["due_diligence_level"] = scored.risk_tier.map({
    "High Risk": "Enhanced Due Diligence (EDD)",
    "Medium Risk": "Standard CDD + supplementary checks",
    "Low Risk": "Standard CDD",
})

scored_sorted = scored.sort_values("total_risk_score", ascending=False)
scored_sorted.to_csv("risk_tiering/entity_risk_scores.csv", index=False)

print(scored_sorted[["entity_id", "jurisdiction", "industry", "owner_count", "has_pep_owner",
                       "total_risk_score", "risk_tier", "due_diligence_level"]].to_string(index=False))

edd_count = (scored.risk_tier == "High Risk").sum()
print(f"\n{edd_count} of {len(scored)} entities require Enhanced Due Diligence — "
      f"driven primarily by {'PEP exposure' if scored[scored.risk_tier=='High Risk'].has_pep_owner.mean() > 0.5 else 'jurisdiction/ownership complexity'}.")
