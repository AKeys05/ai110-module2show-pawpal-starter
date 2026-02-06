# from typing import List, Dict, Optional
from dataclasses import dataclass, field

@dataclass
class Pet:
	name: str
	species: str
	preferences: dict = field(default_factory=dict)

@dataclass
class Task:
	title: str
	duration: int  # in minutes
	priority: str  # 'low', 'med', 'high'

@dataclass
class ScheduledTask:
	task: Task
	time: str  # e.g., '09:00'

class Owner:
	def __init__(self, name: str):
		self.name = name
		self.pets = []  # List[Pet]
		self.task_list = None  # TaskList

	def add_pet(self, pet):
		pass

class TaskList:
	def __init__(self):
		self.tasks = []  # List[Task]

	def add_task(self, task):
		pass

	def edit_task(self, task_id, **kwargs):
		pass

	def display_tasks(self):
		pass

class Scheduler:
	def generate_schedule(self, tasks, pet):
		"""Return a list of ScheduledTask objects."""
		pass

	def explain_schedule(self):
		pass
