from pawpal_system import Owner, Pet, Task, Scheduler, Priority

if __name__ == "__main__":
	# Create an owner
	owner = Owner("Alex")
	print(f"Welcome to PawPal+, {owner.name}!\n")

	# Create pets
	dog = Pet(
		name="Buddy",
		species="Dog",
		preferences={"favorite_toy": "tennis ball", "likes_walks": True},
		restrictions=["no_midday_walks"]
	)

	cat = Pet(
		name="Whiskers",
		species="Cat",
		preferences={"favorite_food": "tuna", "indoor_only": True},
		restrictions=[]
	)

	# Add pets to owner
	owner.add_pet(dog)
	owner.add_pet(cat)
	print(f"Registered pets: {dog.name} (Dog) and {cat.name} (Cat)\n")

	# Create tasks for Buddy (Dog)
	dog_walk = Task(
		title="Morning Walk",
		duration=30,
		priority=Priority.HIGH,
		pet_name="Buddy",
		time_constraint="before 09:00"
	)

	dog_feeding = Task(
		title="Feed Breakfast",
		duration=15,
		priority=Priority.HIGH,
		pet_name="Buddy",
		time_constraint="before 08:00"
	)

	dog_playtime = Task(
		title="Play Fetch",
		duration=20,
		priority=Priority.MEDIUM,
		pet_name="Buddy"
	)

	# Create tasks for Whiskers (Cat)
	cat_feeding = Task(
		title="Feed Breakfast",
		duration=10,
		priority=Priority.HIGH,
		pet_name="Whiskers",
		time_constraint="before 08:00"
	)

	cat_grooming = Task(
		title="Brush Fur",
		duration=15,
		priority=Priority.LOW,
		pet_name="Whiskers"
	)

	# Add tasks to pets
	dog.add_task(dog_walk)
	dog.add_task(dog_feeding)
	dog.add_task(dog_playtime)
	cat.add_task(cat_feeding)
	cat.add_task(cat_grooming)

	print("Tasks added successfully!\n")

	# Display all tasks before scheduling
	print("=" * 50)
	print("ALL TASKS (Before Scheduling)")
	print("=" * 50)
	owner.display_tasks()
	print()

	# Create scheduler and generate schedule
	scheduler = Scheduler(owner)
	print("=" * 50)
	print("GENERATING TODAY'S SCHEDULE...")
	print("=" * 50)
	print()

	schedule = scheduler.generate_schedule()

	# Print the schedule with explanations
	print(scheduler.explain_schedule())

	# Check for any conflicts
	conflicts = scheduler.detect_conflicts()
	if conflicts:
		print("⚠️  CONFLICTS DETECTED:")
		for conflict in conflicts:
			print(f"  - {conflict}")
	else:
		print("✓ No scheduling conflicts detected!")
