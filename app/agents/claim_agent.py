"""
Rule-based claim triage agent — v2.
Multi-factor scoring: amount, recency, description quality, policy type risk,
claimant history, and fraud pre-screening signals.
"""

from datetime import date, timedelta
from typing import Optional

from app.schemas import TriageResult

# Risk multipliers by policy type
POLICY_TYPE_RISK = {
    "health":   1.2,
    "life":     1.5,
    "auto":     1.0,
    "property": 1.1,
    "travel":   0.9,
}

# Claim amount bands (score contribution, label)
AMOUNT_BANDS = [
    (1_000_000, 0.60, "Extreme claim amount (>= $1M)"),
    (500_000,   0.45, "Very high claim amount (>= $500k)"),
    (200_000,   0.30, "High claim amount (>= $200k)"),
    (100_000,   0.20, "Elevated claim amount (>= $100k)"),
    (50_000,    0.10, "Moderate-high claim amount (>= $50k)"),
]

# Keywords that elevate claim sensitivity
SENSITIVE_KEYWORDS = [
    "critical", "emergency", "hospitalization", "surgery", "death",
    "fatal", "total loss", "fraud", "arson", "theft",
]


def _score_amount(amount: float) -> tuple[float, Optional[str]]:
    for threshold, contribution, label in AMOUNT_BANDS:
        if amount >= threshold:
            return contribution, label
    return 0.0, None


def _score_incident_age(incident_date: Optional[date]) -> tuple[float, Optional[str]]:
    if not incident_date:
        return 0.15, "Incident date missing — cannot assess recency"
    days_ago = (date.today() - incident_date).days
    if days_ago > 365:
        return 0.40, f"Incident reported extremely late ({days_ago} days ago, > 1 year)"
    if days_ago > 180:
        return 0.30, f"Incident reported very late ({days_ago} days ago)"
    if days_ago > 90:
        return 0.15, f"Incident reported late ({days_ago} days ago)"
    return 0.0, None


def _score_description(description: str) -> tuple[float, str]:
    word_count = len(description.split())
    issues: list[str] = []
    score = 0.0

    if word_count < 10:
        score += 0.25
        issues.append(f"Very brief description ({word_count} words)")
    elif word_count < 20:
        score += 0.10
        issues.append(f"Short description ({word_count} words)")

    lower = description.lower()
    hit_keywords = [kw for kw in SENSITIVE_KEYWORDS if kw in lower]
    if hit_keywords:
        score += 0.10
        issues.append(f"Sensitive keywords detected: {', '.join(hit_keywords)}")

    return score, "; ".join(issues) if issues else ""


def _score_policy_type(policy_type: Optional[str]) -> tuple[float, Optional[str]]:
    multiplier = POLICY_TYPE_RISK.get(policy_type or "", 1.0)
    if multiplier > 1.1:
        return 0.10 * (multiplier - 1.0), f"High-risk policy type: {policy_type}"
    return 0.0, None


def _apply_policy_type_multiplier(base_score: float, policy_type: Optional[str]) -> float:
    multiplier = POLICY_TYPE_RISK.get(policy_type or "", 1.0)
    return min(base_score * multiplier, 1.0)


def triage_claim(
    claim: dict,
    policy: Optional[dict] = None,
    claimant_history: Optional[list[dict]] = None,
) -> TriageResult:
    """
    Score a claim dict and return a TriageResult.

    Args:
        claim:            The claim dict to evaluate.
        policy:           Optional policy dict for coverage cross-check and type multiplier.
        claimant_history: Optional list of previous claims by the same claimant.
    """
    score = 0.0
    reasons: list[str] = []

    amount = float(claim.get("claim_amount", 0))
    description: str = claim.get("description", "")
    incident_date = claim.get("incident_date")
    policy_type = policy.get("policy_type") if policy else None

    # 1 — Amount scoring
    amount_score, amount_reason = _score_amount(amount)
    if amount_reason:
        score += amount_score
        reasons.append(amount_reason)

    # 2 — Coverage breach
    if policy and amount > policy.get("coverage_amount", float("inf")):
        score += 0.35
        reasons.append(
            f"Claim ${amount:,.0f} exceeds policy coverage ${policy['coverage_amount']:,.0f}"
        )

    # 3 — Incident age
    age_score, age_reason = _score_incident_age(incident_date)
    if age_reason:
        score += age_score
        reasons.append(age_reason)

    # 4 — Description quality + keywords
    desc_score, desc_reason = _score_description(description)
    if desc_score > 0:
        score += desc_score
        if desc_reason:
            reasons.append(desc_reason)

    # 5 — Claimant history (velocity check)
    if claimant_history:
        cutoff = date.today() - timedelta(days=90)
        recent_count = sum(
            1 for c in claimant_history
            if c.get("incident_date") and c["incident_date"] >= cutoff
        )
        if recent_count >= 3:
            score += 0.20
            reasons.append(f"Claimant has {recent_count} claims in the last 90 days")
        elif recent_count >= 2:
            score += 0.10
            reasons.append(f"Claimant has {recent_count} claims in the last 90 days")

    # 6 — Policy type multiplier
    score = _apply_policy_type_multiplier(score, policy_type)
    pt_score, pt_reason = _score_policy_type(policy_type)
    if pt_reason:
        reasons.append(pt_reason)

    score = min(score, 1.0)

    if score >= 0.70:
        flag = "high"
    elif score >= 0.35:
        flag = "medium"
    else:
        flag = "low"

    if not reasons:
        reasons.append("No significant risk factors detected")

    return TriageResult(
        claim_id=claim["id"],
        risk_score=round(score, 2),
        flag=flag,
        reasons=reasons,
    )
