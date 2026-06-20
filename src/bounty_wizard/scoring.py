from __future__ import annotations

from dataclasses import dataclass
from .models import Opportunity, Status


HARD_REJECT_TERMS = [
    "closed",
    "expired",
    "student only",
    "students only",
    "company only",
    "companies only",
    "institutional nomination",
    "invite only",
    "no payout",
    "exposure only",
]


@dataclass
class ScoreResult:
    score: float
    decision: str
    hard_reject: bool
    reasons: list[str]


def score_opportunity(o: Opportunity) -> ScoreResult:
    reasons: list[str] = []
    text_blob = " ".join([
        o.status.value,
        o.status_evidence,
        o.eligibility,
        o.deliverable,
        o.jurisdiction_or_payment_constraints,
        o.notes,
    ]).lower()

    hard_reject = False
    if o.status == Status.closed:
        hard_reject = True
        reasons.append("Status is closed.")

    for term in HARD_REJECT_TERMS:
        if term in text_blob:
            hard_reject = True
            reasons.append(f"Contains hard-reject term: {term!r}.")

    if not o.status_evidence.strip():
        reasons.append("Missing status evidence.")
    if not o.deliverable.strip():
        reasons.append("Missing deliverable clarity.")
    if not o.payout_amount and o.payout_numeric_usd_estimate <= 0:
        reasons.append("No payout/funding amount captured.")

    score = (
        25 * o.domain_fit
        + 20 * o.verification_strength
        + 15 * o.payout_value
        + 15 * o.probability_of_success
        + 10 * o.portfolio_value
        + 10 * o.deadline_accessibility
        + 5 * o.low_admin_friction
        - 20 * o.eligibility_risk
        - 15 * o.payment_risk
        - 15 * o.stale_status_risk
        - 10 * o.competition_noise
    )
    score = max(0, min(100, round(score, 1)))

    if hard_reject:
        decision = "reject"
    elif score >= 85:
        decision = "execute_this_week"
    elif score >= 70:
        decision = "prepare_application"
    elif score >= 55:
        decision = "monitor"
    else:
        decision = "reject"

    return ScoreResult(score=score, decision=decision, hard_reject=hard_reject, reasons=reasons)
