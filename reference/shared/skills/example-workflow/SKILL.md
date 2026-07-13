---
name: example-workflow
description: Plan and execute a fictional migration through explicit review gates.
---

# Example workflow

Use this skill only as a structural example. It does not operate external systems.

## Inputs

- Desired outcome
- In-scope systems
- Constraints
- Named approver

## Stage 1: Scope

1. Restate the outcome and exclusions.
2. Identify unknowns and risks.
3. Write a scope artifact.
4. Stop for human approval.

Do not begin execution from an unapproved scope.

## Stage 2: Plan

1. Convert the approved scope into ordered, reversible steps.
2. Define validation and rollback for each consequential step.
3. Write a plan artifact.
4. Stop for human approval.

## Stage 3: Execute and verify

1. Perform only the approved steps.
2. Record deviations and stop when they materially change scope.
3. Verify the user-visible outcome, not only command success.
4. Write a concise handoff and route durable decisions to the project note.

## Safety boundary

Never treat this example as authorization to access credentials, production systems, or external accounts.
