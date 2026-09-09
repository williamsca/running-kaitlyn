# running-kaitlyn
a personal website tracking kaitlyn's training program for her next race

Run `python3 build.py` to generate `docs/index.html` from `templates/index.html`
and the CSV selected by `plan_file` in `data/config.yaml`. GitHub Actions builds
on changes to the source files or a manual trigger; there is no weekly schedule.
The browser updates the current week, phase, and countdown using its local date.

The active plan uses one CSV row per week, with mileage and workout notes for
each run type. Blank or zero mileage omits a card. Weekly totals are calculated
from the runs, including the race. Reference paces live in config. The former
Four Miler plan remains archived in `data/plan.csv` (its older format is not
supported by the new builder).

Tapping a run toggles completion, saved in Safari/browser localStorage on that
device. Clearing website data clears progress; it does not sync between devices.
Keep `plan_id` stable when editing this plan; use a new ID for a new race so its
completion history stays separate. Runs are identified by week and run type.
