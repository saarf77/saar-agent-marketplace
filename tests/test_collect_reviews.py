import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'plugins/personal-prs-agent/skills/personal-prs-agent/scripts/collect_reviews.py'
spec = importlib.util.spec_from_file_location('collector', SCRIPT)
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)

class CollectorTests(unittest.TestCase):
    def test_timezone_window(self):
        self.assertTrue(c.in_window('2025-01-01T01:00:00+01:00', '2025-01-01T00:00:00Z', '2026-01-01T00:00:00Z'))
        self.assertFalse(c.in_window(None, '2025-01-01T00:00:00Z', '2026-01-01T00:00:00Z'))
    def test_reject_naive_timestamp(self):
        with self.assertRaises(ValueError): c.instant('2025-01-01T00:00:00')
    def test_pagination(self):
        with patch.object(c, 'api', side_effect=[list(range(100)), [100]]) as call:
            self.assertEqual(c.pages('github', 'github.com', 'repos/example/demo/pulls?state=closed'), list(range(101)))
            self.assertIn('page=2', call.call_args.args[2])
    def test_api_failure_is_not_empty_success(self):
        with patch.object(c, 'api', side_effect=RuntimeError('failed')):
            with self.assertRaises(RuntimeError): c.pages('gitlab', 'gitlab.example.com', 'projects/1/discussions')
    def test_cli_is_get_and_no_shell(self):
        from types import SimpleNamespace
        with patch.object(c.subprocess, 'run', return_value=SimpleNamespace(returncode=0, stdout='{}', stderr='')) as run:
            c.api('gitlab', 'gitlab.example.com', 'user')
            args=run.call_args.args[0]
            self.assertEqual(args[0], 'glab'); self.assertEqual(args[args.index('--method')+1], 'GET')
            self.assertFalse(run.call_args.kwargs.get('shell',False))
    def test_reject_host_and_repo_injection(self):
        for host,repo in [('https://github.com','example/demo'), ('github.com','../demo'), ('github.com','example/demo?x=1')]:
            with self.assertRaises(ValueError): c.validate_target(host,repo)
    def test_role_and_ai_markers(self):
        raw={'id':1,'body':':robot: question','author':{'username':'alex'},'created_at':'2025-04-01T00:00:00Z'}
        p=c.point('gitlab',raw,'alex','alex','conversation')
        self.assertEqual(p['role'],'as_author'); self.assertTrue(p['agent_marked'])
        self.assertFalse(c.point('gitlab',{**raw,'body':'[WARN] a concern'},'alex','sam','conversation')['agent_marked'])
    def test_private_output_rejects_git_parent(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'.git').mkdir()
            with self.assertRaises(ValueError): c.prepare_output(root/'nested'/'run')
    def test_output_does_not_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/'run';root.mkdir()
            with self.assertRaises(ValueError): c.prepare_output(root)
    def test_private_file_permissions(self):
        import os,stat
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'data.json';c.save(path,{'ok':True})
            if os.name=='posix':self.assertEqual(stat.S_IMODE(path.stat().st_mode),0o600)

class CollectionFlowTests(unittest.TestCase):
    def args(self, provider):
        from types import SimpleNamespace
        return SimpleNamespace(provider=provider, host='git.example.com', repo='example/demo',
            reviewer='alex', since='2025-01-01T00:00:00Z', until='2026-01-01T00:00:00Z')

    def test_github_cohort_replies_and_empty_approval(self):
        import json
        change={'number':7,'merged_at':'2025-04-01T00:00:00Z','updated_at':'2025-04-02T00:00:00Z','user':{'login':'sam'}}
        out_of_window={**change,'number':8,'merged_at':'2024-12-01T00:00:00Z'}
        inline={'id':1,'body':'Could this be null?','created_at':'2025-03-30T00:00:00Z','user':{'login':'alex'}}
        reply={'id':2,'body':'Fixed','created_at':'2025-03-31T00:00:00Z','user':{'login':'sam'}}
        old={**inline,'id':3,'created_at':'2024-12-31T00:00:00Z'}
        approval={'id':4,'body':'','submitted_at':'2025-04-01T00:00:00Z','state':'APPROVED','user':{'login':'alex'}}
        responses=[{'login':'alex'},[change,out_of_window],[inline,reply,old],[],[approval]]
        with tempfile.TemporaryDirectory() as d, patch.object(c,'api',side_effect=responses):
            root=Path(d); result=c.collect(self.args('github'),root)
            self.assertEqual(result['status'],'complete');self.assertEqual(result['selected'],1)
            points=json.loads((root/'7/target-points.json').read_text())
            self.assertEqual([p['id'] for p in points],[1,4])
            self.assertEqual(points[1]['state'],'APPROVED');self.assertEqual(points[1]['body'],'')
            self.assertEqual(len(json.loads((root/'7/inline.json').read_text())),3)

    def test_gitlab_keeps_author_role_and_partial_approval_failure(self):
        import json
        change={'iid':7,'merged_at':'2025-04-01T00:00:00Z','author':{'username':'alex'}}
        notes=[{'id':1,'body':'Done','created_at':'2025-03-30T00:00:00Z','author':{'username':'alex'}},
               {'id':2,'body':'What about null?','created_at':'2025-03-29T00:00:00Z','author':{'username':'sam'}}]
        responses=[{'username':'alex'},{'id':42},[change],[{'id':'thread1','notes':notes}],RuntimeError('denied')]
        with tempfile.TemporaryDirectory() as d, patch.object(c,'api',side_effect=responses):
            root=Path(d);result=c.collect(self.args('gitlab'),root)
            self.assertEqual(result['status'],'partial');self.assertEqual(result['completed'],1)
            self.assertEqual(result['items'][0]['errors'][0]['endpoint'],'approvals')
            points=json.loads((root/'7/target-points.json').read_text())
            self.assertEqual(len(points),1);self.assertEqual(points[0]['role'],'as_author')
            self.assertEqual(points[0]['discussion_id'],'thread1')
            self.assertTrue((root/'7/discussions.json').exists())

    def test_github_pulls_stop_after_older_updated_page(self):
        change={'number':7,'merged_at':None,'updated_at':'2024-12-01T00:00:00Z'}
        with tempfile.TemporaryDirectory() as d, patch.object(c,'api',side_effect=[{'login':'alex'},[change]*100]) as call:
            result=c.collect(self.args('github'),Path(d))
            self.assertEqual(result['selected'],0);self.assertEqual(call.call_count,2)

if __name__ == '__main__': unittest.main()
