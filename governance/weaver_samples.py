"""Convert SDK OTLP JSON to Weaver 0.19's file-input sample format.

Only metric samples are adapted; resource requirements are checked separately.
"""
import argparse
import json
from pathlib import Path
from governance.check import attrs


def convert(payload):
    samples = []
    for rm in payload.get('resourceMetrics', []):
        for sm in rm.get('scopeMetrics', []):
            for m in sm.get('metrics', []):
                if 'sum' in m and m['sum'].get('isMonotonic'):
                    kind, data = 'counter', m['sum']
                elif 'histogram' in m:
                    kind, data = 'histogram', m['histogram']
                else:
                    raise ValueError('Unsupported metric for Weaver adapter: ' + m['name'])
                points = []
                for p in data.get('dataPoints', []):
                    point = {'attributes': [{'name': k, 'value': v} for k, v in attrs(p.get('attributes', [])).items()]}
                    if kind == 'counter':
                        point['value'] = float(p.get('asDouble', p.get('asInt', 0)))
                    else:
                        point.update(count=int(p['count']), sum=p.get('sum', 0),
                                     bucket_counts=[int(n) for n in p['bucketCounts']])
                        for key in ('min', 'max'):
                            if key in p:
                                point[key] = p[key]
                    points.append(point)
                samples.append({'metric': {'name': m['name'], 'unit': m['unit'],
                                           'instrument': kind, 'data_points': points}})
    if not samples:
        raise ValueError('Cannot adapt empty telemetry')
    return samples


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input')
    parser.add_argument('output')
    args = parser.parse_args()
    Path(args.output).write_text(json.dumps(convert(json.loads(Path(args.input).read_text())), indent=2) + '\n')
