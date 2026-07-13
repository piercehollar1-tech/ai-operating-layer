# Bootstrap prompt

Copy the prompt below into Claude Code or Codex after cloning this repository.

```text
Help me adapt this sanitized AI operating-layer blueprint to my machine.

Safety requirements:
- Treat every file under reference/ as a template, not live configuration.
- Inspect my existing instruction files before proposing changes.
- Do not overwrite global CLAUDE.md, AGENTS.md, settings, hooks, skills, or memory.
- Do not read or copy credentials, .env files, browser data, transcripts, or unrelated personal notes.
- Keep my real shared context outside this public repository.
- Use placeholders in any file that will remain in the public clone.
- Show me the path mapping and proposed diff before changing global configuration.
- Ask before changing system-wide instructions, permissions, hooks, plugins, or shared governance.

Work in this order:
1. Read README.md, docs/architecture.md, docs/setup.md, and reference/README.md.
2. Identify which clients I use and their currently supported instruction locations.
3. Propose a private shared root and map every reference file to its destination.
4. Check for existing files and choose merge, create, or skip for each one.
5. Create the smallest useful private structure with fictional starter content.
6. Merge a thin adapter into each approved client instruction file.
7. Verify each client actually loads the adapter and can follow the pointer chain.
8. Test a disposable cross-client read/write loop, then remove the test data.
9. Report what is verified, what is only inferred, and what remains optional.

Do not install a daemon, background model process, plugin, or external package unless I separately approve it after a security review.
```
