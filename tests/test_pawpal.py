"""Tests for the PawPal+ core system (pawpal_system.py).

Run with:  pytest    (from the repo root)
"""

from datetime import date, timedelta

from pawpal_system import Owner, Pet, Task, Scheduler, to_minutes, parse_time


# --- Two simple sanity checks -----------------------------------------------

def test_task_completion_changes_status():
    """Calling mark_complete() flips the task's status to done."""
    task = Task("Walk the dog")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    """Adding a task to a Pet increases that pet's task count."""
    pet = Pet("Rex")
    assert len(pet.get_tasks()) == 0
    pet.add_task(Task("Feed"))
    assert len(pet.get_tasks()) == 1


# --- Task -------------------------------------------------------------------

def test_task_defaults_and_fields():
    task = Task("Feed", duration=10, frequency="daily", priority="high")
    assert task.description == "Feed"
    assert task.duration == 10
    assert task.frequency == "daily"
    assert task.priority == "high"
    assert task.completed is False


def test_task_edit_updates_only_given_fields():
    task = Task("Walk", duration=20, priority="low")
    task.edit(duration=45, priority="high")
    assert task.duration == 45
    assert task.priority == "high"
    assert task.description == "Walk"  # unchanged


def test_task_completion_toggle():
    task = Task("Brush")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True
    task.mark_incomplete()
    assert task.completed is False


def test_task_priority_rank_orders_high_before_low():
    assert Task(priority="high").priority_rank() < Task(priority="low").priority_rank()
    # Unknown priority falls back to medium.
    assert Task(priority="bogus").priority_rank() == Task(priority="medium").priority_rank()


# --- Pet --------------------------------------------------------------------

def test_pet_add_and_get_tasks():
    pet = Pet("Rex", "dog")
    pet.add_task(Task("Walk", duration=30))
    pet.add_task(Task("Feed", duration=10))
    assert len(pet.get_tasks()) == 2


def test_pet_pending_tasks_excludes_completed():
    pet = Pet("Mia")
    # "once" so completing it doesn't spawn a recurrence (isolates the filter).
    done = pet.add_task(Task("Groom", frequency="once"))
    pet.add_task(Task("Play"))
    done.mark_complete()
    pending = [t.description for t in pet.pending_tasks()]
    assert pending == ["Play"]


def test_pet_remove_task():
    pet = Pet("Rex")
    task = pet.add_task(Task("Walk"))
    pet.remove_task(task)
    assert pet.get_tasks() == []


# --- Owner ------------------------------------------------------------------

def test_owner_manages_multiple_pets():
    owner = Owner("Alex")
    owner.add_pet(Pet("Rex"))
    owner.add_pet(Pet("Mia"))
    assert [p.get_name() for p in owner.get_pets()] == ["Rex", "Mia"]


def test_owner_get_all_tasks_spans_pets():
    owner = Owner("Alex")
    rex = owner.add_pet(Pet("Rex"))
    mia = owner.add_pet(Pet("Mia"))
    rex.add_task(Task("Walk"))
    mia.add_task(Task("Feed"))
    pairs = owner.get_all_tasks()
    assert len(pairs) == 2
    assert {pet.get_name() for pet, _ in pairs} == {"Rex", "Mia"}


# --- Scheduler --------------------------------------------------------------

def _owner_with_tasks():
    owner = Owner("Alex")
    rex = owner.add_pet(Pet("Rex", "dog"))
    mia = owner.add_pet(Pet("Mia", "cat"))
    rex.add_task(Task("Morning walk", duration=30, priority="high"))
    rex.add_task(Task("Vet checkup", duration=45, priority="low"))
    mia.add_task(Task("Feed", duration=10, priority="high"))
    return owner


def test_schedule_orders_by_priority_then_duration():
    schedule = Scheduler().generate_schedule(_owner_with_tasks())
    descriptions = [e["description"] for e in schedule]
    # high (shortest first): Feed(10), Morning walk(30); then low: Vet checkup(45)
    assert descriptions == ["Feed", "Morning walk", "Vet checkup"]


def test_schedule_respects_time_budget():
    schedule = Scheduler().generate_schedule(_owner_with_tasks(), available_minutes=40)
    descriptions = [e["description"] for e in schedule]
    assert descriptions == ["Feed", "Morning walk"]  # 45-min vet checkup dropped


