# Technical defense guide

Read the change and run it yourself before submitting. The assignment explicitly requires being able to explain the code in a live discussion. This implementation was AI assisted; do not imply otherwise.

## Five-minute code tour

1. `api/app/services/portfolios/response_validator.rb`: start with `call`, then `build`, then `verified_evidence?`. Explain why a numeric string does not become an integer and why the coverage map limits confidence.
2. `api/app/services/portfolios/generator.rb`: the session row exists before the portfolio. Lock it so duplicate jobs serialize even on first creation. An inner savepoint protects replacement writes; the outer transaction can then persist a safe failure status.
3. `api/db/migrate/20261029000001_preserve_unassessed_portfolio_skills.rb`: old rows become legacy without rewriting their original ratings. New unassessed rows are null. The check constraint makes status and rating agree.
4. `api/app/services/fit_gap/engine.rb`: compare canonical identities; never match a different ID by label. Unknown and ambiguous evidence stays unassessed. No model is needed for arithmetic or culture inference.
5. `web/src/pages/portfolio/PortfolioPage.tsx` and `components/portfolio/SkillPortfolioCard.tsx`: counts come from returned statuses, evidence precedes the review action, and unassessed rows have no override form.

## Questions to be ready for

**Why isn't a verified quote proof of proficiency?** The validator establishes that the candidate said it, not that it is relevant, correct, or representative. Calibration, semantic evaluation, multilingual interviews and assessor judgment remain separate concerns.

**Why not set missing ratings to zero?** Zero is still a score and would flow into ranking and arithmetic. Null plus an explicit status prevents uncertainty from becoming a negative evaluation.

**What does the lock cost?** The session lock spans the model call. The HTTP read timeout is 180 seconds and provider retries are disabled for this call; Sidekiq owns retries. A read timeout is not a strict end-to-end wall-clock deadline. The lock consumes one DB connection and can delay other writes to the ended session. For larger workloads, use a generation-attempt row, lease and compare-and-swap publication plus an outbox. This slice favors a smaller correctness boundary.

**Does it guarantee exactly-once execution?** It skips completed duplicate jobs and serializes attempts. An upstream call may still finish before a process dies, so retries can incur a second model charge. It does not promise exactly-once provider billing.

**What happens if the worker dies?** The transaction rolls back, preserving the last committed rows. A pending record can remain pending until the durable Sidekiq retry runs. There is no stale-job watchdog or durable outbox in this slice; a manual operational recovery path is still needed for abandoned jobs.

**How is queue failure handled?** Enqueue and the pending transition occur while holding the session lock. A synchronous Redis error rolls the transition back. Redis loss after an acknowledged enqueue still needs an outbox or reconciliation worker.

**What does rollback do?** It restores the old schema on legacy-only data. It refuses a NOT NULL rollback while unassessed rows exist. Making up levels to force rollback would destroy the meaning of those rows. Resolve or archive affected assessments before schema rollback; ordinary code rollback should leave the additive schema in place.

**Why restrict local login?** The baseline user table has no tenant membership relation and accepts a tenant header at password login. That cannot establish organization authorization. The standalone login is opt-in development-only; production requires a trusted upstream organization-bound token. Do not claim the entire authentication system was redesigned.

**What about reviewer audit history?** The original AI rating, latest rationale, reviewer and timestamp are retained. Re-editing an override replaces the previous reviewer rationale. An append-only review ledger is a follow-up, not a delivered feature.

**Why no overall hiring score?** Coverage, proficiency and business hiring judgment are different quantities. An aggregate would hide unassessed requirements and imply calibration this exercise does not have.

**What is still needed before real candidates use it?** Consent and legal-basis policy, retention and deletion operations, candidate correction/access/objection channels, provider arrangements, a data protection impact assessment where applicable, model and bias evaluation, and operational monitoring. The report distinguishes these from implemented safeguards.
