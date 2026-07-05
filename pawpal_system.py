"""PawPal+ core system.

Defines the four domain classes for planning a pet owner's daily care tasks:
Owner, Pet, Task, and Scheduler.

Data-holding objects (Owner, Pet, Task) use Python dataclasses to keep the
code clean; the UML get/set methods are kept as thin accessors.
"""

from dataclasses import dataclass, field


@dataclass
class Owner:
    """A pet owner."""

    name: str = ""

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name


@dataclass
class Pet:
    """A pet belonging to an owner."""

    name: str = ""

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name


@dataclass
class Task:
    """A care task assigned to a specific pet.

    A task has at minimum a duration (minutes) and a priority
    (lower number = higher priority).
    """

    pet: Pet
    name: str = ""
    duration: int = 0
    priority: int = 1

    def set_task(self, name, duration, priority):
        self.name = name
        self.duration = duration
        self.priority = priority

    def get_task(self):
        return {
            "pet": self.pet.get_name() if self.pet else None,
            "name": self.name,
            "duration": self.duration,
            "priority": self.priority,
        }

    def edit_task(self, duration=None, priority=None):
        if duration is not None:
            self.duration = duration
        if priority is not None:
            self.priority = priority


@dataclass
class Scheduler:
    """Builds a daily plan from a collection of tasks."""

    tasks: list = field(default_factory=list)

    def add_task(self, task):
        self.tasks.append(task)

    def generate_schedule(self, max_minutes=None):
        """Return tasks ordered by priority (then shortest duration).

        If max_minutes is given, only include tasks that fit within the
        available time budget.
        """
        ordered = sorted(self.tasks, key=lambda t: (t.priority, t.duration))

        if max_minutes is None:
            return [t.get_task() for t in ordered]

        schedule = []
        remaining = max_minutes
        for task in ordered:
            if task.duration <= remaining:
                schedule.append(task.get_task())
                remaining -= task.duration
        return schedule
