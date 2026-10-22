#!/usr/bin/env python3
"""Extract Table S2 CCl4 group aggregates from a local MarkItDown transcription."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import re

PDF_SHA256 = 'b26583fb964fa2ec4629725a35458014ddfa34e7387e679306aab181dcfeea2a'
MARKDOWN_SHA256 = '2dfd2736ef980e5b3c02bd71778412ab2aa52ed22b569109d8d05884301c3743'


def extract(text):
    start, end = '\nCCl Healthy controls', '\nTAA Healthy controls'
    if text.count(start) != 1 or text.count(end) != 1:
        raise ValueError('Expected distinct CCl4 and TAA sections exactly once')
    section = text.split(start)[1].split(end)[0]
    if end not in text.split(start)[1]:
        raise ValueError('Unexpected section order')
    groups = re.findall(r'\((C-|C\+|R1|R2)\) n=(\d+)', section)
    if [group for group, _ in groups] != ['C-', 'C+', 'R1', 'R2']:
        raise ValueError('Missing or reordered animal counts')
    lines = [line for line in section.splitlines() if line.startswith('Fibrosis (CPA %)')]
    if len(lines) != 1:
        raise ValueError('Expected one CPA row in CCl4 section')
    number = r'(\d+(?:\.\d+)?)'
    values = re.findall(number + r' \(' + number + '-' + number + r'\)', lines[0])
    if len(values) != 4:
        raise ValueError('Expected four median/IQR triples')
    rows = []
    for (group, n), triple, day in zip(groups, values, (None, 0, 7, 14)):
        median, q1, q3 = map(float, triple)
        if int(n) < 1 or not 0 <= q1 <= median <= q3 <= 100:
            raise ValueError('Invalid animal count or CPA quartiles')
        rows.append({'study': 'Hofer2025', 'toxin': 'CCl4', 'group': group,
                     'days_after_withdrawal': day, 'n_animals': int(n),
                     'median_cpa_percent': median, 'q1_cpa_percent': q1, 'q3_cpa_percent': q3,
                     'statistic': 'median_and_IQR', 'unit': 'percent_collagen_proportionate_area',
                     'source_table': 'Supplementary Table2, page13',
                     'design': 'separate sacrifice groups; not individual longitudinal observations'})
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--markdown', required=True, type=Path)
    parser.add_argument('--source-pdf', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    if hashlib.sha256(args.source_pdf.read_bytes()).hexdigest() != PDF_SHA256:
        raise ValueError('Source PDF differs from the MD5-verified NCBI version')
    if hashlib.sha256(args.markdown.read_bytes()).hexdigest() != MARKDOWN_SHA256:
        raise ValueError('Transcription differs from the reviewed MarkItDown output; review before importing')
    if args.output.exists() or args.output.with_suffix('.provenance.json').exists():
        raise FileExistsError('Output or provenance already exists; retain previous evidence')
    text = args.markdown.read_text()
    rows = extract(text)
    with args.output.open('x', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    provenance = {'doi': '10.1002/ueg2.12643', 'pmcid': 'PMC11999040', 'article_version': 1,
                  'pdf_sha256': PDF_SHA256, 'markdown_sha256': hashlib.sha256(args.markdown.read_bytes()).hexdigest(),
                  'csv_sha256': hashlib.sha256(args.output.read_bytes()).hexdigest(),
                  'extractor_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  'method': 'Printed table transcription via existing MarkItDown; no figure digitization, unit conversion, averaging or imputation.',
                  'source_license': 'CC BY-NC-ND; source PDF and derived local review files not redistributed here.',
                  'role': 'candidate external evaluation dataset; values inspected for eligibility before any new prediction test; no fitting performed',
                  'limits': ['IQR is not SD or a confidence interval.', 'No individual animal values reconstructed.',
                             'Control denominator uncertainty not estimated.', 'No established mapping from COL1 tokens to total PSR CPA.']}
    with args.output.with_suffix('.provenance.json').open('x') as stream:
        json.dump(provenance, stream, indent=2); stream.write('\n')
    print(json.dumps({'groups': len(rows), 'source_pdf_verified': True, 'role': provenance['role']}))


if __name__ == '__main__':
    main()
