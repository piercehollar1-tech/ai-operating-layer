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

The blindness runs the other way too. **The model cannot observe a permission prompt.** An approved prompt and an auto-allowed call return the same result; only a denial is visible. So the model's claim that "no prompt appeared" is not evidence. When the question is whether a human was asked, the user's terminal is the authority, or the permission rules read from the settings file.

## Hook mechanics that change the design

**Hooks for one event run together, not in order.** In at least one major client, every matching hook for an event runs in parallel, and the position of a hook in the settings file conveys nothing. For a pre-tool permission decision the most restrictive answer wins (deny, then defer, then ask, then allow); added context from every hook is kept. Consequences: a hook cannot rely on another hook for the same event having run first (a session-end commit cannot see the summary a sibling hook is still writing), and no two hooks should rewrite the same tool's input, because the last to finish wins. Check your client's documentation for its own rule.

**A stop hook fires after the reply has streamed.** Blocking cannot unsend it; it appends a retry and pays for the whole context again. Stop hooks are where you measure and record. Anything about the text itself belongs in the system prompt. See [response contract](response-contract.md).

**A model-evaluated hook on user input has no safe failure mode.** A hook that asks a small model to classify each message, and to return an empty result for follow-ups, was answered with a sentence explaining why a message was a follow-up. The client treated that prose as a block reason, and the user's next five messages, including "what happened?", were refused. Every other hook can be written to fail open or closed deliberately; this one fails closed on the user whenever the evaluator is chatty. Never register one live. Prove in a headless harness, with the settings passed for that run only, that a follow-up passes and a task fires.

**Treat a path placeholder as text.** Some clients substitute placeholders such as a project directory into a hook command as plain text before running it. In shell form, a folder name containing command syntax becomes a command. Exec form (an executable plus an argument list, no shell) never interprets it. Every hook that is shipped to other machines uses exec form.

**A timeout is a silent kill.** A session-start audit measured at about eleven seconds had a ten-second timeout. It was killed every session before it printed, so its findings never reached anyone, and each kill stranded a scratch file. The fix kept the coverage: the timeout was raised, the scripts trap termination and clean up, and the sentinel now prints the previous run's saved result (marked with its age) and refreshes in the background. A saved result older than two days reports itself as stale; a crash is saved and shown; a lock stops two refreshes at once. Measure every hook's runtime against its timeout, and pin the relationship in a probe.

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

**Every trigger in one reviewable file, and every fire counted.** The routing table holds each route's matcher, threshold, and message, and each fire writes one row to a gate log. A route that delivers its content in full is logged as delivered, not fired, and is never held to a conversion rate: without that distinction, a route working as designed shows up in the audit as ignored. A trigger with no fire log has no denominator, and a gate with no denominator cannot be judged.

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

**Scan staged and untracked files, not just tracked ones.** A leak added in the same shell line as the publication — `add`, `commit`, and `push` chained together — is still untracked when a pre-command hook runs. Ignored files normally cannot ship, so the scan may skip them, but not when the command force-adds (`git add -f` publishes an ignored file). Do not restrict the scan to what the index already knows about.

Both of these are stated as rules because both were discovered by a scan that reported clean while a leak sat inside the tree.

**Scan what the push publishes, not just what is on disk.** A push carries every commit the remote does not have. A leak committed and then deleted in a later commit is gone from the working tree and still in the push; a staged copy can differ from the working copy. Scan the staged index and the added lines of every unpushed commit as well as the files.

**Check the destination the push will use.** A remote's push URL can differ from its fetch URL, and a command can change directory (`cd dir && git push`, `git -C dir push`) before it pushes. Resolve the repository and the push URL from the command itself; anything that cannot be resolved is public.

**Never echo the match.** A report that prints the matched line, or the pattern that matched, copies the protected value into logs and the conversation. Report the file, the line, and a rule number.

Two rounds of outside review found these gaps, and a dozen more, in earlier versions of the example hook in [`reference/hooks/`](../reference/hooks/pre-publish-scan.py.example), each after the hook's own probe suite had passed. Each is now a probe with a matching mutation.

### Two layers, because a command string is not a push

A gate that runs before the agent's shell command sees only the command text. It cannot see a file that an earlier step of the same command will create, and it parses shell with patterns that an alias, a script, or `eval` can slip past. Those limits are structural; more patterns do not close them. So the publication gate has two layers:

1. **The agent-side gate**, before the command runs: cheap, catches the ordinary shapes, and fails closed on what it cannot resolve.
2. **Git's own `pre-push` hook**, which git runs with the exact local and remote refs being pushed, after everything earlier in the command has happened. It scans exactly the commits that are about to leave, whatever command started the push.

A hosting provider's secret scanning, where available, is a third layer after the fact: useful for detection, too late for prevention.

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
