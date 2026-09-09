import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('roadmap_build',ROOT/'build.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class RoadmapTests(unittest.TestCase):
    def setUp(self):self.data=json.loads((ROOT/'example.json').read_text(encoding='utf-8'))
    def test_example_valid(self):m.validate(self.data)
    def test_private_rejected_public(self):
        self.data.update(schema='roadmap.private.v1',visibility='private')
        with self.assertRaises(ValueError):m.validate(self.data)
    def test_unreviewed_rejected(self):
        self.data['publication_review']='UNREVIEWED'
        with self.assertRaises(ValueError):m.validate(self.data)
    def test_unexpected_field_rejected(self):
        self.data['private_campaign']='anything'
        with self.assertRaises(ValueError):m.validate(self.data)
    def test_email_backstop(self):
        self.data['intro']='person@example.com'
        with self.assertRaises(ValueError):m.validate(self.data)
    def test_cycle_rejected(self):
        self.data['tasks'][0]['depends']=['T02']
        with self.assertRaises(ValueError):m.validate(self.data)
    def test_unknown_dependency_rejected(self):
        self.data['tasks'][0]['depends']=['T99']
        with self.assertRaises(ValueError):m.validate(self.data)
    def test_no_completion_without_new_evidence_schema(self):
        self.data['tasks'][0]['state']='DONE'
        with self.assertRaises(ValueError):m.validate(self.data)
    def test_boolean_effort_rejected(self):
        self.data['tasks'][0]['hours']=True
        with self.assertRaises(ValueError):m.validate(self.data)
    def test_nan_effort_rejected(self):
        self.data['tasks'][0]['hours']=float('nan')
        with self.assertRaises(ValueError):m.validate(self.data)
    def test_reversed_dates_rejected(self):
        self.data['tasks'][0]['end']='2026-09-01'
        with self.assertRaises(ValueError):m.validate(self.data)
    def test_duplicate_task_rejected(self):
        self.data['tasks'].append(copy.deepcopy(self.data['tasks'][0]))
        with self.assertRaises(ValueError):m.validate(self.data)
    def test_deterministic_build(self):
        with tempfile.TemporaryDirectory() as a,tempfile.TemporaryDirectory() as b:
            m.build(self.data,a,revision='fixture');m.build(self.data,b,revision='fixture')
            for name in ('index.html','snapshot.json','manifest.json'):
                self.assertEqual((Path(a)/name).read_bytes(),(Path(b)/name).read_bytes())
    def test_html_escaped(self):
        self.data['title']='<script>alert(1)</script>'
        with tempfile.TemporaryDirectory() as a:
            m.build(self.data,a)
            text=(Path(a)/'index.html').read_text(encoding='utf-8')
            self.assertNotIn('<script>alert(1)</script>',text)
            self.assertIn('&lt;script&gt;',text)
    def test_no_live_side_effects(self):
        with tempfile.TemporaryDirectory() as a:
            r=m.build(self.data,a)
            self.assertEqual(r['network_calls'],0)
            self.assertFalse(r['automatic_actions'])
            self.assertFalse(r['hosting_verified'])
    def test_private_requires_explicit_flag(self):
        self.data.update(schema='roadmap.private.v1',visibility='private',publication_review='PRIVATE_OWNER_ONLY')
        with tempfile.TemporaryDirectory() as a:
            self.assertEqual(m.build(self.data,a,private=True)['visibility'],'private')

if __name__=='__main__':unittest.main()
