---
name: research-codebase
description: Research how an existing codebase works, trace component interactions, and write an evidence-backed Markdown report before requirements or design work. Adapted from HumanLayer's research_codebase command; focused on current behavior, not a code review or implementation plan.
---

# Research Codebase

Document what exists, where it lives, how it works, and how components interact. Ground conclusions in fresh source inspection; use past research as historical context. This report supplies evidence to SA, domain modeling, and design; it does not approve requirements or decide future architecture.

Modified from HumanLayer's command for portable agent runtimes. Copyright (c) 2024, humanlayer Authors. Licensed under Apache-2.0; see [LICENSE](LICENSE). For provenance, updating, or comparison with the original, read [references/source.md](references/source.md). The archived upstream command is reference material, not a second set of runtime instructions.

## Inputs and scope

Use the research question, repository, named files/ticket, and requested output location from the task. Ask only for a missing question or ambiguous target needed to start. Read repository instructions before research.

Use repository search, file reads, read-only git commands, and available read-only issue/document access. Write the research report only. Source edits, tests or prototypes, commits, publication, and synchronization need their own task scope. Do not add unsolicited critique, root-cause analysis, or improvement proposals. If requested, separate that analysis from observed facts.

## 1. Read the supplied context

Read directly named files in full in the main agent's context before delegating. For large files, read in contiguous portions until complete; truncated output is not a complete read. If a named source is unavailable, record the limitation and whether it blocks the question.

Identify the relevant flows, entry points, data/state, dependencies, and tests. Keep research bounded to the question rather than inventorying the entire repository.

Done when the question, scope, applicable instructions, and available starting evidence are clear.

## 2. Locate, then trace

Break the question into focused areas. Where supported and permitted, delegate independent areas to read-only subagents and run them in parallel. Keep dependent analysis after its locator results. Assign functions rather than assuming HumanLayer's named agents exist:

- Locator: find the relevant code, tests, configuration, and documentation.
- Analyzer: trace how a specific flow works, including relevant error paths and state transitions.
- Pattern finder: locate existing examples and callers without grading them.
- History researcher: find relevant decisions and past research, including `thoughts/` when present.

Give each delegate the question, repository/snapshot, bounded topic, and expected findings with paths, symbols, and line references. They document current behavior and do not change source files. Use available generic subagents; if delegation is unavailable or prohibited, perform these passes sequentially and report that limitation. No particular model, agent name, or task-list tool is required.

External research is outside the default codebase pass. Use it when the user requests it or governing instructions require verification, and include supporting URLs. Access tickets only when relevant and through already available tools.

Done when each relevant area has source-backed findings or an explicit unresolved gap.

## 3. Reconcile the evidence

Collect every dispatched task's result before the final synthesis. A failed or timed-out task is a gap, not a completed investigation; continue useful independent work and report the effect on coverage.

Verify key citations yourself and connect entry points, components, callers, and state/data flows. Distinguish observed behavior, inference, and historical intent. Code describes the current implementation; it does not override business requirements. Present conflicts between code, documents, and the user's description without silently choosing a requirement.

Test source shows what is asserted, not proof that tests passed. Label inspected tests separately from any execution evidence already supplied.

If a path came from `thoughts/searchable/`, remove only the `searchable/` segment and verify the resulting path. Preserve personal/shared subdirectories exactly.

Done when the report can answer the question with checked evidence and clearly bounded uncertainty.

## 4. Capture the snapshot and save the report

Gather metadata with available read-only git/file tools before writing. Record repository identity, current commit/branch, timestamp with timezone, and relevant working-tree changes. If no commit or branch exists, use `null` and explain why. Identify the researching agent without guessing a person's name or model.

Follow the repository's existing research location and naming. Otherwise use `docs/research/YYYY-MM-DD-topic.md`. Reuse the existing report for follow-ups to the same investigation. Repositories using HumanLayer thoughts may retain `thoughts/shared/research/YYYY-MM-DD-[ticket-]topic.md`; the ticket is optional. Do not create a parallel research hierarchy just to satisfy this skill.

Use YAML frontmatter with actual values:

- `date`, `researcher`, `repository`, `topic`, `tags`.
- `git_commit`, `branch`, `working_tree` (clean, dirty, or unavailable), and relevant changed paths or content hashes when findings depend on uncommitted files.
- `status` (`complete`, `partial`, or `blocked`), `last_updated`, `last_updated_by`.

The body covers the research question, a direct summary, detailed findings and connections, code references, current architecture/patterns, relevant history/related research, and open questions/limitations. Omit irrelevant historical sections. Mark future proposals as such only when the task requested them; they are not findings about existing behavior.

Use relative file links plus line numbers and symbols. Add GitHub commit permalinks only after verifying the repository, remote availability of that commit/file, and that the cited lines match that committed version. Being on `main` is insufficient. For dirty or unpushed findings, cite the local snapshot honestly; redact credentials from any repository URL.

Done when the saved report has real metadata, traceable citations, and a status consistent with its coverage. Do not run repository metadata scripts without inspecting them, or automatically run `humanlayer thoughts sync`.

## 5. Return the handoff

Return the report path, the answer in a few sentences, key evidence, and any gaps affecting the next stage. `complete` means the scoped research question is answered; it does not mean SA is approved or implementation is verified.

Use `partial` when useful findings are saved but part of the question remains unverified. Use `blocked` when missing access, sources, or a necessary decision prevents a reliable answer. Name the missing item, its impact, and the minimum next action; keep unaffected findings available.

For follow-ups, recheck current source and append a dated section to the same report. Update `last_updated`, `last_updated_by`, and `last_updated_note`; if the snapshot changed, record the new commit/working-tree context in that section rather than relabeling old findings as current. Publication or sync happens only when separately authorized.
