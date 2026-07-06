from datetime import date

import streamlit as st

from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

# Colored dots make priority scannable at a glance in the tables below.
PRIORITY_BADGE = {"high": "🔴 High", "medium": "🟡 Medium", "low": "🟢 Low"}


def task_row(pet_name, task_dict):
    """Turn a task's raw fields into a polished, human-friendly table row."""
    return {
        "Task": task_dict["description"],
        "Pet": pet_name,
        "Priority": PRIORITY_BADGE.get(task_dict["priority"], task_dict["priority"]),
        "Time": task_dict["time"] or "—",
        "Duration": f"{task_dict['duration']} min",
        "Frequency": task_dict["frequency"].capitalize(),
        "Status": "✅ Done" if task_dict["completed"] else "⬜ Pending",
    }

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

# Streamlit reruns this whole script top-to-bottom on every interaction, so an
# Owner created as a plain variable would be "reborn" empty each rerun. Instead
# we keep ONE Owner in st.session_state (the per-session "vault") and only build
# it the first time — the `not in` check is how we tell "first run" apart from
# "a later rerun where the object already exists."
if "owner" not in st.session_state:
    st.session_state.owner = Owner(owner_name)
owner = st.session_state.owner            # reuse the persisted instance
owner.set_name(owner_name)                # keep its name synced with the input

# Same "check the vault first" pattern for the Pet: create it once, attach it to
# the owner once, then just keep its details synced with the inputs each rerun.
if "pet" not in st.session_state:
    st.session_state.pet = Pet(pet_name, species)
    owner.add_pet(st.session_state.pet)
pet = st.session_state.pet
pet.set_name(pet_name)
pet.species = species

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

col4, col5 = st.columns(2)
with col4:
    frequency = st.selectbox("Frequency", ["daily", "weekly"], index=0)
with col5:
    # Optional start time as "HH:MM"; leave blank for an unscheduled task.
    start_time = st.text_input("Start time (HH:MM, optional)", value="")

# Build a real Task and hand it to the pet — no more loose dicts. The task lives
# on the persisted Pet, so it survives reruns automatically.
if st.button("Add task"):
    pet.add_task(Task(
        description=task_title,
        duration=int(duration),
        priority=priority,
        frequency=frequency,
        time=start_time.strip(),
    ))

tasks = pet.get_tasks()
if tasks:
    scheduler = Scheduler()

    # Let the owner choose the ordering, then delegate to Scheduler.organize so
    # the display matches the same sorting the scheduler uses.
    order_by = st.radio(
        "Order tasks by",
        options=["priority", "time"],
        format_func=lambda o: "Priority (high first, grouped by pet)"
        if o == "priority" else "Start time (chronological)",
        horizontal=True,
    )
    pairs = [(pet, t) for t in tasks]
    ordered = scheduler.organize(pairs, by=order_by)

    pending = len(pet.pending_tasks())
    st.success(
        f"**{pet.get_name()}** has **{len(tasks)}** task(s) — "
        f"{pending} pending, {len(tasks) - pending} done."
    )
    st.table([task_row(p.get_name(), task.to_dict()) for p, task in ordered])

    # Surface any overlapping / malformed start times right next to the list.
    warnings = scheduler.conflict_warnings(owner)
    for message in warnings:
        st.warning(message)
    if not warnings:
        st.caption("✅ No time conflicts detected.")
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption(
    "Shows only tasks due today, ordered by priority (high first), grouped by pet, "
    "then shortest duration."
)

# Time budget is opt-in so "0 minutes" can mean a real empty day rather than
# being overloaded as "no limit."
limit_time = st.checkbox("Limit my time today")
budget = None
if limit_time:
    budget = st.number_input(
        "Time available today (minutes)", min_value=0, max_value=1440, value=60
    )

if st.button("Generate schedule"):
    scheduler = Scheduler()
    today = date.today()
    schedule = scheduler.generate_schedule(owner, available_minutes=budget, today=today)

    # Surface overlapping / malformed start times so the owner can fix them.
    # Lightweight check: returns messages instead of raising on bad input.
    for message in scheduler.conflict_warnings(owner, today=today):
        st.warning(message)

    if schedule:
        total_minutes = sum(entry["duration"] for entry in schedule)
        st.success(
            f"📅 Today's schedule for **{owner.get_name()}** — "
            f"**{len(schedule)}** task(s), **{total_minutes} min** total."
        )
        rows = []
        for i, entry in enumerate(schedule, start=1):
            row = task_row(entry["pet"], entry)
            rows.append({"#": i, **row})
        st.table(rows)
    else:
        st.info("No tasks to schedule yet. Add some tasks above first.")
