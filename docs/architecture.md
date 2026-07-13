# Architecture

This blueprint separates durable knowledge, reusable procedures, and client-specific runtime behavior. The paths below are examples; the private installation may live anywhere outside this public repository.

## Component map

| Component | Example private location | Points to | Responsibility |
|---|---|---|---|
| Claude adapter | `~/.claude/CLAUDE.md` | Shared context root | Translates shared conventions into Claude Code guidance |
| Codex adapter | `~/.codex/AGENTS.md` | Shared context root | Translates the same conventions into Codex guidance |
| Current focus | `your_private_shared_root/TODAY.md` | Active project notes | Short-lived priorities and handoff state |
| Quick context | `your_private_shared_root/QUICK_CONTEXT.md` | Memory and vault indexes | Stable orientation, not a session transcript |
| Hot memory index | `your_private_shared_root/memory/MEMORY.md` | Focused memory files | Small set of facts and links likely to matter again |
| Memory archive | `your_private_shared_root/memory/MEMORY-ARCHIVE.md` | Older memory files | Cold index for less frequent retrieval |
| Vault index | `your_private_shared_root/vault/index.md` | Project, config, and research notes | Long-form durable knowledge |
| Vault log | `your_private_shared_root/vault/log.md` | Recently changed notes | Concise audit trail and optional session recap source |
| Shared skills | `your_private_shared_root/skills/example-skill/SKILL.md` | References, templates, or scripts | Repeatable procedures and review gates |
| Client runtime | Client-owned config directories | Hooks, permissions, plugins, tools | Enforcement and automation specific to one client |

## Suggested private tree

```text
your_private_shared_root/
├── TODAY.md
├── QUICK_CONTEXT.md
├── memory/
│   ├── MEMORY.md
│   ├── MEMORY-ARCHIVE.md
│   ├── project_example.md
│   └── feedback_example.md
├── vault/
│   ├── index.md
│   ├── log.md
│   ├── Projects/
│   ├── Config/
│   ├── Research/
│   └── Sessions/
└── skills/
    └── example-workflow/
        ├── SKILL.md
        ├── references/
        ├── templates/
        └── scripts/
```

Only create subdirectories a real workflow needs. Empty taxonomy is maintenance work, not capability.

## Retrieval flow

The adapters should define a narrow ladder rather than loading the entire shared store:

1. Start with the user request and repository-local instructions.
2. Read `TODAY.md` only when current focus or handoff state matters.
3. Read `QUICK_CONTEXT.md` when personal or system orientation matters.
4. Check `MEMORY.md`, then open only the linked topic file that owns the subject.
5. Search the private index or vault when the hot index does not answer the question.
6. Follow at most one relevant note link before reassessing.

A semantic or hybrid search index can improve step 5, but the Markdown files remain canonical. The index should be rebuildable and should not become a second memory store.

## Persistence flow

Route new information to the smallest durable home:

| New information | Durable home |
|---|---|
| Working preference or repeated correction | Focused feedback memory |
| Project fact, constraint, or decision | Existing project memory or vault project note |
| Reusable multi-step method | Shared skill |
| Cross-project reference material | Vault research or reference note |
| Universal client behavior | Adapter or repository guidance, after review |
| Mechanical safety requirement | Client-specific permission or hook, after review |

Update an existing owner note before creating a duplicate. Keep `MEMORY.md` as pointers and summaries, not a transcript dump.

## Skills and review gates

A skill is a directory with a `SKILL.md` entrypoint and only the supporting resources it needs. For consequential workflows, define explicit stages:

```text
request → scope artifact → human approval → execution artifact → human approval → final delivery
```

Each stage should name its inputs, output path, validation, and stop condition. “The command succeeded” is not enough; verify the user-visible or downstream result.

## Client boundaries

Shared filesystem access does not imply shared runtime behavior:

- Codex does not automatically consume Claude Code hooks, permissions, plugins, or `CLAUDE.md`.
- Claude Code does not automatically consume Codex configuration, hooks, plugins, or `AGENTS.md`.
- A shared skill must still be installed or made discoverable using each client’s supported mechanism.
- Secrets belong in an OS credential store or a private runtime environment, never in memory or the vault.

This boundary is why the adapters stay thin. They translate durable conventions; they do not pretend the clients have identical runtimes.

## Optional infrastructure

These are useful additions, not prerequisites:

- a short session-start recap derived from the last few vault log headings;
- an on-demand full-text or hybrid recall index;
- read-only health checks for broken pointers, stale backups, or hook drift;
- a private backup job for the shared context root;
- Git history for private memory, provided the repository is never made public.

Avoid background model calls and always-on memory daemons unless their value clearly exceeds their cost, privacy surface, and operational complexity.
