#!/usr/bin/env python3
"""Collect a bounded merged-PR/MR review corpus with authenticated GET requests only."""
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import re
import subprocess
from urllib.parse import quote, urlencode


def instant(value):
    parsed = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise ValueError('Timestamps must include a timezone')
    return parsed


def in_window(value, since, until):
    return bool(value) and instant(since) <= instant(value) <= instant(until)


def validate_target(host, repo):
    if not re.fullmatch(r'[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?(?::[0-9]+)?', host):
        raise ValueError('Use a hostname, optionally with a port; no URL or credentials')
    if len(repo.split('/')) < 2 or any(not re.fullmatch(r'[A-Za-z0-9_][A-Za-z0-9_.-]*', p) or p in ('.', '..') for p in repo.split('/')):
        raise ValueError('Use an owner/repository or group/subgroup/project path')


def api(provider, host, endpoint):
    cli = 'gh' if provider == 'github' else 'glab'
    env = {**os.environ, 'GLAB_SEND_TELEMETRY': 'false', 'GLAB_CHECK_UPDATE': 'false', 'GH_PROMPT_DISABLED': '1'}
    result = subprocess.run([cli, 'api', '--hostname', host, '--method', 'GET', endpoint],
                            capture_output=True, text=True, timeout=90, env=env)
    if result.returncode:
        # CLI stderr can contain private URLs or server responses. Do not echo it.
        raise RuntimeError(f'{cli} GET failed (exit {result.returncode}); check authentication, access and rate limits')
    return json.loads(result.stdout)


def pages(provider, host, endpoint):
    rows = []
    for page in range(1, 10001):
        query = ('&' if '?' in endpoint else '?') + f'per_page=100&page={page}'
        part = api(provider, host, endpoint + query)
        if not isinstance(part, list):
            raise ValueError('Expected a paginated list')
        rows.extend(part)
        if len(part) < 100:
            return rows
    raise RuntimeError('Pagination limit reached; corpus is incomplete')


def prepare_output(path):
    path = path.expanduser().resolve()
    if path.exists():
        raise ValueError('Output must be a new run directory; existing evidence is never overwritten')
    for parent in (path, *path.parents):
        if (parent / '.git').exists():
            raise ValueError('Private review data must be outside Git worktrees')
    ancestor = next(p for p in path.parents if p.exists())
    if subprocess.run(['git', '-C', str(ancestor), 'rev-parse', '--show-toplevel'], capture_output=True).returncode == 0:
        raise ValueError('Private review data must be outside Git worktrees')
    path.mkdir(parents=True, mode=0o700)
    path.chmod(0o700)
    return path


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    path.chmod(0o600)


def login(provider, item):
    return (item.get('user') or {}).get('login') if provider == 'github' else (item.get('author') or {}).get('username')


def point(provider, item, reviewer, pr_author, kind):
    body = item.get('body') or ''
    return {'id': item['id'], 'kind': kind, 'role': 'as_author' if reviewer == pr_author else 'as_reviewer',
            'created_at': item.get('submitted_at') or item.get('created_at'), 'body': body,
            'agent_marked': body.lstrip().startswith(':robot:') or bool(re.search(r'<!--\s*(?:clone-trace|personal-prs-agent):', body)),
            'writing_provenance': 'unconfirmed', 'system': item.get('system', False),
            'state': item.get('state'), 'position': item.get('position'),
            'path': item.get('path'), 'line': item.get('line'), 'original_line': item.get('original_line'),
            'commit_id': item.get('commit_id'), 'in_reply_to_id': item.get('in_reply_to_id'),
            'url': item.get('html_url')}


