# Skills and context delivery

A lesson written to a memory file is not a lesson the client will apply. A per-skill notes file the adapter says to "read before invoking" is not a file anyone reads. This document covers the layer that delivers context mechanically, at the moment it applies, and the audit checks that keep the delivery from rotting.

The rule behind it: **written down is not wired up.**

## The measurement

A memory store with zero index drift and 176 lesson files had `applied:` evidence on 22 of them. Nothing loaded a lesson at the moment it applied; recall depended on an on-demand search, a one-line index entry, or remembering. The per-skill context directory had the same shape: a rule in the adapter since it was created, and no loader at all.

## Three delivery mechanisms

### 1. Skill preflight

A post-tool hook on skill invocation injects, once per skill per session:

- the skill's operational context file, verbatim when it is small, otherwise its headings plus a read order; and
- every lesson bound to that skill.

**Resolution is by filename.** A skill named `foo` receives `skill-notes/foo.md`. A skill whose context lives under another name receives nothing, silently, so a skill must declare any other file with a `context:` key in its frontmatter (comma-separated when an orchestrator needs several). An audit check flags a skill that names a context file in its body but has none of its own.

**A lesson is bound two ways.** Declared: a `lessons:` frontmatter line in the skill's context file or its `SKILL.md`, listing lesson slugs (an audit check verifies each slug resolves). Discovered: any memory whose text names the skill, which is free and cannot go stale. The hook injects the union.

**Large context files must put durable rules at the top.** Over a size threshold the file arrives as headings and a read order, so the rules that matter live in the first screen.

**`SKILL.md` loads for cold subagents; the context file never does.** Anything a dispatched agent must know belongs in `SKILL.md`. The context file is the main session's operational memory for that skill.

### 2. Route nudges

A pre-tool hook reads a small routing table and fires the adapter's routing pointers at the tool call: "for this class of fetch, the `web-retrieval` skill owns the access ladder"; "before this design edit, the design pipeline runs first". Thresholds keep one-off calls silent. The hook adds context only; it never blocks.

The routing table declares, per route: the tool matcher, the skill or document that owns the task, the threshold, and the message. An audit check confirms each route names a skill that exists and a tool reachable from the client's hook matcher.

### 3. The skill index

Every skill description costs context every session, and routing quality degrades past a hundred-odd skills, proven by two prunes. So the instruction files do not list skills. A generated index groups them into a dozen use-case categories, rebuilt in the background at session start only when the skills directory changed, and the rule is to read only the matching category. New skills auto-categorize by name pattern; unmatched ones land in an "Uncategorized" bucket so nothing goes invisible.

Skills must be `dir/SKILL.md`. A flat `.md` in the skills directory silently never registers. Verify an install by seeing the skill listed, not by seeing the file on disk.

## Per-skill operational memory

Externally maintained skills are overwritten on update. Anything learned about running one, from effective settings and prompt patterns to gotchas and the user's preferences, belongs in a side file the update cannot touch. That side file is what the preflight hook delivers.

Where an improvement lands depends on the skill's origin: a locally owned skill takes the edit in its `SKILL.md`; a plugin-managed skill takes it in the side file only. Each owned skill carries an `## Improve this skill` footer; the rule is to propose the edit, never silently rewrite.

## Evidence-based promotion and pruning

Each lesson file carries an `applied:` frontmatter line. Each time the lesson actually changes what the client does, that day's date is appended. The audit sentinel then reads the line rather than anyone's memory of usefulness:

| Evidence | Action |
|---|---|
| Applied three or more times across different situations | Promote to an always-loaded adapter rule (stamp `promoted:`) |
| Zero applications in sixty days | Prune |
| Wrong or superseded | Delete the file and its index line |

The stamp is still a manual act, but the preflight hook surfaces the reminder next to the lesson at the moment it is being applied, which is the first place that ask has landed anywhere near the action. If coverage stays near zero after that, the stamp needs a mechanism too, not more prose.

## The "where does this go" router

Every persistent instruction has exactly one correct layer. The adapter carries the table so the choice is made at write time:

| The thing | Its layer |
|---|---|
| Always-true fact or irreversible rule | The adapter (kept short; a hard line count) |
| On-demand how-to or procedure | A skill (its body loads only when invoked) |
| Repeated user-invoked action | A slash command |
| Work that should stay out of the main context | A subagent |
| Something that must be mechanically enforced | A hook |
| Cross-session fact | File memory or the vault |

If it only matters sometimes, it does not belong in the always-loaded adapter.

## Audit checks that keep this from rotting

All of these were negative-tested by breaking them on purpose before they were trusted; a check that has never gone red is not known to work.

- declared lesson slugs resolve to files;
- the routing table is valid, each route's skill exists, and its tools are reachable from the hook matcher;
- both delivery hooks are registered and executable;
- no stale backup twins of hook files sit beside the live ones;
- every owned skill has its improvement footer;
- the skill index header count matches the live skill directory.

## What transfers

- **Deliver at the call, not at session start.** Context injected when a tool runs is read; context loaded at startup is scrolled past.
- **Resolve by convention and require declaration for the exception.** Silent misses are the failure mode; make the exception loud.
- **Count applications, then promote or prune.** A lesson's usefulness is measured, not remembered.
- **Keep the always-loaded set structurally small** with a router table, not a periodic trim.
