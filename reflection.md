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

**Hard constraints** (decide *whether* a task shows up):
- Completion status: completed tasks are dropped from the plan by default.
- Frequency / "due today": a task only appears if it's due — daily unless already done today, weekly only after 7+ days.
- Time budget: if the owner sets how many minutes they have, tasks that don't fit are skipped.

**Ordering constraints** (decide the *sequence* of what's included):
- Priority: high-priority tasks are placed before medium and low ones.
- Pet grouping: tasks for the same pet stay together so the owner finishes one pet at a time.
- Duration: shorter tasks come first when priority is tied.
- Start time: tasks can alternatively be ordered chronologically by their clock time.

**Advisory constraints** (warn but don't block):
- Conflict/format warnings: overlapping start times and invalid time formats are flagged instead of crashing.

I decided priority mattered most because the whole point of the app is helping an owner do the important things first when time is short — so priority drives the
ordering, and the time budget is the hard limit that everything else has to fit inside. Preferences (like "walk before breakfast") are the one thing I did not fully model; the pet-grouping heuristic is the closest I got, and it's something I'd add as an explicit constraint next.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

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
