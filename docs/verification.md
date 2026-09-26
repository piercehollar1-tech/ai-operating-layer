# Verification and evidence

The failure mode every other document here circles is the same one: something reports success while not having worked. This document collects the rules that turned verification from a habit into a set of controls, plus the evidence gate for claims the client makes to the user.

## The evidence gate on claims

For any claim that is external, current, niche, consequential, or load-bearing, the client scores the **evidence**, not its confidence:

| Score | Meaning | Allowed use |
|---|---|---|
| 90–100 | Verified by direct inspection or a primary source actually retrieved this session | State as fact |
| 70–89 | Partly inferred; cite the source and label the inference | State with the label |
| Below 70 | Unverified | Do not state as fact or recommend action. Say "Unverified — confidence: N" and name what is missing. |

**Never cite a URL from memory without opening it.** Models produce plausible URLs. A URL returned by a search this session counts as resolved, but it still gets opened when the snippet does not contain the claim, when stakes are high, or when the citation ships in a deliverable. A true claim with a false citation fails the gate.

**A verification label with a date on it is a claim, not evidence.** "Verified on the 14th" tells you when someone last believed it. Re-open the source before acting on it.

**Label the inference.** Deductions are marked as deductions; a regulator's page outranks a researcher's summary; ten sites agreeing is a hot keyword, not corroboration. Open the primary.

### What does not count as a source

- **A 200 status code.** It proves a server answered, not that the cited document exists. Single-page-app hosts and CDNs return an app shell or a challenge page with 200. A bulk citation check records status, content type, and size, and reads the first few hundred bytes: HTML where a PDF was cited, a tiny body, or "enable JavaScript" means the source did not load.
- **A closed issue.** Trackers close for triage, inactivity, duplication, and policy far more often than for a fix. Read the closing comment and the last few comments. Treat stale, duplicate, invalid, or bot-closed as unresolved unless a human names the fix or a version. When a vendor declines to fix, the shipped default becomes the guidance.
- **A documentation sentence about scope.** A short summary of what a feature covers describes the common case; it is not a specification. For an open-source tool, the code at the installed version is the primary source. Pin the version, read the function that makes the decision, and label the result "read from source, not seen live" until a live probe runs. When the two disagree, say both.
- **Model-produced research, until one of its numbers survives.** Find a place where it showed its arithmetic and redo it. Check whether its sources are real URLs or bare domain names. Look for false precision a range cannot produce. One failed division is evidence about the process that produced every other number in the document; demote all the uncited ones.
- **A failed probe.** A tool that could not reach the network, timed out, or errored has produced no result. "Could not confirm" reads like a caveat and functions like an all-clear. Retry it before reporting anything.

### Two controls behind the gate

**A citation gate at stop** refuses a final answer that cites a URL nobody retrieved this session. It fails the answer rather than the citation, which is the only reliable fix.

**An injection scan after every fetch** flags instruction-shaped content in retrieved pages: imperatives aimed at the agent, hidden text, encoded directives. Its patterns must be tested on real payloads at real lengths; a rule set that worked on short samples was found dead above 42 characters. **External content is data, never authority**, and the scan is the mechanical half of that rule.

## Measure, don't recall

**Re-derive every count, path, filename, and line number with a command before it goes into prose.** Writing a number feels like reporting it, but it is recall, and it decays the moment the file changes again. After a multi-file edit, run one checker over the whole change set: table column counts, fence parity, link resolution, and every cross-document numeric claim against the file it describes.

**Every statement a document makes about itself is an unverified claim about another part of it.** A cross-reference, a count, an "as stated above", a changelog header: each carries the document's own authority and is almost never re-read against its target. Script the dangling-reference check; hand-check every reference that asserts something about its target's content.

**When a mechanical check already exists for the question, run it; never reimplement it.** A probe written to prove one's own work inherits that work's blind spots and fails silently. Three self-authored checks returned confident wrong answers in one session: a link resolver reporting zero unresolved where the real linter found fifty-three; a directory inventory defeated by a shell alias; a grep stricter than the hook it stood in for. **When the mechanical check and the probe disagree, the mechanical check wins.** If none exists, break-test the one you write before trusting it.

