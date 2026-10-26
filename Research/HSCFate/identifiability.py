"""An endpoint counterexample, not biological parameter estimation."""
import json
from pathlib import Path
from run import component, digest, write_json

HERE = Path(__file__).resolve().parent


def calculate():
    spec = json.loads((HERE/'identifiability-spec.json').read_text())
    assert digest(HERE/'identifiability-spec.json') == (HERE/'identifiability-spec.sha256').read_text().strip()
    target = component(30, .5, 3.54)['inactive']
    examples = []
    for half in spec['alternative_inactive_half_days']:
        fate = target / component(30, 1, 3.54, inactive_half=half)['inactive']
        assert 0 <= fate <= 1
        values = {str(day):component(day, fate, 3.54, inactive_half=half)
                  for day in spec['comparison_days']}
        assert abs(values['30']['inactive'] - target) < 1e-12
        assert abs(values['30']['active'] - component(30,.5,3.54)['active']) < 1e-12
        assert all(0 <= p <= 1 for row in values.values() for p in row.values())
        examples.append({'inactive_half_days':half, 'fate_fraction':fate, 'predictions':values})
    for day in ['7','90']:
        assert max(x['predictions'][day]['inactive'] for x in examples) - min(x['predictions'][day]['inactive'] for x in examples) > .01
    return {'spec_sha256':digest(HERE/'identifiability-spec.json'),
            'code_sha256':digest(__file__), 'component_code_sha256':digest(HERE/'run.py'),
            'theoretical_day30_inactive_target':target, 'examples':examples,
            'interpretation':'Same active/inactive day30 endpoints admit different fate/persistence combinations in this conditional subsystem; longitudinal observations distinguish these examples.',
            'biological_fit':False, 'uncertainty_distribution_estimated':False}


if __name__ == '__main__':
    result = calculate()
    write_json(HERE/'identifiability-result.json',result)
    print(json.dumps(result,indent=2))
