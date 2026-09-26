---
name: lesson-verify-before-claiming
description: A green run or an existing file is not proof a component loaded — check the client lists or invokes it before calling an install done
type: feedback
applied: 2030-01-15 2030-02-02
updated: 2030-02-02
---

# Verify before claiming

A skill file sat in the skills directory for a week and never registered, because the client
only loads `dir/SKILL.md` and this was a flat file. Nothing errored. The install was reported
done because the file existed.

**Why:** existence is not consumption. A client shows what it loaded; the filesystem does not.

**How to apply:** after any install, confirm the client lists or invokes the component. After
any hook change, drive the exact registered command with the input it exists to catch. Append
today's date to `applied:` above each time this rule changes what you do; three applications
promote it to the adapter, none in sixty days prunes it (unless a dated `keep:` line says why).

Related: [[project_example]]
