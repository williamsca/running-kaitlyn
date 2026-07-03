# Kaitlyn's Running Plan Site

## Overview

A static, single-page site that shows Kaitlyn her training plan for the week and a
compressed timeline through race day. Rebuilt weekly by a scheduled script. No JavaScript,
no interactivity — just HTML + CSS served from a static host (GitHub Pages or S3).

---

## Architecture

### Data Model

```
data/
  config.yaml        # race name, race date, plan start date, current week override (optional)
  plan.csv           # full training plan: week_number, day, workout_type, description, distance_mi, notes
```

**config.yaml** example:
```yaml
race_name: "Charlottesville 10 Miler"
race_date: 2026-10-03
plan_start_date: 2026-06-30   # Monday of week 1
```

**plan.csv** example:
```csv
week,day,duration_min,label,detail
1,Tuesday,35,Easy,"35 min @ easy pace (10:30–11:00/mi)"
1,Thursday,40,Tempo,"10 min warmup | 15 min @ 8:45/mi | 10 min cooldown"
1,Saturday,60,Long,"60 min @ easy pace; last 10 min pick up to moderate"
2,Thursday,45,Intervals,"10 min warmup | 4x(3 min @ 8:15/mi + 90s jog) | 10 min cooldown"
...
```

- Only rows for prescribed run days (no rest days in the file).
- `duration_min` is total run time in minutes.
- `label` is a short tag (Easy, Tempo, Intervals, Long, Race) used for styling.
- `detail` is the full workout prescription — the primary content Kaitlyn reads,
  displayed prominently.

Why CSV: easy to edit in a spreadsheet, trivial to parse, version-controllable diffs.

### Build Script (`build.py`)

A single Python script (stdlib only — no deps) that:

1. Reads `config.yaml` and `plan.csv`.
2. Computes "current week" from today's date relative to `plan_start_date`.
3. Extracts this week's runs from the CSV.
4. Compresses the full plan into a timeline summary (week number, total mileage, key
   workout label) for all weeks, highlighting the current week and marking past weeks
   as complete.
5. Renders `index.html` from a Jinja-style template (or simple string formatting to
   stay dependency-free).

Internal consistency comes from a single source of truth: the CSV. The config sets the
anchor dates; the script derives everything else. No manual syncing needed.

### Weekly Refresh Loop

A GitHub Actions cron job (runs every Monday at 6 AM ET):

```yaml
on:
  schedule:
    - cron: '0 10 * * 1'   # 10:00 UTC = 6:00 AM ET
```

Steps: checkout, run `build.py`, commit + push the regenerated `index.html` to the
deploy branch (or trigger GitHub Pages rebuild). That's it.

### Reusability for Future Arcs

To start a new training cycle:
1. Update `config.yaml` with the new race name and dates.
2. Replace or edit `plan.csv` with the new plan.
3. Push. The next Monday build picks it up automatically.

The template, build script, and assets stay the same across arcs.

---

## Design

### Principles

- **Static and flat.** No hover states, no animations, no JS. Feels like a printed
  training card pinned to the fridge.
- **Clean and airy.** Generous whitespace. Information hierarchy through size and weight,
  not color or boxes.
- **Charlottesville / Blue Ridge palette.** Muted earthy greens, slate blue (ridge
  silhouette), warm cream/off-white background, a touch of brick-red (UVA Rotunda
  columns). No bright saturated colors.

### Color Palette

| Role        | Color       | Evokes                    |
|-------------|-------------|---------------------------|
| Background  | `#FAF8F4`   | Morning fog, paper        |
| Text        | `#2C3E2D`   | Deep forest green         |
| Accent      | `#5B7E8C`   | Blue Ridge haze           |
| Highlight   | `#A3533A`   | UVA brick                 |
| Muted       | `#C2CABB`   | Piedmont grass, lichen    |

### Layout (top to bottom)

1. **Header** — Site title ("Kaitlyn's 10 Miler") and a small trail/runner illustration
   (from assets). Race date displayed subtly below.

2. **This Week** — The main content block. Shows only prescribed runs (typically 3–4
   per week). Each entry: day name, duration, label tag for quick scanning, and the
   full detail block as the primary readable content. Today's run gets a subtle
   left-border highlight in accent blue.

3. **Timeline** — A horizontal or vertical track showing every week as a compact node:
   week number, total duration (sum of that week's runs), key workout label. Past weeks
   are faded/muted, current week is highlighted, future weeks are normal weight. The
   finish-line asset sits at the end.

4. **Footer** — Small decorative strip. Maybe the winding-trail asset or a silhouette
   ridge line in CSS. No links, no nav — there's only one page.

### Typography

- System font stack (no external requests): `-apple-system, 'Segoe UI', sans-serif`
  for body, a simple serif or monospace for the week labels to give a "training log" feel.
- Large, readable sizes. Nothing below 14px.

### Assets Usage

| Asset                         | Placement                              |
|-------------------------------|----------------------------------------|
| Runner on trail               | Header illustration (small, right-aligned) |
| Winding trail / Blue Ridge    | Background watermark or footer decoration  |
| Finish line (C'ville 10 Miler)| End of the timeline                    |
| UVA Rotunda                   | Maybe a subtle decorative touch, or omit if too busy |
| Bodo's Bagels                 | Easter egg — maybe appears on rest days as a reward icon |

### Responsive

Single-column by default; works on phone screens without media queries needed (the
layout is already linear). Max-width ~640px centered on desktop for comfortable reading.

---

## File Structure (final)

```
running-kaitlyn/
  assets/            # illustrations (PNGs with transparent backgrounds)
  data/
    config.yaml
    plan.csv
  templates/
    index.html       # HTML template with placeholders
    style.css        # inline or linked
  build.py           # generates site
  docs/              # output directory (GitHub Pages serves from here)
    index.html
  .github/
    workflows/
      build.yaml     # weekly cron
  plan.md            # this file
```

---

## Decisions

- **Hosting**: GitHub Pages (served from `docs/` on main branch).
- **Only prescribed runs**: The "This Week" section shows only days with actual runs —
  no rest days, no cross-train placeholders. If there are 3 runs that week, 3 entries.
- **Rich workout detail**: Each run's notes will contain structured workout blocks
  (e.g., "15 min @ easy pace, 4x(3 min @ tempo / 90s jog), 10 min cooldown"). This is
  the most important info on the page — display it clearly and completely.
- **Countdown**: Show "X days until race" prominently near the header.
