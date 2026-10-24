"""Append reviewed evidence to the existing research DB; never replace simulation runs."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sqlite3


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def ingest(database, bundle, backup):
    if not database.is_file() or database.is_symlink():
        raise ValueError('Existing regular database required')
    if backup.exists() or backup.is_symlink():
        raise FileExistsError('Backup already exists')
    records = bundle['records']
    if bundle['schema_version'] != 1 or not records:
        raise ValueError('Nonempty version1 bundle required')
    prepared = []
    for record in records:
        if (not isinstance(record.get('id'), str) or not record['id'] or
                record.get('kind') not in ['source', 'dataset', 'analysis', 'search'] or
                not isinstance(record.get('payload'), dict) or
                not record.get('provenance') or not record.get('validation_scope')):
            raise ValueError('Incomplete evidence record')
        payload = json.dumps(record, sort_keys=True, ensure_ascii=False, allow_nan=False)
        prepared.append((record['id'], record['kind'], record['validation_scope'], digest(payload), payload))
    if len({r[0] for r in prepared}) != len(prepared):
        raise ValueError('Duplicate bundle IDs')
    connection = sqlite3.connect(database, timeout=5)
    try:
        if connection.execute('PRAGMA user_version').fetchone()[0] != 1:
            raise ValueError('Expected existing app schema1')
        before = connection.execute('SELECT id,created_at,model_version,payload FROM runs ORDER BY id').fetchall()
        fd = os.open(backup, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600); os.close(fd)
        with sqlite3.connect(backup) as target:
            connection.backup(target)
        connection.execute('PRAGMA trusted_schema=OFF')
        connection.execute('PRAGMA synchronous=FULL')
        connection.execute('BEGIN IMMEDIATE')
        try:
            connection.execute('CREATE TABLE IF NOT EXISTS research_evidence_v1 (id TEXT PRIMARY KEY NOT NULL, kind TEXT NOT NULL, validation_scope TEXT NOT NULL, sha256 TEXT NOT NULL, payload_json TEXT NOT NULL)')
            inserted = 0
            for row in prepared:
                old = connection.execute('SELECT sha256,payload_json FROM research_evidence_v1 WHERE id=?', (row[0],)).fetchone()
                if old:
                    if old != (row[3], row[4]):
                        raise ValueError('Existing evidence differs; use a new version ID')
                    continue
                connection.execute('INSERT INTO research_evidence_v1 VALUES (?,?,?,?,?)', row)
                inserted += 1
            after = connection.execute('SELECT id,created_at,model_version,payload FROM runs ORDER BY id').fetchall()
            if before != after:
                raise ValueError('Simulation rows changed')
            if connection.execute('PRAGMA quick_check').fetchone()[0] != 'ok':
                raise ValueError('Database integrity check failed')
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        return {'inserted': inserted, 'already_present': len(records)-inserted,
                'simulation_runs_preserved': len(before), 'user_version': 1, 'quick_check': 'ok'}
    finally:
        connection.close()


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['database', 'bundle', 'backup']:
        p.add_argument('--'+name, type=Path, required=True)
    a = p.parse_args()
    print(json.dumps(ingest(a.database, json.loads(a.bundle.read_text()), a.backup)))
