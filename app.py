import streamlit as st
from pawpal_system import Owner, Pet, Task, Priority, Scheduler

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
    for pet in owner.pets:
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
    pet_names = [pet.name for pet in owner.pets]
    selected_pet_name = st.selectbox("Select pet for task", pet_names)

    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    # Optional time constraint
    add_constraint = st.checkbox("Add time constraint")
    time_constraint = None
    if add_constraint:
        constraint_type = st.radio("Constraint type", ["before", "after"])
        constraint_time = st.time_input("Time", value=None)
        if constraint_time:
            time_constraint = f"{constraint_type} {constraint_time.strftime('%H:%M')}"

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
            time_constraint=time_constraint
        )

        # Add task to the selected pet
        selected_pet = owner.get_pet(selected_pet_name)
        if selected_pet:
            selected_pet.add_task(task)
            st.success(f"✅ Added task '{task_title}' for {selected_pet_name}!")
            st.rerun()

    # Display all tasks organized by pet
    st.markdown("#### Current Tasks")
    all_tasks = owner.get_all_tasks()
    if all_tasks:
        tasks_data = []
        for pet in owner.pets:
            for task in pet.tasks:
                tasks_data.append({
                    "Pet": pet.name,
                    "Task": task.title,
                    "Priority": task.priority.name,
                    "Duration (min)": task.duration,
                    "Constraint": task.time_constraint if task.time_constraint else "-",
                    "Status": "✓ Done" if task.completed else "○ Pending"
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
        # Create scheduler and generate schedule
        scheduler = Scheduler(owner)
        schedule = scheduler.generate_schedule()

        # Display the schedule explanation
        st.success("✅ Schedule generated!")
        st.markdown("### Today's Schedule")
        st.text(scheduler.explain_schedule())

        # Check for conflicts
        conflicts = scheduler.detect_conflicts()
        if conflicts:
            st.error("⚠️ Conflicts detected:")
            for conflict in conflicts:
                st.write(f"- {conflict}")
        else:
            st.success("✓ No scheduling conflicts detected!")
