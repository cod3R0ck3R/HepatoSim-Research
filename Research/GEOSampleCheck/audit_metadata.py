#!/usr/bin/env python3
"""Small preflight: nine feature/barcode lists and matrix headers, not count entries."""
import argparse
import gzip
import json
from pathlib import Path
import tarfile
from analyze_geo import sha, write_new


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--archive',type=Path,required=True); p.add_argument('--spec',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True); a=p.parse_args()
    spec=json.loads(a.spec.read_text()); assert sha(a.archive)==spec['archive_sha256']
    rows=[]
    with tarfile.open(a.archive) as t:
        members=t.getmembers()
        for group, samples in spec['groups'].items():
            for sample in samples:
                def find(suffix):
                    hits=[m for m in members if m.name.startswith(sample+'_') and m.name.endswith(suffix)]
                    assert len(hits)==1 and hits[0].isfile()
                    return t.extractfile(hits[0])
                features=gzip.decompress(find('features.tsv.gz').read()).decode().splitlines()
                features=[f.split('\t') for f in features]
                barcodes=gzip.decompress(find('barcodes.tsv.gz').read()).decode().splitlines()
                assert all(len(f)==3 and f[2]=='Gene Expression' for f in features)
                assert len(set(f[0] for f in features))==len(features)
                assert len(set(barcodes))==len(barcodes)
                with gzip.GzipFile(fileobj=find('matrix.mtx.gz')) as z:
                    assert z.readline().strip()==b'%%MatrixMarket matrix coordinate integer general'
                    line=z.readline()
                    while line.startswith(b'%'): line=z.readline()
                    dims=list(map(int,line.split()))
                assert dims[:2]==[len(features),len(barcodes)] and dims[2]>0
                targets={g:[f[0] for f in features if f[1]==g] for g in spec['targets']}
                assert all(len(ids)==1 for ids in targets.values())
                rows.append({'sample':sample,'group':group,'dimensions':dims,'target_feature_ids':targets,
                             'mitochondrial_feature_count':sum(f[1].startswith('mt-') for f in features),
                             'feature_and_barcode_ids_unique':True})
    assert len(rows)==9
    write_new(a.output,{'scope':'Feature/barcode lists and matrix headers only; no count-entry, cell-QC or expression-effect claim',
              'spec_sha256':sha(a.spec),'archive_sha256':sha(a.archive),'samples':rows,'sample_count':9,
              'raw_barcodes':sum(r['dimensions'][1] for r in rows),'declared_nonzero_entries':sum(r['dimensions'][2] for r in rows)})
    print('Nine library metadata checks passed; no expression results computed')


if __name__=='__main__': main()