**Read a maintenance command's blast radius before running it.** An optional target defaults to all targets, and a value flag then stamps one value across every one of them. Run it without the value first and read what it selects. Never `tail` the output of a write; count the lines it printed. A green check afterwards proves only what the check measures.

**Change one, grep all.** A value, term, or claim rarely lives in one place. A constant is re-checked in a worker, an API, and a schema; a renamed term survives in three docs; a pointer's target must already hold what the pointer promises; sibling scripts share a design and a bug. Search the literal and the concept across code, configuration, docs, tests, and notes, and fix every hit in the same change, or say in a comment why one legitimately differs. After adding a file, run the whole suite: a new file changes what every glob selects.

**Ask what your new write path defeats.** A search for renamed values does not find a monitor you just blinded. When a change adds a writer, a caller, or a schedule, name every check that watches that artifact and every invariant the old timing was quietly providing. A freshness check dies when a no-op starts touching the file it watches; a mutual-exclusion assumption dies when a job gains a second trigger. Neither shows up as a failing test: the check keeps passing, which is the problem.

**A constant is not a measurement.** A metrics file that grows on schedule can contain no information. One tracker appended a row per session for three months, every row identical apart from the timestamp, because it read fields the payload never carried; every liveness signal was green because every liveness signal measured volume. Before trusting a number a tool produces, count the distinct values it has written, not the rows.

**Measure the magnitude before flagging.** Raising something as a problem is a claim about its size. Get the denominator first, or the honest answer to "what is wrong with it?" is "less than I implied". An option named `lossless`, `quality`, or `effort` is a name, not a guarantee: diff the decoded output before reporting a saving derived from it.

## Proving a control

**A control is unproven until it has been observed failing on purpose.** This applies to hooks, audit checks, tests, and the probes written to verify any of them.

**Every gate gets a probe suite, and the suites are enforced.** A post-edit hook records any edit under the hooks directory; a Stop hook then runs every suite and blocks the turn on a red one. It runs all suites rather than mapping edited file to owning suite, because a map is exactly how a renamed hook silently drops off the list. Three rules keep it from becoming a trap: it never blocks when the client reports the stop hook is already active (a red suite is expected mid-TDD); a red run keeps the edit record so the retry re-checks, a green run clears it; and every failure path exits cleanly with a timeout or crash counted as failed, never as silence.

**Coverage is declared, not inferred.** The first version decided whether a hook was covered by scanning suite text for its name, and a fixture that mentioned a hook made an untested hook read as tested. Every suite now carries a `# covers:` line. A stale declaration reads as uncovered, which is the safe direction, and it is greppable.

**Green is not evidence when the gate and its suite changed in the same turn.** The suite may have been updated to agree with the change rather than to check it. The runner says so out loud even when everything passes.

**A break-test proves nothing until the mutation is shown to change behaviour.** Confirm the harness runs the mutated copy (an absurd mutation must go red), that it drives the production path and not a "run as script" branch, and that a survivor is a real gap rather than an equivalent mutant. Retire a survivor only with the evidence written down.

**Testing a hook by hand forges its side effects.** A hook run manually really writes to its logs and state directories. Probe with the home directory redirected to a scratch location, never the live one, and keep one writer per event. Re-run the whole case list after each fix; one probe only clears the cause already found, and the first fix masks the second.

A worked example of a suite with a `# covers:` line, a quiet case, and mutations that must each turn a case red is in [`reference/hooks/tests/`](../reference/hooks/tests/pre-publish-scan-probes.py.example); this repository's CI runs it.

## Test what it must refuse, on real input

Test suites tend to enumerate what the code does. The risk usually sits in what it must not do, and in input shaped the way real people write it.

