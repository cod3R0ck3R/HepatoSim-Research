#!/usr/bin/env python3
"""Compare explicit GEO Description, author workbook and cell-metadata labels."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
import tarfile
import xml.etree.ElementTree as ET

NORMALIZE = {'NORMAL':'NORMAL','MASL':'NAFL','MASH':'NASH','NAFL':'NAFL','NASH':'NASH'}
NS = {'m':'http://www.ncbi.nlm.nih.gov/geo/info/MINiML'}


def geo_labels(xml):
    rows = {}
    for sample in ET.fromstring(xml).findall('m:Sample',NS):
        title = sample.findtext('m:Title',default='',namespaces=NS).strip()
        if not title.endswith(', snRNAseq'):
            continue
        if not re.fullmatch(r'JB_\d+, snRNAseq',title):
            raise ValueError('Unexpected RNA library title')
        donor = title.split(',')[0].replace('_','')
        description = sample.findtext('m:Description',default='',namespaces=NS).strip()
        if donor in rows or description not in NORMALIZE:
            raise ValueError('Duplicate donor or missing/unknown GEO Description')
        rows[donor] = {'accession':sample.attrib['iid'],'geo_description':description,'geo_group':NORMALIZE[description]}
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['miniml','workbook','workbook-markdown','cell-metadata','output']:
        parser.add_argument('--'+name,type=Path,required=True)
    a = parser.parse_args()
    with tarfile.open(a.miniml) as archive:
        members = [m for m in archive.getmembers() if m.isfile() and m.name.endswith('.xml')]
        if len(members)!=1 or members[0].size>2000000:raise ValueError('Unexpected MINiML archive')
        geo = geo_labels(archive.extractfile(members[0]).read())
    workbook = {}
    for line in a.workbook_markdown.read_text().splitlines():
        cells = [x.strip().replace('\\_','_') for x in line.strip().strip('|').split('|')]
        if len(cells)==5 and re.fullmatch(r'JB_\d+',cells[1]):
            donor = cells[1].replace('_','')
            if donor in workbook:raise ValueError('Duplicate workbook donor')
            workbook[donor] = {'workbook_group':NORMALIZE[cells[3]],'workbook_accession':cells[4]}
    cells = {}; count = 0
    with a.cell_metadata.open() as f:
        for row in csv.DictReader(f):
            donor,group=row['orig.ident'],NORMALIZE[row['condition']];count+=1
            if donor in cells and cells[donor]!=group:raise ValueError('Mixed per-cell donor label')
            cells[donor]=group
    if not (set(geo)==set(workbook)==set(cells) and len(geo)==18 and count==128223):
        raise ValueError('Unexpected donor/cell coverage')
    rows=[]
    for donor in sorted(geo):
        row={'donor':donor,**geo[donor],**workbook[donor],'cell_metadata_group':cells[donor]}
        if row['accession']!=row['workbook_accession']:raise ValueError('Accession mismatch')
        row['geo_workbook_agree']=row['geo_group']==row['workbook_group']
        row['cell_metadata_agrees']=row['cell_metadata_group']==row['geo_group'];rows.append(row)
    result={'schema_version':1,'accession':'GSE244832','rows':rows,'nuclei':count,
            'geo_workbook_agreement':sum(r['geo_workbook_agree'] for r in rows),
            'cell_metadata_conflicts':[r['donor'] for r in rows if not r['cell_metadata_agrees']],
            'interpretation':'Source agreement is provenance corroboration, not independent biological truth or original-author cell-type verification.',
            'binding':{name:hashlib.sha256(path.read_bytes()).hexdigest() for name,path in vars(a).items() if name!='output'}}
    result['binding']['code_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    with a.output.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps({k:result[k] for k in ['geo_workbook_agreement','cell_metadata_conflicts','nuclei']}))


if __name__=='__main__':main()
