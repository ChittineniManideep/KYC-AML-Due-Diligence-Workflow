"""
KYC periodic review scheduling — refresh cadence is risk-tier dependent
(annual for High risk, longer for Low), and this flags entities overdue
for their next review. Ongoing monitoring, not just onboarding, is a
core FATF risk-based-approach requirement.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

np.random.seed(21)

risk_scores = pd.read_csv("risk_tiering/entity_risk_scores.csv")

REVIEW_CYCLE_MONTHS = {"High Risk": 12, "Medium Risk": 24, "Low Risk": 36}

today = datetime(2026, 9, 1)
last_review = [today - timedelta(days=int(np.random.uniform(30, 900))) for _ in range(len(risk_scores))]

review_data = risk_scores[["entity_id", "risk_tier", "due_diligence_level"]].copy()
review_data["last_review_date"] = [d.strftime("%Y-%m-%d") for d in last_review]
review_data["review_cycle_months"] = review_data.risk_tier.map(REVIEW_CYCLE_MONTHS)
review_data["next_review_due"] = [
    (d + timedelta(days=int(c * 30.4))).strftime("%Y-%m-%d")
    for d, c in zip(last_review, review_data.review_cycle_months)
]
review_data["days_overdue"] = [
    (today - datetime.strptime(nr, "%Y-%m-%d")).days
    for nr in review_data.next_review_due
]
review_data["review_status"] = review_data.days_overdue.apply(
    lambda d: f"OVERDUE by {d} days" if d > 0 else "Current"
)

review_data.to_csv("review_workflow/review_schedule.csv", index=False)

print(review_data[["entity_id", "risk_tier", "review_cycle_months", "next_review_due", "review_status"]].to_string(index=False))

overdue = review_data[review_data.days_overdue > 0]
overdue_high_risk = overdue[overdue.risk_tier == "High Risk"]
print(f"\nTotal overdue reviews: {len(overdue)} of {len(review_data)}")
print(f"Overdue HIGH RISK reviews (compliance priority — EDD entities cannot lapse): {len(overdue_high_risk)}")
if len(overdue_high_risk) > 0:
    print(overdue_high_risk[["entity_id", "days_overdue"]].sort_values("days_overdue", ascending=False).to_string(index=False))
