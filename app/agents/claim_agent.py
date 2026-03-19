"""
Claim Agent — lightweight rule-based agent for auto-triage and fraud signals.
Extend this with an LLM or ML model for production use.
"""
from dataclasses import dataclass
from decimal import Decimal


@dataclass
class TriageResult:
    risk_score: float          # 0.0 – 1.0
    flag: str                  # "low" | "medium" | "high"
    reasons: list[str]


class ClaimAgent:
    """Stateless agent that evaluates a new claim and returns a risk triage."""

    HIGH_AMOUNT_THRESHOLD = Decimal("500000")
    MEDIUM_AMOUNT_THRESHOLD = Decimal("100000")

    def triage(self, claim_amount: Decimal, description: str, incident_date_days_ago: int) -> TriageResult:
        score = 0.0
        reasons: list[str] = []

        if claim_amount >= self.HIGH_AMOUNT_THRESHOLD:
            score += 0.5
            reasons.append("Claim amount is very high")
        elif claim_amount >= self.MEDIUM_AMOUNT_THRESHOLD:
            score += 0.25
            reasons.append("Claim amount is above average")

        if incident_date_days_ago > 180:
            score += 0.3
            reasons.append("Incident reported more than 180 days after occurrence")
        elif incident_date_days_ago > 90:
            score += 0.15
            reasons.append("Incident reported more than 90 days after occurrence")

        if len(description.split()) < 15:
            score += 0.2
            reasons.append("Description is very short — may need more detail")

        score = min(score, 1.0)

        if score >= 0.6:
            flag = "high"
        elif score >= 0.3:
            flag = "medium"
        else:
            flag = "low"

        return TriageResult(risk_score=round(score, 2), flag=flag, reasons=reasons)
