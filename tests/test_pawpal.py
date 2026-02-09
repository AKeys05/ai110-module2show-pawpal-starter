from pawpal_system import Owner, Pet, Task, Priority


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
