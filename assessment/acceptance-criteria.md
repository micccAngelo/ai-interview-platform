# Evidence before rating

Scope recorded before implementation, 29 October 2026.

## Problem and product decision

Recruiters need to distinguish a demonstrated skill gap from an interview that did not collect enough evidence. The current `to_i.clamp(1, 5)` turns missing, malformed and out-of-range ratings into apparently valid ratings. Replacement writes also delete results before validating all rows. The fit/gap UI reads a different field name from the API.

Ship one complete slice: model response -> validated portfolio -> human review -> deterministic vacancy comparison -> export. A rating is a model interpretation supported by a verified candidate quote, never a hiring decision or proof of skill. No culture inference is justified by skill-level arithmetic alone.

## Acceptance criteria

1. Every configured skill appears, including an omitted or untouched skill. Missing evidence never becomes L1.
2. Only an integer 1..5, a known confidence, a nonblank bounded summary, and 1..3 candidate transcript excerpts can produce an assessed rating. Numeric strings, booleans, floats, null, 0 and 6 are not coerced.
3. Evidence must occur within a candidate turn after whitespace normalization. AI-only text and invented quotes cannot support a rating. This establishes provenance, not semantic relevance or model calibration.
4. `not_yet` coverage, absent coverage, omitted skills and invalid ratings produce an explicit not-assessed reason. Confidence cannot exceed the coverage-derived ceiling.
5. Unknown or duplicate configured/discovered identities, invalid array/object shapes and invalid JSON fail the generation without replacing any existing skill rows.
6. All replacement rows and completion status commit together. On timeout/model/database errors retain existing rows, store a safe error message and permit retry. Duplicate jobs serialize on the session row and skip completed work.
7. Existing rows retain their levels but receive `legacy` status; they do not silently acquire verified provenance. Rollback refuses to discard new unrated rows.
8. Assessors may override assessed rows only, with a required rationale. Original AI rating and reviewer attribution remain available. Unassessed evidence requires a follow-up interview instead of a guess.
9. Portfolio, skill override, fit/gap and export endpoints resolve resources through the authenticated tenant. Cross-tenant IDs return 404. Background fit/gap work independently checks both tenants.
10. Fit/gap compares only assessed, valid ratings. Nonmatching canonical IDs cannot fall back to matching labels. Ambiguous custom labels are unassessed. Required levels use `expected_level` consistently.
11. UI shows loading, empty, request-error/retry, generation-failure/retry, partial, legacy and long-text states. Coverage counts come from the loaded portfolio, with no aggregate hire score. Evidence is readable before overriding.
12. UI works at 390px and desktop widths, with keyboard controls, visible focus, labelled inputs and explicit save errors. Existing teal/yellow brand and neutral surfaces are extended.
13. Backend regression tests cover data integrity, duplicate jobs, rollback, evidence, tenant boundaries and fit/gap. Frontend tests cover the actual API contract and human workflow. Deliberately inject a scoring fault, observe a failing test, and revert it with visible Git history.

## Options and trade-offs

| Option | Value / cost | Failure and maintenance |
|---|---|---|
| A. UI warning only | Cheap; helps reviewers notice missing data | Cannot recover fabricated L1 scores or partial writes; leaves API/export unsafe |
| B. Strict evidence boundary + transactional persistence (chosen) | Complete candidate-protection slice; moderate schema and test cost | Session lock spans a bounded model call; conservative quote matching can reject paraphrases; straightforward rollback and no new infrastructure |
| C. Versioned review ledger + outbox + model evaluation service | Strong provenance, durable scheduling and historical review | Larger migration and operational cost; too much surface for this exercise; sensible follow-up once scoring policy is validated |

## Constraints to escalate

- Gemini credentials, external hosting and GitHub publication depend on account access; never invent successful runs or URLs.
- No real candidate data or interviews are available. All screenshots and demonstrations must identify synthetic fixtures.
- Live audio, model quality and suitability for hiring need separate evaluation with consented data. Quote occurrence does not establish relevance, fairness or validity.
- The brief's August 19 deadline is earlier than the current client date; treat it as supplied historical context.
- Retention periods, legal basis, cross-border processor arrangements and candidate correction/access channels require the controller's policy; this slice does not establish UU PDP compliance.

## Design read and reasons

Reading this as: an assessor evidence workspace for recruiters and hiring managers, extending the existing Rakamin teal/yellow visual language. ENERGY 1 / RHYTHM 2 / MOTION 1.

- Dark teal preserves brand identity while giving button text adequate contrast; yellow is reserved for incomplete evidence.
- A review header and coverage strip precede a single-column evidence list: missing signal must be visible before individual ratings.
- System sans typography supports dense excerpts and avoids a font download.
- Large section gaps separate decision context; smaller gaps connect a skill with its evidence.
- Skill surfaces group a rating, its provenance and reviewer action; status text communicates uncertainty without color alone.
- Native details disclose long evidence; no decorative illustration, invented avatar or new logo is needed.
- Fixed light theme matches the existing assessor workspace and its document-reading task; no new theme is introduced.
