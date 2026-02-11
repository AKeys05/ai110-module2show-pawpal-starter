from pawpal_system import Owner, Pet, Task, Priority, Scheduler, Frequency
from datetime import time, date, timedelta


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


# ========== Recurring Task Tests ==========

def test_daily_recurring_task_creates_next_occurrence():
	"""Test that completing a daily recurring task creates tomorrow's task."""
	owner = Owner("Test Owner")
	dog = Pet(name="Rex", species="Dog")
	owner.add_pet(dog)

	today = date.today()
	tomorrow = today + timedelta(days=1)

	# Create daily recurring task
	task = Task(
		title="Daily Walk",
		duration=30,
		priority=Priority.HIGH,
		pet_name="Rex",
		frequency=Frequency.DAILY,
		scheduled_date=today
	)
	owner.add_task("Rex", task)

	# Verify initial state
	assert len(dog.tasks) == 1
	assert task.completed == False

	# Complete the task
	success, next_task = owner.complete_task(task.id)

	# Verify completion and next occurrence
	assert success == True
	assert task.completed == True
	assert next_task is not None
	assert next_task.scheduled_date == tomorrow
	assert next_task.title == task.title
	assert next_task.completed == False
	assert len(dog.tasks) == 2  # Original + next occurrence


def test_weekly_recurring_task_calculation():
	"""Test that weekly recurring tasks calculate correct next date."""
	today = date(2026, 2, 11)  # Tuesday
	next_week = date(2026, 2, 18)  # Next Tuesday

	task = Task(
		title="Weekly Vet Visit",
		duration=60,
		priority=Priority.HIGH,
		pet_name="Rex",
		frequency=Frequency.WEEKLY,
		scheduled_date=today
	)

	next_task = task.clone_for_next_occurrence()

	assert next_task is not None
	assert next_task.scheduled_date == next_week
	assert (next_task.scheduled_date - today).days == 7


def test_non_recurring_task_does_not_create_next_occurrence():
	"""Test that completing a non-recurring task does not create another task."""
	owner = Owner("Test Owner")
	dog = Pet(name="Rex", species="Dog")
	owner.add_pet(dog)

	task = Task(
		title="One-time Grooming",
		duration=45,
		priority=Priority.MEDIUM,
		pet_name="Rex"
		# No frequency set
	)
	owner.add_task("Rex", task)

	# Complete the task
	success, next_task = owner.complete_task(task.id)

	# Verify no next occurrence
	assert success == True
	assert task.completed == True
	assert next_task is None
	assert len(dog.tasks) == 1  # Only the original task


def test_scheduler_filters_future_recurring_tasks():
	"""Test that scheduler only includes today's tasks, not future occurrences."""
	owner = Owner("Test Owner")
	dog = Pet(name="Rex", species="Dog")
	owner.add_pet(dog)

	today = date.today()
	tomorrow = today + timedelta(days=1)

	# Task for today
	task_today = Task(
		title="Today's Walk",
		duration=30,
		priority=Priority.HIGH,
		pet_name="Rex",
		scheduled_date=today
	)

	# Task for tomorrow
	task_tomorrow = Task(
		title="Tomorrow's Walk",
		duration=30,
		priority=Priority.HIGH,
		pet_name="Rex",
		scheduled_date=tomorrow
	)

	owner.add_task("Rex", task_today)
	owner.add_task("Rex", task_tomorrow)

	# Generate schedule
	scheduler = Scheduler(owner)
	schedule = scheduler.generate_schedule()

	# Verify only today's task is scheduled
	scheduled_titles = [item['task'].title for item in schedule]
	assert "Today's Walk" in scheduled_titles
	assert "Tomorrow's Walk" not in scheduled_titles


def test_biweekly_recurring_task():
	"""Test that biweekly tasks calculate correct next date (14 days)."""
	today = date.today()
	two_weeks_later = today + timedelta(weeks=2)

	task = Task(
		title="Biweekly Grooming",
		duration=45,
		priority=Priority.MEDIUM,
		pet_name="Rex",
		frequency=Frequency.BIWEEKLY,
		scheduled_date=today
	)

	next_task = task.clone_for_next_occurrence()

	assert next_task is not None
	assert next_task.scheduled_date == two_weeks_later
	assert (next_task.scheduled_date - today).days == 14


def test_monthly_recurring_task_normal_case():
	"""Test monthly recurrence for normal month transitions."""
	# Task scheduled for January 15
	task = Task(
		title="Monthly Checkup",
		duration=60,
		priority=Priority.HIGH,
		pet_name="Rex",
		frequency=Frequency.MONTHLY,
		scheduled_date=date(2026, 1, 15)
	)

	next_task = task.clone_for_next_occurrence()

	assert next_task is not None
	# Should be February 15
	assert next_task.scheduled_date.month == 2
	assert next_task.scheduled_date.day == 15


def test_parent_task_id_links_recurring_tasks():
	"""Test that generated tasks link back to original via parent_task_id."""
	task = Task(
		title="Daily Walk",
		duration=30,
		priority=Priority.HIGH,
		pet_name="Rex",
		frequency=Frequency.DAILY,
		scheduled_date=date.today()
	)

	original_id = task.id
	next_task = task.clone_for_next_occurrence()

	assert next_task.parent_task_id == original_id

	# Third generation should still link to original
	third_task = next_task.clone_for_next_occurrence()
	assert third_task.parent_task_id == original_id


