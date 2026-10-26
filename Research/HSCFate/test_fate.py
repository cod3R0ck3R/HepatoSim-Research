import math
import random
import tempfile
from pathlib import Path
import unittest
from run import component, specification, common_error, validate, extended_trace


class FateTests(unittest.TestCase):
    def test_kasim_constant_header_aliases(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'trace.csv'
            p.write_text('[T],qHSC,aHSC,aSMA-cells,MFB,react_MFB,react_HSC,iHSC,COL1 high,COL1 low,COL1 tot,iHSC_early,TGFB1_free_total,TGFB1_bound_total,0.05,1.\n90,1,0,0,0,0,0,1,0.5,0,0.5,0,0,0,0.05,1\n')
            rows=extended_trace(p)
            self.assertEqual(rows[0]['react_fate_fraction'],.05)
            self.assertEqual(rows[0]['react_exit_fraction_sum'],1)
            validate(rows,{'model':'control'})

    def test_frozen_inputs(self):
        self.assertEqual(specification()['id'], 'HSR-HSC-FATE-001')

    def test_fate_does_not_change_active_exit(self):
        for day in [0,7,30,90]:
            a=component(day,.05,3.54);b=component(day,.5,3.54)
            self.assertEqual(a['active'],b['active'])
            self.assertAlmostEqual(b['inactive'],10*a['inactive'],places=12)
            self.assertAlmostEqual(sum(a.values()),1,places=12)
            self.assertTrue(all(v>=-1e-12 for v in a.values()))

    def test_waiting_time_simulation(self):
        rng=random.Random(20261026); n=100000; day=7; fate=.5
        counts=dict.fromkeys(['active','early_inactive','inactive','removed'],0)
        for _ in range(n):
            exit_time=rng.expovariate(math.log(2)/3.54)
            if exit_time>day: state='active'
            elif rng.random()>fate: state='removed'
            else:
                mature=exit_time+rng.expovariate(math.log(2)/.75)
                if mature>day: state='early_inactive'
                elif mature+rng.expovariate(math.log(2)/730)>day: state='inactive'
                else: state='removed'
            counts[state]+=1
        for state,p in component(day,fate,3.54).items():
            self.assertLess(abs(counts[state]/n-p),5*math.sqrt(p*(1-p)/n))

    def test_independent_midpoint_quadrature(self):
        # Integrate influx to mature inactive cells, independently of closed-form convolution.
        day=30;n=20000;step=day/n;k=math.log(2)/3.54;mu=math.log(2)/.75;delta=math.log(2)/730
        total=0
        for j in range(n):
            s=(j+.5)*step
            early=.5*k*(math.exp(-k*s)-math.exp(-mu*s))/(mu-k)
            total+=mu*early*math.exp(-delta*(day-s))*step
        self.assertLess(abs(total-component(day,.5,3.54)['inactive']),1e-8)

    def test_validation_rejects_wrong_fate_and_exit_sum(self):
        row={'[T]':90,'COL1 tot':.5,'react_exit_fraction_sum':1,'react_fate_fraction':.5}
        validate([row],{'model':'fate50'})
        for key,value in [('react_exit_fraction_sum',1.5),('react_fate_fraction',.05)]:
            with self.assertRaises(AssertionError):validate([{**row,key:value}],{'model':'fate50'})

    def test_comparison_does_not_ignore_changed_history(self):
        a=[{'[T]':0,'x':1},{'[T]':60,'x':2}];b=[{'[T]':0,'x':3},{'[T]':60,'x':2}]
        self.assertEqual(common_error(a,b,before=60)['maximum_absolute_difference'],2)


if __name__=='__main__':unittest.main()
