#!/usr/bin/env python3
"""Check the shared catalog, native manifests, skill resources and local links."""
import json
from pathlib import Path
import re
from build_claude_agents import check as check_agents

ROOT = Path(__file__).resolve().parents[1]

def read(path):
    return json.loads(path.read_text())

def validate():
    codex = read(ROOT / '.agents/plugins/marketplace.json')
    claude = read(ROOT / '.claude-plugin/marketplace.json')
    assert codex['name'] == claude['name'] == 'saar-agent-marketplace'
    assert len({p['name'] for p in codex['plugins']}) == len(codex['plugins']), 'Duplicate plugin'
    assert {p['name'] for p in codex['plugins']} == {p['name'] for p in claude['plugins']}, 'Catalogs differ'
    for entry in codex['plugins']:
        name = entry['name']
        other = next(p for p in claude['plugins'] if p['name'] == name)
        assert entry['source']['source'] == 'local'
        assert entry['source']['path'] == other['source'] == './plugins/' + name
        assert entry['policy']['installation'] == 'AVAILABLE'
        assert entry['policy']['authentication'] in ('ON_INSTALL', 'ON_USE')
        plugin = ROOT / 'plugins' / name
        a = read(plugin / '.codex-plugin/plugin.json')
        b = read(plugin / '.claude-plugin/plugin.json')
        assert a['name'] == b['name'] == name
        assert a['version'] == b['version'] == other['version']
        assert a['skills'] == b['skills'] == './skills/'
        assert (plugin / 'LICENSE').is_file() and (plugin / 'NOTICE').is_file()
        skills = list((plugin / 'skills').glob('*/SKILL.md'))
        assert skills, 'No skills found'
        for skill in skills:
            content = skill.read_text()
            assert content.startswith('---\n')
            assert f'name: {skill.parent.name}\n' in content
            assert re.search(r'^description: .+', content, re.M)
            assert len(content.splitlines()) < 500
    for file in ROOT.rglob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)', file.read_text()):
            if re.match(r'[a-z]+:', target) or target.startswith('#'):
                continue
            path = (file.parent / target.split('#', 1)[0]).resolve()
            assert path.is_relative_to(ROOT.resolve()), f'Link escapes package: {file}: {target}'
            assert path.exists(), f'Broken link: {file}: {target}'
    assert not check_agents(ROOT), 'Run python3 scripts/build_claude_agents.py to synchronize Claude agents'
    print('Marketplace manifests, versions, skill resources and local links passed.')

if __name__ == '__main__':
    validate()
