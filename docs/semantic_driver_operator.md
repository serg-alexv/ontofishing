# Semantic / Domain Driver Operator

Purpose: add a second-model semantic review layer without giving it ownership of the deterministic scorer.

Roles:

- Codex: repo maintainer, tests, deterministic importer/scorer.
- Grok: high-recall online discovery worker.
- Gemini CLI or Antigravity (`agy`): semantic/domain operator.
- ChatGPT/human: final adversarial audit and execution strategy.

The semantic operator must not rewrite `src/bounty_wizard/scoring.py` directly. It reads raw/ranked opportunity CSV and emits annotation JSON only.

Allowed outputs:

```json
{
  "annotations": [
    {
      "name": "Opportunity name exactly as in CSV when possible",
      "official_url": "https://official.example/path",
      "domain_tags": ["AI safety", "agentic evaluation"],
      "semantic_summary": "One-sentence technical interpretation.",
      "independent_researcher_angle": "How an independent researcher/engineer can credibly approach it.",
      "best_application_angle": "Concrete proposal/product/report angle.",
      "hidden_constraints": ["Possible U.S.-only prize payment"],
      "questions_to_verify": ["Does non-U.S. team member receive money?"],
      "suggested_action": "execute_this_week|prepare_application|monitor|reject",
      "confidence": 0.0
    }
  ]
}
```

Import flow:

```bash
scripts/gemini_domain_driver.sh data/ranked_opportunities.csv
# or
scripts/agy_domain_driver.sh data/ranked_opportunities.csv

python scripts/import_semantic_annotations.py \
  data/ranked_opportunities.csv \
  data/semantic_runs/<run>.json \
  --out data/ranked_opportunities.semantic.csv
```

Boundary rule: semantic annotations are advisory context only. The deterministic `score` and `decision` columns remain the source of truth unless a human/Codex deliberately changes the scoring rubric and tests.
