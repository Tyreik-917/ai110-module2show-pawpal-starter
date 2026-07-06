# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

User actions: Enter and Manage Pet Profile Information, Add and Edit Care Tasks, Generate and View the Daily Schedule

UML design: 
    Classes: Owner, Pet, Task, Scheduler

    Owner:
        Class Attributes: Owners name
        Class Methods: set and get the Owners name
    Pet: 
        Class Attributes: Pets name
        Class Methods: set and get the Pets name
    Task:
        Class Attributes: Pet (to assign task for that specific pet)
        Class Methods: set and gets tasks, add/edit tasks (duration + priority at minimum)
    Scheduler:
        Class Attributes: Task
        Class Methods: Generate a daily schedule/plan based on constraints and priorities
**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.
Yes, in my Pet class I aded a task collection
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

Hard constraints, completion status, frequency/due-today, time budget, Ordering constraints, priority, pet grouping, duration, start time, Advisory constraints, conflict/format warnings.

I decided priority mattered most because the whole point of the app is helping an owner do the important things first when time is short — so priority drives the ordering, and the time budget is the hard limit that everything else has to fit inside Preferences (like "walk before breakfast") are the one thing I did not fully model; the pet-grouping heuristic is the closest I got, and it's something I'd add as an explicit constraint next.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?
Priority order vs. chronological order where the plan is a priority-ranked to-do list, not a time-ordered agenda
---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?
Refactoring - I asked about any future errors that can come from the curretn code and any ways to simplify or optimize the current algos
**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?
The AI made two seperate functions for getting the time but it could have all been done in 1 function. I checked by examing the code and testing it and asking AI if it was reasonable.
---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?
Task ordering and Conflict Detection to ensure the ordering is currect and that all possible conflicts are found
**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?
Mostly confident, I would want to test how this would work if I was to put it on a domain and let real users use it
---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
Having to verify AI suggestions and determining if I should use them or not
**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
I would learn how to prompt better so that the AI could maybe give better answers to my questions


**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

Not everything that the AI gives you should be accepted without understanding it and how it will effect you code
