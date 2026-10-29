# Rakamin fullstack assignment

The completed local implementation and submission materials are in this folder. Everything is kept local, as requested. No pull request, external video upload or hiring-portal submission was made.

## Review the result

| File | Contents |
|---|---|
| [Submission report](assessment/Submission_Report.pdf) | Ten-page technical report covering exploration, product context, prioritized gaps, criteria, trade-offs, implementation and verification |
| [Walkthrough](assessment/walkthrough.webm) | 3 minutes 40 seconds, captioned recording of the local application; no narration |
| [Sample exported portfolio](assessment/sample-portfolio.pdf) | Actual Rails PDF export, including unassessed requirements |
| [Runbook](assessment/RUNBOOK.md) | Setup, local demo, verification commands and deployment limits |
| [Technical defense](assessment/technical-defense.md) | Code tour, decisions, trade-offs and questions to prepare for |
| [Design verification](assessment/design-verification.md) | PASS gate, contrast results and recorded control-by-control behavior |
| [Report design and copy check](assessment/report-design-check.md) | PASS gate for the revised PDF layout and wording, with rendering and text checks |
| [Verification record](assessment/verification.json) | Machine-readable results with links to the corresponding local logs |
| [Prepared PR description](assessment/PR_DESCRIPTION.md) | Ready for your review if you later choose to publish |

## What changed

Missing interview evidence stays **not assessed**, instead of becoming level 1. Model output is validated against candidate transcript turns before an atomic database replacement. Tenant checks, duplicate-job handling and attributed reviewer overrides protect the evidence. The React review and role comparison preserve uncertainty, show explicit errors and support mobile and keyboard use.

All demonstration records are synthetic. No live Gemini call or microphone interview was performed. Quote matching proves provenance, not competence, fairness or suitability for hiring. Read the report and code before presenting or defending the work.

## Verification

- 47 backend examples passed against real PostgreSQL.
- 11 frontend component tests and 3 browser workflow tests passed.
- TypeScript and the Vite production build passed.
- Real API checks verified four skills, two assessed ratings, two null ratings, role comparison and JSON/PDF exports.
- An intentional scoring fault failed the existing regression test; reverting it restored the test without weakening assertions.
- 177 visible text/control contrast samples passed the applicable AA text thresholds.

The raw logs are in `assessment/`. The intentional failure logs are evidence, not unresolved failures. CI configuration is supplied; a GitHub CI run is not claimed. Docker is an alternative setup and was not available for local verification.

## Run the local demo

The task-local Ruby, PostgreSQL and frontend dependencies are already installed on this machine. From PowerShell in this folder:

```powershell
powershell -File scripts/start-local.ps1
```

Open the demo URL printed by the script. The current seeded route is <http://127.0.0.1:5173/assessments/1/sessions/1/portfolio>. The ignored local environment supplies a synthetic demo token. Local secrets, databases and dependencies are excluded from the portable source archive.

For a fresh machine, follow the standard Ruby/Node/PostgreSQL instructions in the runbook. The optional `.runtime` tooling is specific to this Windows host.

## Portable copies and history

`Rakamin2-submission.zip` contains the source and final artifacts, excluding local dependencies, secrets and runtime data. `assessment/evidence-first.bundle` preserves all local branches and commits, including the intentional-fault/revert history. To inspect that history in a separate folder:

```sh
git clone assessment/evidence-first.bundle evidence-review-copy
cd evidence-review-copy
git checkout feat/evidence-first-assessment
git log --graph --oneline --all
```

The source branch is `feat/evidence-first-assessment`. `main` remains at the supplied baseline `b836d02`. The baseline repository's original documentation is retained in `README.md`.
