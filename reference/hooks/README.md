# Example enforcement hooks

Fictional examples showing the shape of a control layer. Concepts are in [../../docs/enforcement.md](../../docs/enforcement.md).

Nothing here is wired up. Adapt it to your client's hook mechanism, replace every fictional term, and test each control by breaking it on purpose before trusting it.

## Files

| File | What it demonstrates |
|---|---|
| `pre-publish-scan.py.example` | Blocking a publish to a public destination when the tree carries private data. Fails closed, scans untracked as well as tracked files, has no exclude list. |
| `private-terms.txt.example` | The shape of a term file — and why it must live outside any published tree. |
| `routes.json.example` | A routing table for a pre-tool nudge: fires the adapter's routing pointers at the tool call, as added context only. |

## Lifecycle map

Hook point names vary by client. These categories do not. A layer that only logs is not an enforcement layer.

| Moment | Blocking controls worth having | Non-blocking |
|---|---|---|
| Session start | — | Inject standing context; surface drift, stale indexes, oversized files |
| Before a tool call | Refuse destructive commands without stated blast radius · block credential-path reads · gate publication · require a context brief on subagent dispatch | — |
| After a tool call | — | Format, log, detect a bad result reported as success |
| After a tool failure | — | Route a known failure to its known fix |
| On user input | — | Reinforce a contract the model drifts from as context fills |
| Before compaction | — | Preserve state summarization would drop |
| At stop | Refuse an answer citing sources nobody retrieved | — |
| Session end | — | Summarize, drain queues, back up — detached, so a slow hook is not cancelled |

## Writing one that works

**Read the payload from stdin as JSON.** Hook input does not arrive in environment variables. A hook written against env vars is a silent no-op — it runs, finds nothing, exits zero, and looks healthy.

**Fail closed.** If the condition cannot be evaluated, block.

**Test by breaking it.** Construct the input the control exists to catch and confirm it blocks. A hook with an inverted condition passes every test where nothing is wrong. Keep the tests next to the hook and re-run them after any change to its patterns.

**Live-probe after a client update.** Hook payload shapes and event names change. A control that silently stopped firing is worse than no control, because you stopped watching for the thing yourself.

**Record the incident that produced it.** A hook whose motivation is undocumented gets weakened by whoever next finds it inconvenient.

**Say it through the channel each party can see.** A permission prompt's reason reaches the user, not the model. An instruction to the model belongs in the added-context field; a fact for the user belongs in the reason. Say it twice when both need it.

**Give every gate a probe suite with a `# covers:` line, and run all suites from a Stop hook after any edit under the hooks directory.** Coverage declared, not inferred; a stale declaration reads as uncovered. See [../../docs/verification.md](../../docs/verification.md).

**Probe with the home directory redirected.** A hook run by hand really writes to its logs and state. One writer per event; re-run the whole case list after each fix.