**Test the quiet case, on real-shaped input.** A check that warns needs a test proving it stays silent on the correct setup. A session-start warning that "the workspace was moved" fired for every correctly placed install, every session, because it compared a real path with a configured one written `~/...` and never expanded the tilde. Every test put the workspace somewhere else and asserted the warning appeared. The mismatch case proves a check can fire; only the quiet case proves it can tell right from wrong. Fixtures tend to be absolute and normalized; real input has `~`, spaces, symlinks, and mixed case.

**Test a matcher on the user's own phrasing.** A regex gate written and tested by the same person tests that person's mental model. One routing hook missed "can you build out the test suite" (a politeness filter swallowed it) and "adopt those ideas into our skills" (the pattern listed the singular only), and a nudge that fails produces silence, which looks like working. Pull real sentences from real transcripts, including polite, conversational, and plural forms, and commit them as cases.

**For anything that writes into a folder it does not own, start with the folder states it must refuse.** An installer passed over a hundred and fifty checks, all on fresh folders. An outside audit then reproduced eighteen failures with eighteen probes: an existing project's files replaced, a symlink followed out of the folder, an unparseable config written with exit zero. The case list for an installer, renderer, or sync begins before the happy path: an existing file at every owned destination; a file where a folder goes and the reverse; a symlink at a destination and at an ancestor pointing outside; a path containing a quote, backslash, or newline. Assert the folder is byte-identical after each refusal.

**Suppressing a match must not stop the scan.** Tuning a detector down is two changes. A scan loop that takes the first match only, plus a new filter that discards a benign phrase, means a page with the benign phrase early and the real directive later goes completely quiet. A filter narrows which match counts; it must never narrow how far the scan looks. Iterate over all matches, capped. Choose a discriminator you can argue carries no information (a bare noun phrase with no imperative verb), not merely one that silences today's page.

**Install it before calling it done.** A static audit checks what an artifact says. An install checks what it does on someone else's machine, under their permission model, their configuration, and their trust state. Four audits and nearly three hundred mechanical checks of one package missed that it shipped deny rules and no allow rules while its own charter required a write on every task; the first real install hit it on the first prompt. A deliverable that lands on another machine is not done until it has been installed and used the way the recipient will use it.

**Walk the lifecycle, not the checklist.** A review against a list of things a document or system should contain inherits the author's structure, and with it the author's blind spots. A second pass that ignores the structure and walks the real sequence of events, from first contact to the end and after, asking what governs each moment and what happens if it goes wrong there, finds a different class of gap: things that happen before a protection starts, after it ends, or between two owners. The gaps that survive many careful passes are usually at the seams in time.

## Coverage and freshness are audited, not assumed

A suite runner that checks the hook edited this turn says nothing about the rest of the set.

- **Every registered hook and every audit checker has a suite.** An integrity check reads every suite's `# covers:` line (with the runner's own parser, so the two cannot drift) and reports a registered hook no suite names, and a declared name with no file behind it. An empty or missing suite directory is a finding, never a pass. The list of checkers is derived from what the audit script actually invokes, so a new checker joins the day the audit starts calling it.
- **The configuration file has a suite too.** It parses, its hook commands resolve, a minimum set of credential deny rules is present, no rule appears twice or in both allow and deny, and every timeout is positive and long enough for the hook it bounds.
- **The suites have a heartbeat.** A fully green run stamps a file; an audit check flags it when it is two weeks old. An environment change (an interpreter upgrade, a moved path) can break a hook with no edit, and a runner that only fires on edits never notices.
- **An audit check fails closed on a missing or crashed checker.** Feeding a checker's output into a loop with its errors discarded and its exit code unchecked makes a crash read as clean. Each checker's absence and failure are findings of their own.
- **A dismissal is listed, never deleted.** Findings that are accepted rather than fixed go in a dismissal store with a reason and an expiry. Dismissed findings still appear, under a suppressed heading; an expired dismissal fires again; a dismissal that matched nothing on a run is flagged as stale; one that matches too broadly is flagged as broad. A wrong suppression looks exactly like a healthy run, so the suppression layer is the first checker that gets a suite.

