#!/usr/bin/env python3
import csv
import datetime
import os
import re

# ── config ────────────────────────────────────────────────────────────────────

def load_config(path):
    config = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            key, _, val = line.partition(":")
            val = val.strip().strip('"')
            config[key.strip()] = val
    return config

def parse_date(s):
    return datetime.date.fromisoformat(s.strip().split("#")[0].strip())

# ── data ──────────────────────────────────────────────────────────────────────

def load_plan(path):
    runs = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            runs.append({
                "week": int(row["week"]),
                "day": row["day"],
                "duration_min": int(row["duration_min"]),
                "label": row["label"],
                "detail": row["detail"],
            })
    return runs

def current_week_number(plan_start, today):
    delta = (today - plan_start).days
    if delta < 0:
        return 0
    return delta // 7 + 1

def week_start_date(plan_start, week_number):
    return plan_start + datetime.timedelta(weeks=week_number - 1)

DAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

def day_date(week_start, day_name):
    idx = DAY_ORDER.index(day_name)
    return week_start + datetime.timedelta(days=idx)

def days_until(target, today):
    return (target - today).days

# ── html helpers ──────────────────────────────────────────────────────────────

LABEL_CLASSES = {
    "Easy":      "label-easy",
    "Tempo":     "label-tempo",
    "Intervals": "label-intervals",
    "Long":      "label-long",
    "Race":      "label-race",
}

def label_tag(label):
    cls = LABEL_CLASSES.get(label, "label-easy")
    return f'<span class="label {cls}">{label}</span>'

