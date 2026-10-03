# Coordinated review panel

The leader owns the result. Specialists return evidence-backed candidates, not published comments. Use native subagents where available; do not depend on the user having named Claude agents installed. If the host cannot delegate, perform the scopes sequentially and disclose that execution mode.

## Applicable scopes

| Scope | Examine | Skip when |
| --- | --- | --- |
| Logic and security | Behavior, edge cases, asynchronous ordering, input boundaries, authorization, data exposure | Never skip the core behavior pass; narrow security depth to the change |
| Architecture and contracts | API compatibility, state ownership, integration boundaries, existing local patterns | The change has no meaningful design or contract surface |
| Tests and quality | Regression coverage for changed behavior, test validity, error paths, actual framework conventions | There is no executable behavior to test; still inspect relevant validation for config/docs |
| Accessibility and UI | Keyboard/focus, accessible names, semantics, states and interactions | No user-facing UI changes; internal/admin interfaces still count as UI |
| Acceptance criteria | Concrete requirements and evidenced deviations | No criteria are supplied or accessible; say criteria were unavailable, do not invent them |

Read test framework versions, package scripts, configuration, and nearby tests. Do not carry forward hardcoded Jest/Vitest/Angular/React guidance from an old repository. Recommend tests for real regression risks; don't demand tests that only mirror implementation. An optional issue tracker may supply criteria when already configured and authorized for read access. The workflow must work without one.

## Dispatch and wait contract

Maintain a small run manifest in the conversation or a private run file:

- target repository, base SHA, head SHA (or local diff fingerprint);
- scope, owner/agent ID, files, applicable/skipped reason;
- status: queued, running, completed, failed, or leader-covered;
- returned candidates and evidence gaps.

Each task receives the same revision, scope, relevant instructions, and an explicit read-only/no-posting boundary. Ask for findings with file/line, trigger, impact, evidence, and uncertainty; allow “no findings.” Never let a specialist delegate unboundedly.

Respect available slots. Dispatch independent scopes in bounded batches; collect results before filling freed slots. A commentary update, timeout, queued state, or silence is not completion. Continue waiting for every launched reviewer, including a reviewer whose result appears redundant. Do not publish or synthesize a final “complete” review while a reviewer is still running.

For a failed reviewer, retry once when useful or cover that scope in the leader with the same evidence standard. If interrupted or inaccessible evidence prevents coverage, record the gap and produce an explicitly partial draft. Do not translate failure into “no issues.” Cancel unnecessary outstanding work explicitly before ending a partial run.

## Synthesis

Check every candidate yourself. Reproduce or trace the claimed behavior where practical. Remove duplicates across scopes and already-addressed discussions. A personal model can adjust emphasis and style; it cannot manufacture a trigger, establish causality, or erase a verified security issue.

Before finalizing, compare the current head or local fingerprint to the reviewed one. If changed, reassess affected findings and repeat the relevant scopes; never relabel stale results as current. If a coherent current revision cannot be established, mark the draft stale/partial.

Report findings and material coverage limits. Keep panel bookkeeping compact; the user needs the result and its evidence, not every agent's internal reasoning.
