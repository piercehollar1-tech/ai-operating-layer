# Example enforcement hooks

Fictional examples showing the shape of a control layer. Concepts are in [../../docs/enforcement.md](../../docs/enforcement.md).

Nothing here is wired up, except that CI runs the probe suite against the example hook. Adapt it to your client's hook mechanism, replace every fictional term, and test each control by breaking it on purpose before trusting it.

## Files

| File | What it demonstrates |
|---|---|
| `pre-publish-scan.py.example` | Blocking a publish to a public destination when it would carry private data. The agent-side layer: parses the command rather than grepping it; checks every push URL each publish really uses; scans file names and contents, the staged index, unpushed commits, commit messages, ref names, notes, symlink targets, and LFS objects; fails closed, including on its own crash; has no exclude list; never echoes the match. Its docstring lists what it cannot see, which is why a git `pre-push` hook is the second layer. |
| `private-terms.txt.example` | The shape of a term file — and why it must live outside any published tree. |
| `routes.json.example` | A routing table for a pre-tool nudge: fires the adapter's routing pointers at the tool call, as added context only. |
| `tests/pre-publish-scan-probes.py.example` | The publication hook's probe suite. Runnable (CI runs it): throwaway repositories built once, a stub `gh` on `PATH`, a redirected home directory, quiet cases written the way real commands look, and mutations that must each be caught, run four at a time. |

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

**Match what the tool will really be given.** A publish gate that looked for `git push` missed `git -C <dir> push`, and scanned the working directory rather than the repository named by `-C`. Global options, chained commands, and other remotes are the ordinary shapes of the input, not edge cases.

**Assume hooks for one event run in parallel.** Order in the settings file conveys nothing. Never let two hooks rewrite the same tool input, and never let one depend on another having run first.

**Use exec form for anything shipped to another machine.** A path placeholder substituted into a shell-form command is interpreted by the shell; exec form (an executable plus an argument list) is not.

**Measure runtime against the timeout.** A hook killed by its timeout prints nothing and looks like a hook with nothing to say.

**Never register a model-evaluated hook on user input live.** If the evaluator answers with anything but the exact no-op result, the user's message is blocked. Prove it in a headless run with temporary settings first.
