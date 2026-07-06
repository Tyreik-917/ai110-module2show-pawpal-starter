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

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

All scheduling logic lives in [`pawpal_system.py`](pawpal_system.py). The core
classes are `Task`, `Pet`, `Owner`, and the stateless `Scheduler`. Every feature
below is exercised by [`tests/test_pawpal.py`](tests/test_pawpal.py) (40 tests) and
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
