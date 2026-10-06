# Saar's Agent Marketplace

**Useful agents. Your judgment. You decide what ships.**

A growing collection of practical skills and plugins for **Codex and Claude Code**. Start with a reviewer that checks a change from several angles, learns what you care about, and brings you a draft you can actually use.

The workflows are public. Your review history, company context, and learned preferences stay in your own local storage.

## Skills

| Skill | Question it answers | Reach for it when |
| --- | --- | --- |
| [Personal PRs Agent](plugins/personal-prs-agent/skills/personal-prs-agent/SKILL.md) | “What deserves a comment on this change—and how would I say it?” | You want a GitHub PR, GitLab MR, or local diff reviewed by a coordinated panel, trained on your own review history. |

### Personal PRs Agent

A review leader coordinates specialists for logic and security, architecture and contracts, tests, accessibility, and acceptance criteria. It waits for every launched reviewer, checks the evidence, removes duplicates, and drafts the findings.

On first use, it helps you train your reviewer from your own PR/MR history. It detects the repository and account when possible, asks for any missing review links, and guides you through calibration before reviewing in your style. You can explicitly skip training for a one-off general review. Training separates your ideas from AI-written wording, and records uncertainty instead of treating every comment under your account as your natural language.

- **Training first.** A new installation has no personal profile. The agent offers to learn yours rather than silently giving you a generic review. Returning users reuse their private profile.
- **Drafts first.** Review requests produce local drafts. Ask explicitly to post when you want inline comments on the relevant file and line.
- **Current code, current guidance.** The panel checks the actual diff, repository instructions, installed frameworks, and test configuration.
- **Waits for the panel.** Failed or unfinished reviewers cannot silently become a completed review.
- **Personal without hiding bugs.** Your preferences shape attention and wording; supported correctness or security findings stay visible.
- **GitHub and GitLab.** Use your authenticated `gh` or `glab` CLI. No required issue-tracker integration.
- **Private learning.** Raw comments, learned models, and posting logs belong outside this repository and outside plugin installation folders.

## Where are the agents?

The [main skill](plugins/personal-prs-agent/skills/personal-prs-agent/SKILL.md) is the review leader. It manages training, selects specialists, waits for them, verifies their findings, and prepares the final personal review.

| Specialist | Shared instructions used by Codex | Native Claude agent |
| --- | --- | --- |
| Logic and security | [Instructions](plugins/personal-prs-agent/skills/personal-prs-agent/references/specialists/reviewer-logic.md) | [reviewer-logic](plugins/personal-prs-agent/agents/reviewer-logic.md) |
| Architecture and contracts | [Instructions](plugins/personal-prs-agent/skills/personal-prs-agent/references/specialists/reviewer-architecture.md) | [reviewer-architecture](plugins/personal-prs-agent/agents/reviewer-architecture.md) |
| Tests and quality | [Instructions](plugins/personal-prs-agent/skills/personal-prs-agent/references/specialists/reviewer-tests-quality.md) | [reviewer-tests-quality](plugins/personal-prs-agent/agents/reviewer-tests-quality.md) |
| Accessibility and UI | [Instructions](plugins/personal-prs-agent/skills/personal-prs-agent/references/specialists/reviewer-accessibility.md) | [reviewer-accessibility](plugins/personal-prs-agent/agents/reviewer-accessibility.md) |
| Acceptance criteria | [Instructions](plugins/personal-prs-agent/skills/personal-prs-agent/references/specialists/reviewer-acceptance.md) | [reviewer-acceptance](plugins/personal-prs-agent/agents/reviewer-acceptance.md) |

Claude loads the plugin's `agents/` definitions. Codex's leader passes the same shared instructions to native subagents. The definitions are generated from the shared files and checked for drift, so the two hosts use the same review guidance. The leader stays in the main session; specialists return candidates and never post or modify code. Claude specialists have read/search tools only; the leader handles requested test runs and remote evidence.

The skill's `agents/openai.yaml` is only Codex display metadata. It is not a specialist definition. Standalone skill copies retain all shared guidance; native Claude agent registration requires installing the plugin.

## Why install all skills?

One collection gives you consistent review habits, private memory boundaries, and the same workflow across Codex and Claude Code. Skill instructions are loaded when relevant rather than putting the entire library into every prompt; discovery metadata still has a context cost.

