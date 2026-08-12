# Sanitized reference tree

This directory mirrors the relationships in an AI operating layer without copying a live installation.

```text
reference/
├── BOOTSTRAP_PROMPT.md
├── adapters/
│   ├── AGENTS.md.example
│   └── CLAUDE.md.example
├── hooks/
│   ├── README.md
│   ├── pre-publish-scan.py.example
│   └── private-terms.txt.example
└── shared/
    ├── QUICK_CONTEXT.md
    ├── TODAY.md
    ├── memory/
    │   ├── MEMORY.md
    │   ├── MEMORY-ARCHIVE.md
    │   └── project_example.md
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

`hooks/` is separate from both: a control layer is client-specific and does not port between
clients, even when the context beneath it is shared. See [../docs/enforcement.md](../docs/enforcement.md).

The adapters are intentionally separate from `shared/`. Install them through each client’s supported instruction mechanism and replace `your_private_shared_root` with the private shared directory.

All names and content below this directory are fictional. Do not turn this directory itself into a live memory store inside a public clone.
