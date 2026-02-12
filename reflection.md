# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

Here are the three core actions I've identified first that a user should be able to do: add their pet, add new tasks, and generate a schedule.

Building Block Brainstorm:
- Pet/Owner class that holds the representation of the pet and owner including both of their names, the species of the pet, and maybe some preferences.

- Tasks class that allows users to add/edit tasks that will feed into the schedule. Each should have a title, duration in minutes, and priority (low, med, high). Must clearly display all current tasks.

- Scheduling class that can produce a daily plan for the pet and explain why the reasoning behind that plan. Must take into account contraints and prioritie from the tasks list. Must clearly display schedule.

The initial design has an Owner, Pet, Task, TaskList, ScheduledTask, and Scheduler class. The Owner class has name and pets attributes with an add_pet method. The Pet class has name, species, and preferences attributes. An owner can own multiple pets. The Task class has title, duration and priority attributes with an edit_task method. The ScheduledTask class references Task and has a task and time attribute. The TaskList class has a tasks attribute with add_task, edit_task, and display_tasks as methods. It contains many Task objects and is used by the Scheduler class. Lastly, the Scheduler class has generate_schedule and explain_schedule methods.


**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

After prompting the AI to review the skeleton for potential bottlenecks and missing relationships, I had it change the design to simplify the 4 core classes to Owner, Pet, Scheduler and Task, change some key attribute data types and add more helper methods.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?

My scheduler considers if a task has to be done before or after a certain time (e.g., breakfast before 10:00 or walk after 12:00) and if its of low, high or medium priority. It also takes preferences into account such as if Buddy the dog prefers evening walks over morning.

- How did you decide which constraints mattered most?

The priority and set times/constraints take the highest precendence in deciding how to configure the schedule. 

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

One tradeoff my scheduler makes is using 15-minute time slots for scheduling tasks instead of precise minute-level times. The cons of this approach are that short tasks can waste slot space, fewer tasks can fit into a single day, and there's less flexibility with scheduling. However, I think this design choice is reasonable because its conceptually simpler, more readable, more realistic to how people schedule tasks (blocks instead of arbitrary times), and has better performance in terms of space.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used the Claude Plan Mode when I wanted to introduce a new method such as filtering, sorting, or conflict detection. When I didn't understand a suggestion or plan it created, I would ask it to clarify and define its relevance/importance. If I was torn between multiple methods of approaching a problem or new implementation, I would ask it brainstorm the pros and cons of each. Prompts/questions that specifically referred to a snippet of code were the most helpful because they targeted exactly what I was asking without my need for repeated prompting.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

I tested the following behaviors:
- change of task completion status
- task count changing when adding tasks
- tasks are correctly scheduled at their listed preferred time 
- marking recurring tasks complete auto-generates the next occurence
- recurring tasks correctly calculate next date
- tasks with overlapping preferred times are detected
- sorting and filtering edge cases (e.g., empty lists, single task, week/month boundaries, etc.)

Theses tests were important because they made sure that every potential user journey will allow for either successful use of system features or a graceful display of warnings.

**b. Confidence**
- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
