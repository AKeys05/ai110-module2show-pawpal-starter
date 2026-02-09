from typing import List, Dict, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import time
import uuid

class Priority(Enum):
	"""Priority levels for tasks, making comparison easier."""
	LOW = 1
	MEDIUM = 2
	HIGH = 3

@dataclass
class Pet:
	name: str
	species: str
	preferences: dict = field(default_factory=dict)
	restrictions: List[str] = field(default_factory=list)  # e.g., ["no_midday_walks", "medication_8am"]

@dataclass
class Task:
	title: str
	duration: int  # in minutes
	priority: Priority
	pet_name: str  # Links task to specific pet - addresses missing Pet-Task relationship
	id: str = field(default_factory=lambda: str(uuid.uuid4()))  # Fixes task identification bottleneck
	is_recurring: bool = False
	time_constraint: Optional[str] = None  # e.g., "before 08:00", "after 18:00"

class Owner:
	def __init__(self, name: str):
		self.name = name
		self.pets: List[Pet] = []
		self.tasks: List[Task] = []  # Absorbed from TaskList
		self.constraints: Dict[str, List[str]] = {}  # pet_name -> list of constraint descriptions

	def add_pet(self, pet: Pet) -> None:
		"""Add a pet to the owner's pet list."""
		pass

	def get_pet(self, pet_name: str) -> Optional[Pet]:
		"""Retrieve a pet by name."""
		pass

	def add_task(self, task: Task) -> None:
		"""Add a task to the owner's task list."""
		pass

	def edit_task(self, task_id: str, **kwargs) -> bool:
		"""Edit a task's properties by task ID. Returns True if successful."""
		pass

	def get_task_by_id(self, task_id: str) -> Optional[Task]:
		"""Retrieve a task by its ID."""
		pass

	def get_tasks_for_pet(self, pet_name: str) -> List[Task]:
		"""Get all tasks for a specific pet."""
		pass

	def add_constraint(self, pet_name: str, constraint: str) -> None:
		"""Add a scheduling constraint for a pet."""
		pass

	def display_tasks(self) -> None:
		"""Display all tasks."""
		pass

class Scheduler:
	def __init__(self, owner: Owner):
		self.owner = owner  # Links scheduler to owner
		self.current_schedule: List[Dict] = []  # Stores generated schedule with explanations
		# Each dict has: {'task': Task, 'time': time, 'pet_name': str, 'reason': str}

	def generate_schedule(self, pet: Optional[Pet] = None) -> List[Dict]:
		"""Generate a schedule for all tasks (or tasks for specific pet).

		Returns list of dicts with keys: task, time, pet_name, reason.
		Stores result in self.current_schedule for later explanation.
		"""
		pass

	def explain_schedule(self) -> str:
		"""Explain the reasoning behind the current schedule.

		Addresses bottleneck: now has access to self.current_schedule
		to explain the decisions made during generation.
		"""
		pass

	def validate_schedule(self, schedule: List[Dict]) -> tuple[bool, List[str]]:
		"""Validate a schedule against constraints.

		Returns (is_valid, list_of_violation_messages).
		"""
		pass

	def detect_conflicts(self) -> List[str]:
		"""Identify any scheduling conflicts in current_schedule."""
		pass
