"""
Fraud Detection Service — multi-factor scoring across claims, payments, and policies.

Flags suspicious patterns:
  - Multiple high-value claims in a short window
  - Claim amounts exceeding policy coverage
  - Rapid repeated claims on same policy
  - Payment anomalies (large amounts, mismatched payer)
"""

from datetime import date, timedelta
from typing import Optional


FRAUD_SCORE_THRESHOLD_HIGH   = 0.75
FRAUD_SCORE_THRESHOLD_MEDIUM = 0.45

# Weights for each signal
SIGNAL_WEIGHTS = {
    "exceeds_coverage":        0.40,
    "rapid_repeat_claim":      0.30,
    "claim_velocity_high":     0.25,
    "late_reporting":          0.20,
    "payment_mismatch":        0.35,
    "duplicate_description":   0.20,
    "suspicious_amount_round": 0.10,
}


def _check_exceeds_coverage(claim: dict, policies: dict) -> tuple[float, Optional[str]]:
    policy = policies.get(claim["policy_id"])
    if not policy:
        return 0.0, None
    if claim["claim_amount"] > policy["coverage_amount"]:
        return SIGNAL_WEIGHTS["exceeds_coverage"], (
            f"Claim amount ${claim['claim_amount']:,.0f} exceeds "
            f"policy coverage ${policy['coverage_amount']:,.0f}"
        )
    return 0.0, None


def _check_rapid_repeat(claim: dict, all_claims: dict) -> tuple[float, Optional[str]]:
    same_policy_claims = [
        c for c in all_claims.values()
        if c["policy_id"] == claim["policy_id"] and c["id"] != claim["id"]
    ]
    # Look for any other claim on the same policy within 30 days
    incident = claim.get("incident_date")
    if not incident:
        return 0.0, None
    window_start = incident - timedelta(days=30)
    window_end   = incident + timedelta(days=30)
    nearby = [
        c for c in same_policy_claims
        if window_start <= c.get("incident_date", date.min) <= window_end
    ]
    if len(nearby) >= 2:
        return SIGNAL_WEIGHTS["rapid_repeat_claim"], (
            f"{len(nearby)} claims on policy {claim['policy_id']} within 30-day window"
        )
    return 0.0, None


def _check_claim_velocity(claimant_id: int, all_claims: dict) -> tuple[float, Optional[str]]:
    """Flag claimants with > 3 claims in the last 90 days."""
    cutoff = date.today() - timedelta(days=90)
    recent = [
        c for c in all_claims.values()
        if c["claimant_id"] == claimant_id
        and c.get("incident_date", date.min) >= cutoff
    ]
    if len(recent) > 3:
        return SIGNAL_WEIGHTS["claim_velocity_high"], (
            f"Claimant {claimant_id} has {len(recent)} claims in the past 90 days"
        )
    return 0.0, None


def _check_late_reporting(claim: dict) -> tuple[float, Optional[str]]:
    incident = claim.get("incident_date")
    if not incident:
        return 0.0, None
    days_late = (date.today() - incident).days
    if days_late > 365:
        return SIGNAL_WEIGHTS["late_reporting"], (
            f"Claim reported {days_late} days after incident (> 1 year)"
        )
    return 0.0, None


def _check_suspicious_amount(claim: dict) -> tuple[float, Optional[str]]:
    amount = claim.get("claim_amount", 0)
    # Round numbers like 100000, 50000, 250000 are suspicious
    if amount >= 1000 and amount % 10000 == 0:
        return SIGNAL_WEIGHTS["suspicious_amount_round"], (
            f"Claim amount ${amount:,.0f} is a suspiciously round number"
        )
    return 0.0, None


def _check_duplicate_description(claim: dict, all_claims: dict) -> tuple[float, Optional[str]]:
    desc = claim.get("description", "").strip().lower()
    duplicates = [
        c for c in all_claims.values()
        if c["id"] != claim["id"]
        and c.get("description", "").strip().lower() == desc
        and desc != ""
    ]
    if duplicates:
        ids = [str(c["id"]) for c in duplicates]
        return SIGNAL_WEIGHTS["duplicate_description"], (
            f"Description matches claim(s): {', '.join(ids)}"
        )
    return 0.0, None


def analyze_claim_fraud(claim: dict, all_claims: dict, policies: dict) -> dict:
    """
    Run all fraud signals against a claim.
    Returns a fraud report dict with score, level, and triggered signals.
    """
    total_score = 0.0
    signals: list[str] = []

    checks = [
        _check_exceeds_coverage(claim, policies),
        _check_rapid_repeat(claim, all_claims),
        _check_claim_velocity(claim["claimant_id"], all_claims),
        _check_late_reporting(claim),
        _check_suspicious_amount(claim),
        _check_duplicate_description(claim, all_claims),
    ]

    for weight, reason in checks:
        if reason:
            total_score += weight
            signals.append(reason)

    total_score = min(total_score, 1.0)

    if total_score >= FRAUD_SCORE_THRESHOLD_HIGH:
        level = "high"
    elif total_score >= FRAUD_SCORE_THRESHOLD_MEDIUM:
        level = "medium"
    else:
        level = "low"

    return {
        "claim_id":    claim["id"],
        "fraud_score": round(total_score, 3),
        "fraud_level": level,
        "signals":     signals if signals else ["No fraud indicators detected"],
        "auto_flag":   total_score >= FRAUD_SCORE_THRESHOLD_HIGH,
    }


def analyze_payment_anomaly(payment: dict, policies: dict, all_payments: dict) -> dict:
    """
    Detect anomalies in a payment record.
    Checks for: amount mismatch vs premium, payer/policy ownership mismatch, duplicate transactions.
    """
    anomalies: list[str] = []
    score = 0.0

    policy = policies.get(payment.get("policy_id"))

    if policy:
        # Amount significantly deviates from expected premium
        expected = policy.get("premium_amount", 0)
        actual   = payment.get("amount", 0)
        if expected > 0 and abs(actual - expected) / expected > 0.5:
            score += 0.30
            anomalies.append(
                f"Payment amount ${actual:,.0f} deviates >50% from expected premium ${expected:,.0f}"
            )

        # Payer does not own the policy
        if policy["owner_id"] != payment.get("payer_id"):
            score += SIGNAL_WEIGHTS["payment_mismatch"]
            anomalies.append(
                f"Payer {payment['payer_id']} does not own policy {policy['id']} "
                f"(owned by {policy['owner_id']})"
            )

    # Duplicate transaction check (same policy + amount + method within 1 day)
    created = payment.get("created_at")
    if created:
        dupes = [
            p for p in all_payments.values()
            if p["id"] != payment["id"]
            and p["policy_id"] == payment["policy_id"]
            and p["amount"] == payment["amount"]
            and p["method"] == payment["method"]
            and abs((p["created_at"] - created).total_seconds()) < 86400
        ]
        if dupes:
            score += 0.25
            anomalies.append(f"Possible duplicate transaction — {len(dupes)} similar payment(s) found")

    score = min(score, 1.0)
    return {
        "payment_id":     payment["id"],
        "anomaly_score":  round(score, 3),
        "anomaly_level":  "high" if score >= 0.6 else "medium" if score >= 0.3 else "low",
        "anomalies":      anomalies if anomalies else ["No anomalies detected"],
        "hold_for_review": score >= 0.6,
    }
