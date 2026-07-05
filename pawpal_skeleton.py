"""PawPal+ class skeleton.

Names, attributes, and empty method stubs based on the UML design.
Fill in the method bodies where marked `pass`.
"""


class Owner:
    def __init__(self, name=""):
        self._name = name  # Owner's name

    def set_name(self, name):
        pass

    def get_name(self):
        pass


class Pet:
    def __init__(self, name=""):
        self._name = name  # Pet's name

    def set_name(self, name):
        pass

    def get_name(self):
        pass


class Task:
    def __init__(self, pet, name="", duration=0, priority=1):
        self._pet = pet            # Pet this task is assigned to
        self._name = name          # Task name
        self._duration = duration  # Duration in minutes
        self._priority = priority  # Priority (lower = higher priority)

    def set_task(self, name, duration, priority):
        pass

    def get_task(self):
        pass

    def add_task(self, name, duration, priority):
        pass

    def edit_task(self, duration=None, priority=None):
        pass


class Scheduler:
    def __init__(self):
        self._tasks = []  # Collection of Task objects

    def add_task(self, task):
        pass

    def generate_schedule(self):
        pass
