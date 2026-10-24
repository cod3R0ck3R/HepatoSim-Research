#!/usr/bin/env python3
"""Download the two pinned GEO inputs; retain originals locally."""
import hashlib
import json
from pathlib import Path
import sys
import urllib.request

root=Path(sys.argv[1]);root.mkdir(parents=True,exist_ok=True)
provenance=json.loads(Path(__file__).with_name('provenance.json').read_text())
for row in provenance['sources']:
    if row['name'] not in ('GSE135251_RAW.tar','GSE135251_family.xml.tgz'):continue
    dest=root/row['name']
    if not dest.exists():
        temp=dest.with_suffix(dest.suffix+'.partial')
        with urllib.request.urlopen(row['url'],timeout=90) as response, temp.open('xb') as out:
            total=0
            while block:=response.read(1048576):
                total+=len(block)
                if total>60000000:raise ValueError('Download cap')
                out.write(block)
        if hashlib.sha256(temp.read_bytes()).hexdigest()!=row['sha256']:raise ValueError('Source hash mismatch')
        temp.rename(dest)
    if hashlib.sha256(dest.read_bytes()).hexdigest()!=row['sha256']:raise ValueError('Existing input hash mismatch')
    print(row['name'],'verified')
