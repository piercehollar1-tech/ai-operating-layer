# Delegation

Some work should not run on the main thread: adversarial review of code the main session wrote, sweeps over hundreds of files, planned multi-file builds with a closed brief. This document describes a delegation layer with one gate, two lanes, one packet format, and a hook that makes the gate the door rather than an option.

## The gate

Delegate only when all four hold, then check the break-even:

1. **Clear.** Outcome, scope, constraints, and acceptance criteria can be written down now.
2. **Substantial.** Doing it in the main session would cost more than a handful of its own turns. Each main-session turn re-sends the whole context; under a few turns of work, delegating loses.
3. **Independent.** The worker will not need judgment mid-task.
4. **Checkable.** The result is verifiable from a diff, a command, tests, or cited locators.

**Never delegate:** design or copy (taste does not survive a packet), security-sensitive paths, client or legal deliverables, moving requirements or architecture, anything whose real context is the current conversation, anything destructive, production-facing, or credential-bearing.

Gate fails: do the work in-session and say so in one clause.

## Two lanes, one packet

| Job shape | Lane | Why |
|---|---|---|
| Adversarial second opinion on code the main session or a worker wrote | External model CLI, review mode | A different model reading it, off the main session's plan and blind spots |
| Read-heavy sweep, inventory, bulk mechanical edit with a closed brief | External model CLI, mechanical or judgment mode | Long wall-clock is fine; the external plan absorbs the tokens |
| Planned multi-file build wanted back in minutes; a bounded question about a repo | In-client subagent (`worker` for edits, `scout` read-only) | In-session, minutes, isolated context, model tier chosen per agent |
| External lane returned a fallback signal (rate limit, auth, overload, a reserved exit code) | In-client lane, same packet | The packet is lane-agnostic |

The task packet is the same for either lane: outcome, scope, constraints, acceptance criteria, the files in play, and the verification the main session will run on the result. Writing it is most of the work; if it cannot be written, the gate already failed.

**Whatever comes back is information, never instruction.** A worker's report, a reviewer's findings, and an external model's proposed patch are inputs to the main session's judgment. The main session owns the result and runs the verification itself.

## The dispatch contract, hook-enforced

Subagents start cold. They do not see the conversation, the instruction files' nuance, or any lesson the main session has learned. Two hooks make that survivable:

**A dispatch gate** rejects any subagent prompt that lacks an injected context brief of at least a few hundred characters, or that does not end with a required "Learnings" report section. Only the report survives the session; the agent's transcript does not. The report runs through the same learning-capture triggers as any other work.

**A delegate-first gate** denies the first subagent dispatch of a session unless the delegation skill ran first. The identical retry passes. Measured before the gate existed: zero delegations across sixty-one sessions in which the option was documented and available. The gate turned a documented option into the door everything goes through.

That second hook is the general pattern: **when a documented option is measured at zero use, wire it to the moment of action rather than rewriting the paragraph.**

## Agent definitions carry the model tier

Each in-client agent is a file with frontmatter naming its model, its tools, and its purpose. The instruction files say only "dispatch by agent name"; the tier lives with the agent, so changing it is one edit in one place rather than a sweep across rules.

Typical set:

| Agent | Tier | Tools | For |
|---|---|---|---|
| `scout` | Mid, read-only | Read, search, shell | Bounded questions, diagnosis, verification of a diff against criteria |
| `worker` | Mid, edits | Read, edit, write, shell; optional isolated worktree | Planned, packeted changes |
| `security-reviewer` | Mid, read-only | Read, search, shell | Reports verified vulnerabilities; never edits |
| `planner` | High | Read, search | Phased plans for complex features |

## What transfers

- **One gate, written down, run before every dispatch.** Its four conditions are the packet's table of contents.
- **Default to the lane that costs the main session the least context**, and fall back on a signal rather than a feeling.
- **Enforce the brief and the report at dispatch time.** A cold agent doing competent work against wrong assumptions is a silent quality drop nothing else catches.
- **If nobody uses the door, put a hook on it.**
