# Provider operations

Use existing authenticated `gh` (GitHub) or `glab` (GitLab) credentials and the actual hostname. Check `api user` read-only and verify the actor matches the user's expected posting identity. Do not print credentials. Use explicit HTTP methods and structured JSON payload files outside Git; never interpolate comment text into shell code.

## Read and draft

Resolve repository and PR/MR from the supplied URL or current remote. Fetch metadata, paginated changed files/diffs and existing discussions, checking truncation/overflow flags. Use local Git objects for missing code where available; otherwise report the gap. Record the reviewed base/head and diff version. Linked ticket content is optional context, not a mandatory provider dependency.

GitHub: use pull request metadata, files, inline comments, issue comments and reviews endpoints. GitLab: use merge request metadata, diffs/versions and discussions. Paginate all applicable collections. Current approval state and historical review events are distinct evidence.

Do not publish on a review request. A request to “post findings 1 and 3” authorizes those comments, not approval, requesting changes, resolving others' threads, merging, pushing code, or changing repository settings. Those are separate actions requiring their own user instruction.

## Publish authorized inline findings

1. Verify target, authorization scope, authenticated actor, complete or explicitly partial review status, and the exact approved text. Apply any user edits.
2. Re-fetch the current head and existing discussions immediately before posting. If the head changed, revalidate findings against the new diff and re-anchor; don't publish stale claims. If meaning changes materially, prepare a corrected draft for the user.
3. Deduplicate by provider/repository/change/head/finding and existing trace markers, plus equivalent live discussions. Use a private opaque run/finding ID in `<!-- personal-prs-agent:ID -->`; never encode private storage paths or corpus IDs. Prefix nonempty posted bodies with `:robot:`. Empty approvals, if explicitly requested separately, remain empty.
4. Anchor to the exact relevant file and line from the provider's current diff. For removed code, use the old side; for new code, use the new side. Respect rename paths and supported line ranges. Never invent a nearby changed-line anchor for a finding outside the diff. If an inline anchor is unavailable, keep that finding drafted and report why; ask about a general-comment fallback only when needed.
5. Use the provider's inline discussion/comment endpoint, not an issue-level comment endpoint. Record the returned comment/discussion ID and URL privately as each write succeeds. Recheck the head during multi-comment runs and stop on drift.
6. On an ambiguous network failure, list existing comments and reconcile the trace before retrying. Never blindly duplicate a potentially successful post. Report posted links and any unposted findings accurately.

A preflight head check cannot make a remote write atomic. If the head moves during publication, stop, disclose which comments refer to the previous revision, and revalidate remaining drafts. Do not silently edit/delete already posted comments or claim race-free delivery.

## GitHub inline payload

Use `gh api --hostname HOST --method POST repos/OWNER/REPO/pulls/NUMBER/comments --input PAYLOAD_FILE` for individually authorized inline comments. Supply `body`, reviewed `commit_id`, repository-relative `path`, one-based `line`, and `side` (`LEFT` or `RIGHT`). For ranges, include the compatible start fields. Derive every coordinate from the current diff; do not rely on a line number in an old draft. See [GitHub review comment API](https://docs.github.com/en/rest/pulls/comments#create-a-review-comment-for-a-pull-request).

## GitLab inline payload

Use `glab api --hostname HOST --method POST projects/PROJECT_ID/merge_requests/IID/discussions --input PAYLOAD_FILE`. Supply `body` and a text `position` with current diff-version `base_sha`, `start_sha`, `head_sha`, `old_path`, `new_path`, and the applicable `old_line`/`new_line`. An unchanged context line needs both coordinates. Use the provider's latest diff version, not guessed SHA relationships. See [GitLab diff discussions](https://docs.gitlab.com/api/discussions/#create-a-new-thread-in-the-merge-request-diff).

## Limits

The bundled collector is read-only; posting is an agent workflow using the authenticated CLI, not an automatic publisher. Provider version, access rights, diff limits, and host capabilities can block an operation. Preserve useful drafts and explain the actual blocker. Never use browser/account switching or another identity to bypass a permission failure.
