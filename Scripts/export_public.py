#!/usr/bin/env python3
"""Create a new audited publication snapshot; never modify original evidence."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import socket

PROJECT = Path(__file__).resolve().parents[1]
EXCLUDED = {'.git', '.build', '.swiftpm', '.serena', '__pycache__', 'build', '.DS_Store', '.resume.lock', 'logs', 'outreach'}
SUFFIXES = {'.md', '.swift', '.json', '.ka', '.csv', '.sh', '.txt', '.sha256', '.h',
            '.modulemap', '.entitlements', '.pbxproj', '.xcscheme', '.py', '.svg', '.png'}
SECRET = re.compile(rb'(?:-----BEGIN [A-Z ]*PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|sk-[A-Za-z0-9]{30,})')
PRIVATE_PATH = re.compile(rb'/(?:Users|home)/[A-Za-z0-9_.-]+')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode()


def numeric_payload(data):
    return b''.join(line for line in data.splitlines(keepends=True) if not line.startswith(b'#'))


def redact_trace(data, project):
    return b''.join(redact(line.decode(), project, socket.gethostname()).encode() if line.startswith(b'#') else line
                    for line in data.splitlines(keepends=True))


def redact(value, project, hostname):
    if isinstance(value, dict):
        result = {k: redact(v, project, hostname) for k, v in value.items()}
        if isinstance(value.get('argv'), list):
            args = result['argv']
            if len(args) < 12 or args[10] != '-d':
                raise ValueError('Unexpected run argv; manual review required')
            args[0] = Path(value['argv'][0]).name
            args[1] = str(Path(*Path(value['argv'][1]).parts[-3:]))
            args[11] = Path(value['argv'][11]).name
        if isinstance(value.get('platform'), list) and len(value['platform']) == 5:
            result['platform'][1] = '<REDACTED_HOST>'
        return result
    if isinstance(value, list):
        return [redact(item, project, hostname) for item in value]
    if isinstance(value, str):
        return value.replace(str(project), '<PROJECT>').replace(str(project.parents[1]), '<WORKSPACE>').replace(hostname, '<REDACTED_HOST>')
    return value


def export(project, destination):
    project, destination = Path(project).resolve(), Path(destination).resolve()
    if destination.exists() or destination.is_relative_to(project):
        raise ValueError('Destination must be new and outside source project')
    selected, omitted = [], []
    for source in sorted(project.rglob('*')):
        relative = source.relative_to(project)
        if relative.parts[:2] == ('Research', 'Coordination'):
            continue
        if any(part in EXCLUDED for part in relative.parts) or not source.is_file():
            continue
        if source.is_symlink():
            raise ValueError(f'Symlink requires review: {relative}')
        if '.log' in [suffix.lower() for suffix in source.suffixes] or (source.suffix == '.ka' and 'vendor' not in relative.parts):
            omitted.append(str(relative))
            continue
        if source.name not in {'.gitignore', 'LICENSE'} and source.suffix not in SUFFIXES:
            raise ValueError(f'Unreviewed file type: {relative}')
        original = source.read_bytes()
        published = original
        receipt = None
        if source.suffix == '.json':
            before = json.loads(original)
            after = redact(before, project, socket.gethostname())
            trace_path = source.with_name('trace.csv')
            trace_export = None
            if source.name == 'run.json' and trace_path.exists():
                trace_original = trace_path.read_bytes()
                if before.get('trace_sha256') != digest(trace_original):
                    raise ValueError(f'Original trace integrity failure: {relative}')
                trace_export = redact_trace(trace_original, project)
                after['trace_sha256'] = digest(trace_export)
            if before != after:
                published = json_bytes(after)
                if source.name == 'run.json':
                    changes = [key for key in before if before[key] != after.get(key)]
                    if changes not in (['argv'], ['argv', 'trace_sha256']):
                        raise ValueError(f'Unexpected run change: {relative}')
                    changed_args = [i for i, (a, b) in enumerate(zip(before['argv'], after['argv'])) if a != b]
                    if changed_args != [0, 1, 11]:
                        raise ValueError(f'Unexpected argv redaction: {relative}')
                    receipt = {'original_sha256': digest(original), 'published_sha256': digest(published),
                               'changed_fields': ['argv[0]', 'argv[1]', 'argv[11]'] + (['trace_sha256'] if 'trace_sha256' in changes else []),
                               'trace_sha256': before.get('trace_sha256'),
                               'published_trace_sha256': after.get('trace_sha256'),
                               'numeric_payload_sha256': digest(numeric_payload(trace_export)) if trace_export is not None else None,
                               'limitation': 'Original path strings withheld. Original digest is an exporter attestation; published bytes and unchanged numeric traces are independently checkable.'}
        elif source.name == 'trace.csv':
            published = redact_trace(original, project)
            if numeric_payload(original) != numeric_payload(published):
                raise ValueError(f'Numeric payload changed: {relative}')
        if SECRET.search(published) or PRIVATE_PATH.search(published):
            raise ValueError(f'Potential private content; review required: {relative}')
        selected.append((relative, original, published, receipt))
    destination.mkdir(parents=True)
    ledger = {'schema_version': 1, 'source_history': 'Present; not exported or audited by this script.' if (project / '.git').exists() else 'No source Git repository; publication starts a new snapshot history.',
              'policy': 'No binaries, local logs, clinical databases, publisher figures or full-text review copies. Original own code: MIT; preserve all third-party license notices.',
              'omitted': omitted, 'files': []}
    for relative, original, published, receipt in selected:
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(published)
        if (project / relative).stat().st_mode & 0o111:
            target.chmod(0o755)
        if receipt is not None:
            target.with_name('manifest-redaction.json').write_bytes(json_bytes(receipt))
        ledger['files'].append({'path': str(relative), 'original_sha256': digest(original),
                                'published_sha256': digest(published), 'metadata_redacted': original != published})
    (destination / 'PUBLICATION_MANIFEST.json').write_bytes(json_bytes(ledger))
    return ledger


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    result = export(PROJECT, args.destination)
    print(json.dumps({'files': len(result['files']), 'metadata_redactions': sum(f['metadata_redacted'] for f in result['files']), 'omitted': len(result['omitted'])}))
