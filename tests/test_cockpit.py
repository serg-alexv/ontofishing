from pathlib import Path

from bounty_wizard.cockpit import (
    CHAT_SOURCE_URLS,
    build_project_update,
    load_opportunity_rows,
    score_csv_for_cockpit,
)


def test_project_update_names_private_chat_sources_without_fabricating_content():
    update = build_project_update("Task 1 scoring tests\nTask 5 optional Notion sync")

    assert "Ontofishing project update" in update
    assert "Private ChatGPT source links" in update
    assert CHAT_SOURCE_URLS[0] in update
    assert "Task 1 scoring tests" in update
    assert "unavailable private transcript content" in update


def test_score_csv_for_cockpit_scores_uploaded_rows(tmp_path: Path):
    source_csv = tmp_path / "opportunities.csv"
    source_csv.write_text(
        "name,official_url,domain,status,status_evidence,deadline,payout_amount,payout_numeric_usd_estimate,"
        "eligibility,deliverable,jurisdiction_or_payment_constraints,source_type,effort,domain_fit,"
        "verification_strength,payout_value,probability_of_success,portfolio_value,deadline_accessibility,"
        "low_admin_friction,eligibility_risk,payment_risk,stale_status_risk,competition_noise,notes\n"
        "Memory Prize,https://example.com/memory,AI safety,open,Official page says open,2026-12-31,"
        "$10000,10000,Independent researchers allowed,Reproducible harness,None,official,M,1,1,1,1,1,1,1,0,0,0,0,Demo row\n",
        encoding="utf-8",
    )

    result = score_csv_for_cockpit(source_csv, tmp_path)

    assert result.output_csv.exists()
    assert result.rows[0]["decision"] == "execute_this_week"
    assert result.rows[0]["fit_score"] == "100"
    assert "Scored 1 opportunity" in result.summary


def test_load_opportunity_rows_returns_demo_columns(tmp_path: Path):
    ranked_csv = tmp_path / "ranked.csv"
    ranked_csv.write_text(
        "name,decision,fit_score,bridge_score,official_url,status_evidence\n"
        "Memory Prize,execute_this_week,100,84.7,https://example.com/memory,Raw evidence hidden\n",
        encoding="utf-8",
    )

    rows = load_opportunity_rows(ranked_csv)

    assert rows == [
        {
            "name": "Memory Prize",
            "decision": "execute_this_week",
            "fit_score": "100",
            "bridge_score": "84.7",
            "official_url": "https://example.com/memory",
        }
    ]
