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

# Lower rank sorts first, so "high" is scheduled before "low".
PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}


@dataclass
class Task:
    """A single care activity.

    Attributes:
        description: what the task is ("Morning walk").
        duration:    how long it takes, in minutes ("time").
        frequency:   how often it recurs ("daily", "weekly", ...).
        priority:    "low" | "medium" | "high".
        completed:   completion status.
    """

    description: str = ""
    duration: int = 0
    frequency: str = "daily"
    priority: str = "medium"
    completed: bool = False

    def edit(self, description=None, duration=None, frequency=None, priority=None):
        """Update any subset of the task's fields; leaves the rest untouched."""
        if description is not None:
            self.description = description
        if duration is not None:
            self.duration = duration
        if frequency is not None:
            self.frequency = frequency
        if priority is not None:
            self.priority = priority

    def mark_complete(self):
        """Mark the task as done."""
        self.completed = True

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
        """Attach a Task to this pet."""
        self.tasks.append(task)
        return task

    def remove_task(self, task):
        """Detach a Task from this pet if present."""
        if task in self.tasks:
            self.tasks.remove(task)

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

    def collect_tasks(self, owner, include_completed=False):
        """Gather (pet, task) pairs across all of an owner's pets."""
        pairs = owner.get_all_tasks()
        if include_completed:
            return pairs
        return [(pet, task) for pet, task in pairs if not task.completed]

    def organize(self, pairs):
        """Order (pet, task) pairs by priority, then by shortest duration."""
        return sorted(pairs, key=lambda pt: (pt[1].priority_rank(), pt[1].duration))

    def generate_schedule(self, owner, available_minutes=None, include_completed=False):
        """Build a daily plan across all of the owner's pets.

        Tasks are ordered by priority (high first), then shortest duration.
        If ``available_minutes`` is given, greedily include only the tasks that
        fit within that time budget. Returns a list of plan entries.
        """
        ordered = self.organize(self.collect_tasks(owner, include_completed))

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
