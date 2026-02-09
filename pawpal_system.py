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
	tasks: List[Task] = field(default_factory=list)  # Pet stores its own tasks

	def add_task(self, task: Task) -> None:
		"""Add a task to this pet's task list."""
		self.tasks.append(task)

	def get_task_by_id(self, task_id: str) -> Optional[Task]:
		"""Find a task by its ID."""
		for task in self.tasks:
			if task.id == task_id:
				return task
		return None

	def get_incomplete_tasks(self) -> List[Task]:
		"""Return all tasks that haven't been completed."""
		return [task for task in self.tasks if not task.completed]

	def get_tasks_by_priority(self, priority: Priority) -> List[Task]:
		"""Return all tasks with the specified priority."""
		return [task for task in self.tasks if task.priority == priority]

@dataclass
class Task:
	title: str
	duration: int  # in minutes
	priority: Priority
	pet_name: str  # Links task to specific pet - addresses missing Pet-Task relationship
	id: str = field(default_factory=lambda: str(uuid.uuid4()))  # Fixes task identification bottleneck
	is_recurring: bool = False
	time_constraint: Optional[str] = None  # e.g., "before 08:00", "after 18:00"
	completed: bool = False  # Completion status

class Owner:
	def __init__(self, name: str):
		self.name = name
		self.pets: List[Pet] = []
		self.constraints: Dict[str, List[str]] = {}  # pet_name -> list of constraint descriptions

	def add_pet(self, pet: Pet) -> None:
		"""Add a pet to the owner's pet list."""
		self.pets.append(pet)

	def get_pet(self, pet_name: str) -> Optional[Pet]:
		"""Retrieve a pet by name."""
		for pet in self.pets:
			if pet.name == pet_name:
				return pet
		return None

	def add_task(self, pet_name: str, task: Task) -> bool:
		"""Add a task to a specific pet's task list. Returns True if successful."""
		pet = self.get_pet(pet_name)
		if pet:
			pet.add_task(task)
			return True
		return False

	def edit_task(self, task_id: str, **kwargs) -> bool:
		"""Edit a task's properties by task ID. Returns True if successful."""
		# Search through all pets to find the task
		for pet in self.pets:
			task = pet.get_task_by_id(task_id)
			if task:
				for key, value in kwargs.items():
					if hasattr(task, key):
						setattr(task, key, value)
				return True
		return False

	def get_task_by_id(self, task_id: str) -> Optional[Task]:
		"""Retrieve a task by its ID across all pets."""
		for pet in self.pets:
			task = pet.get_task_by_id(task_id)
			if task:
				return task
		return None

	def get_tasks_for_pet(self, pet_name: str) -> List[Task]:
		"""Get all tasks for a specific pet."""
		pet = self.get_pet(pet_name)
		return pet.tasks if pet else []

	def get_all_tasks(self) -> List[Task]:
		"""Get all tasks across all pets."""
		all_tasks = []
		for pet in self.pets:
			all_tasks.extend(pet.tasks)
		return all_tasks

	def add_constraint(self, pet_name: str, constraint: str) -> None:
		"""Add a scheduling constraint for a pet."""
		if pet_name not in self.constraints:
			self.constraints[pet_name] = []
		self.constraints[pet_name].append(constraint)

	def display_tasks(self) -> None:
		"""Display all tasks organized by pet."""
		if not self.pets:
			print("No pets registered.")
			return

		for pet in self.pets:
			print(f"\n{pet.name} ({pet.species}):")
			if not pet.tasks:
				print("  No tasks.")
			else:
				for task in pet.tasks:
					status = "✓" if task.completed else "○"
					print(f"  {status} [{task.priority.name}] {task.title} ({task.duration} min)")
					if task.time_constraint:
						print(f"      Constraint: {task.time_constraint}")

