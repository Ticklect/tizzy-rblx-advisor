# Tizzy RBLX Advisor

Unofficial Roblox development and game-business advisor distilled from **21 public Tizzy RBLX videos**.

It helps with Roblox game ideas, retention, discovery, ads, monetization, live ops, market research, packaging, onboarding, analytics, production, and iteration using patterns extracted from the public material.

> **Unofficial:** this project is not Tizzy RBLX, is not endorsed by Tizzy RBLX, and must not claim to speak for him. It models publicly observable reasoning patterns and public examples without inventing private views or experiences.

## Download / install

### One-click downloads

| Target | Download |
| --- | --- |
| ChatGPT / Codex | [tizzy-rblx-advisor-chatgpt.zip](https://github.com/Ticklect/tizzy-rblx-advisor/releases/latest/download/tizzy-rblx-advisor-chatgpt.zip) |
| Claude.ai | [tizzy-rblx-advisor-claude.zip](https://github.com/Ticklect/tizzy-rblx-advisor/releases/latest/download/tizzy-rblx-advisor-claude.zip) |
| Full universal package | [tizzy-rblx-advisor-universal.zip](https://github.com/Ticklect/tizzy-rblx-advisor/releases/latest/download/tizzy-rblx-advisor-universal.zip) |
| Checksums | [SHA256SUMS.txt](https://github.com/Ticklect/tizzy-rblx-advisor/releases/latest/download/SHA256SUMS.txt) |

### Claude.ai

1. Open this repo's **Releases** page.
2. Download `tizzy-rblx-advisor-claude.zip`.
3. Go to **Customize > Skills > + > Create skill > Upload a skill**.
4. Upload the ZIP and enable it.

### Claude Code

Inside Claude Code, run:

```text
/plugin marketplace add Ticklect/tizzy-rblx-advisor
/plugin install tizzy-rblx-advisor@tizzy-rblx-advisor
```

This follows Anthropic's documented marketplace + install flow.

### ChatGPT / Codex

**ZIP:** download `tizzy-rblx-advisor-chatgpt.zip` from Releases. ChatGPT ZIP upload is permission/workspace dependent; where enabled, eligible workspace owners/admins can use **Admin > Plugins > Add > Upload plugin**.

**Codex CLI:**

```bash
codex plugin marketplace add Ticklect/tizzy-rblx-advisor
codex plugin add tizzy-rblx-advisor@tizzy-rblx-advisor
```

**GitHub marketplace:** supported ChatGPT/Codex workspaces can import this repository directly:

```text
https://github.com/Ticklect/tizzy-rblx-advisor
```

The repository includes the OpenAI marketplace manifest at `.agents/plugins/marketplace.json` and the standard Agent Plugins `plugin.json`.

## What it covers

- game design and core loops
- PTR, bounce, D1/D7/D28 and discovery funnels
- monetization and economy guardrails
- live ops and update strategy
- market research and game-idea selection
- titles, icons, thumbnails and packaging
- onboarding and UX diagnosis
- MVP scope, team and execution
- public case studies and source provenance
- regression checks to reduce generic advice

## How it reasons

1. Establish the signal/proof.
2. Kill the bad assumption.
3. Classify the real bottleneck.
4. Reverse-engineer the mechanism.
5. Make the smallest useful bet.
6. Name the metric or player behavior that should move.
7. Check second-order risks.
8. Separate current platform facts, user data, public examples, and inference.

## Structure

```text
plugin.json                         Agent Plugins manifest
.codex-plugin/plugin.json          ChatGPT/Codex metadata overlay
.agents/plugins/marketplace.json   ChatGPT/Codex marketplace
.claude-plugin/plugin.json         Claude Code plugin manifest
.claude-plugin/marketplace.json    Claude Code marketplace
skills/tizzy-advisor/SKILL.md      Main skill
skills/tizzy-advisor/references/   Topic modules, source map and evals
dist/                              Ready-to-upload ZIPs
```

## Current-platform facts

Roblox discovery, ads, monetization tools, safety gates and other platform behavior can change. The skill treats the video corpus as historical/public reasoning evidence and should verify current Roblox facts when they matter.

## Source provenance

See `skills/tizzy-advisor/references/source-map.md`. The repository contains distilled notes and original behavioral examples, not full copied transcripts.

## Version

Portable release: **3.0.2**.