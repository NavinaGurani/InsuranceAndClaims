"""
Rule-based claim triage agent.
Scores a claim dict and returns a risk flag: low / medium / high.
Easily swappable with an LLM call.
"""

from datetime import date
from app.schemas import TriageResult


def triage_claim(claim: dict) -> TriageResult:
    """Score a claim dict and return a TriageResult."""
    score = 0.0
    reasons: list[str] = []

    amount = float(claim.get("claim_amount", 0))
    description: str = claim.get("description", "")
    incident_date = claim.get("incident_date")

    # Amount-based scoring
    if amount >= 500_000:
        score += 0.5
        reasons.append("Very high claim amount (>= $500k)")
    elif amount >= 100_000:
        score += 0.25
        reasons.append("High claim amount (>= $100k)")

    # Age of incident
    if incident_date:
        days_ago = (date.today() - incident_date).days
        if days_ago > 180:
            score += 0.3
            reasons.append(f"Incident reported very late ({days_ago} days ago)")
        elif days_ago > 90:
            score += 0.15
            reasons.append(f"Incident reported late ({days_ago} days ago)")

    # Description length
    if len(description.split()) < 15:
        score += 0.2
        reasons.append("Description is too brief (< 15 words)")

    score = min(score, 1.0)
    flag = "high" if score >= 0.6 else "medium" if score >= 0.3 else "low"

    if not reasons:
        reasons.append("No significant risk factors detected")

    return TriageResult(
        claim_id=claim["id"],
        risk_score=round(score, 2),
        flag=flag,
        reasons=reasons,
    )