def test_schedule_excludes_completed_tasks():
    today = date(2026, 7, 5)
    owner = _owner_with_tasks()
    # Complete every task on the first pet; the recurring copies are deferred to
    # a later day, so today's plan still shows only Mia's Feed.
    for task in owner.get_pets()[0].get_tasks():
        task.mark_complete(on_date=today)
    schedule = Scheduler().generate_schedule(owner, today=today)
    assert [e["description"] for e in schedule] == ["Feed"]


def test_schedule_entries_are_tagged_with_pet_name():
    schedule = Scheduler().generate_schedule(_owner_with_tasks())
    feed = next(e for e in schedule if e["description"] == "Feed")
    assert feed["pet"] == "Mia"


# --- Due-today filtering (frequency) ----------------------------------------

def test_due_today_daily_excludes_task_done_today():
    today = date(2026, 7, 5)
    task = Task("Feed", frequency="daily")
    assert task.due_today(today) is True
    task.mark_complete(on_date=today)
    assert task.due_today(today) is False


def test_due_today_weekly_within_and_beyond_seven_days():
    today = date(2026, 7, 5)
    task = Task("Vet checkup", frequency="weekly")
    task.mark_complete(on_date=today - timedelta(days=6))
    assert task.due_today(today) is False  # only 6 days ago
    task.last_completed = today - timedelta(days=8)
    assert task.due_today(today) is True   # 8 days ago


def test_due_today_unknown_frequency_behaves_as_daily():
    today = date(2026, 7, 5)
    task = Task("Mystery", frequency="fortnightly")
    assert task.due_today(today) is True
    task.mark_complete(on_date=today)
    assert task.due_today(today) is False


def test_generate_schedule_filters_by_due_today():
    today = date(2026, 7, 5)
    owner = _owner_with_tasks()
    # Complete Mia's daily "Feed" today -> it should drop out of today's plan.
    for pet in owner.get_pets():
        for task in pet.get_tasks():
            if task.description == "Feed":
                task.mark_complete(on_date=today)
    schedule = Scheduler().generate_schedule(owner, today=today)
    assert "Feed" not in [e["description"] for e in schedule]


def test_generate_schedule_without_today_is_backward_compatible():
    # No `today` -> schedule everything pending, unchanged from before.
    schedule = Scheduler().generate_schedule(_owner_with_tasks())
    assert [e["description"] for e in schedule] == ["Feed", "Morning walk", "Vet checkup"]


# --- Batch by pet & zero budget ---------------------------------------------

def test_organize_batches_same_priority_tasks_by_pet():
    owner = Owner("Alex")
    rex = owner.add_pet(Pet("Rex"))
    mia = owner.add_pet(Pet("Mia"))
    rex.add_task(Task("Rex walk", duration=20, priority="high"))
    mia.add_task(Task("Mia feed", duration=10, priority="high"))
    rex.add_task(Task("Rex play", duration=15, priority="high"))
    scheduler = Scheduler()
    ordered = scheduler.organize(scheduler.collect_tasks(owner))
    names = [task.description for _, task in ordered]
    # Mia sorts before Rex; each pet's tasks stay together (shortest first).
    assert names == ["Mia feed", "Rex play", "Rex walk"]


def test_generate_schedule_zero_budget_returns_empty_plan():
    schedule = Scheduler().generate_schedule(_owner_with_tasks(), available_minutes=0)
    assert schedule == []


# --- Start times, chronological sort & conflict detection -------------------

def test_to_minutes_converts_hhmm():
    assert to_minutes("07:30") == 450
    assert to_minutes("00:00") == 0
    assert to_minutes("14:00") == 840
    assert to_minutes("") == 24 * 60  # unscheduled sorts last


def test_organize_by_time_orders_chronologically_with_unscheduled_last():
    owner = Owner("Alex")
    pet = owner.add_pet(Pet("Rex"))
    pet.add_task(Task("Afternoon", duration=10, time="14:00"))
    pet.add_task(Task("Unscheduled", duration=10, time=""))
    pet.add_task(Task("Morning", duration=10, time="07:30"))
    pet.add_task(Task("Midday", duration=10, time="09:15"))
    scheduler = Scheduler()
    ordered = scheduler.organize(scheduler.collect_tasks(owner), by="time")
    names = [task.description for _, task in ordered]
    assert names == ["Morning", "Midday", "Afternoon", "Unscheduled"]


