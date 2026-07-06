# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

========================================
Today's Schedule for Alex
========================================
1. [ HIGH ] Feed for Mia (10 min, daily)
2. [ HIGH ] Morning walk for Rex (30 min, daily)
3. [ LOW  ] Vet checkup for Rex (45 min, weekly)
========================================

```
# e.g.:
# Daily plan for Biscuit (Golden Retriever):
#   08:00 — Morning walk (30 min) [priority: high]
#   09:00 — Feeding (10 min) [priority: high]
#   ...
```

## 🧪 Testing PawPal+

Run the full test suite from the repo root:

```bash
python -m pytest
```

The suite (`tests/test_pawpal.py`, 47 tests) covers every scheduling behavior in
`pawpal_system.py`:

- **Domain model** — `Task`, `Pet`, and `Owner` field defaults, editing,
  completion toggling, priority ranking, and add/remove/lookup across pets.
- **Task ordering** — priority-first ordering (`(priority_rank, pet name,
  duration)`, so a pet's tasks stay grouped) and chronological `by="time"`
  ordering with unscheduled tasks last.
- **Time-budget greedy fill** — `generate_schedule` includes only tasks that fit
  under `available_minutes` (including the zero-budget and empty-owner edge cases).
- **Frequency / due-today filtering** — daily vs. weekly `due_today`, unknown
  frequencies treated as daily, and `collect_tasks` honoring both completion and
  `today`, including the `include_completed=True` branch.
- **Recurrence on completion** — completing a daily/weekly task spawns the next
  occurrence deferred to the correct day, non-recurring tasks don't spawn, and
  chained recurrence (completing a spawned copy spawns the next one).
- **Conflict detection** — overlap and duplicate-time flagging, back-to-back
  tasks allowed, crash-safe handling of malformed times via `parse_time`, and the
  distinction between raw `find_conflicts` and the filtering `conflict_warnings`.

Sample output from a successful run:

```
============================= test session starts ==============================
platform darwin -- Python 3.9.23, pytest-8.4.2, pluggy-1.6.0 -- /Users/student/micromamba/bin/python
cachedir: .pytest_cache
rootdir: /Users/student/ai110-module2show-pawpal-starter
collecting ... collected 47 items

tests/test_pawpal.py::test_task_completion_changes_status PASSED         [  2%]
tests/test_pawpal.py::test_adding_task_increases_pet_task_count PASSED   [  4%]
tests/test_pawpal.py::test_task_defaults_and_fields PASSED               [  6%]
tests/test_pawpal.py::test_task_edit_updates_only_given_fields PASSED    [  8%]
tests/test_pawpal.py::test_task_completion_toggle PASSED                 [ 10%]
tests/test_pawpal.py::test_task_priority_rank_orders_high_before_low PASSED [ 12%]
tests/test_pawpal.py::test_pet_add_and_get_tasks PASSED                  [ 14%]
tests/test_pawpal.py::test_pet_pending_tasks_excludes_completed PASSED   [ 17%]
tests/test_pawpal.py::test_pet_remove_task PASSED                        [ 19%]
tests/test_pawpal.py::test_owner_manages_multiple_pets PASSED            [ 21%]
tests/test_pawpal.py::test_owner_get_all_tasks_spans_pets PASSED         [ 23%]
tests/test_pawpal.py::test_schedule_orders_by_priority_then_duration PASSED [ 25%]
tests/test_pawpal.py::test_schedule_respects_time_budget PASSED          [ 27%]
tests/test_pawpal.py::test_schedule_excludes_completed_tasks PASSED      [ 29%]
tests/test_pawpal.py::test_schedule_entries_are_tagged_with_pet_name PASSED [ 31%]
tests/test_pawpal.py::test_due_today_daily_excludes_task_done_today PASSED [ 34%]
tests/test_pawpal.py::test_due_today_weekly_within_and_beyond_seven_days PASSED [ 36%]
tests/test_pawpal.py::test_due_today_unknown_frequency_behaves_as_daily PASSED [ 38%]
tests/test_pawpal.py::test_generate_schedule_filters_by_due_today PASSED [ 40%]
tests/test_pawpal.py::test_generate_schedule_without_today_is_backward_compatible PASSED [ 42%]
tests/test_pawpal.py::test_organize_batches_same_priority_tasks_by_pet PASSED [ 44%]
tests/test_pawpal.py::test_generate_schedule_zero_budget_returns_empty_plan PASSED [ 46%]
tests/test_pawpal.py::test_to_minutes_converts_hhmm PASSED               [ 48%]
tests/test_pawpal.py::test_organize_by_time_orders_chronologically_with_unscheduled_last PASSED [ 51%]
tests/test_pawpal.py::test_find_conflicts_flags_overlap PASSED           [ 53%]
tests/test_pawpal.py::test_complete_task_spawns_next_daily_occurrence PASSED [ 55%]
tests/test_pawpal.py::test_complete_task_weekly_occurrence_defers_seven_days PASSED [ 57%]
tests/test_pawpal.py::test_complete_task_non_recurring_does_not_spawn PASSED [ 59%]
tests/test_pawpal.py::test_completed_recurring_task_leaves_one_pending_in_schedule PASSED [ 61%]
tests/test_pawpal.py::test_filter_tasks_by_completion_status PASSED      [ 63%]
tests/test_pawpal.py::test_filter_tasks_by_pet_name_is_case_insensitive PASSED [ 65%]
tests/test_pawpal.py::test_filter_tasks_combines_completion_and_pet_name PASSED [ 68%]
tests/test_pawpal.py::test_filter_tasks_no_filters_returns_all PASSED    [ 70%]
tests/test_pawpal.py::test_parse_time_valid_and_invalid PASSED           [ 72%]
tests/test_pawpal.py::test_to_minutes_is_crash_safe_on_bad_input PASSED  [ 74%]
tests/test_pawpal.py::test_conflict_warnings_reports_overlap PASSED      [ 76%]
tests/test_pawpal.py::test_conflict_warnings_flags_two_tasks_at_same_time PASSED [ 78%]
tests/test_pawpal.py::test_conflict_warnings_flags_invalid_time_without_crashing PASSED [ 80%]
tests/test_pawpal.py::test_conflict_warnings_empty_when_back_to_back PASSED [ 82%]
tests/test_pawpal.py::test_find_conflicts_allows_back_to_back PASSED     [ 85%]
tests/test_pawpal.py::test_collect_tasks_include_completed_keeps_done_tasks PASSED [ 87%]
tests/test_pawpal.py::test_generate_schedule_include_completed_shows_done_tasks PASSED [ 89%]
tests/test_pawpal.py::test_generate_schedule_empty_owner_returns_empty PASSED [ 91%]
tests/test_pawpal.py::test_generate_schedule_pets_without_tasks_returns_empty PASSED [ 93%]
tests/test_pawpal.py::test_completing_spawned_copy_spawns_the_next_occurrence PASSED [ 95%]
tests/test_pawpal.py::test_find_conflicts_reports_spurious_overlap_on_invalid_times PASSED [ 97%]
tests/test_pawpal.py::test_conflict_warnings_does_not_report_overlap_for_invalid_times PASSED [100%]

============================== 47 passed in 0.02s ==============================
```

### Confidence Level: ★★★★☆ (4 / 5)

Based on the 47 passing tests, I have **high but not absolute** confidence in the
reliability of the core scheduling logic.

**Why 4 stars:**

- All 47 tests pass deterministically and fast, with no flakiness or warnings.
- Coverage is broad: ordering, greedy time-budget fill, frequency/due-today
  filtering, recurrence (including the chained back-reference case), and conflict
  detection.
- Edge cases are tested, not just happy paths — empty owner, zero budget, unknown
  frequency, malformed times, and back-to-back (non-conflicting) tasks.

**Why not 5 stars:**

- Tests cover `pawpal_system.py` only — `app.py` (Streamlit UI) and `main.py`
  (CLI demo) have no automated tests.
- One documented rough edge remains in the code: `find_conflicts` reports a
  *spurious* overlap when two times are unparseable (both fall back to minute
  1440). `conflict_warnings` guards against this by filtering bad times first, but
  callers using `find_conflicts` directly on unvalidated input are exposed.
- No coverage measurement or property-based/fuzz testing, so untested branches
  may still exist.

**Bottom line:** the scheduling engine is solid and trustworthy; the withheld star
reflects the untested UI/CLI layers and the known `find_conflicts` quirk.

## 📐 Smarter Scheduling

All scheduling logic lives in [`pawpal_system.py`](pawpal_system.py). The core
classes are `Task`, `Pet`, `Owner`, and the stateless `Scheduler`. Every feature
below is exercised by [`tests/test_pawpal.py`](tests/test_pawpal.py) (47 tests) and
demoed in [`main.py`](main.py).

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.organize(pairs, by="priority" \| "time")` | Priority-first or chronological |
| Filtering | `Scheduler.filter_tasks`, `Scheduler.collect_tasks`, `Task.due_today`, `Pet.pending_tasks` | By pet, completion status, and frequency due-date |
| Conflict handling | `Scheduler.conflict_warnings`, `Scheduler.find_conflicts`, `parse_time` | Overlaps + malformed times; warns, never crashes |
| Recurring tasks | `Task.mark_complete`, `Task.next_occurrence`, `Scheduler.complete_task` | Daily/weekly auto-spawn the next occurrence |
| Daily plan | `Scheduler.generate_schedule` | Greedy fill under a time budget |

### Sorting behavior

`Scheduler.organize(pairs, by=...)` returns the `(pet, task)` pairs in one of two
orders:

- **`by="priority"`** (default) — sorts by `(priority_rank, pet name, duration)`,
  so high-priority tasks come first, a pet's tasks are **grouped together** (fewer
  trips between pets), and shorter tasks lead within a tier. Priority ranking is
  computed by `Task.priority_rank()` (`high`/`medium`/`low` → `0/1/2`, unknown →
  medium).
- **`by="time"`** — sorts chronologically using the module helper `to_minutes()`,
  which converts a `"HH:MM"` start time to minutes since midnight; unscheduled
  (blank) tasks sort last.

### Filtering behavior

- **By completion / by pet** — `Scheduler.filter_tasks(owner, completed=None,
  pet_name=None)`. Both filters are optional and combine with AND;
  `pet_name` is case-insensitive.
- **For the daily plan** — `Scheduler.collect_tasks(owner, include_completed=False,
  today=None)` drops completed tasks and, when a `today` date is supplied, tasks
  not due today — in a single pass.
- **Frequency due-date** — `Task.due_today(today)`: a `daily` task is due unless it
  was already completed today; a `weekly` task is due if never completed or 7+ days
  have passed.
- **Pending only** — `Pet.pending_tasks()` returns a pet's not-yet-completed tasks.

### Conflict detection logic

- **`Scheduler.conflict_warnings(owner, today=None)`** — the crash-safe, human-facing
  check. It returns a list of warning **strings** (empty when the day is clear) for
  (a) tasks with an unparseable start time and (b) overlaps where one task's
  `start + duration` runs past the next task's start. Times are parsed defensively
  by `parse_time()`, so bad input like `"8am"` produces a warning instead of an
  exception.
- **`Scheduler.find_conflicts(pairs)`** — the underlying algorithm: sorts timed
  tasks chronologically and sweeps adjacent pairs for overlap, returning the
  conflicting `(pet, task)` pairs. `conflict_warnings` reuses it.

### Recurring task logic

Completing a recurring task automatically schedules its next occurrence:

- **`Task.mark_complete(on_date=None)`** — marks the task done and, if it is
  `daily`/`weekly` **and** attached to a pet, adds a fresh pending copy for the
  next occurrence (the completed task stays as history) and returns it.
- **`Task.next_occurrence(completion_date)`** — builds that copy, setting its
  `last_completed` so `due_today` defers it to the next day (daily) or next week
  (weekly) instead of reappearing immediately.
- **`Scheduler.complete_task(pet, task, on_date=None)`** — a convenience wrapper
  that ensures the back-reference is set, then delegates to `mark_complete`.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
