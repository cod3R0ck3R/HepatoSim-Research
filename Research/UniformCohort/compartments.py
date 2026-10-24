#!/usr/bin/env python3
"""Outcome-blind addendum using explicitly cited reanalysis cluster assignments."""
import argparse
import json
import math
from pathlib import Path
import numpy as np
import analyze


def merge(result, spec):
    rows=[]
    for name,clusters in spec['compartments'].items():
        donors=sorted({r['donor'] for r in result['donor_cluster_values']})
        for d in donors:
            source=[r for r in result['donor_cluster_values'] if r['donor']==d and r['cluster'] in clusters]
            if len(source)!=len(clusters) or len({r['condition'] for r in source})!=1:raise ValueError('Missing/duplicate/inconsistent compartment rows')
            total=sum(r['total_UMI'] for r in source)
            genes={g:{'UMI':sum(r['genes'][g]['UMI'] for r in source),
                      'detected_nuclei':sum(r['genes'][g]['detected_nuclei'] for r in source)} for g in source[0]['genes']}
            for v in genes.values():v['log2cpm']=math.log2(1+1e6*v['UMI']/total) if total else None
            rows.append({'donor':d,'condition':source[0]['condition'],'compartment':name,
                         'nuclei':sum(r['nuclei'] for r in source),'total_UMI':total,'genes':genes})
    return rows


def summarize(result,spec):
    rows=merge(result,spec);tests=[];rng=np.random.Generator(np.random.PCG64(spec['seed']))
    for compartment,gene in spec['contrasts']:
        groups=[[r for r in rows if r['compartment']==compartment and r['condition']==g and r['nuclei']>=spec['min_nuclei']] for g in spec['contrast']]
        a,b=groups;t={'compartment':compartment,'gene':gene,'disease_donors':[r['donor'] for r in a],'control_donors':[r['donor'] for r in b]}
        if min(len(a),len(b))>=spec['min_donors_per_group']:
            t.update(analyze.statistics([r['genes'][gene]['log2cpm'] for r in a],[r['genes'][gene]['log2cpm'] for r in b],rng));t['status']='exploratory_tested'
        else:t.update(status='insufficient_donors',exact_permutation_p=1.0)
        tests.append(t)
    for t,q in zip(tests,analyze.shared.bh([t['exact_permutation_p'] for t in tests])):t['bh_q_2']=q
    markers={}
    for g in ['CD163','NGFR']:
        markers[g]={}
        for name in spec['compartments']:
            subset=[r for r in rows if r['compartment']==name];den=sum(r['total_UMI'] for r in subset)
            markers[g][name]={'pooled_cpm':1e6*sum(r['genes'][g]['UMI'] for r in subset)/den,
                'detected_fraction':sum(r['genes'][g]['detected_nuclei'] for r in subset)/sum(r['nuclei'] for r in subset)}
    return {'schema_version':1,'accession':result['accession'],'donor_compartment_values':rows,'tests':tests,
        'compartment_nuclei':{name:sum(r['nuclei'] for r in rows if r['compartment']==name) for name in spec['compartments']},
        'marker_coherence_descriptive':markers,'joint_direction_rule_met':all(t.get('loo_min',-1)>0 and t.get('mean_log2cpm_difference',-1)>0 for t in tests),
        'label_scope':'Published reanalysis assignments; myeloid is not pure macrophages. Marker coherence does not prove purity.',
        'independent_biological_validation':False,'drug_effect_estimated':False}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['result','spec','output']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();result=json.loads(a.result.read_text());spec=json.loads(a.spec.read_text())
    if result['binding']['code_sha256']!=analyze.shared.sha(analyze.__file__) or result['binding']['parser_sha256']!=analyze.shared.sha(analyze.shared.__file__):raise ValueError('Input code binding mismatch')
    out=summarize(result,spec);out['binding']={'input_result_sha256':analyze.shared.sha(a.result),'spec_sha256':analyze.shared.sha(a.spec),'code_sha256':analyze.shared.sha(__file__),'statistics_code_sha256':analyze.shared.sha(analyze.__file__),'numpy':np.__version__}
    analyze.shared.write_new(a.output,out);print(json.dumps({'result_sha256':analyze.shared.sha(a.output),'joint_direction_rule_met':out['joint_direction_rule_met'],'tests':out['tests']}))

if __name__=='__main__':main()
