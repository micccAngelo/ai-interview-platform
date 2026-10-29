# Preserve unassessed evidence through portfolio review and role comparison

A missing or malformed model rating previously became a valid-looking L1 score, and replacement generation deleted old skill rows before validating all new rows. A SQL skill omitted from the interview now remains explicitly unassessed through persistence, review, fit/gap comparison and export.

The response validator checks strict rating types, configured identities, candidate-quote provenance and coverage-based confidence ceilings. Generation publishes atomically under a session lock, skips completed duplicate work and preserves existing rows on failure. Assessor overrides require a rationale; portfolio, override and export lookups are bound to the verified token's tenant. Fit/gap uses deterministic comparisons, the actual `expected_level` contract and conservative identity matching. Provider response bodies and assessor notes are filtered from logs.

The React review workspace shows evidence coverage, follow-up reasons, original AI ratings and reviewer overrides, with explicit loading, empty, request-error and generation-failure states. It extends the existing design system and includes mobile and enlarged-text verification.

Validation evidence is recorded in `assessment/verification.json` and the committed command logs. Tests exercise real PostgreSQL writes and rollback, concurrent duplicate jobs, tenant boundaries, HTTP retry behavior, UI recovery and the API presentation contract. A deliberate missing-rating fault and its revert are retained on the seeded-fault branch; assertions were not weakened. CI configuration is included, with GitHub execution reported separately from local runs.

Rollout: apply the additive migration before deploying both services. Existing rows are labelled `legacy` without changing their original levels. Schema rollback refuses to invent levels for new unassessed rows. Standalone password login is now opt-in development-only because the baseline user model has no tenant-membership relation; production requires trusted organization sign-in.

Limits: synthetic fixtures and an injected model response do not validate live Gemini, audio quality or hiring fairness. A session lock spans the model call. A durable outbox, abandoned-job watchdog and append-only override ledger remain follow-ups. The change makes no UU PDP compliance claim.
