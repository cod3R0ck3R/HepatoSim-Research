"""Bounded acquisition and matrix-header audit; no cell-level statistical inference."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import tarfile
import time
import urllib.request

URL='https://ftp.ncbi.nlm.nih.gov/geo/series/GSE295nnn/GSE295293/suppl/GSE295293_RAW.tar'


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    a.output.mkdir(exist_ok=False,parents=True)
    target=a.output/'GSE295293_RAW.tar';partial=target.with_suffix('.partial')
    start=time.monotonic();h=hashlib.sha256();size=0
    with urllib.request.urlopen(URL,timeout=30) as response, partial.open('xb') as out:
        expected=response.headers.get('Content-Length')
        while chunk:=response.read(1024*1024):
            size+=len(chunk)
            if size>450*1024**2 or time.monotonic()-start>180:
                raise RuntimeError('Acquisition budget exceeded; partial retained, not complete')
            out.write(chunk);h.update(chunk)
    if expected and size!=int(expected):raise ValueError('Incomplete HTTP body')
    partial.rename(target)
    matrices=[]
    with tarfile.open(target) as tar:
        members=tar.getmembers()
        for member in members:
            if not member.isfile():raise ValueError('Unexpected non-file tar member')
            if member.name.endswith('matrix.mtx.gz'):
                with tar.extractfile(member) as raw, gzip.GzipFile(fileobj=raw) as stream:
                    header=stream.readline().decode().strip()
                    if not header.startswith('%%MatrixMarket matrix coordinate'):raise ValueError('Unexpected matrix format')
                    line=stream.readline()
                    while line.startswith(b'%'):line=stream.readline()
                    dims=list(map(int,line.split()))
                    if len(dims)!=3 or min(dims)<=0:raise ValueError('Invalid matrix dimensions')
                    matrices.append({'file':member.name,'features':dims[0],'barcodes':dims[1],'nonzero_entries':dims[2]})
    if len(matrices)!=9:raise ValueError('Expected nine sample matrices')
    (a.output/'receipt.json').write_text(json.dumps({'url':URL,'sha256':h.hexdigest(),'bytes':size,'seconds':time.monotonic()-start,'matrix_headers':matrices,'scope':'Downloaded archive and inspected headers only; raw entries, QC and sample-level inference not yet audited'},indent=2)+'\n')
    print(json.dumps({'downloaded_bytes':size,'matrix_count':len(matrices),'sha256':h.hexdigest()}))


if __name__=='__main__':main()
