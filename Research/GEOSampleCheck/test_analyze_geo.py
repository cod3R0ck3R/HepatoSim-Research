import gzip
import io
import tarfile
import unittest
import tempfile
import subprocess
import sys
import hashlib
import json
from pathlib import Path
import numpy as np
from analyze_geo import coordinates, audit_sample, contrast, bh, summarize, read_checkpoint, sample_hash

class Check(unittest.TestCase):
    def matrix(self, body, dims='2 2 2'):
        return io.BytesIO(('%%MatrixMarket matrix coordinate integer general\n'+dims+'\n'+body).encode())
    def test_coordinates_and_chunk_boundary(self):
        rows=list(coordinates(self.matrix('1 1 3\n2 2 4\n'),chunk=1))
        self.assertEqual(sum(int(x[3].sum()) for x in rows),7)
    def test_invalid_inputs(self):
        for body in ['1 1 1\n1 1 2\n','2 2 1\n1 1 2\n','0 1 1\n2 2 2\n','1 1 -1\n2 2 2\n','1 1 1\n','1 1 1.5\n2 2 2\n']:
            with self.subTest(body=body), self.assertRaises(ValueError): list(coordinates(self.matrix(body),chunk=1))
    def test_sample_qc_oracle(self):
        stream=io.BytesIO()
        payloads={'features.tsv.gz':b'e1\tA\tGene Expression\ne2\tmt-X\tGene Expression\ne3\tB\tGene Expression\n','barcodes.tsv.gz':b'a\nb\nc\n','matrix.mtx.gz':b'%%MatrixMarket matrix coordinate integer general\n3 3 6\n1 1 10\n2 1 1\n1 2 10\n2 2 10\n1 3 10\n3 3 1\n'}
        with tarfile.open(fileobj=stream,mode='w') as t:
            for suffix,b in payloads.items():
                b=gzip.compress(b); m=tarfile.TarInfo('S_'+suffix); m.size=len(b); t.addfile(m,io.BytesIO(b))
        stream.seek(0)
        q={'gene_min_cells':2,'features_strict_min':1,'features_strict_max':4,'counts_strict_max':100,'mitochondrial_percent_strict_max':20,'mitochondrial_symbol_prefix':'mt-'}
        with tarfile.open(fileobj=stream) as t: s=audit_sample(t,'S','g',['A','B'],q)
        self.assertEqual(s['raw']['total'],42); self.assertEqual(s['retained_barcodes'],1)
        self.assertEqual(s['qc'],{'total':11,'targets':{'A':10,'B':0}})
    def test_statistics_known_oracle(self):
        r=contrast([4.,5.,6.],[1.,2.,3.]); self.assertAlmostEqual(r['mean_log2cpm_difference'],3)
        self.assertEqual(r['exact_permutation_p'],.1); self.assertEqual((r['loo_min'],r['loo_max']),(2.,4.))
        self.assertEqual(contrast([1,1,1],[1,1,1])['exact_permutation_p'],1)
        np.testing.assert_allclose(bh([.01,.04,.03]),[.03,.04,.04])
    def test_checkpoint_binding_and_damage(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'sample.json'; row={'sample':'s','total':12}; binding={'spec':'a','code':'b'}
            value={'binding':binding,'sample':row,'sample_sha256':sample_hash(row)}
            p.write_text(json.dumps(value)); self.assertEqual(read_checkpoint(p,binding),row)
            with self.assertRaises(ValueError): read_checkpoint(p,{'spec':'changed'})
            value['sample']['total']=13; p.write_text(json.dumps(value))
            with self.assertRaises(ValueError): read_checkpoint(p,binding)

    def test_cli_resume_and_exact_replay(self):
        with tempfile.TemporaryDirectory() as d:
            d=Path(d); script=Path(__file__).with_name('analyze_geo.py')
            spec=json.loads(Path(__file__).with_name('specification-v1.json').read_text())
            archive=d/'fixture.tar'
            features=''.join(f'e{i}\t{g}\tGene Expression\n' for i,g in enumerate(spec['targets']+[f'g{i}' for i in range(202)]))
            matrix='%%MatrixMarket matrix coordinate integer general\n210 4 840\n'+''.join(f'{r} {c} 1\n' for c in range(1,5) for r in range(1,211))
            with tarfile.open(archive,'w') as t:
                for sample in [s for ss in spec['groups'].values() for s in ss]:
                    for suffix,content in [('features.tsv.gz',features),('barcodes.tsv.gz','a\nb\nc\nd\n'),('matrix.mtx.gz',matrix)]:
                        data=gzip.compress(content.encode()); m=tarfile.TarInfo(sample+'_'+suffix); m.size=len(data); t.addfile(m,io.BytesIO(data))
            spec['archive_sha256']=hashlib.sha256(archive.read_bytes()).hexdigest()
            sp=d/'spec.json'; sp.write_text(json.dumps(spec)); checkpoints=d/'checkpoints'
            common=[sys.executable,'-B',str(script),'--spec',str(sp),'--checkpoints',str(checkpoints)]
            def run(name,replay=False):
                cmd=common+['--output',str(d/name)]+(['--replay'] if replay else ['--archive',str(archive)])
                subprocess.run(cmd,check=True,capture_output=True,timeout=20)
            run('first.json'); times={f.name:f.stat().st_mtime_ns for f in checkpoints.iterdir()}
            run('resume.json'); run('replay.json',True)
            self.assertEqual(times,{f.name:f.stat().st_mtime_ns for f in checkpoints.iterdir()})
            self.assertEqual((d/'first.json').read_bytes(),(d/'resume.json').read_bytes())
            self.assertEqual((d/'first.json').read_bytes(),(d/'replay.json').read_bytes())
            result=json.loads((d/'first.json').read_text())
            self.assertEqual(result['totals'],{'raw_barcodes':36,'retained_barcodes':36})
            self.assertTrue(all(r['mean_log2cpm_difference']==0 and r['exact_permutation_p']==1 for r in result['contrasts']['qc']))

    def test_no_pseudoreplication(self):
        with self.assertRaises(ValueError): summarize({'groups':{'g':['s']}},[])

if __name__=='__main__': unittest.main()
