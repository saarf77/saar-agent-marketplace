# Contributing

Keep each plugin useful without private company context or a particular developer's identity. Never contribute real review history, credentials, learned profiles, or private repository examples. Use synthetic fixtures.

Put shared skills in `plugins/<name>/skills/`. Add native manifests under `.codex-plugin/` and `.claude-plugin/`, register the plugin in both root catalogs, and keep names and versions aligned. Add one clear row to the README skill table. Include a license and attribution for derived material.

Skills should separate analysis from external actions, identify missing evidence, and document any dependency or capability limitation. Do not install schedulers or posting hooks as a side effect. Keep personal memory outside the source and plugin cache.

For Personal PRs Agent, edit the canonical role files under `plugins/personal-prs-agent/skills/personal-prs-agent/references/specialists/`. Run `python3 scripts/build_claude_agents.py` to regenerate the self-contained Claude definitions under the plugin's `agents/` directory; do not hand-edit those generated files. Keep specialists read-only and leave orchestration, training, personal wording, and posting with the leader.

Before submitting a change:

```sh
python3 scripts/validate_marketplace.py
python3 -m unittest discover -s tests -v
```

Also validate affected plugin packages with your host's validator. For behavioral changes, exercise synthetic scenarios covering incomplete reviewers, stale diff positions, user authorization, and AI-written training evidence. Explain what you actually verified; mocked API tests are not live provider integration tests.
