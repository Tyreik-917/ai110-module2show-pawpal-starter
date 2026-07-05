"""PawPal+ class skeleton.

Names, attributes, and empty method stubs based on the UML design.
Fill in the method bodies where marked `pass`.

Relationships modeled here:
- Owner  1 --> * Pet   (an owner has one or more pets)
- Pet    1 --> * Task  (a pet has many care tasks)
- Task   * --> 1 Pet   (each task is assigned to exactly one pet)
- Scheduler o-- * Task (a scheduler aggregates the tasks it plans)
"""


class Owner:
    def __init__(self, name=""):
        self._name = name   # Owner's name
        self._pets = []      # Pets this owner owns (Owner 1 --> * Pet)

    def set_name(self, name):
        pass

    def get_name(self):
        pass

    def add_pet(self, pet):
        pass

    def get_pets(self):
        pass


class Pet:
    def __init__(self, name=""):
        self._name = name   # Pet's name
        self._tasks = []     # Tasks assigned to this pet (Pet 1 --> * Task)

    def set_name(self, name):
        pass

    def get_name(self):
        pass

    def add_task(self, task):
        # Should keep both sides of the link in sync:
        # append to self._tasks AND ensure task._pet points back to this pet.
        pass

    def get_tasks(self):
        pass


class Task:
    def __init__(self, pet, name="", duration=0, priority=1):
        self._pet = pet            # Pet this task is assigned to (Task * --> 1 Pet)
        self._name = name          # Task name
        self._duration = duration  # Duration in minutes
        self._priority = priority  # Priority as int (lower number = higher priority)

    def set_task(self, name, duration, priority):
        pass

    def get_task(self):
        pass

    def edit_task(self, duration=None, priority=None):
        pass


class Scheduler:
    def __init__(self):
        self._tasks = []  # Collection of Task objects (Scheduler o-- * Task)

    def add_task(self, task):
        pass

    def generate_schedule(self, available_minutes=None):
        # Build a daily plan based on constraints and priorities.
        # Strategy: sort tasks by (priority, duration); if available_minutes is
        # given, greedily select tasks that fit within the time budget.
        pass
