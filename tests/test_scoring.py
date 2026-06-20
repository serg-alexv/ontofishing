from bounty_wizard.models import Opportunity, Status
from bounty_wizard.scoring import score_opportunity


def base_opportunity(**kwargs):
    data = dict(
        name="Example",
        official_url="https://example.com",
        domain="AI safety",
        status=Status.open,
        status_evidence="Official page says open",
        payout_amount="$10000",
        payout_numeric_usd_estimate=10000,
        eligibility="Independent researchers allowed",
        deliverable="Reproducible submission",
        effort="M",
        domain_fit=1,
        verification_strength=1,
        payout_value=1,
        probability_of_success=1,
        portfolio_value=1,
        deadline_accessibility=1,
        low_admin_friction=1,
    )
    data.update(kwargs)
    return Opportunity.model_validate(data)


def test_high_score_executes_this_week():
    result = score_opportunity(base_opportunity())
    assert result.score >= 85
    assert result.decision == "execute_this_week"


def test_mid_score_prepares_application():
    result = score_opportunity(
        base_opportunity(
            domain_fit=0.7,
            verification_strength=0.7,
            payout_value=0.7,
            probability_of_success=0.7,
            portfolio_value=0.7,
            deadline_accessibility=0.7,
            low_admin_friction=0.7,
        )
    )
    assert 70 <= result.score < 85
    assert result.decision == "prepare_application"


def test_closed_is_hard_reject():
    result = score_opportunity(base_opportunity(status=Status.closed))
    assert result.hard_reject
    assert result.decision == "reject"
    assert any("Status is closed" in r for r in result.reasons)


def test_student_only_is_hard_reject():
    result = score_opportunity(base_opportunity(eligibility="student only"))
    assert result.hard_reject
    assert result.decision == "reject"
    assert any("student only" in r.lower() for r in result.reasons)


def test_missing_status_evidence_warns():
    result = score_opportunity(base_opportunity(status_evidence=""))
    assert any("Missing status evidence" in r for r in result.reasons)
    assert not result.hard_reject
