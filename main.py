"""PawPal+ testing ground.

A temporary terminal script to verify the core logic in pawpal_system.py works
before wiring it into the Streamlit UI. Run with:  python3 main.py
"""

from pawpal_system import Owner, Pet, Task, Scheduler


def main():
    # 1. Create an owner and at least two pets.
    owner = Owner("Alex")
    rex = owner.add_pet(Pet("Rex", "dog"))
    mia = owner.add_pet(Pet("Mia", "cat"))

    # 2. Add at least three tasks with different times (durations, in minutes).
    rex.add_task(Task("Morning walk", duration=30, frequency="daily", priority="high"))
    rex.add_task(Task("Vet checkup", duration=45, frequency="weekly", priority="low"))
    mia.add_task(Task("Feed", duration=10, frequency="daily", priority="high"))

    # 3. Build and print "Today's Schedule".
    scheduler = Scheduler()
    schedule = scheduler.generate_schedule(owner)

    print("=" * 40)
    print(f"Today's Schedule for {owner.get_name()}")
    print("=" * 40)
    for i, entry in enumerate(schedule, start=1):
        print(f"{i}. [{entry['priority'].upper():^6}] "
              f"{entry['description']} for {entry['pet']} "
              f"({entry['duration']} min, {entry['frequency']})")
    print("=" * 40)


if __name__ == "__main__":
    main()
