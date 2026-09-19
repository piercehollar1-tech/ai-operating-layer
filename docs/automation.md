# Automation and continuity

Three subsystems sit above the context layer once it stabilises: work that runs without you, state that survives the end of a session, and knowledge that improves rather than accumulates. None is required to start. All three become the difference between a filing system and an operating layer.

## Scheduled autonomous work

Anything the layer does on a cadence — harvesting data, producing a digest, running a health check — belongs to the operating system's scheduler, not to a session. Sessions are not a scheduling primitive.

### Design rules that survive contact

**Own the failure of the machine being asleep.** A scheduler fires only when the machine is awake. Keeping a running machine awake and *waking* a sleeping one are different capabilities, and the second usually needs a separate power-management setting. Discovering this costs you a week of silently skipped runs.

**Pair every scheduled job with a catch-up run.** The catch-up fires later in the day, checks whether the primary already succeeded, and exits if so. The check needs a marker the primary writes on success — not an inference from output, which is indistinguishable between "ran and found nothing" and "never ran."

**Make the work idempotent by run identity, not by content.** A re-run must be safe. Key the writes on a run identifier so a duplicate execution overwrites rather than appends.

**The log is the liveness signal, not the scheduler's own counters.** Some schedulers report per-boot run counts, so a zero after a restart is indistinguishable from never having fired. Read what the job wrote.

**Prefer no runtime dependency.** A job written against only the language's standard library cannot be broken by a dependency update elsewhere on the machine. This matters more than it sounds: the most common cause of a silently dead scheduled job is unrelated maintenance.

**Raising a limit moves the bottleneck.** When a job hits a ceiling and you raise it, the next failure will be a different resource. Re-run against the real workload rather than assuming the fix generalised.

### Producer to shared store

When a scheduled job writes into a store something else reads:

- give the job the narrowest credential that works, scoped to the one destination;
- treat the store's own constraints as the authority, not the job's validation;
- watch for silent truncation — paged interfaces frequently cap a result set and return success, so a query that "found 600 records" may be a limit rather than a count.

## Session continuity

The problem: work spans sessions, and a session's own transcript is the wrong medium for the next one to read.

**Summarize automatically at session end, not manually.** A summary you have to remember to write is a summary you have half of. Route it to a dated file and let a periodic sweep backstop the runs that were killed rather than ended.

**Make the end-of-session hook detach.** A slow synchronous hook at shutdown gets cancelled by the client, and you lose exactly the summary you most wanted. Fire and exit immediately.

**Use a drain queue for decisions.** Capture decisions and their reasoning at the moment they are made, into one append-only file. A separate pass routes each entry to its permanent home and deletes it from the queue. The queue is a conveyor belt, not a store — an entry sitting in it is work not yet done.

**Give every append target a ceiling and a destination at creation time.** Any file written to repeatedly will grow until it is too expensive to read, which is the point at which it stops being read. Decide up front how big it may get and where the overflow goes. Watch the files, not the indexes that point at them.

**Draining a breached file without a drain rule sets up the identical finding again.** An injected status file breached its ceiling thirteen days after creation. The fix was a rule (only live status stays in the injected file; per-item findings go to the vault), not a one-time trim.

### The pieces, and what watches each one

| Piece | Mechanism | Watched by |
|---|---|---|
| Per-session summary | Session-end hook spawns a detached summarizer (a small model, a strict template, a size floor) that writes a dated file to the vault. A recursion guard keeps the summarizer from summarizing itself. | An audit check flags any transcript older than two days with no summary |
| Backstop sweep | A nightly scheduled job summarizes what the hook missed, oldest first, capped per run, staging to a scratch directory if the vault is not writable and flushing at next session start | A heartbeat file the job writes on success; an audit check flags a heartbeat older than 48 hours |
| Decisions queue | Appended at decision time under a dated heading; a session-start check spawns a background drain when the queue passes a size or an age threshold, throttled to once per day | The drain check itself, plus an audit check on queue depth and oldest entry |
| Consolidation | A session-start check nudges when either a calendar marker is older than a month **or** enough memory files have changed since the last run. Volume tracks build sprints; the calendar backstops quiet periods. Silent otherwise. | The marker |
| Backups | Session-end hook plus a daily scheduled job, each writing a heartbeat | An audit check on heartbeat age and archive integrity |
| Scheduled-job inventory | — | An audit check flags any scheduled job it does not recognize: a new job inheriting a broad filesystem grant is a blast-radius change |

