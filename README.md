# Personal AI Operating Layer

A persistent memory and skill-orchestration system I built on top of [Claude Code](https://claude.com/claude-code), my primary AI development environment. It's the setup I use every day to do real automation work — and a running experiment in making an AI assistant accumulate knowledge and handle repeatable, multi-step work reliably.

> This repository documents the system at a conceptual level. It's a personal environment, so the live configuration isn't published here.

## Why I built it

Out of the box, an AI assistant forgets everything between sessions and treats every task the same way. I wanted mine to **carry context across days** and to **run repeatable workflows without me re-explaining them each time.** So I built two systems and wired them into my daily environment.

## 1. File-based memory

A memory layer where each fact, project, preference, or lesson is its own small file with structured metadata, indexed so the relevant ones surface automatically at the start of every session.

- Remembers ongoing projects, past mistakes, and working preferences
- Gets *more* useful over time instead of resetting each session
- A learning protocol captures every correction or non-obvious fix as a durable lesson rather than losing it

## 2. Staged, review-gated skill pipeline

A workflow system for repeatable, multi-step jobs — things like client onboarding or research-to-report — where work moves through **numbered stages with a human checkpoint between each**, so nothing ships unreviewed.

- Each stage declares exactly what context to load
- Human review gates between stages keep the process interpretable and safe
- Adapted from patterns circulating in the open-source Claude Code community, integrated and tuned to my own workflows

## What I actually learned: distrust silent success

Early on, I added components that *looked* installed but had silently never loaded — because I'd verified the files existed instead of verifying the system consumed them. For days I relied on capabilities that weren't actually running.

That reshaped how I work. I now treat **"it exists" and "it works" as separate claims**, and I only allow myself to assert the second one. After any install or config change, I confirm the system actually picked it up — listing what loaded and testing the real symptom, not the artifact. That single discipline has since caught dead integrations and a misconfigured deploy gate before they caused damage.

A visible error is a gift; a silent one costs you days.

## Stack

- **Environment:** Claude Code
- **Memory:** structured Markdown files with metadata + an auto-loaded index
- **Automation:** n8n, Claude API, workflow integrations
- **Discipline:** verification-after-change as a standing rule, not an afterthought

---

*Built and maintained by [Pierce Hollar](https://www.linkedin.com/in/pierce-hollar-111276361).*
