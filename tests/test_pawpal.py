from pawpal_system import Owner, Pet, Task, Priority, Scheduler
from datetime import time


def test_task_completion_status_changes():
	"""Test that task completion status can be changed."""
	# Create an owner and pet
	owner = Owner("Test Owner")
	dog = Pet(name="Rex", species="Dog")
	owner.add_pet(dog)

	# Create a task
	task = Task(
		title="Walk",
		duration=30,
		priority=Priority.HIGH,
		pet_name="Rex"
	)

	# Add task to pet
	dog.add_task(task)

	# Verify task starts as incomplete
	assert task.completed == False

	# Change completion status using edit_task
	owner.edit_task(task.id, completed=True)

	# Verify completion status changed
	assert task.completed == True

	# Change it back
	owner.edit_task(task.id, completed=False)

	# Verify it changed back
	assert task.completed == False


def test_adding_task_increases_pet_task_count():
	"""Test that adding a task to a Pet increases that pet's task count."""
	# Create a pet
	cat = Pet(name="Mittens", species="Cat")

	# Verify initial task count is 0
	assert len(cat.tasks) == 0

	# Create and add first task
	task1 = Task(
		title="Feed",
		duration=10,
		priority=Priority.HIGH,
		pet_name="Mittens"
	)
	cat.add_task(task1)

	# Verify task count increased to 1
	assert len(cat.tasks) == 1

	# Create and add second task
	task2 = Task(
		title="Groom",
		duration=15,
		priority=Priority.MEDIUM,
		pet_name="Mittens"
	)
	cat.add_task(task2)

	# Verify task count increased to 2
	assert len(cat.tasks) == 2

	# Verify the correct tasks are in the list
	assert task1 in cat.tasks
	assert task2 in cat.tasks


def test_preferred_time_scheduling():
	"""Test that tasks are scheduled at preferred time when available."""
	owner = Owner("Test Owner")
	dog = Pet(name="Rex", species="Dog")
	owner.add_pet(dog)

	# Task with preferred time at 8:00 AM
	task = Task(
		title="Walk",
		duration=30,
		priority=Priority.MEDIUM,
		pet_name="Rex",
		preferred_time=time(8, 0)
	)
	owner.add_task("Rex", task)

	# Generate schedule
	scheduler = Scheduler(owner)
	schedule = scheduler.generate_schedule()

	# Verify task scheduled at preferred time
	assert schedule[0]['time'] == time(8, 0)
	assert "preferred time" in schedule[0]['reason'].lower()


def test_preferred_time_with_constraint_fallback():
	"""Test fallback to constraint when preferred time unavailable."""
	owner = Owner("Test Owner")
	dog = Pet(name="Rex", species="Dog")
	owner.add_pet(dog)

	# Task 1: High priority, occupies 7:00-7:30 AM
	task1 = Task(
		title="Feed",
		duration=30,
		priority=Priority.HIGH,
		pet_name="Rex",
		preferred_time=time(7, 0)
	)

	# Task 2: Prefers 7:00 AM but has fallback constraint
	task2 = Task(
		title="Walk",
		duration=30,
		priority=Priority.LOW,
		pet_name="Rex",
		preferred_time=time(7, 0),
		time_constraint="before 09:00"
	)

	owner.add_task("Rex", task1)
	owner.add_task("Rex", task2)

	# Generate schedule
	scheduler = Scheduler(owner)
	schedule = scheduler.generate_schedule()

	# Find tasks in schedule (they may be in any order due to time sorting)
	feed_item = next(item for item in schedule if item['task'].title == "Feed")
	walk_item = next(item for item in schedule if item['task'].title == "Walk")

	# Task 1 (Feed) gets preferred time
	assert feed_item['time'] == time(7, 0)
	assert "preferred time" in feed_item['reason'].lower()

	# Task 2 (Walk) falls back to available slot within constraint
	assert walk_item['time'] != time(7, 0)  # Not preferred time
	assert walk_item['time'] < time(9, 0)  # Within constraint
	assert "unavailable" in walk_item['reason'].lower()


def test_preferred_time_validation():
	"""Test that incompatible preferred_time and constraint are detected."""
	task = Task(
		title="Walk",
		duration=30,
		priority=Priority.HIGH,
		pet_name="Rex",
		preferred_time=time(10, 0),      # 10:00 AM
		time_constraint="before 09:00"   # Must finish by 9:00 AM
	)

	is_valid, error = task.validate_time_settings()
	assert not is_valid
	assert error is not None
	assert "before" in error.lower() or "constraint" in error.lower()
