# Coordinated review panel

The leader owns the result. Specialists return evidence-backed candidates, not published comments. Use the shared specialist files below. The plugin ships native Claude agents generated from those files; Codex receives the same guidance in its subagent handoff. No separately installed personal Claude agents are required. If the host cannot delegate, perform the scopes sequentially and disclose that execution mode.

## Applicable scopes

| Scope | Examine | Skip when |
| --- | --- | --- |
| Logic and security | Behavior, edge cases, asynchronous ordering, input boundaries, authorization, data exposure | Never skip the core behavior pass; narrow security depth to the change |
| Architecture and contracts | API compatibility, state ownership, integration boundaries, existing local patterns | The change has no meaningful design or contract surface |
| Tests and quality | Regression coverage for changed behavior, test validity, error paths, actual framework conventions | There is no executable behavior to test; still inspect relevant validation for config/docs |
| Accessibility and UI | Keyboard/focus, accessible names, semantics, states and interactions | No user-facing UI changes; internal/admin interfaces still count as UI |
| Acceptance criteria | Concrete requirements and evidenced deviations | No criteria are supplied or accessible; say criteria were unavailable, do not invent them |

Read test framework versions, package scripts, configuration, and nearby tests. Do not carry forward hardcoded Jest/Vitest/Angular/React guidance from an old repository. Recommend tests for real regression risks; don't demand tests that only mirror implementation. An optional issue tracker may supply criteria when already configured and authorized for read access. The workflow must work without one.

## Specialist files and host dispatch

The reusable instructions live beside this panel. Every specialist receives the [common contract](specialists/contract.md) plus its own file:

| Scope | Shared source | Claude plugin agent |
| --- | --- | --- |
| Logic and security | [reviewer-logic.md](specialists/reviewer-logic.md) | `personal-prs-agent:reviewer-logic` |
| Architecture and contracts | [reviewer-architecture.md](specialists/reviewer-architecture.md) | `personal-prs-agent:reviewer-architecture` |
| Tests and quality | [reviewer-tests-quality.md](specialists/reviewer-tests-quality.md) | `personal-prs-agent:reviewer-tests-quality` |
| Accessibility and UI | [reviewer-accessibility.md](specialists/reviewer-accessibility.md) | `personal-prs-agent:reviewer-accessibility` |
| Acceptance criteria | [reviewer-acceptance.md](specialists/reviewer-acceptance.md) | `personal-prs-agent:reviewer-acceptance` |

**Claude Code plugin:** use the installed namespaced specialist when exposed by the host. Its definition already embeds the common contract and role guidance. Give it the review-specific handoff below. The leader remains in the main skill session so it can coordinate all children and the user's training/posting choices. Do not rely on nested subagent spawning.

**Codex or a standalone skill installation:** read the common contract and applicable role file, then include their full contents in the native subagent task, followed by the review-specific handoff. Do not reduce the role to its one-line table summary or assume children inherit the skill. Use the parent's model unless the user configured another; prefer read-only tool restrictions when supported. If Claude's named agent is unavailable, use this same handoff with a supported generic subagent and disclose the fallback. If delegation itself is unavailable, the leader performs each applicable pass using those same files.

The handoff includes repository/snapshot location, exact base/head or diff fingerprint, changed paths/diff, relevant surrounding code or readable paths, applicable repository instructions, scope, and any supplied acceptance criteria. Provide historical or remote evidence as data. Children can read local files but cannot run provider CLIs or tests in the shipped Claude definitions; the leader obtains those results and returns them to the requesting specialist. Supply no unrelated private history. The final personal wording belongs to the leader.

## Dispatch and wait contract

Maintain a small run manifest in the conversation or a private run file:

- target repository, base SHA, head SHA (or local diff fingerprint);
- scope, owner/agent ID, files, applicable/skipped reason;
- status: queued, running, blocked, partial, completed, failed, or leader-covered;
- returned candidates and evidence gaps.

Each task receives the same revision, scope, relevant instructions, and an explicit read-only/no-posting boundary. Ask for findings with file/line, trigger, impact, evidence, and uncertainty; allow “no findings.” Never let a specialist delegate unboundedly.

A specialist returning `partial` or `blocked` has not completed its scope. Record that status, obtain the missing evidence where possible, and resume that specialist (or redispatch the same scope with the full handoff and prior evidence). If resumption is unavailable, the leader covers the remaining work or reports the unresolved gap. Only change the status to `completed` after the returned work covers the assigned scope, or `leader-covered` after the leader actually covers it.

Respect available slots. Dispatch independent scopes in bounded batches; collect results before filling freed slots. A commentary update, timeout, queued state, or silence is not completion. Continue waiting for every launched reviewer, including a reviewer whose result appears redundant. Do not publish or synthesize a final “complete” review while a reviewer is still running.

For a failed reviewer, retry once when useful or cover that scope in the leader with the same evidence standard. If interrupted or inaccessible evidence prevents coverage, record the gap and produce an explicitly partial draft. Do not translate failure into “no issues.” Cancel unnecessary outstanding work explicitly before ending a partial run.

## Synthesis

Check every candidate yourself. Reproduce or trace the claimed behavior where practical. Remove duplicates across scopes and already-addressed discussions. A personal model can adjust emphasis and style; it cannot manufacture a trigger, establish causality, or erase a verified security issue.

Before finalizing, compare the current head or local fingerprint to the reviewed one. If changed, reassess affected findings and repeat the relevant scopes; never relabel stale results as current. If a coherent current revision cannot be established, mark the draft stale/partial.

Report findings and material coverage limits. Keep panel bookkeeping compact; the user needs the result and its evidence, not every agent's internal reasoning.