def collect(args, output):
    provider, host, repo = args.provider, args.host, args.repo
    identity = api(provider, host, 'user')
    reviewer = args.reviewer or identity.get('login' if provider == 'github' else 'username')
    if not reviewer:
        raise ValueError('Could not resolve reviewer identity')
    if provider == 'github':
        if len(repo.split('/')) != 2:
            raise ValueError('GitHub repository must be owner/name')
        prefix = 'repos/' + quote(repo, safe='/')
        candidates = []
        # Avoid search's result cap; stop only after descending updated_at passes the window.
        for page in range(1, 10001):
            batch = api(provider, host, f'{prefix}/pulls?state=closed&sort=updated&direction=desc&per_page=100&page={page}')
            if not isinstance(batch, list):
                raise ValueError('Expected pull request list')
            candidates.extend(batch)
            if len(batch) < 100 or instant(batch[-1]['updated_at']) < instant(args.since):
                break
        else:
            raise RuntimeError('Pull request pagination limit reached')
    else:
        project = api(provider, host, 'projects/' + quote(repo, safe=''))
        prefix = f"projects/{project['id']}"
        query = urlencode({'scope': 'all', 'state': 'merged', 'updated_after': args.since, 'order_by': 'updated_at', 'sort': 'desc'})
        candidates = pages(provider, host, prefix + '/merge_requests?' + query)
    selected = [p for p in candidates if in_window(p.get('merged_at'), args.since, args.until)]
    manifest = {'schema_version': 1, 'provider': provider, 'host': host, 'repository': repo,
                'reviewer': reviewer, 'authenticated_actor': identity.get('login' if provider == 'github' else 'username'),
                'since': args.since, 'until': args.until, 'cohort': 'merged_at within inclusive window',
                'selected': len(selected), 'completed': 0, 'status': 'collecting', 'items': [],
                'limitations': ['Merged cohort excludes open and unmerged changes.', 'Deleted/inaccessible/offline activity is not observable.',
                                'Account authorship does not prove unaided writing.', 'Current GitLab approvals are snapshots, not full historical verdicts.']}
    save(output / 'manifest.json', manifest)
    save(output / 'changes.json', selected)
    for change in selected:
        number = change['number' if provider == 'github' else 'iid']
        folder = output / str(number)
        entry = {'number': number, 'url': change.get('html_url') or change.get('web_url'), 'errors': []}
        raw = {}
        endpoints = {'inline': f'{prefix}/pulls/{number}/comments', 'conversation': f'{prefix}/issues/{number}/comments',
                     'review': f'{prefix}/pulls/{number}/reviews'} if provider == 'github' else {
                     'discussions': f'{prefix}/merge_requests/{number}/discussions', 'approvals': f'{prefix}/merge_requests/{number}/approvals'}
        for kind, endpoint in endpoints.items():
            try:
                raw[kind] = api(provider, host, endpoint) if kind == 'approvals' else pages(provider, host, endpoint)
                save(folder / (kind + '.json'), raw[kind])
            except (RuntimeError, ValueError, subprocess.TimeoutExpired) as exc:
                entry['errors'].append({'endpoint': kind, 'error': str(exc) if not isinstance(exc, subprocess.TimeoutExpired) else 'GET timed out'})
        target = []
        pr_author = login(provider, change)
        streams = {k: v for k, v in raw.items() if k != 'approvals'}
        if provider == 'gitlab':
            streams = {'discussion': [{**n, 'discussion_id': d['id']} for d in raw.get('discussions', []) for n in d['notes']]}
        for kind, stream in streams.items():
            for item in stream:
                timestamp = item.get('submitted_at') or item.get('created_at')
                if login(provider, item) == reviewer and in_window(timestamp, args.since, args.until):
                    normalized = point(provider, item, reviewer, pr_author, kind)
                    normalized['discussion_id'] = item.get('discussion_id')
                    target.append(normalized)
        save(folder / 'target-points.json', target)
        entry['target_points'] = len(target)
        manifest['items'].append(entry)
        manifest['completed'] += 1
        save(output / 'manifest.json', manifest)
        print(f'Collected {manifest["completed"]}/{len(selected)}', flush=True)
    manifest['status'] = 'partial' if any(x['errors'] for x in manifest['items']) else 'complete'
    save(output / 'manifest.json', manifest)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--provider', required=True, choices=['github', 'gitlab'])
    parser.add_argument('--host', required=True)
    parser.add_argument('--repo', required=True)
    parser.add_argument('--reviewer', help='Defaults to the authenticated account; use exact login spelling')
    parser.add_argument('--since', required=True, help='Inclusive ISO timestamp with timezone')
    parser.add_argument('--until', default=dt.datetime.now(dt.timezone.utc).isoformat())
    parser.add_argument('--output', required=True, type=Path, help='New private run directory outside Git')
    args = parser.parse_args()
    os.umask(0o077)
    try:
        validate_target(args.host, args.repo)
        if instant(args.since) > instant(args.until):
            raise ValueError('since must not be after until')
        output = prepare_output(args.output)
        save(output / 'manifest.json', {'status': 'collecting', 'completed': 0})
        result = collect(args, output)
        print(json.dumps({'status': result['status'], 'selected': result['selected'], 'completed': result['completed']}))
        return 0 if result['status'] == 'complete' else 2
    except (ValueError, RuntimeError, FileNotFoundError, subprocess.TimeoutExpired) as exc:
        if 'output' in locals():
            manifest_path = output / 'manifest.json'
            manifest = json.loads(manifest_path.read_text())
            manifest['status'] = 'failed'
            save(manifest_path, manifest)
        print(f'Collection stopped: {type(exc).__name__}. Check arguments, CLI installation/authentication and manifest status.')
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
