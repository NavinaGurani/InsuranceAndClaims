"""
In-memory mock data stores. All data lives here — no database required.
Mutate these dicts/lists directly from route handlers.
"""

from datetime import date, datetime

# ── Users ──────────────────────────────────────────────────────────────────────
USERS: dict[int, dict] = {
    1: {
        "id": 1,
        "email": "admin@insure.io",
        "full_name": "Alice Admin",
        "role": "admin",
        "is_active": True,
        "created_at": datetime(2024, 1, 1),
    },
    2: {
        "id": 2,
        "email": "agent@insure.io",
        "full_name": "Bob Agent",
        "role": "agent",
        "is_active": True,
        "created_at": datetime(2024, 1, 2),
    },
    3: {
        "id": 3,
        "email": "customer@insure.io",
        "full_name": "Carol Customer",
        "role": "customer",
        "is_active": True,
        "created_at": datetime(2024, 1, 3),
    },
    4: {
        "id": 4,
        "email": "dave@insure.io",
        "full_name": "Dave Doe",
        "role": "customer",
        "is_active": True,
        "created_at": datetime(2024, 2, 1),
    },
}

# ── Policies ───────────────────────────────────────────────────────────────────
POLICIES: dict[int, dict] = {
    1: {
        "id": 1,
        "policy_number": "POL-0001",
        "owner_id": 3,
        "policy_type": "health",
        "status": "active",
        "coverage_amount": 500000.00,
        "premium_amount": 1200.00,
        "start_date": date(2024, 1, 1),
        "end_date": date(2025, 1, 1),
        "description": "Comprehensive health coverage for Carol.",
        "created_at": datetime(2024, 1, 5),
    },
    2: {
        "id": 2,
        "policy_number": "POL-0002",
        "owner_id": 3,
        "policy_type": "auto",
        "status": "active",
        "coverage_amount": 150000.00,
        "premium_amount": 600.00,
        "start_date": date(2024, 3, 1),
        "end_date": date(2025, 3, 1),
        "description": "Auto insurance for Carol's sedan.",
        "created_at": datetime(2024, 3, 1),
    },
    3: {
        "id": 3,
        "policy_number": "POL-0003",
        "owner_id": 4,
        "policy_type": "life",
        "status": "active",
        "coverage_amount": 1000000.00,
        "premium_amount": 2500.00,
        "start_date": date(2024, 2, 1),
        "end_date": date(2034, 2, 1),
        "description": "20-year term life policy for Dave.",
        "created_at": datetime(2024, 2, 5),
    },
    4: {
        "id": 4,
        "policy_number": "POL-0004",
        "owner_id": 4,
        "policy_type": "property",
        "status": "expired",
        "coverage_amount": 300000.00,
        "premium_amount": 900.00,
        "start_date": date(2023, 1, 1),
        "end_date": date(2024, 1, 1),
        "description": "Home insurance — expired.",
        "created_at": datetime(2023, 1, 10),
    },
}

# ── Claims ─────────────────────────────────────────────────────────────────────
CLAIMS: dict[int, dict] = {
    1: {
        "id": 1,
        "claim_number": "CLM-0001",
        "policy_id": 1,
        "claimant_id": 3,
        "status": "approved",
        "claim_amount": 25000.00,
        "incident_date": date(2024, 4, 10),
        "description": "Hospitalization due to appendix surgery. All bills attached.",
        "reviewer_notes": "Verified with hospital. Approved.",
        "created_at": datetime(2024, 4, 15),
    },
    2: {
        "id": 2,
        "claim_number": "CLM-0002",
        "policy_id": 2,
        "claimant_id": 3,
        "status": "under_review",
        "claim_amount": 8000.00,
        "incident_date": date(2024, 6, 1),
        "description": "Minor collision in parking lot. Bumper damage.",
        "reviewer_notes": None,
        "created_at": datetime(2024, 6, 5),
    },
    3: {
        "id": 3,
        "claim_number": "CLM-0003",
        "policy_id": 3,
        "claimant_id": 4,
        "status": "submitted",
        "claim_amount": 50000.00,
        "incident_date": date(2024, 7, 20),
        "description": "Critical illness diagnosed. Requesting partial benefit payout.",
        "reviewer_notes": None,
        "created_at": datetime(2024, 7, 22),
    },
    4: {
        "id": 4,
        "claim_number": "CLM-0004",
        "policy_id": 1,
        "claimant_id": 3,
        "status": "rejected",
        "claim_amount": 5000.00,
        "incident_date": date(2023, 12, 1),
        "description": "Dental procedure claim.",
        "reviewer_notes": "Dental not covered under this health plan.",
        "created_at": datetime(2024, 1, 10),
    },
    5: {
        "id": 5,
        "claim_number": "CLM-0005",
        "policy_id": 1,
        "claimant_id": 3,
        "status": "paid",
        "claim_amount": 12000.00,
        "incident_date": date(2024, 2, 14),
        "description": "Emergency room visit for fracture.",
        "reviewer_notes": "Approved and disbursed.",
        "created_at": datetime(2024, 2, 20),
    },
}

# ── Payments ───────────────────────────────────────────────────────────────────
PAYMENTS: dict[int, dict] = {
    1: {
        "id": 1,
        "transaction_id": "TXN-0001",
        "policy_id": 1,
        "payer_id": 3,
        "amount": 1200.00,
        "status": "completed",
        "method": "card",
        "reference": "STRIPE-abc123",
        "created_at": datetime(2024, 1, 5),
    },
    2: {
        "id": 2,
        "transaction_id": "TXN-0002",
        "policy_id": 2,
        "payer_id": 3,
        "amount": 600.00,
        "status": "completed",
        "method": "bank_transfer",
        "reference": "BANK-xyz456",
        "created_at": datetime(2024, 3, 2),
    },
    3: {
        "id": 3,
        "transaction_id": "TXN-0003",
        "policy_id": 3,
        "payer_id": 4,
        "amount": 2500.00,
        "status": "completed",
        "method": "upi",
        "reference": "UPI-789qrs",
        "created_at": datetime(2024, 2, 6),
    },
    4: {
        "id": 4,
        "transaction_id": "TXN-0004",
        "policy_id": 2,
        "payer_id": 3,
        "amount": 600.00,
        "status": "pending",
        "method": "wallet",
        "reference": None,
        "created_at": datetime(2024, 6, 10),
    },
}

# ── Counters for auto-incrementing IDs ─────────────────────────────────────────
NEXT_IDS: dict[str, int] = {
    "user": 5,
    "policy": 5,
    "claim": 6,
    "payment": 5,
}

# ── Valid state transitions for claims ─────────────────────────────────────────
CLAIM_TRANSITIONS: dict[str, list[str]] = {
    "submitted":    ["under_review"],
    "under_review": ["approved", "rejected"],
    "approved":     ["paid"],
    "rejected":     [],
    "paid":         [],
}
