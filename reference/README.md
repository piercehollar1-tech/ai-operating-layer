# Sanitized reference tree

This directory mirrors the relationships in an AI operating layer without copying a live installation.

```text
reference/
├── BOOTSTRAP_PROMPT.md
├── adapters/
│   ├── AGENTS.md.example
│   ├── CLAUDE.md.example
│   └── output-style.md.example
├── agents/
│   ├── task-packet.md.example
│   └── worker.md.example
├── hooks/
│   ├── README.md
│   ├── pre-publish-scan.py.example
│   ├── private-terms.txt.example
│   ├── routes.json.example
│   └── tests/
│       └── pre-publish-scan-probes.py.example
└── shared/
    ├── QUICK_CONTEXT.md
    ├── TODAY.md
    ├── memory/
    │   ├── MEMORY.md
    │   ├── MEMORY-ARCHIVE.md
    │   ├── feedback_lesson-example.md
    │   └── project_example.md
    ├── skill-notes/
    │   └── example-workflow.md
    ├── skills/
    │   └── example-workflow/
    │       └── SKILL.md
    └── vault/
        ├── index.md
        ├── log.md
        ├── Config/
        │   └── system-map.md
        └── Projects/
            └── example-project.md
```

`hooks/`, `agents/`, and the output style are separate from both: a control layer, an agent
definition, and a system-prompt style are client-specific and do not port between clients, even
when the context beneath them is shared. See [../docs/enforcement.md](../docs/enforcement.md),
[../docs/delegation.md](../docs/delegation.md), and
[../docs/response-contract.md](../docs/response-contract.md).

`hooks/tests/` holds a probe suite for the example publication hook: a `# covers:` line, quiet
cases, the inputs the hook exists to catch, and mutations that must each turn a case red. Unlike
the rest of this directory it is runnable: CI runs the cases, and `--mutations` runs the
mutations after a change to the hook. See
[../docs/verification.md](../docs/verification.md).

`agents/task-packet.md.example` is a filled-in packet for a delegated worker; the worker
definition beside it is the agent that receives one.

`shared/skill-notes/` is the per-skill operational memory the preflight hook injects on
invocation; `shared/memory/feedback_lesson-example.md` shows a lesson with its `applied:` line.
See [../docs/context-delivery.md](../docs/context-delivery.md).

The adapters are intentionally separate from `shared/`. Install them through each client’s supported instruction mechanism and replace `your_private_shared_root` with the private shared directory.

All names and content below this directory are fictional. Do not turn this directory itself into a live memory store inside a public clone.
