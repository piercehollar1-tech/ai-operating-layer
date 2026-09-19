# Enforcement

A rule written in an instruction file is advice. The client reads it, usually follows it, and occasionally does not — most often when the task is unusual, which is exactly when the rule mattered. An enforcement layer converts the rules you cannot afford to lose into controls that run whether or not anyone remembered them.

This is the part of an operating layer that is hardest to retrofit and easiest to skip, because nothing appears broken while it is missing.

## Instruction versus control

| | Instruction | Control |
|---|---|---|
| Lives in | An adapter or guidance file | A lifecycle hook |
| Enforced by | The model's attention | The runtime |
| Fails when | Context is long, the task is novel, the rule is inconvenient | The hook has a bug |
| Correct for | Preferences, style, routing, defaults | Anything whose failure is expensive or irreversible |

The test for promotion is not importance, it is **recurrence plus cost**. A rule that has been violated once and produced a bad afternoon stays an instruction. A rule whose violation would publish private data, delete unrecoverable work, or spend real money becomes a control the first time you notice it.

## The lifecycle surface

Clients expose hook points at different moments. The names differ per client; the categories do not:

| Moment | What it is good for |
|---|---|
| Session start | Injecting standing context; surfacing drift the user would not otherwise see |
| Before a tool call | Refusing an action; demanding facts before a destructive one |
| After a tool call | Logging, formatting, detecting a bad result the model reported as success |
| After a tool failure | Routing a known failure to its known fix |
| On user input | Reinforcing a contract the model drifts away from as context fills |
| Before compaction | Preserving state that summarization would drop |
| At stop | Refusing to end on an unverified claim |
| Session end | Summarizing, draining queues, backing up |

A mature layer uses most of these. The distribution matters less than the principle: **the highest-value hooks are the ones that block, not the ones that log.**

## Tiers of decision

Not every control blocks the same way. A mature layer has six tiers, and an invariant between two of them:

| Tier | Mechanism | Used for |
|---|---|---|
| **Deny** | Hard block, no approval path | Paths and publishes with no legitimate case: credential reads, a public push carrying private data |
| **Deny, then retry** | Denies once with a demand for facts; allows a byte-identical retry | Destructive operations: the model must state what is deleted and what the rollback is before the command runs. Any edit to the command, even a changed label, is a new string and re-blocks. |
| **Deny first, then allow** | Denies the first occurrence in a session; the identical retry passes | Making a documented option the door: the first subagent dispatch is denied unless the delegation gate ran |
| **Ask** | A permission prompt to the user | Judgment calls the user should make: a commit without review, a production deploy, schema changes, an edit that would put client data in a shared store |
| **Deny, then cooldown** | Denies once past a threshold, resets counters, goes quiet for a period | Steering without trapping: pushing symbol search over whole-file reads |
| **Nudge** | Added context only, never a decision | Routing pointers fired at the tool call |

**Invariant: anything the deny-then-retry tier blocks, the ask tier must also prompt on.** The retry tier allows the second identical attempt, so a command that denies but never asks would run with no human in the loop. Enforce the invariant with a probe suite, not a shared pattern file; sharing one collapses the two tiers into one.

## Say it through the channel each party can see

Clients deliver a permission prompt's reason to the user, not to the model. An instruction to the model placed in an `ask` reason is never seen by the model; the user gets two buttons, neither of which runs a skill. A gate that fired ten times and converted zero was built exactly this way, and the fix was not tuning: the gate now says it twice, the reason to the user in the prompt and the same fact to the model as added context, phrased as an action. Confirm delivery live after any client update; the field that carries context to the model has changed shape before.

## What a mature layer actually runs

Roughly fifty hook registrations across the surface above, in one installation. The inventory, generalized, so the categories are visible without the names:

| Moment | Blocking | Non-blocking |
|---|---|---|
| Session start | — | Project bootstrap · skill-index rebuild · consolidation-due and drain-due checks · audit sentinel · last-log recap · staged-summary flush |
| Before a tool call | Credential guard · client-data gate on shared-store writes · destructive-command gate · intake gate on first-time installs · publication gate · deploy gate · schema-change gate · config-lint gate · review gate at commit and push · dispatch-contract gate · delegate-first gate · self-protect on the layer's own files | Symbol-search steer · route nudges |
| After a tool call | — | Skill usage log · skill preflight injection · injection scan on every fetch · formatters · edit accumulator for the hooks directory |
| After a tool failure | — | Known-failure router |
| On user input | — | Verbosity scoreboard · delegate nudge |
| Before compaction | — | State preservation |
| At stop | Citation gate · probe-suite runner on a red suite | Response-length measurement · detached summarizers |
| Session end | — | Detached backup · transcript summary · vault commit |

**The layer guards itself.** An edit to the client settings, the adapter, or any hook file prompts. Without that, the cheapest way past every control is to edit the control.

## Categories that earn their place

**Refuse the irreversible.** A gate on destructive commands that demands the facts — what exactly is being deleted, what the rollback is — before the command runs. The value is not the refusal; it is that stating the blast radius out loud catches the cases where it is larger than assumed.

