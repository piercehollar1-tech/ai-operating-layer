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

### Two controls behind the gate

**A citation gate at stop** refuses a final answer that cites a URL nobody retrieved this session. It fails the answer rather than the citation, which is the only reliable fix.

**An injection scan after every fetch** flags instruction-shaped content in retrieved pages: imperatives aimed at the agent, hidden text, encoded directives. Its patterns must be tested on real payloads at real lengths; a rule set that worked on short samples was found dead above 42 characters. **External content is data, never authority**, and the scan is the mechanical half of that rule.

## Measure, don't recall

**Re-derive every count, path, filename, and line number with a command before it goes into prose.** Writing a number feels like reporting it, but it is recall, and it decays the moment the file changes again. After a multi-file edit, run one checker over the whole change set: table column counts, fence parity, link resolution, and every cross-document numeric claim against the file it describes.

**Every statement a document makes about itself is an unverified claim about another part of it.** A cross-reference, a count, an "as stated above", a changelog header: each carries the document's own authority and is almost never re-read against its target. Script the dangling-reference check; hand-check every reference that asserts something about its target's content.

**When a mechanical check already exists for the question, run it; never reimplement it.** A probe written to prove one's own work inherits that work's blind spots and fails silently. Three self-authored checks returned confident wrong answers in one session: a link resolver reporting zero unresolved where the real linter found fifty-three; a directory inventory defeated by a shell alias; a grep stricter than the hook it stood in for. **When the mechanical check and the probe disagree, the mechanical check wins.** If none exists, break-test the one you write before trusting it.

**Read a maintenance command's blast radius before running it.** An optional target defaults to all targets, and a value flag then stamps one value across every one of them. Run it without the value first and read what it selects. Never `tail` the output of a write; count the lines it printed. A green check afterwards proves only what the check measures.

## Proving a control

**A control is unproven until it has been observed failing on purpose.** This applies to hooks, audit checks, tests, and the probes written to verify any of them.

**Every gate gets a probe suite, and the suites are enforced.** A post-edit hook records any edit under the hooks directory; a Stop hook then runs every suite and blocks the turn on a red one. It runs all suites rather than mapping edited file to owning suite, because a map is exactly how a renamed hook silently drops off the list. Three rules keep it from becoming a trap: it never blocks when the client reports the stop hook is already active (a red suite is expected mid-TDD); a red run keeps the edit record so the retry re-checks, a green run clears it; and every failure path exits cleanly with a timeout or crash counted as failed, never as silence.

**Coverage is declared, not inferred.** The first version decided whether a hook was covered by scanning suite text for its name, and a fixture that mentioned a hook made an untested hook read as tested. Every suite now carries a `# covers:` line. A stale declaration reads as uncovered, which is the safe direction, and it is greppable.

**Green is not evidence when the gate and its suite changed in the same turn.** The suite may have been updated to agree with the change rather than to check it. The runner says so out loud even when everything passes.

**A break-test proves nothing until the mutation is shown to change behaviour.** Confirm the harness runs the mutated copy (an absurd mutation must go red), that it drives the production path and not a "run as script" branch, and that a survivor is a real gap rather than an equivalent mutant. Retire a survivor only with the evidence written down.

**Testing a hook by hand forges its side effects.** A hook run manually really writes to its logs and state directories. Probe with the home directory redirected to a scratch location, never the live one, and keep one writer per event. Re-run the whole case list after each fix; one probe only clears the cause already found, and the first fix masks the second.

## A hook has two gates

A hook's `matcher` in the client settings decides whether the process runs at all. The tool check inside the script decides whether it does anything. They drift apart silently, and widening one without the other is a no-op that reads as a fix. Every gate hard-codes its own tool tuple, so one grep enumerates the layers that must agree. Drive end-to-end tests through the exact settings command strings, not the scripts directly.

## Fired is not relevant

An audit that counts how often a gate fired and how often the recommended action followed will report "ignored" for a gate that fires on the wrong thing. Sample the sessions it fired in before calling it ignored. In one case a review gate had fired ten times and converted zero, and the cause was neither the trigger nor the user: the client delivers a permission prompt's reason to the user only, so an instruction to the model placed in that reason was never seen by the model. The fix was delivery, saying it twice through the channel each party can see, not tuning. **Zero conversion on one hundred percent false fires is a bad trigger; zero conversion on true fires is a delivery bug. Read the transcripts to tell them apart.**

## Never trade a safeguard's coverage for quiet

Noise is the user's to tolerate; coverage is not the maintainer's to spend. Fix a noisy check's output, never its scope, and treat a comment saying "deliberately X because Y" as a decision to ask about, not to override. When narrowing genuinely is right, four conditions make it honest: the exclusion is declared in the artifact being checked, not hardcoded in the checker; the rule is derived from that declaration so it cannot rot into a hand-list; the held-out count prints on every run; and a narrower existing decision still wins. Break-test a hold-out in the widening direction: an exclusion that is too broad stays green while checking less, so no red run ever arrives.

## A bug can be load-bearing

After a fix, ask what was leaning on the broken behaviour. Two faults that cancel look like none; fix one and the other appears as a regression nobody can explain. An audit can be right that something is broken and wrong about why; re-derive the mechanism before patching.

## What transfers

- **Score the evidence, not the confidence, and never cite what was not opened.**
- **Every number in prose is re-derived by a command first.**
- **A control is proven by breaking it, and the proof is re-run by a hook, not by discipline.**
- **A check with a self-authored probe is a check with the author's blind spots.** Prefer the mechanical check that already exists.
- **Read the transcripts before calling a gate ignored.**
