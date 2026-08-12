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
