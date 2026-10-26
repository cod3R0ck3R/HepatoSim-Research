import math
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import check
from check import sign_interval, summarize, spec, validate


class Checks(unittest.TestCase):
    def test_exact_binomial_boundary_intervals(self):
        low=sign_interval(0,10);high=sign_interval(10,10)
        self.assertEqual(low[0],0);self.assertEqual(high[1],1)
        self.assertAlmostEqual(low[1],1-.025**.1,places=12)
        self.assertAlmostEqual(high[0],.025**.1,places=12)
        middle=sign_interval(5,10)
        self.assertAlmostEqual(middle[0],1-middle[1],places=12)

    def test_bootstrap_reproducible_and_constant_null(self):
        self.assertEqual(summarize([0]*10,1000,4)['mean_bootstrap_percentile_95'],[0,0])
        self.assertEqual(summarize([-1,2,3],1000,4),summarize([-1,2,3],1000,4))
        with self.assertRaises(AssertionError):summarize([1],1000,4)
        with self.assertRaises(AssertionError):summarize([1,math.nan],1000,4)

    def test_mean_and_standard_error(self):
        r=summarize([1,2,3],1000,7)
        self.assertEqual(r['mean'],2);self.assertEqual(r['sd'],1)
        self.assertAlmostEqual(r['mc_standard_error'],1/math.sqrt(3))

    def test_frozen_design(self):
        s=spec();self.assertEqual(len(s['jobs']),11)
        self.assertEqual(set(s['archives']),{str(x) for x in range(101,111)})

    def test_binomial_coverage_on_fixed_probability_grid(self):
        for n in [7,10]:
            bounds=[sign_interval(k,n) for k in range(n+1)]
            for i in range(101):
                p=i/100
                coverage=sum(math.comb(n,k)*p**k*(1-p)**(n-k) for k,(lo,hi) in enumerate(bounds) if lo-1e-12<=p<=hi+1e-12)
                self.assertGreaterEqual(coverage,.95-1e-10)

    def test_public_trace_mapping_rejects_altered_content(self):
        previous=check.HERE
        with tempfile.TemporaryDirectory() as td:
            check.HERE=Path(td)
            try:
                path=Path(td)/'trace.csv'
                path.write_text('[T],qHSC,iHSC,aSMA-cells,COL1 tot\n0,1,0,0,0.5\n')
                entry={'original_sha256':'original-test-hash','published_sha256':check.digest(path),'numeric_sha256':hashlib.sha256(json.dumps(check.read_trace(path),sort_keys=True).encode()).hexdigest()}
                (Path(td)/'public-trace-map.json').write_text(json.dumps({'trace.csv':entry}))
                self.assertTrue(check.trace_matches(path,'original-test-hash'))
                self.assertFalse(check.trace_matches(path,'wrong-original-hash'))
                path.write_text(path.read_text().replace('0.5','0.6'))
                self.assertFalse(check.trace_matches(path,'original-test-hash'))
            finally:
                check.HERE=previous

    def test_validator_catches_wrong_history_and_alternative(self):
        control=[{'[T]':i/2,'COL1 tot':.5,'iHSC':1} for i in range(181)]
        rows=[{**r,'react_fate_fraction':.05 if r['[T]']<60 else .5,'react_exit_fraction_sum':1,'inactive_lifetime_days':730 if r['[T]']<60 else 30} for r in control]
        job={'model':'lowpersist_fate50','fate_after':.5}
        validate(rows,job,control)
        for index,key,value in [(0,'iHSC',2),(180,'inactive_lifetime_days',730),(180,'react_fate_fraction',.05),(0,'[T]',1)]:
            changed=[dict(r) for r in rows];changed[index][key]=value
            with self.assertRaises(AssertionError):validate(changed,job,control)
        with self.assertRaises(AssertionError):validate(rows[:150]+rows[151:],job,control)
        with self.assertRaises(AssertionError):validate(rows,job,control[:-1])

    def test_same_time_updates_require_identical_biology(self):
        control=[{'[T]':i/2,'COL1 tot':.5,'iHSC':1} for i in range(181)]
        rows=[{**r,'react_fate_fraction':.05 if r['[T]']<=60 else .5,'react_exit_fraction_sum':1,'inactive_lifetime_days':730 if r['[T]']<=60 else 30} for r in control]
        transition={**rows[120],'[T]':60.000001,'react_fate_fraction':.5}
        pair=[transition,{**transition,'inactive_lifetime_days':30}]
        job={'model':'lowpersist_fate50','fate_after':.5}
        validate(rows[:121]+pair+rows[121:],job,control)
        for bad in [[pair[0]], [pair[0],{**pair[1],'iHSC':2}], [pair[0],{**pair[1],'[T]':60.000002}]]:
            with self.assertRaises(AssertionError):validate(rows[:121]+bad+rows[121:],job,control)

    def test_revalidation_binds_original_manifest_and_checker(self):
        with tempfile.TemporaryDirectory() as td:
            folder=Path(td)
            record={'status':'invalid_output','returncode':0,'error':'AssertionError: ','trace_sha256':'trace'}
            (folder/'run.json').write_text(json.dumps(record))
            receipt={'run_manifest_sha256':check.digest(folder/'run.json'),'checker_sha256':check.digest(check.__file__),
                     'trace_sha256':'trace','reason':'Sequential same-time parameter updates; unchanged biological state'}
            (folder/'revalidation.json').write_text(json.dumps(receipt))
            self.assertTrue(check.record_for(folder)['output_event_revalidated'])
            receipt['checker_sha256']='changed'
            (folder/'revalidation.json').write_text(json.dumps(receipt))
            with self.assertRaises(AssertionError):check.record_for(folder)


if __name__=='__main__':unittest.main()
