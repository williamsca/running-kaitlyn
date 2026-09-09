#!/usr/bin/env python3
"""Build the static training site; dates and completion are handled in the browser."""
import csv
import datetime
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent


def load_config(path):
    config = {}
    for line in path.read_text().splitlines():
        if line.strip() and not line.lstrip().startswith('#'):
            key, value = line.split(':', 1)
            config[key.strip()] = value.strip().strip('"')
    return config


def load_plan(path):
    weeks = []
    with path.open(newline='') as source:
        for row in csv.DictReader(source):
            week = int(row['week'])
            datetime.date.fromisoformat(row['week_start'])
            runs = []
            for kind in ('easy', 'quality', 'long', 'race'):
                miles = float(row[f'{kind}_miles'] or 0)
                if miles <= 0:
                    continue
                detail = row.get(f'{kind}_workout', '')
                if kind == 'easy' and row['phase'] == 'Race':
                    detail = 'Easy shakeout only'
                runs.append(dict(id=f'week-{week}-{kind}', kind=kind, miles=miles, detail=detail))
            weeks.append(dict(week=week, start=row['week_start'], phase=row['phase'],
                              notes=row['notes'], runs=runs, total=sum(r['miles'] for r in runs)))
    if [w['week'] for w in weeks] != list(range(1, len(weeks) + 1)):
        raise ValueError('Plan weeks must be consecutive, starting with week 1')
    return weeks


def build():
    config = load_config(BASE / 'data/config.yaml')
    weeks = load_plan(BASE / 'data' / config['plan_file'])
    data = json.dumps(dict(config=config, weeks=weeks), ensure_ascii=False).replace('<', '\\u003c')
    html = (BASE / 'templates/index.html').read_text().replace('__PLAN_DATA__', data)
    (BASE / 'docs/index.html').write_text(html)
    print(f'Built docs/index.html: {len(weeks)} weeks')


if __name__ == '__main__':
    build()
