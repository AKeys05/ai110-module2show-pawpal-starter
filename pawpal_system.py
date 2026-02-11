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
	preferred_time: Optional[time] = None  # User's preferred time for task
	time_constraint: Optional[str] = None  # e.g., "before 08:00", "after 18:00"
	completed: bool = False  # Completion status

	@staticmethod
	def parse_preferred_time(time_str: str) -> Optional[time]:
		"""Parse time string (e.g., '08:00', '8:00 AM') to time object.

		Returns None if parsing fails.
		"""
		if not time_str:
			return None

		try:
			# Try 24-hour format (HH:MM)
			if ':' in time_str and ('AM' not in time_str.upper() and 'PM' not in time_str.upper()):
				hour, minute = map(int, time_str.strip().split(':'))
				return time(hour, minute)

			# Try 12-hour format (HH:MM AM/PM)
			from datetime import datetime
			parsed = datetime.strptime(time_str.strip(), '%I:%M %p')
			return parsed.time()
		except:
			return None

	def validate_time_settings(self) -> tuple[bool, Optional[str]]:
		"""Validate that preferred_time and time_constraint are compatible.

		Returns (is_valid, error_message).
		"""
		if not self.preferred_time or not self.time_constraint:
			return True, None

		# Need to parse constraint - use a temporary scheduler instance
		# This is a bit awkward but avoids circular dependencies
		from datetime import datetime, timedelta

		constraint = self.time_constraint.lower().strip()
		earliest = None
		latest = None

		if "before" in constraint:
			time_str = constraint.split("before")[1].strip()
			hour, minute = map(int, time_str.split(":"))
			latest = time(hour, minute)
		elif "after" in constraint:
			time_str = constraint.split("after")[1].strip()
			hour, minute = map(int, time_str.split(":"))
			earliest = time(hour, minute)

		# Check if preferred time satisfies constraint
		if earliest and self.preferred_time < earliest:
			return False, f"Preferred time {self.preferred_time.strftime('%I:%M %p')} is before constraint earliest time"

		if latest:
			# Check if task would finish by latest time
			preferred_dt = datetime.combine(datetime.today(), self.preferred_time)
			end_dt = preferred_dt + timedelta(minutes=self.duration)
			end_time = end_dt.time()

			if end_time > latest:
				return False, f"Task ending at {end_time.strftime('%I:%M %p')} exceeds constraint latest time"

		return True, None

