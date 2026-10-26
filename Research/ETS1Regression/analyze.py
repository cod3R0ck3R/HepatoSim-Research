"""Audit Lee2025 Figure2 Sirius-red source normalization; Python standard library only."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import platform
import posixpath
import statistics
import xml.etree.ElementTree as ET
import zipfile

NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
REL = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'
GROUPS = ['control_injury', 'knockout_injury', 'control_regression', 'knockout_regression']


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def worksheet(path, name):
    """Read published literals; never evaluate workbook formulas or infer missing values."""
    with zipfile.ZipFile(path) as z:
        if any(i.file_size > 10_000_000 for i in z.infolist()):
            raise ValueError('Unexpected workbook member size')
        strings = []
        if 'xl/sharedStrings.xml' in z.namelist():
            strings = [''.join(e.itertext()) for e in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si', NS)]
        sheets = ET.fromstring(z.read('xl/workbook.xml')).findall('m:sheets/m:sheet', NS)
        selected = [s for s in sheets if s.attrib['name'] == name]
        if len(selected) != 1:
            raise ValueError('Missing or duplicate worksheet')
        relations = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
        targets = [r.attrib['Target'] for r in relations if r.attrib['Id'] == selected[0].attrib[REL]]
        if len(targets) != 1:
            raise ValueError('Ambiguous worksheet relationship')
        target = targets[0]
        target = target.lstrip('/') if target.startswith('/') else posixpath.normpath('xl/' + target)
        if not target.startswith('xl/worksheets/'):
            raise ValueError('Unexpected worksheet target')
        cells = {}
        for c in ET.fromstring(z.read(target)).findall('.//m:sheetData/m:row/m:c', NS):
            ref = c.attrib['r']
            if c.find('m:f', NS) is not None:
                raise ValueError('Formula requires a separately reviewed recalculation')
            v = c.find('m:v', NS)
            kind = c.attrib.get('t')
            if kind == 'inlineStr':
                value = ''.join(c.find('m:is', NS).itertext())
            elif v is None or v.text is None:
                continue
            elif kind == 's':
                value = strings[int(v.text)]
            elif kind in [None, 'n']:
                value = float(v.text)
                if not math.isfinite(value):
                    raise ValueError('Nonfinite source value')
            else:
                raise ValueError('Unexpected cell type')
            if ref in cells:
                raise ValueError('Duplicate cell reference')
            cells[ref] = value
    return cells


def extract(cells):
    expected = {'A1': 'Sirius Red+ area (%)', 'A2': 'CCl4', 'C2': 'Regression',
                'A3': 'ETS1flox/flox', 'B3': 'ETS1ΔHSC', 'C3': 'ETS1flox/flox', 'D3': 'ETS1ΔHSC'}
    if any(cells.get(k) != v for k, v in expected.items()):
        raise ValueError('Source header or group order changed')
    result = []
    for col in 'ABCD':
        entries = sorted((int(k[1:]), v) for k, v in cells.items() if k[0] == col and k[1:].isdigit() and int(k[1:]) >= 4)
        if [r for r, _ in entries] != list(range(4, 4 + len(entries))) or len(entries) < 2:
            raise ValueError('Missing or insufficient graph points')
        values = [v for _, v in entries]
        if any(not isinstance(v, (float, int)) or not math.isfinite(v) or v <= 0 for v in values):
            raise ValueError('Expected positive finite graph values')
        result.append(values)
    return result


def from_markdown(text, name):
    sections = text.split('## ')
    selected = [s for s in sections if s.splitlines() and s.splitlines()[0].strip() == name]
    if len(selected) != 1:
        raise ValueError('Markdown section not unique')
    rows = [line.strip().strip('|').split('|') for line in selected[0].splitlines()[1:] if line.startswith('|')]
    rows = [[x.strip() for x in row] for row in rows]
    if rows[0][0] != 'Sirius Red+ area (%)' or rows[2][0] != 'CCl4' or rows[2][2] != 'Regression':
        raise ValueError('Markdown table layout changed')
    if rows[3][:4] != ['ETS1flox/flox', 'ETS1ΔHSC', 'ETS1flox/flox', 'ETS1ΔHSC']:
        raise ValueError('Markdown group order changed')
    return [[float(row[i]) for row in rows[4:] if row[i] != 'NaN'] for i in range(4)]


def compare(absolute, supplied, tolerances):
    if len(absolute) != 4 or len(supplied) != 4 or any(len(g) < 2 for g in absolute + supplied):
        raise ValueError('Four nonempty groups required')
    if any(not math.isfinite(x) or x <= 0 for g in absolute + supplied for x in g):
        raise ValueError('Nonpositive or nonfinite value')
    baselines = [statistics.mean(absolute[i]) for i in [0, 1]]
    derived = [[x / baselines[i % 2] for x in values] for i, values in enumerate(absolute)]
    groups = []
    for name, a, d, c in zip(GROUPS, absolute, derived, supplied):
        errors = [abs(x-y) for x, y in zip(sorted(d), sorted(c))] if len(d) == len(c) else None
        groups.append({'group': name, 'n_B': len(a), 'n_C': len(c), 'B_mean_percent_area': statistics.mean(a),
                       'B_sd_percent_area': statistics.stdev(a), 'derived_normalized_mean': statistics.mean(d),
                       'supplied_C_mean': statistics.mean(c), 'max_sorted_abs_discrepancy': max(errors) if errors else None,
                       'matched_by_tolerance': {str(t): sum(x <= t for x in errors) if errors else 0 for t in tolerances},
                       'pass_by_tolerance': {str(t): errors is not None and all(x <= t for x in errors) for t in tolerances}})
    ratios = {}
    for name, data in [('derived_from_B', derived), ('supplied_C', supplied)]:
        means = [statistics.mean(g) for g in data]
        control = means[2] / means[0]; knockout = means[3] / means[1]
        ratios[name] = {'control_remaining_fraction': control, 'knockout_remaining_fraction': knockout,
                        'knockout_vs_control_ratio_of_remaining_fractions': knockout/control}
    counts_equal = len({len(g) for g in absolute + supplied}) == 1
    return {'groups': groups, 'descriptive_ratios': ratios, 'counts_equal': counts_equal,
            'normalization_pass_by_tolerance': {str(t): counts_equal and all(g['pass_by_tolerance'][str(t)] for g in groups) for t in tolerances}}


def check_conversion(original, converted):
    # MarkItDown rounds displayed decimals; all calculations use original XLSX literals.
    if len(original) != len(converted) or any(len(a) != len(b) for a, b in zip(original, converted)):
        raise ValueError('Converted group sizes differ')
    error = max(abs(x-y) for a, b in zip(original, converted) for x, y in zip(a, b))
    if error > 5e-6:
        raise ValueError('Workbook literals disagree with rounded MarkItDown conversion')
    return error


def run(workbook, markdown, spec_path):
    spec = json.loads(Path(spec_path).read_text())
    if sha(workbook) != spec['source_sha256'] or sha(markdown) != spec['markdown_sha256']:
        raise ValueError('Input hash differs from frozen specification')
    b = extract(worksheet(workbook, 'Fig. 2B')); c = extract(worksheet(workbook, 'Fig. 2C'))
    text = Path(markdown).read_text()
    conversion = {name: check_conversion(values, from_markdown(text, name))
                  for name, values in [('Fig. 2B', b), ('Fig. 2C', c)]}
    result = compare(b, c, spec['tolerances'])
    result.update(spec_id=spec['id'], spec_sha256=sha(spec_path), source_sha256=sha(workbook), markdown_sha256=sha(markdown),
                  code_sha256=sha(__file__), python=platform.python_version(), independent_extraction_match_within_5e_6=True,
                  markdown_rounding_max_error=conversion,
                  sample_n_provenance={'article_results': 6, 'figure_legend': 7, 'source_B': [len(g) for g in b], 'source_C': [len(g) for g in c]},
                  animal_identifiers_available=False, inference_performed=False, calibration_performed=False,
                  status='descriptive_source_audit_only', biological_validation=False)
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    for arg in ['workbook', 'markdown', 'spec', 'output']:
        p.add_argument('--'+arg, type=Path, required=True)
    a = p.parse_args()
    result = run(a.workbook, a.markdown, a.spec)
    with a.output.open('x') as f:
        json.dump(result, f, indent=2, ensure_ascii=False, allow_nan=False); f.write('\n')
    print(json.dumps({'status': result['status'], 'normalization_pass': result['normalization_pass_by_tolerance']}))
