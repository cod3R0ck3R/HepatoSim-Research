#!/usr/bin/env python3
"""Render audited benchmark traces. Requires matplotlib; no fitting or simulation."""
import argparse
import json
from pathlib import Path
import statistics

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from analyze_benchmark import quantile
from run_benchmark import at_time, digest, read_trace


LABELS = {
    'repository_default': 'Originalcode: TGFβ1-Pool 6',
    'caption_literal': 'Wörtliche Legende: TGFβ1-Pool 1',
    'without_reinactivation': 'Ohne erneute Inaktivierung reaktivierter MFB',
    'reinactivation_10pct': '10 % erneute Inaktivierung reaktivierter MFB',
}


def verified_traces(condition, results):
    traces = []
    for run in condition['runs']:
        if run['analysis_status'] != 'eligible':
            continue
        path = results / run['job_id'] / 'trace.csv'
        if digest(path) != run['trace_sha256']:
            raise ValueError(f'Trace differs from analysis snapshot: {path}')
        traces.append(read_trace(path))
    if len(traces) != len(condition['completed_seeds']):
        raise ValueError('Analysis seed count and eligible traces disagree')
    return traces


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--analysis', type=Path, required=True)
    parser.add_argument('--results', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True, help='New figure directory')
    args = parser.parse_args()
    data = json.loads(args.analysis.read_text())
    series = {c['id']: verified_traces(c, args.results) for c in data['conditions']}
    args.output.mkdir(parents=True, exist_ok=False)
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
                         'axes.spines.top': False, 'axes.spines.right': False})
    grid = [i / 2 for i in range(481)]
    fig, axes = plt.subplots(2, 2, figsize=(13, 8), sharex=True, layout='constrained')
    for axis, condition in zip(axes.flat, data['conditions']):
        traces = series[condition['id']]
        expected = len(condition['expected_seeds'])
        for index, rows in enumerate(traces):
            axis.plot([r['[T]'] for r in rows], [r['COL1 tot'] / 0.5 for r in rows],
                      color='#196D93', alpha=0.45, linewidth=0.8,
                      label='Einzelne stochastische Läufe' if index == 0 else None)
        if condition['status'] == 'complete':
            values = [[at_time(rows, t)['COL1 tot'] / 0.5 for rows in traces] for t in grid]
            axis.fill_between(grid, [quantile(v, 0.05) for v in values],
                              [quantile(v, 0.95) for v in values], color='#196D93', alpha=0.14,
                              label='5.–95. Perzentil der Seeds')
            axis.plot(grid, [statistics.mean(v) for v in values], color='#16435A',
                      linewidth=1.7, label='Mittel der festgelegten Seeds')
        elif not traces:
            axis.text(0.5, 0.5, 'Keine abgeschlossenen Läufe', ha='center', va='center', transform=axis.transAxes)
        axis.scatter([32, 60], [12, 14], color='#A65516', marker='D', s=28,
                     label='Ungefähre Entwicklungsziele (kein unabhängiger Test)', zorder=5)
        axis.axhline(1, color='#666666', linestyle=':', label='Konstante Baseline')
        axis.axvspan(4, 60, color='#CDA443', alpha=0.10)
        axis.axvline(60, color='#999999', linestyle='--', linewidth=0.8)
        state = 'vollständig' if condition['status'] == 'complete' else 'UNVOLLSTÄNDIG'
        axis.set_title(f"{LABELS[condition['id']]}\nn = {len(traces)}/{expected}; {state}", fontsize=11)
        axis.set(xlim=(0, 243), xlabel='Modellzeit [Tage]', ylabel='COL1 / initiales COL1 [fach]')
        axis.grid(alpha=0.15)
    legend = {}
    for axis in axes.flat:
        handles, labels = axis.get_legend_handles_labels()
        legend.update(zip(labels, handles))
    fig.legend(legend.values(), legend.keys(), loc='outside lower center', ncols=2, fontsize=8)
    fig.suptitle('Eigene Reproduktion: Kollagen im Kappa-Modell von Bouguéon et al. (2024)\n'
                 'Maus-/CCl₄-Kontext; TGFβ1 als Eingangssignal; keine menschliche Prognose', fontsize=14)
    for extension in ('png', 'svg'):
        fig.savefig(args.output / f'collagen-trajectories.{extension}', dpi=170)
    plt.close(fig)

    condition = next(c for c in data['conditions'] if c['id'] == 'repository_default')
    traces = series['repository_default']
    fig, axes = plt.subplots(1, 3, figsize=(13, 4), layout='constrained')
    for axis, observable, label in zip(axes, ('qHSC', 'iHSC', 'aSMA-cells'),
                                       ('Quieszente HSC', 'Inaktivierte HSC', 'αSMA-Modellzellen')):
        for rows in traces:
            axis.plot([r['[T]'] for r in rows], [r[observable] for r in rows],
                      color='#196D93', alpha=0.3, linewidth=0.7)
        if condition['status'] == 'complete':
            values = [[at_time(rows, t)[observable] for rows in traces] for t in grid]
            axis.plot(grid, [statistics.mean(v) for v in values], color='#16435A', linewidth=1.8)
        axis.axvspan(4, 60, color='#CDA443', alpha=0.10)
        axis.axvline(60, color='#999999', linestyle='--', linewidth=0.8)
        axis.set(title=label, xlabel='Modellzeit [Tage]', ylabel='Zellzahl im Modell', xlim=(0, 243))
        axis.grid(alpha=0.15)
    fig.suptitle(f"Fig. 2 B2: eigene Referenz-Zellverläufe, n = {len(traces)}/10 ({condition['status']})\n"
                 'Linien: Seeds; dunkler Mittelwert nur bei vollständiger Bedingung. Keine histologische Flächenmessung.', fontsize=11)
    for extension in ('png', 'svg'):
        fig.savefig(args.output / f'cell-trajectories.{extension}', dpi=170)
    plt.close(fig)
    provenance = {'analysis_sha256': digest(args.analysis), 'matplotlib': matplotlib.__version__,
                  'script_sha256': digest(__file__),
                  'plot_sampling': '0.5-day grid; last observation <= t, no extrapolation; raw individual traces retained',
                  'limits': 'Bands represent seed variability only. Shading marks nominal stimulation days4–60, last pulse56.5. Targets12/14 are approximate published development summaries; errors unknown.',
                  'files': {p.name: digest(p) for p in sorted(args.output.iterdir()) if p.suffix in ('.png', '.svg')}}
    (args.output / 'figure-provenance.json').write_text(json.dumps(provenance, indent=2, ensure_ascii=False) + '\n')


if __name__ == '__main__':
    main()