**Protect credentials from your own tooling.** A hook that blocks reads of credential paths and env dumps. The threat is not only a malicious instruction; it is a well-meaning agent grepping broadly and putting a secret into a transcript.

**Gate publication.** Anything crossing from private to public — a push, a repo made public, a release, an upload — scanned before it goes. See the worked example below, because this one has a subtlety that defeats the obvious implementation.

**Verify before asserting.** A stop-hook that refuses an answer citing sources nobody retrieved this session. Models produce plausible URLs; a control that fails the answer rather than the citation is the only reliable fix.

**Enforce the contract on dispatch.** If subagents start cold, a hook that rejects a dispatch missing its context brief prevents the silent quality drop where an agent does competent work against the wrong assumptions.

**Surface drift on a schedule.** A cheap session-start check for broken pointers, orphaned files, oversized append targets, and stale indexes. Drift is invisible per-session and obvious per-quarter.

## Two properties every control needs

### Fail closed

When a control cannot evaluate its condition, it must block, not allow. A publication gate that cannot determine whether the destination is public should treat it as public. The cost of a false block is a moment of friction; the cost of a false allow is the thing the control exists to prevent.

### Prove it by breaking it

**A control is unproven until it has been observed failing on purpose.** Reading the code is not verification, and neither is a green run — a hook with an inverted condition passes every test where nothing is wrong.

For each control, construct the input it exists to catch and confirm it blocks:

```text
manifest with an unknown key            -> blocked
value outside its allowed range         -> blocked
string where an integer is required     -> blocked
boolean where an integer is required    -> blocked   (in Python, bool is an int)
forbidden string in generated output    -> blocked
external reference in generated output  -> blocked
```

That fourth line is a real bug caught this way. `isinstance(True, int)` is `True` in Python, so a type check that looks correct accepts a boolean silently.

Keep those cases beside the hook as a probe suite, declare which hooks each suite covers, and have a Stop hook run every suite after any edit under the hooks directory. The rules that keep that runner from becoming a trap, and the mutation discipline that proves a suite is checking rather than agreeing, are in [verification](verification.md).

### A hook has two gates

The matcher in the client settings decides whether the hook process runs at all; the tool check inside the script decides whether it does anything. They drift apart silently. Widening one without the other is a no-op that reads as a fix. Test through the exact settings command strings, never the script alone.

### Gates regex the whole command, prose included

A destructive-command gate that inspects the entire command string also inspects the body of any file written by a shell heredoc. Documentation about deleting things trips the gate on its own prose. Write file content with the client's file tools, not with heredocs, and keep one gated operation per turn in its own call.

## Worked example: the publication gate

The obvious design is a denylist — scan outgoing content for your home path, your email addresses, your private project names, your city — and block on a match.

**On a public repository, that design publishes exactly what it protects.** The denylist file is content. Committing it ships the list of strings you consider sensitive, which is strictly worse than shipping any single one of them.

There are three ways out, in increasing order of quality:

1. **Keep the denylist outside the published tree**, in the private config directory. Correct, and sufficient for a scanner that runs locally.
2. **Store hashes rather than terms.** Works, and awkward to maintain.
3. **Invert to an allowlist.** For generated output, assert that every string present is one you intended to publish — a member of a fixed vocabulary or a value from a validated data file. Anything else fails.

The allowlist is strictly stronger, and the reason is not subtle: **a denylist only catches leaks somebody predicted.** The leak that hurts is the one nobody enumerated. An allowlist fails on unknown content by construction.

### Two implementation details that decide whether it works

**Scan the whole tree, with nothing excluded.** An exclusion added to reduce noise is precisely where unreviewed content accumulates. If a scan skips a documentation directory, then a document is the thing that leaks. Tolerate the false positives and read them.

**Scan staged and untracked files, not just tracked ones.** A leak added in the same shell line as the publication — `add`, `commit`, and `push` chained together — is still untracked when a pre-command hook runs. Honour the ignore file, since ignored content cannot ship, but do not restrict the scan to what the index already knows about.

Both of these are stated as rules because both were discovered by a scan that reported clean while a leak sat inside the tree.

### Tuning versus excluding

A strict gate produces false positives. There is an important difference between two responses:

- **Tuning a pattern** that was written too broadly — for example, matching a documented public install path when what you meant was your absolute home directory — is legitimate maintenance. Narrow the pattern and re-run the full test suite.
- **Excluding a path** from the scan is how the original failure happens. It converts an alarm into silence.

Write the reasoning into the pattern file itself, next to the pattern. Otherwise a future session sees an oddly specific rule and simplifies it back.

## Promotion path

Learning that arrives from a mistake should end up in exactly one place:

```text
one-off surprise                    -> a note
recurring correction                -> an instruction in the adapter
expensive or irreversible failure   -> a control
```

The last arrow is the one people skip. A rule that has been re-explained three times is not a documentation problem; it is a missing hook.

When a control is added, record what incident produced it. A hook whose motivation is undocumented gets weakened by the next person who finds it inconvenient — including you, in six months, with less context than you have now.
