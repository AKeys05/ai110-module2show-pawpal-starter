"""Demo of conflict detection features in PawPal."""

from pawpal_system import Owner, Pet, Task, Scheduler, Priority, Frequency
from datetime import time, date

def demo_conflict_detection():
	"""Demonstrate the lightweight conflict detection strategy."""
	print("=" * 60)
	print("PawPal+ Conflict Detection Demo")
	print("=" * 60)
	print()

	# Setup
	owner = Owner("Jordan")
	dog = Pet(name="Buddy", species="Dog")
	cat = Pet(name="Whiskers", species="Cat")
	owner.add_pet(dog)
	owner.add_pet(cat)

	# Scenario 1: Same pet conflict - critical warning
	print("Scenario 1: Same Pet Conflict (Critical)")
	print("-" * 60)

	walk1 = Task(
		title="Morning Walk",
		duration=30,
		priority=Priority.HIGH,
		pet_name="Buddy",
		preferred_time=time(8, 0)  # 8:00-8:30 AM
	)

	walk2 = Task(
		title="Dog Park Visit",
		duration=45,
		priority=Priority.MEDIUM,
		pet_name="Buddy",
		preferred_time=time(8, 15)  # 8:15-9:00 AM (overlaps!)
	)

	owner.add_task("Buddy", walk1)
	owner.add_task("Buddy", walk2)

	scheduler = Scheduler(owner)
	warnings = scheduler.detect_preferred_time_conflicts()

	print(f"Added 2 tasks for Buddy with overlapping preferred times:")
	print(f"  - Morning Walk: 8:00 AM (30 min)")
	print(f"  - Dog Park Visit: 8:15 AM (45 min)")
	print()
	print("Conflict warnings:")
	for warning in warnings:
		print(f"  {warning}")
	print()

	# Scenario 2: Different pet conflict - informational warning
	print("\nScenario 2: Multi-Pet Conflict (Informational)")
	print("-" * 60)

	cat_feeding = Task(
		title="Cat Breakfast",
		duration=10,
		priority=Priority.HIGH,
		pet_name="Whiskers",
		preferred_time=time(8, 0)  # Same time as dog walk
	)

	owner.add_task("Whiskers", cat_feeding)

	scheduler = Scheduler(owner)
	warnings = scheduler.detect_preferred_time_conflicts()

	print(f"Added Cat Breakfast at 8:00 AM (same as Dog's Morning Walk)")
	print()
	print("All conflict warnings:")
	for warning in warnings:
		print(f"  {warning}")
	print()

	# Scenario 3: Generate schedule and see how conflicts are resolved
	print("\nScenario 3: Scheduler Resolution")
	print("-" * 60)

	schedule = scheduler.generate_schedule()

	print("The scheduler automatically resolves conflicts:")
	print()
	for item in schedule:
		if item['time']:
			task = item['task']
			scheduled_time = item['time'].strftime('%I:%M %p')
			preferred = task.preferred_time.strftime('%I:%M %p') if task.preferred_time else "None"
			print(f"  {scheduled_time:12} | {task.pet_name:10} | {task.title}")
			if task.preferred_time and item['time'] != task.preferred_time:
				print(f"               (preferred: {preferred}, rescheduled)")
		else:
			print(f"  NOT SCHEDULED | {item['pet_name']:10} | {item['task'].title}")
	print()

	# Verify final schedule has no conflicts
	conflicts = scheduler.detect_conflicts()
	print(f"Final schedule conflicts: {len(conflicts)}")
	print()

	# Scenario 4: No conflicts - sequential tasks
	print("\nScenario 4: No Conflicts (Sequential Tasks)")
	print("-" * 60)

	owner2 = Owner("Alex")
	dog2 = Pet(name="Max", species="Dog")
	owner2.add_pet(dog2)

	task1 = Task(
		title="Morning Walk",
		duration=30,
		priority=Priority.HIGH,
		pet_name="Max",
		preferred_time=time(7, 0)  # 7:00-7:30
	)

	task2 = Task(
		title="Breakfast",
		duration=15,
		priority=Priority.HIGH,
		pet_name="Max",
		preferred_time=time(7, 30)  # 7:30-7:45 (no overlap)
	)

	owner2.add_task("Max", task1)
	owner2.add_task("Max", task2)

	scheduler2 = Scheduler(owner2)
	warnings2 = scheduler2.detect_preferred_time_conflicts()

	print(f"Added 2 sequential tasks for Max:")
	print(f"  - Morning Walk: 7:00 AM (30 min)")
	print(f"  - Breakfast: 7:30 AM (15 min)")
	print()
	print(f"Conflict warnings: {len(warnings2)}")
	if len(warnings2) == 0:
		print("  ✓ No conflicts detected - tasks are perfectly sequential!")
	print()

	print("=" * 60)
	print("Demo Complete!")
	print("=" * 60)

if __name__ == "__main__":
	demo_conflict_detection()