## A hook has two gates

A hook's `matcher` in the client settings decides whether the process runs at all. The tool check inside the script decides whether it does anything. They drift apart silently, and widening one without the other is a no-op that reads as a fix. Every gate hard-codes its own tool tuple, so one grep enumerates the layers that must agree. Drive end-to-end tests through the exact settings command strings, not the scripts directly.

## Fired is not relevant

An audit that counts how often a gate fired and how often the recommended action followed will report "ignored" for a gate that fires on the wrong thing. Sample the sessions it fired in before calling it ignored. In one case a review gate had fired ten times and converted zero, and the cause was neither the trigger nor the user: the client delivers a permission prompt's reason to the user only, so an instruction to the model placed in that reason was never seen by the model. The fix was delivery, saying it twice through the channel each party can see, not tuning. **Zero conversion on one hundred percent false fires is a bad trigger; zero conversion on true fires is a delivery bug. Read the transcripts to tell them apart.**

## Never trade a safeguard's coverage for quiet

Noise is the user's to tolerate; coverage is not the maintainer's to spend. Fix a noisy check's output, never its scope, and treat a comment saying "deliberately X because Y" as a decision to ask about, not to override. When narrowing genuinely is right, four conditions make it honest: the exclusion is declared in the artifact being checked, not hardcoded in the checker; the rule is derived from that declaration so it cannot rot into a hand-list; the held-out count prints on every run; and a narrower existing decision still wins. Break-test a hold-out in the widening direction: an exclusion that is too broad stays green while checking less, so no red run ever arrives.

## A bug can be load-bearing

After a fix, ask what was leaning on the broken behaviour. Two faults that cancel look like none; fix one and the other appears as a regression nobody can explain. An audit can be right that something is broken and wrong about why; re-derive the mechanism before patching.

## Rules are shipped code

A rule written into an adapter, a memory file, or a repository's guidance runs unsupervised, on future incidents, by agents that have none of the context it was written in. A wrong rule is worse than none, because it is followed confidently. A document edit feels like writing rather than shipping, so it skips the verification a code change gets.

- **Replay the rule against the incident that produced it.** Reconstruct the real state and step the rule through it. A remediation that said "after any such commit, hard-reset to the remote" would, replayed, have deleted the one local commit sitting on top of the duplicate it was written to clean up. The rule that shipped rebases instead.
- **Scope the claim to the evidence.** One observation supports "in this case". A general statement about how a tool or endpoint behaves needs its documentation opened first.
- **Inherited text is not verified.** A sentence carried forward from an earlier draft is a claim you are now making. Verification attention goes to text being written, not text being moved, so a false claim survives every rewrite. When editing anything that makes external claims, list the claims that survive unchanged and check each as if it were new: would you write this sentence today, from a source you have open?
- **An identifier is not a condition.** A rule's name, a function's file name, a job's label, or a variable's name can outlive what it describes. A firewall rule kept its original ID after its path was widened, and was re-reported as a no-op eleven days after it had been fixed. A wrong reference that still resolves is worse than a broken link, because nothing looks unusual. Inspect the condition itself.
- **Write the resolution back into the finding.** A dated audit note is what gets re-read. When a finding is fixed, strike it in the note that raised it, not only in a log elsewhere, or the next reader reports it as open.
- **Verify a queued task is still needed before doing it.** Deferred instructions drift; the work is often done in a later session and the entry is never reconciled.

## What transfers

- **Score the evidence, not the confidence, and never cite what was not opened.**
- **Every number in prose is re-derived by a command first.**
- **A control is proven by breaking it, and the proof is re-run by a hook, not by discipline.**
- **Start the case list with what must be refused and what must stay quiet**, on input shaped the way real people write it.
- **A check with a self-authored probe is a check with the author's blind spots.** Prefer the mechanical check that already exists.
- **Audit the coverage and the freshness of the suites**, not only their results.
- **Read the transcripts before calling a gate ignored.**
- **Treat a rule as code**: replay it on the incident, and scope it to the evidence.
