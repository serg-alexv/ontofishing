# Cross-model funding monitor bridge

Purpose: keep funding/recruiting state observable across different models without making any model the source of truth.

## Roles

- **Watcher model** (Gemini/Antigravity/Codex/other): high-recall read-only monitoring. It may inspect authorized mail/browser sources, official funding pages, and the repository. It must not send applications, accept contracts, or claim a stage transition from its own inference.
- **Git**: shared, sanitized coordination bus. It stores schemas, public/sanitized state, escalation issues, compiler inputs, and evidence pointers. Do not commit raw private email bodies, credentials, cookies, addresses, bank information, passports, or private attachments.
- **ChatGPT**: verifier/strategist. It can independently re-read connected Gmail and GitHub, audit the watcher event, decide the smallest next action, prepare drafts, and execute only actions authorized in the active conversation.
- **Human owner**: final authority for identity/KYC, relocation claims, contract acceptance, payments, bank/wallet details, publication of private evidence, and irreversible actions.

## State machine

A route may occupy one of these states:

```text
DISCOVERED
  -> QUALIFIED
  -> CONTACTED
  -> REPLIED
  -> ELIGIBILITY_OK | ELIGIBILITY_HOLD
  -> PROPOSAL_REQUESTED
  -> SUBMITTED
  -> UNDER_REVIEW
  -> OFFERED
  -> CONTRACTED
  -> DELIVERING
  -> ACCEPTANCE_PENDING
  -> ACCEPTED
  -> PAYMENT_DUE
  -> PAID
```

Terminal/side states: `DECLINED`, `DEADLINE_PASSED`, `PARKED`, `WITHDRAWN`, `DELIVERY_FAILED`, `UNKNOWN`.

**Evidence rule:** no stage may advance merely because a model says it should. Each transition must carry an evidence pointer and observed timestamp. `PAID` requires settlement evidence, not an award email or sent invoice.

## Watcher event contract

The watcher produces a local/private event record, then may publish only a sanitized escalation pointer to GitHub.

Required fields:

```json
{
  "schema": "funding-event.v1",
  "event_id": "stable-id-or-hash",
  "observed_at": "RFC3339",
  "route_id": "FREEBSD-01",
  "event_type": "HUMAN_REPLY",
  "from_stage": "CONTACTED",
  "proposed_stage": "REPLIED",
  "source_kind": "gmail|official_web|github|other",
  "source_pointer_private": "kept outside public git",
  "sanitized_summary": "one paragraph",
  "deadline": null,
  "requires_chatgpt": true,
  "requires_human": false,
  "dedupe_key": "hash-or-provider-message-id-kept-private",
  "confidence": "direct|provider_representation|inference",
  "next_action_hint": "one sentence"
}
```

## Escalation to ChatGPT

When a material event occurs, the watcher creates or updates a GitHub issue titled:

`[CHATGPT ESCALATION] <route-id> — <event type>`

The issue body must contain only sanitized information:

```text
Observed at:
Route:
Current stage:
Proposed stage:
Sanitized event:
Deadline:
Why material:
Private evidence location: Gmail / local private ledger (do not paste body)
Requested ChatGPT action: verify source -> classify -> propose/draft next move
```

ChatGPT treats the issue as a **hint**, then verifies the source independently before acting.

## Material-event filter

Escalate only:

- human reply or decision;
- eligibility/payment condition;
- invitation to a full proposal or reviewer assignment;
- request for information;
- contract, milestone, acceptance, invoice or payment event;
- delivery failure;
- deadline or promised-response window expiry;
- contradiction that changes whether work should continue.

Do not escalate routine newsletters, duplicate CC copies, unchanged pages, or our own sent mail.

## FreeBSD example — 2026-09-09

Sanitized classification:

- stage: `REPLIED_COMMITTEE_REVIEW_PENDING`;
- technical scope: **not rejected**; proposal committee will review alignment;
- current payment gate: Foundation says it cannot send funds to the applicant's current country; contracting may become possible after a real relocation plus a bank account in another country;
- expected next event: committee response within roughly three weeks on whether to submit a full proposal after relocation;
- next action now: acknowledge briefly if desired, prepare nothing expensive yet, and monitor the promised window;
- prohibited interpretation: not an award, not technical approval, not a reason to fake location/banking.

## Manual compile loop

```text
authorized source
  -> watcher reads
  -> local/private event JSON
  -> sanitized route-state update
  -> git diff
  -> deterministic compiler
  -> dashboard/site
  -> optional GitHub issue escalation
  -> ChatGPT independently verifies material event
```

The site is a projection, not authority. Rebuilding it must not refresh evidence timestamps unless a source was actually rechecked.
