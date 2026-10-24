import sqlite3
import tempfile
from pathlib import Path
import unittest
from import_evidence import ingest


class ImportTests(unittest.TestCase):
    def test_append_replay_and_conflict_rollback(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); db=root/'research.sqlite'
            with sqlite3.connect(db) as c:
                c.execute('CREATE TABLE runs(id TEXT,created_at REAL,model_version TEXT,payload BLOB)')
                c.execute("INSERT INTO runs VALUES ('old',1,'demo',X'0001')")
                c.execute('PRAGMA user_version=1')
            record={'id':'test-v1','kind':'analysis','validation_scope':'synthetic software fixture',
                    'provenance':{'test':True},'payload':{'value':1}}
            bundle={'schema_version':1,'records':[record]}
            result=ingest(db,bundle,root/'backup1')
            self.assertEqual(result['inserted'],1)
            self.assertEqual(result['simulation_runs_preserved'],1)
            self.assertEqual(ingest(db,bundle,root/'backup2')['inserted'],0)
            new=dict(record,id='new-v1'); changed=dict(record,payload={'value':2})
            with self.assertRaises(ValueError):
                ingest(db,dict(bundle,records=[new,changed]),root/'backup3')
            with sqlite3.connect(db) as c:
                self.assertEqual(c.execute('SELECT count(*) FROM research_evidence_v1').fetchone()[0],1)
                self.assertEqual(c.execute('SELECT payload FROM runs').fetchone()[0],b'\0\1')
                self.assertEqual(c.execute('PRAGMA user_version').fetchone()[0],1)
            with self.assertRaises(FileExistsError): ingest(db,bundle,root/'backup1')


if __name__ == '__main__': unittest.main()
