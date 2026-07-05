"""Tests for the PawPal+ core system (pawpal_system.py).

Run with:  pytest    (from the repo root)
"""

from pawpal_system import Owner, Pet, Task, Scheduler


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
    done = pet.add_task(Task("Groom"))
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
    owner = _owner_with_tasks()
    # Complete every task on the first pet.
    for task in owner.get_pets()[0].get_tasks():
        task.mark_complete()
    schedule = Scheduler().generate_schedule(owner)
    assert [e["description"] for e in schedule] == ["Feed"]


def test_schedule_entries_are_tagged_with_pet_name():
    schedule = Scheduler().generate_schedule(_owner_with_tasks())
    feed = next(e for e in schedule if e["description"] == "Feed")
    assert feed["pet"] == "Mia"