def test_find_conflicts_flags_overlap():
    owner = Owner("Alex")
    pet = owner.add_pet(Pet("Rex"))
    pet.add_task(Task("Walk", duration=30, time="08:00"))   # 08:00-08:30
    pet.add_task(Task("Groom", duration=20, time="08:15"))  # overlaps
    scheduler = Scheduler()
    conflicts = scheduler.find_conflicts(scheduler.collect_tasks(owner))
    assert len(conflicts) == 1
    (_, earlier), (_, later) = conflicts[0]
    assert (earlier.description, later.description) == ("Walk", "Groom")


# --- Recurring tasks (auto next occurrence) ---------------------------------

def test_complete_task_spawns_next_daily_occurrence():
    today = date(2026, 7, 5)
    pet = Pet("Rex")
    task = pet.add_task(Task("Feed", duration=10, frequency="daily", time="07:00"))
    new_task = Scheduler().complete_task(pet, task, on_date=today)
    # Original is now history; a fresh pending copy was added for tomorrow.
    assert task.completed is True
    assert new_task is not None and new_task.completed is False
    assert len(pet.get_tasks()) == 2
    # The copy carries the same details but is not due again today...
    assert new_task.description == "Feed" and new_task.time == "07:00"
    assert new_task.due_today(today) is False
    # ...and becomes due the next day.
    assert new_task.due_today(today + timedelta(days=1)) is True


def test_complete_task_weekly_occurrence_defers_seven_days():
    today = date(2026, 7, 5)
    pet = Pet("Rex")
    task = pet.add_task(Task("Vet checkup", frequency="weekly"))
    new_task = Scheduler().complete_task(pet, task, on_date=today)
    assert new_task.due_today(today + timedelta(days=6)) is False
    assert new_task.due_today(today + timedelta(days=7)) is True


def test_complete_task_non_recurring_does_not_spawn():
    today = date(2026, 7, 5)
    pet = Pet("Rex")
    task = pet.add_task(Task("One-off bath", frequency="once"))
    result = Scheduler().complete_task(pet, task, on_date=today)
    assert result is None
    assert len(pet.get_tasks()) == 1
    assert task.completed is True


def test_completed_recurring_task_leaves_one_pending_in_schedule():
    today = date(2026, 7, 5)
    owner = Owner("Alex")
    rex = owner.add_pet(Pet("Rex"))
    feed = rex.add_task(Task("Feed", duration=10, frequency="daily", priority="high"))
    Scheduler().complete_task(rex, feed, on_date=today)
    # Today's plan: the completed original and the deferred next copy both drop out.
    assert Scheduler().generate_schedule(owner, today=today) == []
    # Tomorrow: the spawned occurrence is due again.
    tomorrow = today + timedelta(days=1)
    assert [e["description"] for e in Scheduler().generate_schedule(owner, today=tomorrow)] == ["Feed"]


def test_filter_tasks_by_completion_status():
    owner = _owner_with_tasks()
    target = owner.get_pets()[0].get_tasks()[0]  # Rex's "Morning walk"
    target.frequency = "once"  # avoid a recurrence copy so we test only the filter
    target.mark_complete()
    scheduler = Scheduler()
    done = [t.description for _, t in scheduler.filter_tasks(owner, completed=True)]
    pending = [t.description for _, t in scheduler.filter_tasks(owner, completed=False)]
    assert done == ["Morning walk"]
    assert set(pending) == {"Vet checkup", "Feed"}


def test_filter_tasks_by_pet_name_is_case_insensitive():
    owner = _owner_with_tasks()
    scheduler = Scheduler()
    rex_tasks = {t.description for _, t in scheduler.filter_tasks(owner, pet_name="rex")}
    assert rex_tasks == {"Morning walk", "Vet checkup"}


def test_filter_tasks_combines_completion_and_pet_name():
    owner = _owner_with_tasks()
    for _, task in Scheduler().filter_tasks(owner, pet_name="Rex"):
        task.mark_complete()
    scheduler = Scheduler()
    result = scheduler.filter_tasks(owner, completed=True, pet_name="Rex")
    assert {t.description for _, t in result} == {"Morning walk", "Vet checkup"}
    # No completed tasks belong to Mia.
    assert scheduler.filter_tasks(owner, completed=True, pet_name="Mia") == []


