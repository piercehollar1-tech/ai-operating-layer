---
skill: example-workflow
lessons: lesson-verify-before-claiming, lesson-scope-before-plan
updated: 2026-01-01
---

# example-workflow — operational context

This file is fictional. It shows the shape of a per-skill context file: the operational memory
that a preflight hook injects when the skill is invoked. It is separate from `SKILL.md` because
an externally maintained skill is overwritten on update, and because a cold subagent reads only
`SKILL.md` — anything a dispatched agent must know belongs there, not here.

Durable rules sit at the top. Past a size threshold this file arrives as headings plus a read
order, so the first screen has to carry the rules that matter.

## Rules (read first)

- Stage 1 stops for approval even when the scope looks obvious. Two of the three past runs that
  skipped the stop had to be re-scoped.
- The plan artifact names a rollback for every consequential step, or the approver sends it back.
- Verify the downstream result, not the command's exit code.

## Effective settings

- Scope artifact: `Projects/<project>/scope.md`, under 60 lines.
- Plan artifact: `Projects/<project>/plan.md`, ordered, one validation per step.

## Gotchas

- The example system's dry-run flag reports success on an empty target set. Confirm the target
  count before reading the dry run as evidence.

## Applied

Append the date each time a rule above changed what was done. Three or more across different
situations promotes the rule to the adapter; none in sixty days prunes it.

applied: 2026-01-01
