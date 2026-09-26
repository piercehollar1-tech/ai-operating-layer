# Operating pitfalls

The other documents describe what the layer should do. This one collects the traps that made it
silently do something else: shell behaviour, headless runs, background work, and publishing. Every
entry below failed without an error at least once. That is the common thread: **each of these
produces a plausible result, exits zero, and is wrong.**

## Shell and process traps

**Shell state does not survive between tool calls.** Each shell call an agent makes is usually a
separate process; only the working directory may persist. A procedure that computes a temporary
path in one call and reads it in the next reads a path that never existed. Anything shared across
steps gets a literal path chosen up front, or the steps collapse into one call.

**The working directory does persist, and that is its own trap.** A relative output path (`-o
page.html`, `> out.txt`) lands wherever the last `cd` left the shell, which during a deploy is a
repository. The next `git add -A` stages it. Every scratch write gets an absolute path into a
session scratch directory, never a bare filename. Before `git add -A` in a repository you have been
probing in, read `git status --porcelain`, or stage explicit paths.

**A leading `VAR=value` applies to the first command of a pipeline only.** `VAR=x echo '{}' |
hook.sh` sets the variable for `echo`, not for the hook. A "sandboxed" probe written that way runs
the hook against the real environment. Export first, or put the assignment on the command that
reads it.

**Know which shell you are in.** zsh does not word-split an unquoted `$var`, so a loop over a
space-separated list silently becomes one iteration; use arrays. In zsh, `path`, `fpath`, and
`cdpath` are tied to the search paths, so a variable with one of those names rebinds `PATH`. A
login shell (`-l`) and an interactive shell (`-i`) read different startup files. Scripts that
must behave the same everywhere name their interpreter and run under it explicitly.

**A detached child can die with the call that started it.** In a sandboxed tool call, `nohup cmd
&` may lose filesystem access when the call returns. Anything that must outlive the call uses the
client's own background-task mechanism.

**Never edit a script while a background process is running it.** Shells read scripts
incrementally; an edit mid-run can end the run early with no error, which reads as a clean finish.
Check for a live run first, or copy the script and run the copy.

**A delete on a path that is already gone succeeds.** Exit code zero is not evidence anything
happened. Before acting on a queued or deferred instruction, look at the target; after acting,
confirm the post-state.

## Headless and background runs

**A headless run auto-denies what an interactive one would ask about.** A missing grant therefore
looks like a model failure (exit zero, nothing done) rather than a permission error. List every
path the run reads or writes, grant each one explicitly, and verify the run by its output
artifact, never by its exit code.

**A child session runs the parent's lifecycle hooks.** A headless run started from a hook can
trigger the same session-start and session-end hooks, including the one that started it. Guard
with an environment sentinel the child inherits.

**Save the rejected output.** When a headless call fails a format check, keep what it actually
returned. A character count in a log is not evidence of anything, and the output is usually the
diagnosis.

**The machine bounds the fan-out.** On a small machine, heavy local jobs (media processing, OCR,
builds, test suites) run one or two at a time, never one per item. Wide fan-outs against one
remote host also get rate-limited, so parallel ends up slower as well as heavier. Light network
calls parallelize; local compute mostly does not.

## Publishing and repositories

**Verify a publish by tree, not by history.** When content reaches a remote by any route other
than a plain push of reviewed local commits (an automation that commits from an archive, a web
upload, a bot), the commit list proves nothing about content. `git fetch` then `git diff
<reviewed-local-head> origin/<branch> --stat` being empty is the proof that the reviewed tree is
the published one. A release archive gets the same file-by-file comparison against its tag.

**A checkout is not the repository.** Git on Windows converts text files to CRLF on checkout by
default, while `git archive` does not, so a clone and a release zip of one commit differ. Any
repository that ships scripts, hooks, or files whose bytes are measured pins line endings in
`.gitattributes` (`* text=auto eol=lf`). `git ls-files --eol` shows whether anything is pinned.

**Review the tree that ships, not the tree on disk.** A review of a dirty working tree describes
code that is not deployed. Run `git status --porcelain` before any verdict, and review the
committed state when it differs.

**Attribute every change before committing it.** Another agent session in the same repository is
a real possibility. A file that changed with no edit from this session is not yours to commit until
you know where the change came from. Read modification times with the full date, not time only.

**Prefer the lossless operation.** Rebase over a hard reset; a dirty-tree check before either.
Reserve a destructive step for the state where it is provably a no-op (the diff against the target
is empty).

## What transfers

- **Silence is not success.** Every trap above exits zero. Check the artifact, the count, or the
  post-state.
- **Choose paths, do not compute them across calls.** Absolute, literal, in a scratch directory.
- **Pin what varies by machine**: the interpreter, the shell, the line endings.
- **Prove a publish by comparing trees.**