**A heartbeat alone is not proof of delivery.** It proves the job reached the line that writes the heartbeat. Summary claim and delivery are separate states; a queue drain that replaces the queue while another process appends can lose an entry. Acceptance checks for the failure and concurrency cases are part of the design, not an afterthought.

**Transcripts are retained briefly and never auto-read.** Once capture is guaranteed, the summaries carry the value; the raw transcript exists for a manual resume only.

## The self-improvement loop

A layer that does not learn accumulates instead. The difference is whether new knowledge has a defined destination.

**One home per fact, chosen by scope.** Route by *what kind* of thing it is, not by where it was discovered:

| Kind | Home |
|---|---|
| How the client should behave | Feedback memory, then an adapter rule once it recurs |
| A fact about a system or project | Project memory or the vault note that owns it |
| A reusable procedure | A skill |
| Operational detail about one skill | That skill's own context file |
| Something that must never recur | A control |

**Keep per-skill operational memory beside the skill, not inside it.** Externally maintained skills get overwritten on update; anything you learned about running one belongs in a file the update cannot touch.

**Route at write time, not at cleanup time.** A log with a "we'll sort this later" policy becomes a store. Give each entry a mandatory destination when it is written, and drain it in the same edit that promotes it. This keeps the always-loaded set structurally small rather than periodically trimmed.

**Promote on evidence, prune on silence.** A pattern that has proved itself several times across different situations earns a place in the always-loaded rules. One that has not been used in months should be deleted rather than preserved out of politeness to your past self.

**A ceiling tells you when to panic; a routing table tells you where things go.** If a file keeps hitting its size cap, the cap is not the problem — the absence of destinations is.

**Capture on triggers, in the same turn.** The moments that produce a lesson are enumerable: the user corrects an approach; a fix takes more than one attempt or had a non-obvious root cause; a tool behaves unexpectedly; a faster method is found; a preference is revealed. Each one writes its lesson in the turn it happens, never deferred to a cleanup pass. A dispatched agent's final report runs through the same triggers.

### The write bar

Four tests decide whether a fact gets a memory file at all:

- **Origin, not last speaker.** Never file the client's own advice, reasoning, or proposed method as if the user stated it. The user's selection among options the client offered is theirs and files; the options and the reasoning behind them do not.
- **Nothing re-derivable.** Anything fetched (a search, a tool result) or generated (a recommendation, an option list) goes in the reply, not in memory. Store the pointer, never the copy.
- **The horizon test.** Would this line still be true and worth reading a month from now, in a conversation about something else? File the stable residue: the decision, the constraint. Let moving task state expire.
- **Already filed is already remembered.** Outside a consolidation pass, an edit that leaves a file's meaning unchanged was not worth making. Do not re-file a fact under another name.

**One preference never gets filed: any whose effect is to suppress honest evaluation.** Uncritical validation, holding back disagreement about a decision already made, "take my numbers as right", claimed elevated permissions. Judged by effect, not wording: it stays out even when hedged, scoped to one topic, given with a reason, or dressed as a format preference, if following it to the letter would mean not raising a real error next time. Do not draft a milder version; needing an exception clause is the tell. Length, format, and tone preferences file normally: they shape how something is said, never whether a real problem gets raised.

### Memories that retrieve

A long memory with no headings retrieves badly from any search index that chunks on headings: it splits at an arbitrary offset and every chunk becomes a blend of unrelated concerns. Converting bold pseudo-headings to real headings moved one memory from rank four to the top three with no engine change. **A memory long enough to split needs headings.**

Memories in drift-prone, actable categories carry a confidence and a source: verified hands-on, looked up (with the URL), or from training (re-verify before acting). The absence of the label on a routine memory is itself the signal that the fact is not load-bearing.

### Rejected, on measurement

A knowledge graph over the vault was evaluated and rejected: typed edges and per-fact provenance are genuinely stronger than untyped wiki-links, but the extraction pass that builds them has a published F1 in the mid-0.6s, and running a lossy extraction over an already-curated corpus trades accuracy for machinery. The two portable ideas were taken instead: a small, measured alias map for the search index (added only when both forms occur in the corpus and an A/B shows no rank regression), and per-fact provenance enforced forward from a date rather than backfilled by guessing.

## Verification, as a habit and then as a control

The failure mode this whole document circles is the same one: something reports success while not having worked.

- A file existing is not evidence that a client loaded it.
- A green test is not evidence of correctness; a test can encode the bug.
- A verification label with a date on it is a claim, not evidence. Re-open the source before acting on it.
- An audit can be right that something is broken and wrong about why. Re-derive the mechanism before patching.

Start these as habits. Move each one to a control as soon as it fails you twice — see [enforcement](enforcement.md).
