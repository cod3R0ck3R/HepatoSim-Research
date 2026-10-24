#!/usr/bin/env python3
"""Retrieve immutable GEO inputs to a private directory; never overwrite existing data."""
import argparse
import hashlib
import json
from pathlib import Path
import signal
import tarfile
import time
import urllib.request


def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--verify-only',action='store_true');a=p.parse_args()
    spec=json.loads(Path(__file__).with_name('analysis-spec-v2.json').read_text())
    signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('Retrieval budget expired')));signal.alarm(600)
    a.output.mkdir(parents=True,exist_ok=True)
    base='https://ftp.ncbi.nlm.nih.gov/geo/series/GSE244nnn/GSE244832/suppl/'
    downloads={'processed.tar.gz':'GSE244832_hLIVER_processed_files.tar.gz','metadata.xlsx':'GSE244832_240605_18liver_metadata.xlsx'}
    for name,remote in downloads.items():
        dest=a.output/name
        if dest.exists():
            if sha(dest)!=spec['files'][name]['sha256']:raise ValueError('Existing file mismatch: '+name)
            continue
        if a.verify_only:raise ValueError('Missing file: '+name)
        partial=dest.with_suffix(dest.suffix+'.partial');size=0
        with urllib.request.urlopen(base+remote,timeout=45) as r,partial.open('xb') as f:
            while b:=r.read(1048576):
                size+=len(b)
                if size>spec['files'][name]['bytes']:raise ValueError('Download exceeds pinned size')
                f.write(b);time.sleep(.05)
        if size!=spec['files'][name]['bytes'] or sha(partial)!=spec['files'][name]['sha256']:raise ValueError('Downloaded content changed')
        partial.rename(dest)
    required={name for name in spec['files'] if name.endswith('.csv')}
    if not a.verify_only and any(not(a.output/n).exists() for n in required):
        start=time.monotonic();cpu=time.process_time()
        with tarfile.open(a.output/'processed.tar.gz','r|gz') as archive:
            for member in archive:
                name=Path(member.name).name
                if name in required:
                    if not member.isfile() or member.name!='processed_files/'+name or member.size!=spec['files'][name]['bytes']:raise ValueError('Unexpected archive member')
                    dest=a.output/name
                    if not dest.exists():
                        with dest.open('xb') as f:f.write(archive.extractfile(member).read())
                delay=(time.process_time()-cpu)*5-(time.monotonic()-start)
                if delay>0:time.sleep(delay)
    for name,receipt in spec['files'].items():
        if sha(a.output/name)!=receipt['sha256']:raise ValueError('Input verification failed: '+name)
    print(json.dumps({'verified_files':len(spec['files']),'raw_data_redistributed':False}))

if __name__=='__main__':main()
