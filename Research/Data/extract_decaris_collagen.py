"""Read complete collagen I/III rows only; preserve published units and missingness."""
import argparse
import hashlib
import json
from pathlib import Path
import re


def extract(abundance, synthesis):
    subjects = ['003', '004', '005', '007', '009', '011']
    for text in [abundance, synthesis]:
        if re.findall(r'#(\d{3})', text)[:6] != subjects:
            raise ValueError('Subject column order changed')
    marker = 'Supplementary Table 2 Fractional synthesis rate - % new per day (k)'
    if marker not in synthesis or 'Total fraction new' not in synthesis:
        raise ValueError('Missing measurement/unit sections')
    fraction, rate = synthesis.split(marker, 1)
    rows = []
    for accession in ['P02452', 'P08123', 'P02461']:
        arrays = []
        for text, percent in [(abundance, False), (fraction, True), (rate, True)]:
            lines = [line for line in text.splitlines() if accession in line]
            if len(lines) != 1:
                raise ValueError('Missing or duplicated collagen row')
            tail = lines[0].split(accession)[1]
            values = re.findall(r'(\d+(?:\.\d+)?)%', tail) if percent else tail.split()[:6]
            if len(values) != 6:
                raise ValueError('Incomplete collagen row; do not impute')
            arrays.append([float(x) for x in values])
        for i, subject in enumerate(subjects):
            rows.append({'published_subject_id': subject, 'uniprot': accession,
                         'relative_abundance_units': arrays[0][i],
                         'fraction_new_percent_over_labeling_period': arrays[1][i],
                         'fractional_synthesis_percent_per_day': arrays[2][i]})
    if any(not 0 <= row['fraction_new_percent_over_labeling_period'] <= 100 for row in rows):
        raise ValueError('Invalid percentage')
    return rows


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['abundance', 'synthesis', 'output']:
        p.add_argument('--'+name, required=True, type=Path)
    a = p.parse_args()
    rows = extract(a.abundance.read_text(), a.synthesis.read_text())
    with a.output.open('x') as stream:
        json.dump({'rows':rows, 'source_doi':'10.1371/journal.pone.0123311',
                   'input_sha256':{x.name:hashlib.sha256(x.read_bytes()).hexdigest() for x in [a.abundance,a.synthesis]},
                   'method':'Printed tables via MarkItDown; no digitization, imputation or unit conversion; three complete collagen chains only',
                   'limits':'Six hepatic subjects; not paired regression observations, no separately measured clearance rate'},stream,indent=2)