def escape(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def render_detail(detail):
    # Split on | for multi-block workouts
    blocks = [b.strip() for b in detail.split("|")]
    if len(blocks) == 1:
        return f'<p class="detail">{escape(blocks[0])}</p>'
    parts = "".join(f'<li>{escape(b)}</li>' for b in blocks)
    return f'<ol class="detail-blocks">{parts}</ol>'

def render_run_card(run, date, is_today):
    today_class = " today" if is_today else ""
    date_str = date.strftime("%A, %b %-d") if os.name != "nt" else date.strftime("%A, %b %d").replace(" 0", " ")
    duration_str = f"{run['duration_min']} min" if run['duration_min'] > 0 else "Race day"
    return f"""
    <div class="run-card{today_class}">
      <div class="run-header">
        <span class="run-day">{date_str}</span>
        <span class="run-duration">{duration_str}</span>
        {label_tag(run['label'])}
      </div>
      {render_detail(run['detail'])}
    </div>"""

def render_timeline(runs, current_week, plan_start, race_date, total_weeks):
    weeks = {}
    for r in runs:
        w = r["week"]
        weeks.setdefault(w, {"duration": 0, "labels": []})
        weeks[w]["duration"] += r["duration_min"]
        if r["label"] not in weeks[w]["labels"]:
            weeks[w]["labels"].append(r["label"])

    nodes = []
    for w in range(1, total_weeks + 1):
        wdata = weeks.get(w, {"duration": 0, "labels": []})
        wstart = week_start_date(plan_start, w)
        wend = wstart + datetime.timedelta(days=6)
        date_range = f"{wstart.strftime('%b %-d') if os.name != 'nt' else wstart.strftime('%b %d').replace(' 0', ' ')}–{wend.strftime('%-d') if os.name != 'nt' else wend.strftime('%d').lstrip('0')}"

        if w < current_week:
            state = "past"
        elif w == current_week:
            state = "current"
        else:
            state = "future"

        key_labels = ", ".join(wdata["labels"]) if wdata["labels"] else "Race"
        total_min = wdata["duration"]
        duration_str = f"{total_min} min" if total_min > 0 else ""

        nodes.append(f"""
      <div class="week-node {state}">
        <div class="week-dates">{date_range}</div>
        <div class="week-labels">{key_labels}</div>
        {"<div class='week-duration'>" + duration_str + "</div>" if duration_str else ""}
      </div>""")

    finish = """
      <div class="week-node finish">
        <div class="week-labels">Race Day</div>
      </div>"""

    return f'<div class="timeline">{"".join(nodes)}{finish}</div>'

# ── full page ─────────────────────────────────────────────────────────────────

CSS = """
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  background: #FAF8F4;
  color: #2C3E2D;
  font-family: -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif;
  font-size: 17px;
  line-height: 1.6;
  max-width: 660px;
  margin: 0 auto;
  padding: 2rem 1.25rem 4rem;
}

/* ── header ── */
.site-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 2.5rem;
  border-bottom: 2px solid #C2CABB;
  padding-bottom: 1.5rem;
}
.header-text h1 {
  font-size: 1.75rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: #2C3E2D;
  line-height: 1.2;
}
.race-meta {
  margin-top: 0.4rem;
  font-size: 0.9rem;
  color: #5B7E8C;
}
.countdown {
  font-size: 2.25rem;
  font-weight: 800;
  color: #A3533A;
  line-height: 1;
  text-align: right;
  white-space: nowrap;
}
.countdown-label {
  font-size: 0.75rem;
  color: #5B7E8C;
  text-align: right;
  margin-top: 0.2rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}
/* ── section titles ── */
.section-title {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: #5B7E8C;
  margin-bottom: 1rem;
}

/* ── run cards ── */
.this-week { margin-bottom: 3rem; }

.run-card {
  border-left: 3px solid #C2CABB;
  padding: 0.75rem 0 0.75rem 1rem;
  margin-bottom: 1.25rem;
}
.run-card.today {
  border-left-color: #5B7E8C;
}
.run-header {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  flex-wrap: wrap;
  margin-bottom: 0.4rem;
}
.run-day {
  font-weight: 600;
  font-size: 0.95rem;
}
.run-duration {
  font-size: 0.85rem;
  color: #5B7E8C;
}
.label {
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  padding: 0.15em 0.5em;
  border-radius: 3px;
}
.label-easy      { background: #E8EFE6; color: #3A6640; }
.label-tempo     { background: #E8F0F3; color: #2F5F6E; }
.label-intervals { background: #F3EBE6; color: #7A3B24; }
.label-long      { background: #EDE8E3; color: #5C4A38; }
.label-race      { background: #A3533A; color: #FAF8F4; }

.detail {
  font-size: 0.95rem;
  color: #3E5040;
}
.detail-blocks {
  list-style: none;
  font-size: 0.95rem;
  color: #3E5040;
  padding-left: 0;
}
.detail-blocks li {
  padding: 0.25rem 0;
  padding-left: 1.2rem;
  position: relative;
}
.detail-blocks li::before {
  content: "→";
  position: absolute;
  left: 0;
  color: #C2CABB;
  font-size: 0.8rem;
  top: 0.35rem;
}

/* ── timeline ── */
.timeline-section { margin-bottom: 3rem; }

.timeline {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}
.week-node {
  border: 1px solid #C2CABB;
  border-radius: 6px;
  padding: 0.5rem 0.65rem;
  min-width: 80px;
  font-size: 0.78rem;
}
.week-node.past {
  opacity: 0.4;
}
.week-node.current {
  border-color: #5B7E8C;
  border-width: 2px;
  background: #F0F5F6;
}
.week-node.finish {
  border-style: dashed;
  border-color: #A3533A;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
}
.week-dates {
  color: #7A8F7D;
  font-size: 0.7rem;
}
.week-labels {
  color: #5B7E8C;
  font-size: 0.72rem;
  margin-top: 0.15rem;
}
.week-duration {
  color: #A3533A;
  font-size: 0.7rem;
  font-weight: 600;
}

/* ── footer ── */
.site-footer {
  border-top: 1px solid #C2CABB;
  padding-top: 1rem;
}
.footer-text {
  font-size: 0.78rem;
  color: #7A8F7D;
}
"""

def render_page(config, runs, today):
    race_date = parse_date(config["race_date"])
    plan_start = parse_date(config["plan_start_date"])
    race_name = config["race_name"]

    current_week = current_week_number(plan_start, today)
    total_weeks = max(r["week"] for r in runs)
    days_left = days_until(race_date, today)

    # This week's runs
    week_runs = [r for r in runs if r["week"] == current_week]
    week_start = week_start_date(plan_start, current_week)

    if week_runs:
        cards = ""
        for run in week_runs:
            run_date = day_date(week_start, run["day"])
            is_today = (run_date == today)
            cards += render_run_card(run, run_date, is_today)
        this_week_html = f'<section class="this-week"><p class="section-title">This week</p>{cards}</section>'
    else:
        this_week_html = f'<section class="this-week"><p class="section-title">This week</p><p>No runs scheduled — rest up!</p></section>'

    timeline_html = f'<section class="timeline-section"><p class="section-title">Training timeline</p>{render_timeline(runs, current_week, plan_start, race_date, total_weeks)}</section>'

    race_date_str = race_date.strftime("%B %-d, %Y") if os.name != "nt" else race_date.strftime("%B %d, %Y").replace(" 0", " ")

    countdown_str = f"{days_left}" if days_left > 0 else "Race day!"
    countdown_label = "days to race" if days_left > 0 else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{race_name} Training</title>
  <style>{CSS}</style>
</head>
<body>

<header class="site-header">
  <div class="header-text">
    <h1>Kaitlyn's<br>Training Plan</h1>
    <p class="race-meta">{race_name} &middot; {race_date_str}</p>
  </div>
  <div>
    <div class="countdown">{countdown_str}</div>
    {"<div class='countdown-label'>" + countdown_label + "</div>" if countdown_label else ""}
  </div>
</header>

{this_week_html}
{timeline_html}

<footer class="site-footer">
  <p class="footer-text">Updated every Monday &middot; {today.strftime("%B %-d, %Y") if os.name != "nt" else today.strftime("%B %d, %Y").replace(" 0", " ")}</p>
</footer>

</body>
</html>"""

# ── main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    base = os.path.dirname(os.path.abspath(__file__))
    config = load_config(os.path.join(base, "data", "config.yaml"))
    runs = load_plan(os.path.join(base, "data", "plan.csv"))
    today = datetime.date.today()
    html = render_page(config, runs, today)
    out_path = os.path.join(base, "docs", "index.html")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Built {out_path} (week {current_week_number(parse_date(config['plan_start_date']), today)}, {days_until(parse_date(config['race_date']), today)} days to race)")
