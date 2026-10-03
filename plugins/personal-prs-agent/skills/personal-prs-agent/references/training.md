# Private training and resync

Training is the first-use onboarding path for a new personal reviewer. Begin collection when the user asks to train or chooses training in onboarding; installation alone does not authorize collecting their history. Learning and reviewing remain separate operations. Nothing in this public package is a personal profile.

## Storage and identity

Use `~/.local/share/personal-prs-agent/` by default, or a user-selected absolute `PERSONAL_PRS_HOME`. Resolve symlinks and verify the destination is outside every Git checkout and installed plugin/cache before writing. Create private directories with mode 0700 and files with mode 0600 where supported. Local data still enters the configured AI host's context when analyzed; never imply local storage guarantees offline processing.

Use a hash of `(provider, hostname, reviewer ID/login)` for profile directories and `(provider, hostname, full repository path)` for model directories. Store the explicit mapping privately. Do not use unchecked remote names as filesystem paths. Never store credentials. Keep these logical resources:

- `identity.json`: confirmed account, provider/host, schema version, dates, repository mapping;
- `VOICE.md`: user-confirmed voice rules with provenance/confidence;
- `models/<repository-key>/MODEL.md`: attention map, reflexes, exceptions, evidence links and gaps;
- `runs/<run-id>/`: raw collection, manifest, calibration and evidence ledger;
- `posting/`: private review head, authorized findings, trace IDs, provider IDs and outcomes.

Do not overwrite a user's pre-existing private reviewer skill or move their data into this marketplace. Read only the profile relevant to the current identity/repository.

## Onboarding inputs and readiness

Accept a repository URL, its PR/MR listing, or individual reviewed change URLs. Derive repository/provider from those links or the current checkout. Use the authenticated identity as a candidate and confirm any ambiguity; the MR author is not automatically the reviewer to imitate. If only individual links are authorized, collect those read-only rather than expanding to whole repositories. Explain that a few examples may support only a provisional profile.

Offer a private display name inferred from the confirmed handle; naming is optional and never controls the hashed storage identity. Ask about known AI-assisted writing during calibration, without assuming that all comments posted from the account are human-written.

Track `onboarding_status` as `collecting`, `needs_calibration`, `provisional`, or `ready` in `identity.json`, with the covered repositories and dates. Record failed/partial collection separately. Set `ready` only after code-grounded evidence supports a useful profile and material calibration ambiguities have been resolved with the user; do not use an arbitrary comment count as proof. Report weak areas even when the overall profile is usable. Explicitly skipping training leaves the user untrained.

After training, briefly show what was learned, its limitations and private location, then continue any original review request. On future invocations, reuse the matching profile; do not repeat onboarding or recollect two years of history on every review.

## Establish the cohort

Confirm the reviewer identity from `gh api user` or `glab api user`, unless the user explicitly supplies a different account. Authenticate through existing CLI credentials; never ask the user to paste a token into chat. Determine provider and hostname from the supplied repository/PR URL, not a hardcoded public host. Resolve ambiguous identities before training.

Default to the last two calendar years ending at the current time when no period is supplied (clamp leap-day subtraction to February 28). Record concrete UTC bounds. The included collector selects **merged changes whose merge timestamp falls within those inclusive bounds**, then filters target-account activity by activity timestamp within the same bounds. It excludes open and unmerged changes and older changes with recent discussion. If the user wants all review activity, explain that this collector's cohort is narrower and use an explicitly adapted read-only collection; do not claim full coverage.

## Collect with bounded, read-only requests

From the installed skill directory, use the bundled Python script with explicit arguments. Example uses synthetic names and a fresh private run folder:

```sh
python3 scripts/collect_reviews.py \
  --provider github --host github.com --repo example/project \
  --reviewer example-reviewer \
  --since 2024-01-01T00:00:00Z --until 2026-01-01T00:00:00Z \
  --output "$HOME/.local/share/personal-prs-agent/runs/example-new-run"
```

For GitLab use `--provider gitlab`, the actual hostname, and full group/subgroup/project path. Python 3.9+, Git, and the provider CLI are required. The script uses GET requests only and refuses an existing output directory or a Git worktree destination. Never direct output into the skill or plugin cache even if that cache is not a Git checkout.

The collector paginates rather than relying on a capped search result. It retains discussion replies and review metadata, writes target-account points separately, and records partial endpoint failures. `complete` means collection completed for the selected cohort, not that the model is trained or that deleted/inaccessible activity exists. Exit code 2 indicates partial or failed collection. Preserve the failed run, report gaps, and use a new run directory for retries; there is no automatic resume.

GitHub review records can include empty approvals. GitLab current approvals are snapshots, not historical verdict events. System notes can supply historical context but should not become writing samples. Do not equate zero comments, absent approvals, or inaccessible endpoints with a silent approval.

## Learn from code and interaction

Use the actual historical code, diff revision, nearby implementation and git history to ground each important claim. Fetch read-only historical objects when needed and authorized; do not checkout over the user's work. Narrative summaries alone cannot establish what a comment meant. Keep unresolved locations explicitly unresolved.

Build an evidence ledger separating:

1. **Finding ownership:** human-confirmed idea, unknown, or agent-originated.
2. **Writing provenance:** human-confirmed wording, AI-written, mixed, or unknown.
3. **Role:** reviewer, author replying to a review, system event, explicit verdict.
4. **Outcome:** accepted change, rejected concern, explanation, repeated dispute, unresolved, or unknown.

Account authorship is not proof of human wording. The collector's marker detection is only a hint. Ask the user about uncertain provenance with a compact, concrete calibration set. Do not classify all severity labels as AI or assume any fixed phrase belongs to the user's voice. Exclude known AI wording from voice learning; preserve user-confirmed finding ownership. Keep author-side replies distinct from reviewer style.

Learn IF/WHAT/WHERE/WHEN/WHO/WHY: triggers, concerns, areas, timing, interaction patterns, and reasoning. Then distill an attention map, conditional review reflexes, voice examples, and negative space. Negative space requires a defensible opportunity denominator and repeated corroboration; absence of comments alone is unknown. Track independent changes, not repeated copies of the same note, as evidence. Mark small samples low confidence.

When the corpus is large enough, hold out independent changes and check whether the provisional model predicts which concerns merit comments without overproducing stylistic noise. Report this as a limited calibration check, not proof of identity fidelity.

Ask a compact “Calibrate reviewer” set naming real files/packages from the user's private corpus, not generic personality questions. Include uncertain voice provenance, disputed findings, and candidate preferences. Save explicit answers as strongest evidence. Draft provisional models while answers are pending, clearly labeled; never invent approval of a preference.

## Resync and report

Resync only when asked. Collect a fresh bounded run since the last verified cutoff, with an overlap window for late edits/replies; deduplicate by provider/host/repository/type/object ID. If the request needs follow-up on older changes outside the merged cohort, fetch those known IDs separately and document the scope. Preserve previous evidence and version the model rather than silently overwriting provenance.

Direct user corrections can teach what to learn or unlearn. Generated comments, replies, and rejected drafts are feedback signals, not automatically positive examples. Review alone never edits memory.

Report exact dates, repositories, confirmed identity, cohort, selected/completed counts, usable independent human samples, AI/mixed exclusions, verdict limitations, failed endpoints, code-grounding gaps, calibration status, and private storage location. Do not describe a provisional or partial profile as a faithful clone.
