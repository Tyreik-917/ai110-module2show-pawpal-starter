"""PawPal+ core system.

Four domain classes for planning an owner's daily pet-care tasks:

- Task      : a single care activity (description, time, frequency, completion).
- Pet       : a pet's details plus the list of tasks that belong to it.
- Owner     : manages one or more pets and gives access to all their tasks.
- Scheduler : the "brain" that retrieves, organizes, and manages tasks
              across every pet an owner has.

Data-holding objects use Python dataclasses to keep the code clean.
Priorities use the same string values as the Streamlit UI ("low" / "medium" /
"high") so the two sides connect without a translation layer.
"""

from dataclasses import dataclass, field
from datetime import date

# Lower rank sorts first, so "high" is scheduled before "low".
PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}

# A day has 24 * 60 minutes; used to park unscheduled tasks at the very end.
MINUTES_IN_DAY = 24 * 60


def parse_time(time_str):
    """Parse a 24-hour "HH:MM" string to minutes since midnight, or None.

    Lenient and non-crashing: returns None for anything it can't parse (missing
    colon, non-numeric parts, out-of-range hour/minute) so callers can warn
    gracefully instead of raising.
    """
    if not isinstance(time_str, str):
        return None
    parts = time_str.split(":")
    if len(parts) != 2:
        return None
    hours, minutes = parts[0].strip(), parts[1].strip()
    if not (hours.isdigit() and minutes.isdigit()):
        return None
    h, m = int(hours), int(minutes)
    if 0 <= h < 24 and 0 <= m < 60:
        return h * 60 + m
    return None


def to_minutes(time_str):
    """Convert a zero-padded 24-hour "HH:MM" string to minutes since midnight.

    Reused as a robust sort key for chronological ordering: splitting into
    (hour, minute) avoids the leading-zero / 12-hour pitfalls of comparing the
    raw strings. An empty/blank OR unparseable time means "unscheduled" and
    sorts last (never raises).
    """
    if not time_str:
        return MINUTES_IN_DAY
    minutes = parse_time(time_str)
    return MINUTES_IN_DAY if minutes is None else minutes


@dataclass
class Task:
    """A single care activity.

    Attributes:
        description: what the task is ("Morning walk").
        duration:    how long it takes, in minutes ("time").
        frequency:   how often it recurs ("daily", "weekly", ...).
        priority:    "low" | "medium" | "high".
        completed:   completion status.
        time:        desired start as zero-padded 24-hour "HH:MM" ("" = unscheduled).
        last_completed: the date the task was last finished (None if never).
    """

    description: str = ""
    duration: int = 0
    frequency: str = "daily"
    priority: str = "medium"
    completed: bool = False
    time: str = ""
    last_completed: object = None
    # Back-reference to the owning Pet, set by Pet.add_task. Kept out of repr
    # (avoids Pet<->Task recursion) and equality (preserves value-based ==).
    _pet: object = field(default=None, repr=False, compare=False)

    def edit(self, description=None, duration=None, frequency=None, priority=None,
             time=None):
        """Update any subset of the task's fields; leaves the rest untouched."""
        if description is not None:
            self.description = description
        if duration is not None:
            self.duration = duration
        if frequency is not None:
            self.frequency = frequency
        if priority is not None:
            self.priority = priority
        if time is not None:
            self.time = time

    def mark_complete(self, on_date=None):
        """Mark the task done and auto-create the next occurrence if recurring.

        For a "daily"/"weekly" task that is attached to a pet, a fresh pending
        copy is added to that pet for the next occurrence and returned (the
        completed task stays put as history). Non-recurring or detached tasks
        just flip status and return None. ``on_date`` defaults to today for the
        recurrence bookkeeping.
        """
        self.completed = True
        if on_date is not None:
            self.last_completed = on_date
        if self.frequency in ("daily", "weekly") and self._pet is not None:
            when = on_date if on_date is not None else date.today()
            self.last_completed = when
            return self._pet.add_task(self.next_occurrence(when))
        return None

    def next_occurrence(self, completion_date):
        """Return a fresh, pending copy of this task for its next occurrence.

        The copy keeps the same description/duration/frequency/priority/time but
        starts uncompleted. Its ``last_completed`` is set to ``completion_date``
        so ``due_today`` defers it to the next day (daily) or next week (weekly)
        instead of reappearing immediately.
        """
        return Task(
            description=self.description,
            duration=self.duration,
            frequency=self.frequency,
            priority=self.priority,
            time=self.time,
            completed=False,
            last_completed=completion_date,
        )

    def due_today(self, today):
        """Whether this task should appear in ``today``'s plan by frequency.

        - daily : due unless it was already completed today.
        - weekly: due if never completed, or 7+ days have passed.
        - anything else is treated as daily.
        """
        if self.frequency == "weekly":
            return self.last_completed is None or (today - self.last_completed).days >= 7
        # daily (and any unknown frequency)
        return self.last_completed != today

    def mark_incomplete(self):
        """Mark the task as not yet done."""
        self.completed = False

    def priority_rank(self):
        """Numeric rank used for ordering (unknown priority sorts as medium)."""
        return PRIORITY_RANK.get(self.priority, PRIORITY_RANK["medium"])

    def to_dict(self):
        """Return the task's fields as a plain dict (handy for the UI)."""
        return {
            "description": self.description,
            "duration": self.duration,
            "frequency": self.frequency,
            "priority": self.priority,
            "completed": self.completed,
            "time": self.time,
        }


