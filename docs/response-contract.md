# Response contract

A reply-length rule that lives in an instruction file does not hold. This document describes the version that does: the contract in the system prompt, a measurement after every reply, the score delivered on the next turn, and an audit that notices when the whole thing has drifted.

## The measurement that forced the redesign

The rule existed for two months before anyone counted. Counting every final reply in the client's transcripts gave this shape (the numbers are from one installation; the shape is what matters):

| | Result |
|---|---|
| Median chat prose per reply | ~360 words against a 250-word ceiling |
| Replies over even the widest cap | roughly four in five |
| Replies that named their tier and then exceeded it | over half |

Rewriting the rule had made it worse. Naming the tier had not helped. The diagnosis is not that the numbers were wrong: **an instruction nothing measures is a suggestion.** Nothing in the system could show the rule being broken, so it was broken continuously and invisibly.

Three things were wrong with the design:

1. **The rule lived in the wrong layer.** Instruction files arrive as context after the system prompt. Context loses to momentum in a long session.
2. **The model chose its own tier.** Every reply ended with a self-assessment of how much room it deserved, made by the party that wants the room. The uncapped tier was an escape hatch, and it was used on judgment rather than on a trigger.
3. **There was no feedback.** Not one reply had ever been scored.

## The four layers

| Layer | Mechanism | Job |
|---|---|---|
| **Contract** | An output-style file loaded into the system prompt | The tiers, the caps, the triggers. Some clients re-inject adherence reminders for system-prompt styles on their own, which an instruction-file line never gets. |
| **Measurement** | A Stop hook | Counts the chat prose of every final reply against its ceiling and appends one row to a log. Deliverables (code, files, tables the user asked for) are excluded from the count. |
| **Feedback** | A user-prompt hook | Injects the last reply's length versus its cap, its reading grade, any undefined jargon, and the session's running record into the next turn. About sixty tokens, and it is evidence rather than a lecture. |
| **Anti-rot** | An audit check | Flags when the over-cap rate exceeds a threshold across a window, when the kill switch is on, or when the caps drift between the contract file and the measuring hook. |

### The contract itself

The tier is chosen by the request, not by the model. Match the first row that fits; when two fit, take the lower.

| Tier | The request looks like | Cap |
|---|---|---|
| T1 | A lookup, a yes/no, a confirmation, one edit | One answer line |
| T2 | Normal work: a fix, a small build, a status | Answer line plus a few bullets, ~120 words |
| T3 | An audit, research, a design, several questions at once | Answer line plus bullets under at most two labels, ~250 words |
| T0 | **Only** a trigger in the user's own words: a security warning, confirming a destructive action, steps they must run themselves, a question they repeated | Uncapped |

"Explain" and "tell me more" are not T0. They bump one tier and narrow the target: answer the specific gap, in simpler terms, without restating what was already said. The tier is a ceiling, never a target.

Shape, every time: answer line, then `**label** — fact` support bullets, then at most one open item. Never a restatement of the question, a recap of visible work, a closing summary, or an unrequested menu of next steps.

The cap governs the prose around the work, never the work. Cutting a fact to hit a cap is a failure; it means the reply was mis-tiered, so move up one tier and say so.

### Why the Stop hook measures instead of blocking

A Stop hook fires after the reply has already streamed. Blocking cannot unsend it; it appends a retry to the original, so the user gets the long answer and a second one, and pays context for both. Any length check crude enough to write is crude enough to block an answer that genuinely needed the room. So the hook measures and reports, and the next turn opens with the score.

### The dial lives outside the prompt

A state file holds one word: `low`, `medium`, or `high`. Both hooks read it live. The user changes one word instead of re-arguing the rule in prose, and the contract text stays stable. Stable prompt, movable knob.

## Plain-language requirement

The same layer measures reading grade. The target is roughly an eighth-grade level: short sentences, common words, no jargon unless it is defined in the same breath, no invented labels. File names, commands, and the exact names of things are not jargon. The scoreboard lists any undefined technical term from the last reply, so the drift is visible before it becomes habit.

## What transfers

- **Put a rule the model drifts from in the system prompt, not an instruction file.**
- **Measure every instance and deliver the score at the next decision point.** Evidence lands where a lecture does not.
- **Take tier selection away from the party that benefits from the wider tier.** Bind it to observable features of the request.
- **Give the uncapped path a trigger phrase, not a judgment call.**
- **Audit the measuring layer.** A kill switch left on, or caps that drift between two files, silently turns the control back into a suggestion.
