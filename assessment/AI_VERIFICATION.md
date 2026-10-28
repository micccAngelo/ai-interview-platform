# AI verification log

The implementation and documentation were developed with AI assistance. The candidate must review and understand the code before submission and live defense.

## Verified risky assumption: frontend tests alone prove fullstack correctness

The generated frontend tests mock API clients. They prove rendering and recovery behavior, but cannot prove tenant isolation or database atomicity. Review identified this limitation. Separate PostgreSQL-backed Rails request/service specs were added for cross-tenant access, export, overrides, stale reports, and failure rollback. Browser contract tests are explicitly labeled synthetic fixtures and are not represented as live-API coverage.

## Verified risky contract: generated level types

The original frontend describes `PortfolioSkill.ai_level` as a string and `SkillComparison.required_level`, while database/API emit integer levels and `expected_level`. Following those types would produce a blank required-level column. The implementation checks the Rails serializer and schema, updates the shared contract, and asserts actual L3/L4 text using an API-shaped fixture. Do not fix this by defaulting missing values to L1.

## Verified setup failure

An initial Windows test run failed because esbuild could not read an ancestor directory under the restricted sandbox. The same assertions passed outside the sandbox. This is recorded as an environment failure, not a product test failure. The first cold browser navigation exceeded 30 seconds while Vite compiled the application; the browser suite allows 90 seconds for cold startup without removing assertions.

Final test results are recorded separately from these observations. No unexecuted Rails test is counted as passing.
