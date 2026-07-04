# /training-plan — Generate training plan CSV

Read `data/config.yaml` and use Claude to build a complete `data/plan.csv` that covers every week from `plan_start_date` through race week.

## Inputs from config.yaml

- `race_name` — name of the race
- `race_location` — location
- `race_date` — race date (YYYY-MM-DD)
- `plan_start_date` — first Monday of the plan (YYYY-MM-DD)
- `goal_pace` — target race pace (MM:SS per mile)

## Your task

1. Read `data/config.yaml`.
2. Calculate the number of training weeks between `plan_start_date` and `race_date`.
3. Design a periodized plan appropriate for the race distance and goal pace. Use these guidelines:
   - Build volume gradually (no more than ~10% per week), with a recovery week every 3–4 weeks (reduce volume ~20%).
   - Taper for the final 1–2 weeks before race day.
   - Include a mix of run types: Easy, Tempo, Intervals, Long, and Race (race day only).
   - Each week should have 2–4 runs. Long runs go on Saturday. Easy/Tempo/Intervals go on Tuesday and/or Thursday.
   - Append 4–6 × 20–30 sec strides (accelerate to ~90% effort, walk/jog back for full recovery) to most Easy runs throughout the plan, including recovery weeks and taper. Omit only on the day before a hard workout or the day before race day.
   - Race week: include one final shakeout Easy run mid-week if desired, then Race on the race's day of week.
   - `duration_min` should be 0 for the Race row.
   - `detail` should be a plain-English description of the workout. Use `|` to separate blocks within a single workout (e.g. warmup | main set | cooldown).
4. Write the result to `data/plan.csv` with exactly these columns (no extras):

```
week,day,duration_min,label,detail
```

Valid values for `label`: Easy, Tempo, Intervals, Long, Race.
Valid values for `day`: Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday.

5. After writing the file, run `python build.py` to regenerate `docs/index.html`.

## Output

Confirm how many weeks the plan covers and how many rows were written to `data/plan.csv`.