def test_filter_tasks_no_filters_returns_all():
    owner = _owner_with_tasks()
    assert len(Scheduler().filter_tasks(owner)) == 3


# --- Lightweight, non-crashing conflict detection ---------------------------

def test_parse_time_valid_and_invalid():
    assert parse_time("07:30") == 450
    assert parse_time("00:00") == 0
    assert parse_time("7:5") == 425      # missing zero-padding still parses
    assert parse_time("") is None
    assert parse_time("8am") is None     # no colon
    assert parse_time("25:00") is None   # hour out of range
    assert parse_time("07:99") is None   # minute out of range
    assert parse_time("07:30:00") is None
    assert parse_time(None) is None      # non-string


def test_to_minutes_is_crash_safe_on_bad_input():
    # Bad times must not raise; they sort last (as "unscheduled").
    assert to_minutes("garbage") == 24 * 60
    assert to_minutes("8am") == 24 * 60


def test_conflict_warnings_reports_overlap():
    owner = Owner("Sam")
    pet = owner.add_pet(Pet("Bo"))
    pet.add_task(Task("Walk", duration=40, time="08:00"))      # 08:00-08:40
    pet.add_task(Task("Groom", duration=30, time="08:20"))     # overlaps by 20 min
    warnings = Scheduler().conflict_warnings(owner)
    assert len(warnings) == 1
    assert "conflict" in warnings[0].lower()
    assert "20 min" in warnings[0]


def test_conflict_warnings_flags_two_tasks_at_same_time():
    owner = Owner("Sam")
    pet = owner.add_pet(Pet("Bo"))
    pet.add_task(Task("Walk", duration=30, time="07:00"))
    pet.add_task(Task("Vet call", duration=15, time="07:00"))  # identical start
    warnings = Scheduler().conflict_warnings(owner)
    assert len(warnings) == 1
    assert "conflict" in warnings[0].lower()
    assert "Walk" in warnings[0] and "Vet call" in warnings[0]


def test_conflict_warnings_flags_invalid_time_without_crashing():
    owner = Owner("Sam")
    pet = owner.add_pet(Pet("Bo"))
    pet.add_task(Task("Meds", duration=5, time="8am"))
    warnings = Scheduler().conflict_warnings(owner)  # must not raise
    assert len(warnings) == 1
    assert "invalid" in warnings[0].lower()


def test_conflict_warnings_empty_when_back_to_back():
    owner = Owner("Sam")
    pet = owner.add_pet(Pet("Bo"))
    pet.add_task(Task("Walk", duration=30, time="08:00"))   # 08:00-08:30
    pet.add_task(Task("Feed", duration=10, time="08:30"))   # starts exactly at 08:30
    assert Scheduler().conflict_warnings(owner) == []


def test_find_conflicts_allows_back_to_back():
    owner = Owner("Alex")
    pet = owner.add_pet(Pet("Rex"))
    pet.add_task(Task("Walk", duration=30, time="08:00"))   # 08:00-08:30
    pet.add_task(Task("Feed", duration=10, time="08:30"))   # starts exactly at 08:30
    scheduler = Scheduler()
    assert scheduler.find_conflicts(scheduler.collect_tasks(owner)) == []


# --- include_completed inclusion branch -------------------------------------

def test_collect_tasks_include_completed_keeps_done_tasks():
    """collect_tasks(include_completed=True) retains completed tasks.

    The default drops them; the inclusion branch must keep both done and
    pending tasks.
    """
    owner = _owner_with_tasks()
    rex_walk = owner.get_pets()[0].get_tasks()[0]  # Rex's "Morning walk"
    rex_walk.frequency = "once"                    # no recurrence copy to confuse the count
    rex_walk.mark_complete()
    scheduler = Scheduler()

    # Default: the completed task is filtered out.
    default = [t.description for _, t in scheduler.collect_tasks(owner)]
    assert "Morning walk" not in default

    # include_completed=True: it comes back.
    included = [t.description for _, t in scheduler.collect_tasks(owner, include_completed=True)]
    assert included.count("Morning walk") == 1
    assert set(included) == {"Morning walk", "Vet checkup", "Feed"}


