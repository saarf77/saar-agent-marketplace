import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('agent_builder', ROOT / 'scripts/build_claude_agents.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)

class AgentPackagingTests(unittest.TestCase):
    def test_shipped_agents_match_shared_sources(self):
        self.assertEqual(builder.check(ROOT), [])

    def test_missing_and_stale_agents_detected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / builder.SOURCE
            source.mkdir(parents=True)
            (source / 'contract.md').write_text('Read-only common contract\n')
            for name in builder.ROLES:
                (source / (name + '.md')).write_text('Specific guidance\n')
            self.assertEqual(len(builder.check(root)), len(builder.ROLES))
            builder.build(root)
            self.assertEqual(builder.check(root), [])
            (source / 'reviewer-logic.md').write_text('Changed behavioral guidance\n')
            self.assertEqual(builder.check(root), ['reviewer-logic.md'])

    def test_generated_agents_are_self_contained_and_read_only(self):
        for name, description in builder.ROLES.items():
            result = builder.render(ROOT, name, description)
            self.assertIn('tools: Read, Grep, Glob\n', result)
            self.assertIn((ROOT / builder.SOURCE / 'contract.md').read_text().strip(), result)
            self.assertIn((ROOT / builder.SOURCE / (name + '.md')).read_text().strip(), result)
            self.assertNotIn('${CLAUDE_PLUGIN_ROOT}', result)

if __name__ == '__main__':
    unittest.main()
