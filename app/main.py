"""
Insurance & Claims Management API — simplified sample project.
Uses in-memory mock data; no database required.

Auth: pass `user_id` as a query parameter (e.g. ?user_id=1).
  user 1 = admin, user 2 = agent, user 3/4 = customer
"""

from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app.mock_data import (
    USERS, POLICIES, CLAIMS, PAYMENTS, NEXT_IDS, CLAIM_TRANSITIONS,
)
from app.schemas import (
    UserCreate, UserOut,
    PolicyCreate, PolicyUpdate, PolicyOut,
    ClaimCreate, ClaimStatusUpdate, ClaimOut,
    PaymentCreate, PaymentOut,
    TriageResult,
    FraudReport, PaymentAnomalyReport,
    BulkClaimStatusUpdate, BulkClaimStatusResult,
)
from app.agents.claim_agent import triage_claim
from app.services.fraud_detection import analyze_claim_fraud, analyze_payment_anomaly

app = FastAPI(
    title="Insurance & Claims API (Mock)",
    version="1.0.0",
    description="Sample project with in-memory mock data. Pass ?user_id=1/2/3/4 to simulate auth.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Helpers ────────────────────────────────────────────────────────────────────

def get_user(user_id: int) -> dict:
    user = USERS.get(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Unknown user_id")
    return user


def next_id(entity: str) -> int:
    uid = NEXT_IDS[entity]
    NEXT_IDS[entity] += 1
    return uid


def check_policy_access(policy: dict, user: dict) -> None:
    if user["role"] == "customer" and policy["owner_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")


def check_claim_access(claim: dict, user: dict) -> None:
    if user["role"] == "customer" and claim["claimant_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")


def check_payment_access(payment: dict, user: dict) -> None:
    if user["role"] == "customer" and payment["payer_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")


# ── Health ─────────────────────────────────────────────────────────────────────

@app.get("/health", tags=["health"])
def health():
    return {"status": "ok", "data": "in-memory mock"}


# ── Users ──────────────────────────────────────────────────────────────────────

@app.get("/api/v1/users", response_model=list[UserOut], tags=["users"])
def list_users(user_id: int = Query(...)):
    user = get_user(user_id)
    if user["role"] not in ("admin", "agent"):
        raise HTTPException(status_code=403, detail="Admins and agents only")
    return list(USERS.values())


@app.post("/api/v1/users", response_model=UserOut, status_code=201, tags=["users"])
def create_user(body: UserCreate, user_id: int = Query(...)):
    user = get_user(user_id)
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    if any(u["email"] == body.email for u in USERS.values()):
        raise HTTPException(status_code=409, detail="Email already exists")
    uid = next_id("user")
    new_user = {
        "id": uid,
        "email": body.email,
        "full_name": body.full_name,
        "role": body.role,
        "is_active": True,
        "created_at": datetime.utcnow(),
    }
    USERS[uid] = new_user
    return new_user


# ── Policies ───────────────────────────────────────────────────────────────────

@app.get("/api/v1/policies", response_model=list[PolicyOut], tags=["policies"])
def list_policies(user_id: int = Query(...)):
    user = get_user(user_id)
    if user["role"] == "customer":
        return [p for p in POLICIES.values() if p["owner_id"] == user["id"]]
    return list(POLICIES.values())


@app.get("/api/v1/policies/{policy_id}", response_model=PolicyOut, tags=["policies"])
def get_policy(policy_id: int, user_id: int = Query(...)):
    user = get_user(user_id)
    policy = POLICIES.get(policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    check_policy_access(policy, user)
    return policy


@app.post("/api/v1/policies", response_model=PolicyOut, status_code=201, tags=["policies"])
def create_policy(body: PolicyCreate, user_id: int = Query(...)):
    user = get_user(user_id)
    pid = next_id("policy")
    policy = {
        "id": pid,
        "policy_number": f"POL-{pid:04d}",
        "owner_id": user["id"],
        "policy_type": body.policy_type,
        "status": "pending",
        "coverage_amount": body.coverage_amount,
        "premium_amount": body.premium_amount,
        "start_date": body.start_date,
        "end_date": body.end_date,
        "description": body.description,
        "created_at": datetime.utcnow(),
    }
    POLICIES[pid] = policy
    return policy


@app.patch("/api/v1/policies/{policy_id}", response_model=PolicyOut, tags=["policies"])
def update_policy(policy_id: int, body: PolicyUpdate, user_id: int = Query(...)):
    user = get_user(user_id)
    if user["role"] not in ("admin", "agent"):
        raise HTTPException(status_code=403, detail="Admins and agents only")
    policy = POLICIES.get(policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    if body.status is not None:
        policy["status"] = body.status
    if body.description is not None:
        policy["description"] = body.description
    return policy


# ── Claims ─────────────────────────────────────────────────────────────────────

@app.get("/api/v1/claims", response_model=list[ClaimOut], tags=["claims"])
def list_claims(user_id: int = Query(...)):
    user = get_user(user_id)
    if user["role"] == "customer":
        return [c for c in CLAIMS.values() if c["claimant_id"] == user["id"]]
    return list(CLAIMS.values())


@app.get("/api/v1/claims/{claim_id}", response_model=ClaimOut, tags=["claims"])
def get_claim(claim_id: int, user_id: int = Query(...)):
    user = get_user(user_id)
    claim = CLAIMS.get(claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    check_claim_access(claim, user)
    return claim


@app.post("/api/v1/claims", response_model=ClaimOut, status_code=201, tags=["claims"])
def create_claim(body: ClaimCreate, user_id: int = Query(...)):
    user = get_user(user_id)
    policy = POLICIES.get(body.policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    if user["role"] == "customer" and policy["owner_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="You do not own this policy")
    cid = next_id("claim")
    claim = {
        "id": cid,
        "claim_number": f"CLM-{cid:04d}",
        "policy_id": body.policy_id,
        "claimant_id": user["id"],
        "status": "submitted",
        "claim_amount": body.claim_amount,
        "incident_date": body.incident_date,
        "description": body.description,
        "reviewer_notes": None,
        "created_at": datetime.utcnow(),
    }
    CLAIMS[cid] = claim
    return claim


@app.patch("/api/v1/claims/{claim_id}/status", response_model=ClaimOut, tags=["claims"])
def update_claim_status(claim_id: int, body: ClaimStatusUpdate, user_id: int = Query(...)):
    user = get_user(user_id)
    if user["role"] not in ("admin", "agent"):
        raise HTTPException(status_code=403, detail="Admins and agents only")
    claim = CLAIMS.get(claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    allowed = CLAIM_TRANSITIONS.get(claim["status"], [])
    if body.status not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot transition from '{claim['status']}' to '{body.status}'. Allowed: {allowed}",
        )
    claim["status"] = body.status
    if body.reviewer_notes is not None:
        claim["reviewer_notes"] = body.reviewer_notes
    return claim


@app.get("/api/v1/claims/{claim_id}/triage", response_model=TriageResult, tags=["claims"])
def triage(claim_id: int, user_id: int = Query(...)):
    user = get_user(user_id)
    if user["role"] not in ("admin", "agent"):
        raise HTTPException(status_code=403, detail="Admins and agents only")
    claim = CLAIMS.get(claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    policy = POLICIES.get(claim["policy_id"])
    claimant_history = [
        c for c in CLAIMS.values()
        if c["claimant_id"] == claim["claimant_id"] and c["id"] != claim_id
    ]
    return triage_claim(claim, policy=policy, claimant_history=claimant_history)


@app.get("/api/v1/claims/{claim_id}/fraud", response_model=FraudReport, tags=["claims"])
def fraud_analysis(claim_id: int, user_id: int = Query(...)):
    user = get_user(user_id)
    if user["role"] not in ("admin", "agent"):
        raise HTTPException(status_code=403, detail="Admins and agents only")
    claim = CLAIMS.get(claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    return analyze_claim_fraud(claim, all_claims=CLAIMS, policies=POLICIES)


@app.post("/api/v1/claims/bulk-status", response_model=BulkClaimStatusResult, tags=["claims"])
def bulk_update_claim_status(body: BulkClaimStatusUpdate, user_id: int = Query(...)):
    user = get_user(user_id)
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    updated, skipped, errors = [], [], []
    for cid in body.claim_ids:
        claim = CLAIMS.get(cid)
        if not claim:
            errors.append(f"Claim {cid} not found")
            continue
        allowed = CLAIM_TRANSITIONS.get(claim["status"], [])
        if body.status not in allowed:
            skipped.append(cid)
            errors.append(
                f"Claim {cid}: cannot transition '{claim['status']}' → '{body.status}'"
            )
            continue
        claim["status"] = body.status
        if body.reviewer_notes is not None:
            claim["reviewer_notes"] = body.reviewer_notes
        updated.append(cid)
    return BulkClaimStatusResult(updated=updated, skipped=skipped, errors=errors)


# ── Payments ───────────────────────────────────────────────────────────────────

@app.get("/api/v1/payments", response_model=list[PaymentOut], tags=["payments"])
def list_payments(user_id: int = Query(...)):
    user = get_user(user_id)
    if user["role"] == "customer":
        return [p for p in PAYMENTS.values() if p["payer_id"] == user["id"]]
    return list(PAYMENTS.values())


@app.get("/api/v1/payments/{payment_id}", response_model=PaymentOut, tags=["payments"])
def get_payment(payment_id: int, user_id: int = Query(...)):
    user = get_user(user_id)
    payment = PAYMENTS.get(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    check_payment_access(payment, user)
    return payment


@app.post("/api/v1/payments", response_model=PaymentOut, status_code=201, tags=["payments"])
def create_payment(body: PaymentCreate, user_id: int = Query(...)):
    user = get_user(user_id)
    policy = POLICIES.get(body.policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    if user["role"] == "customer" and policy["owner_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="You do not own this policy")

    # Pre-flight anomaly check on the candidate payment record
    candidate = {
        "id": -1,
        "policy_id": body.policy_id,
        "payer_id": user["id"],
        "amount": body.amount,
        "method": body.method,
        "created_at": datetime.utcnow(),
    }
    anomaly = analyze_payment_anomaly(candidate, policies=POLICIES, all_payments=PAYMENTS)
    if anomaly["hold_for_review"] and not body.fraud_override:
        raise HTTPException(
            status_code=402,
            detail={
                "message": "Payment held for fraud review. Use fraud_override=true to force (admin only).",
                "anomaly_score": anomaly["anomaly_score"],
                "anomalies": anomaly["anomalies"],
            },
        )
    if body.fraud_override and user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins may override fraud holds")

    pid = next_id("payment")
    payment = {
        "id": pid,
        "transaction_id": f"TXN-{pid:04d}",
        "policy_id": body.policy_id,
        "payer_id": user["id"],
        "amount": body.amount,
        "status": "completed",
        "method": body.method,
        "reference": f"MOCK-REF-{pid:04d}",
        "created_at": datetime.utcnow(),
    }
    PAYMENTS[pid] = payment
    return payment


@app.get("/api/v1/payments/{payment_id}/anomaly", response_model=PaymentAnomalyReport, tags=["payments"])
def payment_anomaly(payment_id: int, user_id: int = Query(...)):
    user = get_user(user_id)
    if user["role"] not in ("admin", "agent"):
        raise HTTPException(status_code=403, detail="Admins and agents only")
    payment = PAYMENTS.get(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return analyze_payment_anomaly(payment, policies=POLICIES, all_payments=PAYMENTS)