def test_backward_compatibility_with_existing_tasks():
	"""Test that existing non-recurring tasks work without changes."""
	owner = Owner("Test Owner")
	dog = Pet(name="Rex", species="Dog")
	owner.add_pet(dog)

	# Old-style task (no frequency, no scheduled_date)
	task = Task(
		title="Old Task",
		duration=30,
		priority=Priority.HIGH,
		pet_name="Rex"
	)
	owner.add_task("Rex", task)

	# Should still work with complete_task
	success, next_task = owner.complete_task(task.id)

	assert success == True
	assert task.completed == True
	assert next_task is None


# ========== Conflict Detection Tests ==========

def test_same_pet_conflict_detection():
	"""Test that overlapping preferred times for the same pet are detected."""
	owner = Owner("Test Owner")
	dog = Pet(name="Rex", species="Dog")
	owner.add_pet(dog)

	# Two tasks for same pet with overlapping preferred times
	task1 = Task(
		title="Morning Walk",
		duration=30,
		priority=Priority.HIGH,
		pet_name="Rex",
		preferred_time=time(8, 0)  # 8:00-8:30 AM
	)

	task2 = Task(
		title="Breakfast",
		duration=15,
		priority=Priority.HIGH,
		pet_name="Rex",
		preferred_time=time(8, 15)  # 8:15-8:30 AM (overlaps!)
	)

	owner.add_task("Rex", task1)
	owner.add_task("Rex", task2)

	scheduler = Scheduler(owner)

	# Check preferred time conflicts BEFORE scheduling
	warnings = scheduler.detect_preferred_time_conflicts()

	# Should detect same-pet conflict
	assert len(warnings) > 0
	assert any("Same pet conflict" in w for w in warnings)
	assert any("Rex" in w for w in warnings)


def test_different_pet_conflict_detection():
	"""Test that overlapping preferred times for different pets are detected."""
	owner = Owner("Test Owner")
	dog = Pet(name="Rex", species="Dog")
	cat = Pet(name="Whiskers", species="Cat")
	owner.add_pet(dog)
	owner.add_pet(cat)

	# Tasks for different pets with overlapping preferred times
	task1 = Task(
		title="Dog Walk",
		duration=30,
		priority=Priority.HIGH,
		pet_name="Rex",
		preferred_time=time(8, 0)
	)

	task2 = Task(
		title="Cat Feeding",
		duration=15,
		priority=Priority.HIGH,
		pet_name="Whiskers",
		preferred_time=time(8, 0)  # Same time as dog walk
	)

	owner.add_task("Rex", task1)
	owner.add_task("Whiskers", task2)

	scheduler = Scheduler(owner)

	# Check preferred time conflicts
	warnings = scheduler.detect_preferred_time_conflicts()

	# Should detect multi-pet conflict
	assert len(warnings) > 0
	assert any("Multi-pet conflict" in w for w in warnings)
	assert any("Rex" in w and "Whiskers" in w for w in warnings)


def test_preferred_time_warnings():
	"""Test that preferred time warnings detect both same-pet and multi-pet conflicts."""
	owner = Owner("Test Owner")
	dog = Pet(name="Rex", species="Dog")
	cat = Pet(name="Whiskers", species="Cat")
	owner.add_pet(dog)
	owner.add_pet(cat)

	# Same-pet conflict - overlapping preferred times
	task1 = Task(
		title="Walk 1",
		duration=30,
		priority=Priority.HIGH,
		pet_name="Rex",
		preferred_time=time(8, 0)
	)
	task2 = Task(
		title="Walk 2",
		duration=30,
		priority=Priority.HIGH,
		pet_name="Rex",
		preferred_time=time(8, 15)
	)

	# Different-pet conflict
	task3 = Task(
		title="Cat Play",
		duration=20,
		priority=Priority.HIGH,
		pet_name="Whiskers",
		preferred_time=time(8, 0)
	)

	owner.add_task("Rex", task1)
	owner.add_task("Rex", task2)
	owner.add_task("Whiskers", task3)

	scheduler = Scheduler(owner)

	# Check preferred time conflicts
	warnings = scheduler.detect_preferred_time_conflicts()

	# Should have both same-pet and multi-pet warnings
	assert len(warnings) >= 2
	assert any("Same pet conflict" in w for w in warnings)
	assert any("Multi-pet conflict" in w for w in warnings)


def test_no_conflicts_with_sequential_tasks():
	"""Test that sequential tasks don't trigger conflict warnings."""
	owner = Owner("Test Owner")
	dog = Pet(name="Rex", species="Dog")
	owner.add_pet(dog)

	# Sequential tasks (no overlap)
	task1 = Task(
		title="Morning Walk",
		duration=30,
		priority=Priority.HIGH,
		pet_name="Rex",
		preferred_time=time(8, 0)  # 8:00-8:30
	)

	task2 = Task(
		title="Breakfast",
		duration=15,
		priority=Priority.HIGH,
		pet_name="Rex",
		preferred_time=time(8, 30)  # 8:30-8:45 (no overlap)
	)

	owner.add_task("Rex", task1)
	owner.add_task("Rex", task2)

	scheduler = Scheduler(owner)

	# Check preferred time conflicts
	warnings = scheduler.detect_preferred_time_conflicts()

	# Should have no warnings
	assert len(warnings) == 0

	# Also verify the schedule executes without conflicts
	scheduler.generate_schedule()
	conflicts = scheduler.detect_conflicts()
	assert len(conflicts) == 0