class Owner:
	def __init__(self, name: str):
		self.name = name
		self.pets: Dict[str, Pet] = {}  # Changed to dict for O(1) pet lookup
		self.task_index: Dict[str, Task] = {}  # Task ID -> Task for O(1) task lookup
		self.constraints: Dict[str, List[str]] = {}  # pet_name -> list of constraint descriptions

	def add_pet(self, pet: Pet) -> None:
		"""Add a pet to the owner's pet list."""
		self.pets[pet.name] = pet
		# Index any existing tasks on the pet
		for task in pet.tasks:
			self.task_index[task.id] = task

	def get_pet(self, pet_name: str) -> Optional[Pet]:
		"""Retrieve a pet by name."""
		return self.pets.get(pet_name)

	def add_task(self, pet_name: str, task: Task) -> bool:
		"""Add a task to a specific pet's task list. Returns True if successful."""
		pet = self.get_pet(pet_name)
		if pet:
			pet.add_task(task)
			self.task_index[task.id] = task  # Add to index for O(1) lookup
			return True
		return False

	def edit_task(self, task_id: str, **kwargs) -> bool:
		"""Edit a task's properties by task ID. Returns True if successful."""
		task = self.get_task_by_id(task_id)  # Use get_task_by_id which has fallback logic
		if task:
			for key, value in kwargs.items():
				if hasattr(task, key):
					setattr(task, key, value)
			return True
		return False

	def get_task_by_id(self, task_id: str) -> Optional[Task]:
		"""Retrieve a task by its ID across all pets."""
		# Try index first for O(1) lookup
		task = self.task_index.get(task_id)
		if task:
			return task
		# Fall back to searching if not in index (handles tasks added directly to pets)
		for pet in self.pets.values():
			task = pet.get_task_by_id(task_id)
			if task:
				# Add to index for future lookups
				self.task_index[task_id] = task
				return task
		return None

	def get_tasks_for_pet(self, pet_name: str) -> List[Task]:
		"""Get all tasks for a specific pet."""
		pet = self.get_pet(pet_name)
		return pet.tasks if pet else []

	def get_all_tasks(self) -> List[Task]:
		"""Get all tasks across all pets."""
		all_tasks = []
		for pet in self.pets.values():
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

		for pet in self.pets.values():
			print(f"\n{pet.name} ({pet.species}):")
			if not pet.tasks:
				print("  No tasks.")
			else:
				for task in pet.tasks:
					status = "✓" if task.completed else "○"
					print(f"  {status} [{task.priority.name}] {task.title} ({task.duration} min)")
					if task.preferred_time:
						print(f"      Preferred time: {task.preferred_time.strftime('%I:%M %p')}")
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

		# Schedule tasks starting at 6 AM using time slot bitmap
		start_time = 6 * 60  # 6:00 AM in minutes
		max_time = 22 * 60  # 10 PM
		slot_duration = 15  # Each slot represents 15 minutes
		num_slots = (max_time - start_time) // slot_duration  # 64 slots (6 AM to 10 PM)

		# Initialize bitmap: False = available, True = occupied
		time_slots = [False] * num_slots

		for task in sorted_tasks:
			# Calculate how many 15-minute slots this task needs
			slots_needed = (task.duration + slot_duration - 1) // slot_duration  # Round up

			# Find a suitable time slot
			scheduled = False
			scheduled_time = None
			reason = ""

			# NEW: Try preferred time first
			if task.preferred_time:
				preferred_minutes = self._time_to_minutes(task.preferred_time)
				preferred_slot = (preferred_minutes - start_time) // slot_duration

				# Check if preferred slot is valid and available
				if 0 <= preferred_slot <= num_slots - slots_needed:
					if not any(time_slots[preferred_slot:preferred_slot + slots_needed]):
						# Check constraint compatibility (if constraint exists)
						if task.time_constraint is None or self._can_schedule_at(preferred_minutes, task.duration, task.time_constraint):
							# Schedule at preferred time
							for i in range(preferred_slot, preferred_slot + slots_needed):
								time_slots[i] = True

							# Smart break insertion
							if task.duration > 30 and preferred_slot + slots_needed < num_slots:
								time_slots[preferred_slot + slots_needed] = True

							scheduled = True
							scheduled_time = task.preferred_time
							reason = f"Scheduled at preferred time {task.preferred_time.strftime('%I:%M %p')}"

			# Fallback: Try constraint-based or any available slot
			if not scheduled:
				for slot_index in range(num_slots - slots_needed + 1):
					attempt_time = start_time + (slot_index * slot_duration)

					# Check if all required consecutive slots are free
					if not any(time_slots[slot_index:slot_index + slots_needed]):
						# Check if it meets time constraints
						if self._can_schedule_at(attempt_time, task.duration, task.time_constraint):
							# Mark slots as occupied
							for i in range(slot_index, slot_index + slots_needed):
								time_slots[i] = True

							# Smart break insertion: add 15-min break after tasks > 30 min
							if task.duration > 30 and slot_index + slots_needed < num_slots:
								time_slots[slot_index + slots_needed] = True

							scheduled = True
							scheduled_time = self._minutes_to_time(attempt_time)

							# Build reason
							if task.preferred_time:
								reason = f"Preferred time {task.preferred_time.strftime('%I:%M %p')} unavailable, scheduled based on {task.priority.name} priority"
							else:
								reason = f"Scheduled based on {task.priority.name} priority"
							break  # Task scheduled, move to next task

			# Add common reason elements and schedule entry
			if scheduled:
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
