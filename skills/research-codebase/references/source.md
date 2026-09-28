# HumanLayer source and adaptation

This skill is adapted from [HumanLayer research_codebase](https://github.com/humanlayer/humanlayer/blob/main/.claude/commands/research_codebase.md), selected by the user on 2026-09-28. It is distinct from Matt Pocock's general `research` skill.

- Pinned commit: `c2c31d656807cad9d389acfcbc19002733958218` (source file's latest change returned by GitHub on retrieval).
- Commit date: `2025-10-15T22:01:05Z`; retrieved: `2026-09-28`.
- [Pinned source](https://github.com/humanlayer/humanlayer/blob/c2c31d656807cad9d389acfcbc19002733958218/.claude/commands/research_codebase.md).
- Unmodified local copy: [upstream-research-codebase.md](upstream-research-codebase.md).
- Source SHA-256: `92adbe8276e81cd0ce1d53193a947b79b696a793e3c4febeb9f40e6e23158890`.
- Copyright (c) 2024, humanlayer Authors. [Original license notice](upstream-LICENSE); full [Apache-2.0 license](../LICENSE). No repository-root NOTICE was found at the pinned commit.

## Deliberate changes

| Original command | Portable skill |
| --- | --- |
| Claude command with `model: opus` | Standard skill metadata; runtime/role chooses the model |
| Always ask for a topic and wait | Start when the task already supplies the question |
| Named Task agents and TodoWrite | Preserve locator → analyzer/pattern/history responsibilities with available tools; parallel independent work when permitted, sequential fallback reported |
| HumanLayer thoughts and `hack/spec_metadata.sh` | Existing repository research convention and directly verified git metadata; no required HumanLayer CLI |
| Always `humanlayer thoughts sync` | Save locally; publication/sync needs separate authorization |
| Permalinks inferred from main/pushed state | Verify remote commit/file and matching lines; identify uncommitted snapshots |
| Completed report template | Complete/partial/blocked reflects actual coverage and access limits |

The current-state-only focus, full reading of named files before delegation, source-first synthesis, cross-component tracing, historical context, precise references, and append-only follow-up sections are retained. Research feeds Project Lead SA; it does not replace domain modeling, grill, spec, or approval.

Read the archived command only when checking provenance or updating this adaptation. Its original runtime-specific instructions do not override `SKILL.md`.