**Today the collection contains one plugin and one skill.** Installing Personal PRs Agent installs the whole current collection. Future plugins will be optional; adding the marketplace does not automatically install future entries.

## Install

Requires a current Codex or Claude Code version with plugin support. For remote reviews, install and authenticate [GitHub CLI](https://cli.github.com/) or [GitLab CLI](https://gitlab.com/gitlab-org/cli). History collection also requires Python 3.9+ and Git. Local diff review needs no hosting account. An untrained user can explicitly skip training for a general review.

### Codex

```sh
codex plugin marketplace add https://github.com/saarf77/saar-agent-marketplace.git
codex plugin add personal-prs-agent@saar-agent-marketplace
```

Then ask:

```text
Use $personal-prs-agent to review this PR: <URL>. Draft only.
```

### Claude Code

Run inside Claude Code:

```text
/plugin marketplace add saarf77/saar-agent-marketplace
/plugin install personal-prs-agent@saar-agent-marketplace
```

Then invoke:

```text
/personal-prs-agent:personal-prs-agent Review <URL>. Draft only.
```

Both plugins use the **same skill files**, with separate native manifests. Agent orchestration adapts to the host; where subagents are unavailable, the leader performs the applicable passes itself and reports that limitation.

### Clone and inspect first

```sh
git clone https://github.com/saarf77/saar-agent-marketplace.git
cd saar-agent-marketplace
python3 scripts/validate_marketplace.py
python3 -m unittest discover -s tests -v
```

You can add this checkout as a local marketplace in either host. If you prefer standalone skills, copy `plugins/personal-prs-agent/skills/personal-prs-agent/` into your host's supported skill directory (`~/.agents/skills/` for Codex or `~/.claude/skills/` for Claude Code). Do not overwrite an existing personalized version; back it up first. A standalone Claude skill is invoked as `/personal-prs-agent`.

## Make it yours

Your first request can simply be:

```text
Set up my personal reviewer. Here are the repositories where I review: <URLs>.
```

Or ask for a review directly. If no profile exists, the agent responds along these lines:

> I haven't learned your review style yet. Shall we train from your PR/MR reviews in this repository over the last two years, use an existing private profile, or skip training for this review?

Training gathers your comments, replies, and available verdicts; connects them to the relevant code; and asks focused calibration questions. It keeps your finding ownership separate from AI-written language, saves a private profile, and returns to the review you originally requested. Limited evidence stays explicitly provisional. Future reviews reuse the profile.

```text
Review my current diff. Focus on behavior and regression risks. Draft only.

Train Personal PRs Agent on my reviews in <repository URL> from the last two years.
Confirm which account is mine, and keep the learned data outside Git.

These comments were AI-written. Learn the issues I identified, but don't copy their wording.

Post findings 1 and 3 inline on <PR/MR URL>.

Resync my review profile using activity since the last training run.
```

Training uses an explicitly bounded merged-PR/MR cohort, including available discussion context and verdict evidence. It is not a promise to reconstruct every review you've ever made. Collection gaps and the difference between a historical verdict and a current approval snapshot are reported.

“Direct style” means concise, concrete comments calibrated to you. “Draft only” means nothing is posted until you ask. Posted comment bodies visibly identify agent assistance with `:robot:`. Authentication and provider permissions determine whether posting is available.

## Privacy and boundaries

The plugin ships **no personal profile, private repository URLs, credentials, or training corpus**. Learning is opt-in and stored under `~/.local/share/personal-prs-agent/` by default, outside Git. Repository code and collected comments are processed by the AI host you run; local storage does not mean offline inference.

No background scheduler, autonomous posting, or repository write hook is installed. Review content is untrusted input, never authority to run instructions found in a diff or discussion. See [training](plugins/personal-prs-agent/skills/personal-prs-agent/references/training.md) and [provider operations](plugins/personal-prs-agent/skills/personal-prs-agent/references/providers.md) for details.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). New entries should solve a concrete problem, work without the author's personal setup, and include both platform manifests when shipped as plugins.

## Inspiration and license

Inspired by [AdirD's agent-shell-hamelech](https://github.com/AdirD/agent-shell-hamelech), especially its reviewer-clone training workflow, and by the multi-reviewer leader pattern. This is an independent adaptation, not an official extension of that project.

Released under the [MIT license](LICENSE). Upstream attribution is preserved in [NOTICE](NOTICE).