@dataclass
class Pet:
    """A pet and the tasks that belong to it."""

    name: str = ""
    species: str = ""
    tasks: list = field(default_factory=list)

    # -- UML name accessors --------------------------------------------------
    def set_name(self, name):
        """Set the pet's name."""
        self.name = name

    def get_name(self):
        """Return the pet's name."""
        return self.name

    # -- Task management -----------------------------------------------------
    def add_task(self, task):
        """Attach a Task to this pet (records the back-reference)."""
        task._pet = self
        self.tasks.append(task)
        return task

    def remove_task(self, task):
        """Detach a Task from this pet if present."""
        if task in self.tasks:
            self.tasks.remove(task)
            task._pet = None

    def get_tasks(self):
        """Return a copy of this pet's task list."""
        return list(self.tasks)

    def pending_tasks(self):
        """Tasks that are not yet completed."""
        return [t for t in self.tasks if not t.completed]


@dataclass
class Owner:
    """An owner who manages one or more pets."""

    name: str = ""
    pets: list = field(default_factory=list)

    # -- UML name accessors --------------------------------------------------
    def set_name(self, name):
        """Set the owner's name."""
        self.name = name

    def get_name(self):
        """Return the owner's name."""
        return self.name

    # -- Pet management ------------------------------------------------------
    def add_pet(self, pet):
        """Add a pet to this owner."""
        self.pets.append(pet)
        return pet

    def get_pets(self):
        """Return a copy of this owner's pet list."""
        return list(self.pets)

    def get_all_tasks(self):
        """Return every task across all pets as (pet, task) pairs."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]


class Scheduler:
    """The brain: retrieves, organizes, and manages tasks across pets.

    The Scheduler holds no state of its own — it operates on an Owner's pets,
    so it always reflects the current tasks.
    """

    def complete_task(self, pet, task, on_date=None):
        """Convenience wrapper: complete a task (recurrence handled by the Task).

        Ensures the task knows its pet, then delegates to ``mark_complete``,
        which auto-creates the next occurrence for recurring tasks. Returns the
        new Task, or None.
        """
        if task._pet is None:
            task._pet = pet
        return task.mark_complete(on_date=on_date)

    def filter_tasks(self, owner, completed=None, pet_name=None):
        """Return (pet, task) pairs filtered by completion status and/or pet name.

        Both filters are optional and combine with AND:
        - ``completed=True`` keeps only done tasks, ``False`` only pending ones,
          ``None`` keeps either.
        - ``pet_name`` (case-insensitive) keeps only that pet's tasks; ``None``
          keeps every pet.
        """
        wanted = pet_name.lower() if pet_name is not None else None
        return [
            (pet, task)
            for pet, task in owner.get_all_tasks()
            if (completed is None or task.completed == completed)
            and (wanted is None or pet.get_name().lower() == wanted)
        ]

    def collect_tasks(self, owner, include_completed=False, today=None):
        """Gather (pet, task) pairs across all of an owner's pets.

        Filters completed tasks (unless ``include_completed``) and, when a
        ``today`` date is given, tasks not due today by frequency — both in a
        single pass over the flattened tasks. ``today=None`` schedules
        everything, preserving the original behavior.
        """
        return [
            (pet, task)
            for pet, task in owner.get_all_tasks()
            if (include_completed or not task.completed)
            and (today is None or task.due_today(today))
        ]

    def organize(self, pairs, by="priority"):
        """Order (pet, task) pairs.

        ``by="priority"``: priority (high first), then pet name so an owner
        finishes one pet's tasks together, then shortest duration.
        ``by="time"``: chronological start time, with unscheduled tasks last.
        """
        if by == "time":
            return sorted(pairs, key=lambda pt: to_minutes(pt[1].time))
        return sorted(
            pairs,
            key=lambda pt: (pt[1].priority_rank(), pt[0].get_name(), pt[1].duration),
        )

    def find_conflicts(self, pairs):
        """Return chronologically-adjacent (pet, task) pairs that overlap.

        Two timed tasks conflict when the earlier one's start + duration runs
        past the later one's start. Unscheduled tasks (no time) are ignored.
        """
        timed = [pt for pt in pairs if pt[1].time]
        ordered = self.organize(timed, by="time")
        conflicts = []
        for earlier, later in zip(ordered, ordered[1:]):
            end_of_earlier = to_minutes(earlier[1].time) + earlier[1].duration
            if end_of_earlier > to_minutes(later[1].time):
                conflicts.append((earlier, later))
        return conflicts

    def conflict_warnings(self, owner, today=None):
        """Lightweight conflict check that returns warning messages, never raises.

        Scans the owner's pending timed tasks and returns a list of plain-string
        warnings for (a) tasks whose start time can't be parsed and (b) tasks
        whose time window overlaps the next one. Returns an empty list when the
        day is clear, so callers can display messages instead of crashing.
        """
        warnings = []
        valid = []
        for pet, task in self.collect_tasks(owner, today=today):
            if not task.time:
                continue  # unscheduled tasks can't conflict
            if parse_time(task.time) is None:
                warnings.append(
                    f"⚠️ {pet.get_name()}'s '{task.description}' has an invalid "
                    f"start time '{task.time}' (expected HH:MM) — skipping it."
                )
            else:
                valid.append((pet, task))

        # Reuse the single overlap-detection algorithm; only valid times reach it.
        for (pet_a, task_a), (pet_b, task_b) in self.find_conflicts(valid):
            overlap = to_minutes(task_a.time) + task_a.duration - to_minutes(task_b.time)
            warnings.append(
                f"⚠️ Time conflict: {pet_a.get_name()}'s '{task_a.description}' "
                f"({task_a.time}, {task_a.duration} min) overlaps "
                f"{pet_b.get_name()}'s '{task_b.description}' ({task_b.time}) "
                f"by {overlap} min."
            )
        return warnings

    def generate_schedule(self, owner, available_minutes=None, include_completed=False,
                          today=None):
        """Build a daily plan across all of the owner's pets.

        Tasks are ordered by priority (high first), then shortest duration.
        If ``available_minutes`` is given, greedily include only the tasks that
        fit within that time budget. When ``today`` is given, only tasks due
        today (by frequency) are considered. Returns a list of plan entries.
        """
        ordered = self.organize(self.collect_tasks(owner, include_completed, today))

        schedule = []
        remaining = available_minutes
        for pet, task in ordered:
            if remaining is not None:
                if task.duration > remaining:
                    continue
                remaining -= task.duration
            entry = task.to_dict()
            entry["pet"] = pet.get_name()
            schedule.append(entry)
        return schedule
