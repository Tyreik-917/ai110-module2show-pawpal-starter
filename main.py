"""PawPal+ testing ground.

A temporary terminal script to verify the core logic in pawpal_system.py works
before wiring it into the Streamlit UI. Run with:  python3 main.py

Tasks are added deliberately OUT OF ORDER (mixed pets, priorities, and times)
so the sorting and filtering methods have something real to reorganize.
"""

from pawpal_system import Owner, Pet, Task, Scheduler


def show(pairs):
    """Print a list of (pet, task) pairs as a numbered, readable list."""
    for i, (pet, task) in enumerate(pairs, start=1):
        when = f"at {task.time}, " if task.time else "unscheduled, "
        status = "done" if task.completed else "pending"
        print(f"  {i}. [{task.priority.upper():^6}] {task.description} for "
              f"{pet.get_name()} ({when}{task.duration} min, {task.frequency}, {status})")


def main():
    # 1. Create an owner and two pets.
    owner = Owner("Alex")
    rex = owner.add_pet(Pet("Rex", "dog"))
    mia = owner.add_pet(Pet("Mia", "cat"))

    # 2. Add tasks OUT OF ORDER: a low task before high ones, a late time before
    #    early ones, pets interleaved, and one already completed.
    rex.add_task(Task("Vet checkup", duration=45, frequency="weekly", priority="low",
                      time="15:00"))
    mia.add_task(Task("Evening play", duration=15, frequency="daily", priority="medium",
                      time="18:00"))
    rex.add_task(Task("Morning walk", duration=30, frequency="daily", priority="high",
                      time="07:30"))
    mia.add_task(Task("Feed", duration=10, frequency="daily", priority="high",
                      time="07:00"))
    # Already finished today — set via the constructor so this history entry
    # doesn't itself spawn a recurrence (we demo the auto-spawn explicitly below).
    rex.add_task(Task("Brush", duration=5, frequency="daily", priority="low",
                      time="20:00", completed=True))

    scheduler = Scheduler()

    print("=" * 52)
    print("Tasks as entered (raw order)")
    print("=" * 52)
    show(owner.get_all_tasks())

    # 3a. Sorting by priority (high first, grouped by pet, then shortest first).
    print("\n" + "=" * 52)
    print("Sorted by PRIORITY (pending only)")
    print("=" * 52)
    show(scheduler.organize(scheduler.collect_tasks(owner)))

    # 3b. Sorting chronologically by start time.
    print("\n" + "=" * 52)
    print("Sorted by TIME (chronological)")
    print("=" * 52)
    show(scheduler.organize(scheduler.collect_tasks(owner), by="time"))

    # 4a. Filtering by completion status.
    print("\n" + "=" * 52)
    print("Filtered: COMPLETED tasks only")
    print("=" * 52)
    show(scheduler.filter_tasks(owner, completed=True))

    # 4b. Filtering by pet name.
    print("\n" + "=" * 52)
    print("Filtered: Rex's tasks only")
    print("=" * 52)
    show(scheduler.filter_tasks(owner, pet_name="Rex"))

    # 5. Lightweight conflict detection: returns warnings, never crashes — even
    #    on a malformed start time like "8am".
    print("\n" + "=" * 52)
    print("Conflict warnings (overlaps + bad times, non-crashing)")
    print("=" * 52)
    clash = Owner("Sam")
    bo = clash.add_pet(Pet("Bo", "dog"))
    # Two tasks scheduled at the SAME time -> should be flagged as a conflict.
    bo.add_task(Task("Walk", duration=30, priority="high", time="07:00"))
    bo.add_task(Task("Vet call", duration=15, priority="high", time="07:00"))
    bo.add_task(Task("Meds", duration=5, priority="high", time="8am"))  # invalid time
    warnings = scheduler.conflict_warnings(clash)
    if warnings:
        for message in warnings:
            print(f"  {message}")
    else:
        print("  none")

    # 6. Recurrence: completing a daily task auto-creates the next occurrence.
    print("\n" + "=" * 52)
    print("Recurrence: complete Mia's daily 'Feed'")
    print("=" * 52)
    feed = next(task for _, task in scheduler.filter_tasks(owner, pet_name="Mia")
                if task.description == "Feed")
    print("Mia's tasks before:")
    show(scheduler.filter_tasks(owner, pet_name="Mia"))
    feed.mark_complete()  # attached + daily -> spawns the next occurrence
    print("Mia's tasks after (original done, a fresh pending 'Feed' appears):")
    show(scheduler.filter_tasks(owner, pet_name="Mia"))
    print("=" * 52)


if __name__ == "__main__":
    main()
