---
name: example-skill
description: Example skill showing the SKILL.md structure. Use when the user asks how to write a skill, or asks for a walkthrough of this template.
---

# Example skill

A skill is a procedure the agent loads on its own when the situation matches its `description`.
Use skills for multi-step tasks you want performed consistently.

Delete this directory and add your own.

## Frontmatter

- `name` must match the directory name
- `description` is the only part the agent reads before deciding to load the skill, so state both
  what it does and when to use it
- `disable-model-invocation: true` makes the skill user-triggered only

## Workflow

Give the agent explicit steps. Numbered steps with a stated stopping point work better than a
description of the goal.

### 1. Gather input

Ask the user for the target file or directory. Do not guess.

### 2. Do the work

Perform the task, then report which files changed.

### 3. Confirm

Summarize what was done and ask whether to continue.

## References

Split long supporting material into separate files and link them, so the agent loads the detail only
when it needs it.

- Skill-specific: put files under `example-skill/references/` and link them relatively
- Shared between skills: put them in the top-level `references/`, such as
  [example-template.md](../../references/example-template.md)
