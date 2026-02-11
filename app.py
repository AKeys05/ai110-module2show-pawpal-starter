import streamlit as st
import datetime
from pawpal_system import Owner, Pet, Task, Priority, Scheduler, Frequency

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

# Initialize owner in session_state
st.subheader("Owner Information")
owner_name = st.text_input("Owner name", value="Jordan")

if "owner" not in st.session_state:
    st.session_state.owner = Owner(owner_name)
else:
    # Update owner name if changed
    if st.session_state.owner.name != owner_name:
        st.session_state.owner.name = owner_name

owner = st.session_state.owner

st.divider()

# Pet Management Section
st.subheader("🐾 Manage Pets")

# Display existing pets
if owner.pets:
    st.write("**Your Pets:**")
    pets_data = []
    for pet in owner.pets.values():
        pets_data.append({
            "Name": pet.name,
            "Species": pet.species.capitalize(),
            "Tasks": len(pet.tasks)
        })
    st.table(pets_data)
else:
    st.info("No pets added yet. Add your first pet below!")

# Add new pet
st.markdown("#### Add a Pet")
col1, col2 = st.columns(2)
with col1:
    new_pet_name = st.text_input("Pet name", value="Mochi", key="new_pet_name")
with col2:
    new_pet_species = st.selectbox("Species", ["dog", "cat", "bird", "rabbit", "other"], key="new_pet_species")

if st.button("Add Pet"):
    # Check if pet already exists
    if owner.get_pet(new_pet_name):
        st.warning(f"⚠️ A pet named '{new_pet_name}' already exists!")
    else:
        new_pet = Pet(name=new_pet_name, species=new_pet_species)
        owner.add_pet(new_pet)
        st.success(f"✅ Added {new_pet_name} the {new_pet_species}!")
        st.rerun()

st.divider()

st.markdown("### Tasks")
st.caption("Add tasks for your pets.")

if not owner.pets:
    st.warning("⚠️ Please add at least one pet before creating tasks.")
else:
    # Pet selector for tasks
    pet_names = [pet.name for pet in owner.pets.values()]
    selected_pet_name = st.selectbox("Select pet for task", pet_names)

    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    # Optional preferred time
    use_preferred_time = st.checkbox("Set preferred time")
    preferred_time = None
    if use_preferred_time:
        preferred_time = st.time_input("Preferred time", value=datetime.time(8, 0))

    # Optional time constraint
    add_constraint = st.checkbox("Add time constraint")
    time_constraint = None
    if add_constraint:
        constraint_type = st.radio("Constraint type", ["before", "after"])
        constraint_time = st.time_input("Constraint time", value=None)
        if constraint_time:
            time_constraint = f"{constraint_type} {constraint_time.strftime('%H:%M')}"

    # Recurring task options
    is_recurring = st.checkbox("Make this a recurring task")
    frequency = None
    scheduled_date = None

    if is_recurring:
        col1, col2 = st.columns(2)
        with col1:
            frequency_str = st.selectbox(
                "Frequency",
                ["daily", "weekly", "biweekly", "monthly"],
                help="How often should this task repeat?"
            )
            frequency = Frequency(frequency_str)
        with col2:
            scheduled_date = st.date_input(
                "Start date",
                value=datetime.date.today(),
                help="When should this recurring task start?"
            )
    else:
        # For non-recurring tasks, set scheduled_date to today
        scheduled_date = datetime.date.today()

    if st.button("Add task"):
        # Map string priority to Priority enum
        priority_map = {
            "low": Priority.LOW,
            "medium": Priority.MEDIUM,
            "high": Priority.HIGH
        }

        task = Task(
            title=task_title,
            duration=int(duration),
            priority=priority_map[priority],
            pet_name=selected_pet_name,
            preferred_time=preferred_time,
            time_constraint=time_constraint,
            frequency=frequency,
            scheduled_date=scheduled_date
        )

        # Add task to the selected pet
        selected_pet = owner.get_pet(selected_pet_name)
        if selected_pet:
            selected_pet.add_task(task)
            # Also add to owner's task index for fast lookup
            st.session_state.owner.task_index[task.id] = task

            recurring_msg = f" (recurring {frequency.value})" if frequency else ""
            st.success(f"✅ Added task '{task_title}' for {selected_pet_name}{recurring_msg}!")
            st.rerun()

    # Display all tasks organized by pet
    st.markdown("#### Current Tasks")
    all_tasks = owner.get_all_tasks()

    if all_tasks:
        # Show incomplete tasks with action buttons
        incomplete_tasks = [t for t in all_tasks if not t.completed]

        if incomplete_tasks:
            st.write("**Pending Tasks:**")
            for pet in owner.pets.values():
                pet_incomplete = [t for t in pet.tasks if not t.completed]
                if pet_incomplete:
                    st.markdown(f"**{pet.name}:**")

                    for task in pet_incomplete:
                        col1, col2 = st.columns([4, 1])

                        with col1:
                            # Task details
                            recurring_badge = f" `{task.frequency.value}`" if task.frequency else ""
                            st.write(f"**{task.title}**{recurring_badge}")

                            details = f"{task.duration} min • {task.priority.name}"
                            if task.preferred_time:
                                details += f" • {task.preferred_time.strftime('%I:%M %p')}"
                            if task.scheduled_date:
                                details += f" • {task.scheduled_date.strftime('%Y-%m-%d')}"
                            st.caption(details)

                        with col2:
                            # Complete button
                            if st.button("✓ Complete", key=f"complete_{task.id}"):
                                success, next_task = owner.complete_task(task.id)

                                if success:
                                    if next_task:
                                        st.success(f"✅ Completed! Next occurrence: {next_task.scheduled_date}")
                                    else:
                                        st.success("✅ Task completed!")
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to complete task")

        # Show completed tasks in collapsible section
        completed_tasks = [t for t in all_tasks if t.completed]
        if completed_tasks:
            with st.expander(f"Completed Tasks ({len(completed_tasks)})"):
                tasks_data = []
                for task in completed_tasks:
                    tasks_data.append({
                        "Pet": task.pet_name,
                        "Task": task.title,
                        "Priority": task.priority.name,
                        "Date": task.scheduled_date.strftime('%Y-%m-%d') if task.scheduled_date else "-"
                    })
                st.table(tasks_data)
    else:
        st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")

if st.button("Generate schedule"):
    # Check if there are any tasks
    all_tasks = owner.get_all_tasks()

    if not all_tasks:
        st.warning("⚠️ Please add at least one task before generating a schedule.")
    else:
        # Create scheduler and check for preferred time conflicts BEFORE scheduling
        scheduler = Scheduler(owner)

        # Check for potential conflicts in preferred times
        warnings = scheduler.detect_preferred_time_conflicts()
        if warnings:
            st.warning("⚠️ Preferred Time Conflicts Detected:")
            for warning in warnings:
                if "Same pet conflict" in warning:
                    st.error(warning)
                else:
                    st.info(warning)
            st.caption("The scheduler will try to resolve these conflicts automatically.")

        # Generate schedule
        schedule = scheduler.generate_schedule()

        # Display the schedule explanation
        st.success("✅ Schedule generated!")
        st.markdown("### Today's Schedule")
        st.text(scheduler.explain_schedule())

        # Check for conflicts in final schedule (should be rare)
        conflicts = scheduler.detect_conflicts()
        if conflicts:
            st.error("⚠️ Final schedule conflicts detected:")
            for conflict in conflicts:
                st.write(f"- {conflict}")
        else:
            st.success("✓ No scheduling conflicts in final schedule!")