class Scheduler:
	def __init__(self, owner: Owner):
		self.owner = owner  # Links scheduler to owner
		self.current_schedule: List[Dict] = []  # Stores generated schedule with explanations
		# Each dict has: {'task': Task, 'time': time, 'pet_name': str, 'reason': str}

	def _parse_time_constraint(self, constraint: str) -> tuple[Optional[time], Optional[time]]:
		"""Parse time constraint string into time bounds.

		Examples: 'before 08:00' -> (None, 08:00), 'after 18:00' -> (18:00, None)
		Returns (earliest_time, latest_time)
		"""
		if not constraint:
			return (None, None)

		constraint = constraint.lower().strip()
		if "before" in constraint:
			time_str = constraint.split("before")[1].strip()
			hour, minute = map(int, time_str.split(":"))
			return (None, time(hour, minute))
		elif "after" in constraint:
			time_str = constraint.split("after")[1].strip()
			hour, minute = map(int, time_str.split(":"))
			return (time(hour, minute), None)
		return (None, None)

	def _time_to_minutes(self, t: time) -> int:
		"""Convert time to minutes since midnight for easier arithmetic."""
		return t.hour * 60 + t.minute

	def _minutes_to_time(self, minutes: int) -> time:
		"""Convert minutes since midnight back to time object."""
		hours = minutes // 60
		mins = minutes % 60
		return time(hours % 24, mins)

	def _can_schedule_at(self, start_minutes: int, duration: int, constraint: Optional[str]) -> bool:
		"""Check if a task can be scheduled at a given time considering constraints."""
		if not constraint:
			return True

		earliest, latest = self._parse_time_constraint(constraint)
		task_start = self._minutes_to_time(start_minutes)
		task_end = self._minutes_to_time(start_minutes + duration)

		if earliest and task_start < earliest:
			return False
		if latest and task_end > latest:
			return False
		return True

	def generate_schedule(self, pet_name: Optional[str] = None) -> List[Dict]:
		"""Generate a schedule for all tasks (or tasks for specific pet).

		Returns list of dicts with keys: task, time, pet_name, reason.
		Stores result in self.current_schedule for later explanation.
		"""
		self.current_schedule = []

		# Get tasks to schedule
		if pet_name:
			tasks = self.owner.get_tasks_for_pet(pet_name)
		else:
			tasks = self.owner.get_all_tasks()

		# Filter out completed tasks
		tasks = [t for t in tasks if not t.completed]

		if not tasks:
			return self.current_schedule

		# Sort tasks by priority (high to low), then by duration (longer first)
		sorted_tasks = sorted(
			tasks,
			key=lambda t: (t.priority.value, -t.duration),
			reverse=True
		)

		# Schedule tasks starting at 6 AM
		current_time_minutes = 6 * 60  # 6:00 AM in minutes
		scheduled_times = []  # Track occupied time slots

		for task in sorted_tasks:
			# Find a suitable time slot
			scheduled = False
			attempt_time = current_time_minutes

			# Try to find a time slot that works for up to 16 hours (6 AM to 10 PM)
			max_time = 22 * 60  # 10 PM

			while attempt_time + task.duration <= max_time and not scheduled:
				# Check if time slot is free
				slot_free = True
				for scheduled_time, scheduled_duration in scheduled_times:
					# Check for overlap
					if not (attempt_time + task.duration <= scheduled_time or
					        attempt_time >= scheduled_time + scheduled_duration):
						slot_free = False
						break

				# Check if it meets time constraints
				if slot_free and self._can_schedule_at(attempt_time, task.duration, task.time_constraint):
					scheduled = True
					scheduled_time = self._minutes_to_time(attempt_time)

					# Build reason
					reason = f"Scheduled based on {task.priority.name} priority"
					if task.time_constraint:
						reason += f" (constraint: {task.time_constraint})"

					# Check for pet restrictions
					pet = self.owner.get_pet(task.pet_name)
					if pet and pet.restrictions:
						reason += f" considering pet restrictions: {', '.join(pet.restrictions)}"

					self.current_schedule.append({
						'task': task,
						'time': scheduled_time,
						'pet_name': task.pet_name,
						'reason': reason
					})

					scheduled_times.append((attempt_time, task.duration))
					current_time_minutes = attempt_time + task.duration
				else:
					attempt_time += 15  # Try next 15-minute slot

			if not scheduled:
				# Couldn't schedule this task
				reason = f"Could not schedule due to time constraints or conflicts"
				self.current_schedule.append({
					'task': task,
					'time': None,
					'pet_name': task.pet_name,
					'reason': reason
				})

		# Sort schedule by time
		self.current_schedule.sort(key=lambda x: self._time_to_minutes(x['time']) if x['time'] else 9999)

		return self.current_schedule

	def explain_schedule(self) -> str:
		"""Explain the reasoning behind the current schedule.

		Addresses bottleneck: now has access to self.current_schedule
		to explain the decisions made during generation.
		"""
		if not self.current_schedule:
			return "No schedule has been generated yet. Use generate_schedule() first."

		explanation = "=== Daily Care Schedule ===\n\n"

		for item in self.current_schedule:
			task = item['task']
			scheduled_time = item['time']
			pet_name = item['pet_name']
			reason = item['reason']

			if scheduled_time:
				explanation += f"⏰ {scheduled_time.strftime('%I:%M %p')}\n"
			else:
				explanation += f"⏰ NOT SCHEDULED\n"

			explanation += f"   Task: {task.title}\n"
			explanation += f"   Pet: {pet_name}\n"
			explanation += f"   Duration: {task.duration} minutes\n"
			explanation += f"   Priority: {task.priority.name}\n"
			explanation += f"   Why: {reason}\n\n"

		# Add summary
		scheduled_count = sum(1 for item in self.current_schedule if item['time'] is not None)
		total_count = len(self.current_schedule)

		explanation += f"=== Summary ===\n"
		explanation += f"Scheduled: {scheduled_count}/{total_count} tasks\n"

		if scheduled_count < total_count:
			explanation += f"⚠️ {total_count - scheduled_count} task(s) could not be scheduled\n"

		return explanation

	def validate_schedule(self, schedule: List[Dict]) -> tuple[bool, List[str]]:
		"""Validate a schedule against constraints.

		Returns (is_valid, list_of_violation_messages).
		"""
		violations = []

		# Check for overlapping tasks
		for i, item1 in enumerate(schedule):
			if item1['time'] is None:
				continue

			start1 = self._time_to_minutes(item1['time'])
			end1 = start1 + item1['task'].duration

			for item2 in schedule[i+1:]:
				if item2['time'] is None:
					continue

				start2 = self._time_to_minutes(item2['time'])
				end2 = start2 + item2['task'].duration

				# Check for overlap
				if not (end1 <= start2 or start1 >= end2):
					violations.append(
						f"Tasks '{item1['task'].title}' and '{item2['task'].title}' overlap at "
						f"{item1['time'].strftime('%I:%M %p')}"
					)

		# Check time constraints
		for item in schedule:
			if item['time'] is None:
				violations.append(f"Task '{item['task'].title}' is not scheduled")
				continue

			task = item['task']
			if task.time_constraint:
				earliest, latest = self._parse_time_constraint(task.time_constraint)
				task_time = item['time']
				task_end_minutes = self._time_to_minutes(task_time) + task.duration
				task_end_time = self._minutes_to_time(task_end_minutes)

				if earliest and task_time < earliest:
					violations.append(
						f"Task '{task.title}' scheduled at {task_time.strftime('%I:%M %p')} "
						f"violates constraint: {task.time_constraint}"
					)
				if latest and task_end_time > latest:
					violations.append(
						f"Task '{task.title}' ends at {task_end_time.strftime('%I:%M %p')} "
						f"violates constraint: {task.time_constraint}"
					)

		return len(violations) == 0, violations

	def detect_conflicts(self) -> List[str]:
		"""Identify any scheduling conflicts in current_schedule."""
		is_valid, violations = self.validate_schedule(self.current_schedule)
		return violations