def test_generate_schedule_include_completed_shows_done_tasks():
    """generate_schedule(include_completed=True) plans completed tasks too."""
    owner = _owner_with_tasks()
    rex_walk = owner.get_pets()[0].get_tasks()[0]
    rex_walk.frequency = "once"
    rex_walk.mark_complete()

    without = [e["description"] for e in Scheduler().generate_schedule(owner)]
    assert "Morning walk" not in without

    with_done = [e["description"] for e in Scheduler().generate_schedule(owner, include_completed=True)]
    assert "Morning walk" in with_done
    # The plan entry reflects its completed status.
    walk_entry = next(e for e in
                      Scheduler().generate_schedule(owner, include_completed=True)
                      if e["description"] == "Morning walk")
    assert walk_entry["completed"] is True


# --- Empty owner / pets with no tasks ---------------------------------------

def test_generate_schedule_empty_owner_returns_empty():
    """An owner with no pets yields an empty plan (no crash)."""
    assert Scheduler().generate_schedule(Owner("Nobody")) == []


def test_generate_schedule_pets_without_tasks_returns_empty():
    """Pets that have no tasks contribute nothing to the plan."""
    owner = Owner("Alex")
    owner.add_pet(Pet("Rex", "dog"))
    owner.add_pet(Pet("Mia", "cat"))
    assert Scheduler().generate_schedule(owner) == []


# --- Chained recurrence (back-reference propagates to copies) ----------------

def test_completing_spawned_copy_spawns_the_next_occurrence():
    """Completing the auto-created copy spawns its own next occurrence.

    Because next_occurrence's copy is attached via Pet.add_task, the copy also
    gets a `_pet` back-reference, so completing it recurs again (day 3).
    """
    day1 = date(2026, 7, 5)
    day2 = day1 + timedelta(days=1)
    pet = Pet("Rex")
    original = pet.add_task(Task("Feed", duration=10, frequency="daily", time="07:00"))

    # Day 1: complete original -> spawns copy for day 2.
    copy2 = original.mark_complete(on_date=day1)
    assert copy2 is not None and copy2._pet is pet
    assert len(pet.get_tasks()) == 2

    # Day 2: complete the spawned copy -> it must itself spawn a day-3 copy.
    copy3 = copy2.mark_complete(on_date=day2)
    assert copy3 is not None and copy3.completed is False
    assert copy3 is not copy2
    assert len(pet.get_tasks()) == 3
    # The third copy is due on day 3, not before.
    assert copy3.due_today(day2) is False
    assert copy3.due_today(day2 + timedelta(days=1)) is True


# --- find_conflicts vs. invalid times ---------------------------------------

def test_find_conflicts_reports_spurious_overlap_on_invalid_times():
    """Raw find_conflicts can flag a bogus conflict when times are unparseable.

    Invalid times fall back to to_minutes -> 1440, so two invalid-time tasks
    collapse to the same slot and register a (spurious) overlap. This documents
    why conflict_warnings must filter bad times out *before* overlap detection.
    """
    owner = Owner("Sam")
    pet = owner.add_pet(Pet("Bo"))
    pet.add_task(Task("A", duration=5, time="8am"))   # unparseable -> 1440
    pet.add_task(Task("B", duration=5, time="9pm"))   # unparseable -> 1440
    scheduler = Scheduler()
    # find_conflicts is blind to validity and reports the spurious overlap.
    assert len(scheduler.find_conflicts(scheduler.collect_tasks(owner))) == 1


def test_conflict_warnings_does_not_report_overlap_for_invalid_times():
    """conflict_warnings filters invalid times first, so no spurious overlap.

    It should emit one invalid-time warning per bad task and *no* conflict
    warning, unlike raw find_conflicts above.
    """
    owner = Owner("Sam")
    pet = owner.add_pet(Pet("Bo"))
    pet.add_task(Task("A", duration=5, time="8am"))
    pet.add_task(Task("B", duration=5, time="9pm"))
    warnings = Scheduler().conflict_warnings(owner)
    assert len(warnings) == 2
    assert all("invalid" in w.lower() for w in warnings)
    assert not any("conflict" in w.lower() for w in warnings)
