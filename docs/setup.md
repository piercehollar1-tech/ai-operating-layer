# Setup guide

This is a manual, review-first rollout. It avoids overwriting an existing client configuration and keeps the real context outside the public repository.

## 1. Choose a private shared root

Pick a private absolute path, represented below as `your_private_shared_root`. A neutral location such as `~/ai-context` is easier to share across clients than a client-owned configuration directory.

Copy the structure under [`reference/shared`](../reference/shared) into that private location. Replace all fictional examples with your own content only in the private copy.

Do not put credentials, raw transcripts, environment files, or browser data in the shared root.

## 2. Install thin client adapters

Use the dummy files in [`reference/adapters`](../reference/adapters) as source material. Merge the relevant sections into existing global instructions; do not blindly replace them.

### Claude Code

The user-level instruction file is normally `~/.claude/CLAUDE.md`. Project-specific guidance can live in a repository `CLAUDE.md` or `.claude/CLAUDE.md`.

1. Review `CLAUDE.md.example`.
2. Replace `your_private_shared_root` with the private absolute path.
3. Merge it into the appropriate user or project instruction file.
4. Use Claude Code’s `/memory` view to confirm which instruction and memory files actually loaded.
5. Keep the adapter's "when instructions conflict" section: once skills, notes, and memory exist, they will disagree, and the order has to be written down before that happens.

Claude Code also supports per-project auto memory. If you use it, keep its `MEMORY.md` concise and decide deliberately whether it is the canonical memory store or merely a client-local supplement. Do not create two competing sources of truth by accident.

### Codex

The global instruction file is normally `~/.codex/AGENTS.md`, unless `CODEX_HOME` is set elsewhere. If `AGENTS.override.md` exists at that level, Codex uses it instead. Repository `AGENTS.md` files add more specific guidance as Codex walks from the project root toward the working directory.

1. Review `AGENTS.md.example`.
2. Replace `your_private_shared_root` with the private absolute path.
3. Merge it into the global file.
4. Start a fresh Codex run and test that it can locate the shared root and follow one harmless adapter rule.
5. Keep the same "when instructions conflict" section as the Claude Code adapter, so both clients settle a conflict the same way.

Keep repository-specific commands and conventions in that repository’s `AGENTS.md`, not in the global adapter.

## 3. Make shared skills discoverable

The reference skill is only a structural example. For a real skill:

1. Keep one clear `SKILL.md` entrypoint.
2. Put large instructions, templates, and scripts in named subdirectories.
3. Add the skill through each client’s supported skill or plugin mechanism.
4. Confirm the client lists or invokes it before claiming installation succeeded.

The private shared directory may hold the canonical skill source, while client-specific installation uses a copy, link, or plugin package. Choose one ownership model and document it.

## 4. Test the complete loop

Use fictional or disposable data for the first test:

1. Ask client A to find `QUICK_CONTEXT.md` through its adapter.
2. Ask it to locate the example project through `MEMORY.md` without bulk-reading the vault.
3. Ask it to save one disposable project decision in the correct owner note and append a concise log entry.
4. Ask client B to retrieve that decision through the same pointer chain.
5. Delete the disposable entry.

This verifies the behavior, not merely the presence of files.

## 5. Add the first controls

Only after the manual loop works. Start with the two whose failure is worst, not the two that are
easiest:

1. **A publication gate** on anything crossing from private to public, in two layers: an
   agent-side hook before the command, and git's own `pre-push` hook, which sees the exact
   commits being pushed.
2. **A credential guard** blocking reads of secret paths and environment dumps.

For each one, before trusting it: construct the input it exists to catch and confirm it blocks.
**A control is unproven until it has been observed failing on purpose** — a hook with an inverted
condition passes every test where nothing is wrong. Keep those cases beside the hook and re-run them
after any change to its patterns.

Read the payload from stdin as JSON. A hook written against environment variables is a silent no-op:
it runs, finds nothing, exits zero, and looks healthy. Live-probe again after any client update.

Full treatment in [enforcement](enforcement.md).

## 6. Add automation one piece at a time

- an on-demand recall index;
- a minimal startup recap;
- private backups;
- read-only health checks;
- scheduled workers, each paired with a catch-up run and a success marker;
- automatic session summaries, fired from a **detached** end-of-session hook so a slow one is not
  cancelled.

Test the real loading or enforcement path after each change. Keep runtime state out of protected
configuration or executable directories. Failure modes and design rules in
[automation](automation.md).

## 7. Wire delivery, then measure

Only after the controls above are proven:

- a skill-preflight hook that injects `skill-notes/<skill>.md` and bound lessons on invocation,
  and a routing table fired at the tool call ([context delivery](context-delivery.md));
- the reply contract as an output style in the system prompt, with a Stop hook that measures
  every reply and a prompt hook that reports the score ([response contract](response-contract.md));
- the delegation gate, with the dispatch-contract and delegate-first hooks
  ([delegation](delegation.md)), and a task-packet template
  ([example](../reference/agents/task-packet.md.example));
- probe suites for every blocking gate, the affected ones run by a Stop hook after any hook
  edit (all of them when the edited file has no suite), with an audit check that every hook and
  checker has one or declares it has none, and that the suites ran recently
  ([verification](verification.md); a runnable example is in
  [`reference/hooks/tests/`](../reference/hooks/tests/pre-publish-scan-probes.py.example)).

For each one, take the baseline measurement first. A rule with no count is a suggestion, and the
count is what tells you whether the wiring worked.

## Public-release checklist

Before publishing changes derived from a private installation:

- inspect the complete staged diff;
- search for usernames, home paths, emails, project IDs, domains, tokens, and private URLs — over the
  **whole tree with nothing excluded**, and over untracked files as well as tracked ones;
- confirm no live `CLAUDE.md`, `AGENTS.md`, database, transcript, or local settings file is staged;
- confirm every example is fictional;
- pin line endings in `.gitattributes` if the repository ships scripts or hooks
  ([operating pitfalls](operations.md));
- verify all Markdown links resolve;
- review the rendered repository on GitHub.

The copyable [bootstrap prompt](../reference/BOOTSTRAP_PROMPT.md) gives an AI client the same safety constraints.
