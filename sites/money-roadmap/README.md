# Manual money roadmap site

This directory is a **public generic example and compiler**, not a copy of the owner's funding campaign. No private applications, correspondence, personal financial thresholds, recipient identities, account bindings, or payment records belong in this public repository.

## Build and inspect

Python 3.11+, standard library only:

```sh
python3 -m unittest discover -s sites/money-roadmap -p test_build.py -v
python3 sites/money-roadmap/build.py --input sites/money-roadmap/example.json --out reports/money-roadmap --revision "$(git rev-parse HEAD)"
python3 -m http.server 8787 --bind 127.0.0.1 --directory reports/money-roadmap
```

Open localhost port 8787. Output is static HTML, a reviewed snapshot, and an input/output hash manifest. Building is not deploying. The manual GitHub Actions workflow uploads a public build artifact; it does not create a hosted Pages site or auto-merge anything. Existing scoring and Hugging Face workflows are unchanged.

## Update cycle

1. Read the actual source and classify it as public or private.
2. Edit the appropriate JSON and its source date. Build time must not refresh evidence dates.
3. Review the diff. Public schema allows only generic examples. Free-text review remains mandatory: rejecting emails alone is not a privacy proof.
4. Test, build, inspect desktop/mobile, then commit a review branch.
5. Run the manual public workflow after it is available on the default branch. Do not enable a schedule, provider/API keys, scraping, mail access, or automatic submissions.

Personalised plans use a separate `roadmap.private.v1` file outside public Git and require `--private`. Keep all private output outside public deploy paths. `noindex`, obscure URLs and feature branches do not provide confidentiality.

## Roadmap semantics

Need → sample → offer → written scope → payment terms → delivery → explicit acceptance → credited money. A grant programme's maximum, an unanswered application, an invoice and a payment promise are not received income. An advance may still be refundable. Restricted support and freely disposable earned money remain separate.

The site shows four diagrams: cash transitions, planned timeline, obstacle/fallback branches and the Git/manual compilation process. Each task has an owner, effort cap, dependency, deliverable, transition gate and stop/fallback.

## Copilot review capsule

Review only the generic compiler, example data, tests and workflow. Do not request private campaign data. Verify schema/visibility rejection, unknown fields, duplicate IDs, dependency cycles, date ranges, deterministic output, HTML escaping, mobile readability and local controls. Record commands and actual results; do not auto-merge, deploy, send messages, enable paid resources, or claim financial outcomes. A task document is not evidence that an agent has been assigned or started.
