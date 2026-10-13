"""Verify runnable Markdown directly, including deliberately failing experiments."""
import json
import re
from pathlib import Path
from .code_runner import execute

CONTENT = Path(__file__).resolve().parent / 'content'
FENCE = re.compile(r'^```(c|assembly|machine|rust|verilog|boot) run:([a-z0-9-]+)\n(.*?)^```\s*$', re.M | re.S)


def documented_experiments():
    catalog = json.loads((CONTENT / 'catalog.json').read_text())
    hardware = json.loads((CONTENT / 'hardware.json').read_text())
    extras = json.loads((CONTENT / 'experiments.json').read_text())
    specifications = {(item['file'], item['id']): item for item in extras}
    assert len(specifications) == len(extras), 'Duplicate experiment specification.'
    references = {}
    engines = {}
    for track in catalog:
        for lesson in track['lessons']:
            references[(lesson['file'], track['engine'])] = lesson['expected_state']
            engines[lesson['file']] = {track['engine']}
    for system in hardware:
        for lab in system['labs']:
            engines[lab['file']] = {'c', 'assembly'}
            for engine in engines[lab['file']]:
                references[(lab['file'], engine)] = lab['expected_state']
    seen = set()
    seen_extra = set()
    found_references = set()
    for filename, allowed in engines.items():
        text = (CONTENT / 'lessons' / filename).read_text()
        for match in FENCE.finditer(text):
            engine, identifier, code = match.groups()
            key = (filename, engine, identifier)
            assert key not in seen, f'Duplicate runnable block: {key}'
            seen.add(key)
            assert engine in allowed, f'Wrong terminal engine: {key}'
            if identifier == 'reference':
                spec = {'expected': references[(filename, engine)]}
                found_references.add((filename, engine))
            else:
                spec = specifications[(filename, identifier)]
                seen_extra.add((filename, identifier))
            yield {'file': filename, 'engine': engine, 'id': identifier, 'code': code, **spec}
    assert found_references == set(references), 'An authored guide is missing its runnable reference.'
    assert seen_extra == set(specifications), 'An experiment specification has no matching runnable block.'


def verify_experiment(item):
    from .views import state_checks
    result = execute(item['code'], item['engine'])
    if 'error_contains' in item:
        assert result['errors'], f"{item['file']} / {item['id']}: expected a diagnostic"
        assert item['error_contains'].lower() in '\n'.join(result['errors']).lower(), result['errors']
    else:
        assert not result['errors'], result['errors']
        if 'expected' in item:
            checks = state_checks(result, item['expected'])
            assert checks and all(check['passed'] for check in checks), checks
        if 'expected_outputs' in item:
            rows = result['state']['truth_table']
            for signal, values in item['expected_outputs'].items():
                assert [row[signal] for row in rows] == values, (signal, rows, values)
    return result


def verify_documented_experiments():
    items = list(documented_experiments())
    for item in items:
        try:
            verify_experiment(item)
        except AssertionError as error:
            raise AssertionError(f"{item['file']} / {item['id']}: {error}") from error
    return {'documented_programs': len(items),
            'intentional_error_experiments': sum('error_contains' in item for item in items)}
