# Orca capability research — 2026-09-25

Scope: read-only research of the installed Orca and first-party documentation. No Run/Task/Dispatch creation, agent prompt, account change, app restart, worktree mutation, settings change, or external message was performed. No credentials or transcript contents were printed. This note is research, not an approved design.

## Recommendation for the first grill

Use one small persistent delivery controller with one explicitly owned Orca coordinator identity. Let Orca own worker placement, Task/Dispatch lifecycle, terminal/session resources, and mailbox delivery; let the controller alone own feature states, artifact versions, G1/G2/G3, finding resolution, publication outbox, and review/fix budgets. A valid Orca `worker_done` is an execution settlement, never PR Pass.

For MVP, run the controller as a foreground command in a dedicated Orca terminal on this Mac, with a persistent run store and explicit `resume`. This is a recommendation, not yet a user decision. It keeps a real coordinator identity available and avoids promising that an arbitrary launchd service can borrow another agent's terminal. A lead agent can produce design/finding judgments through tasks or invoke the deterministic controller; it should not independently dispatch a second outer loop.

Orca's current native Run explicitly does not schedule/place workers. The old scheduler verbs are retired. Therefore this architecture does not need a second agent orchestration framework. Orca decision gates are human/DAG decisions, not the three delivery evidence gates. [S3, S4, S8]

## Identity and version — proven locally

- `/usr/local/bin/orca` is a symlink to `/Applications/Orca.app/Contents/Resources/bin/orca`.
- The launcher is a shell script executing bundled Electron in Node mode against `app.asar.unpacked/out/cli/index.js`; this is the desktop-bundled CLI, not an unrelated npm executable. [S1]
- Bundle identifier: `com.stablyai.orca`; app and runtime version: `1.4.209`; macOS arm64.
- Build ID: `1.4.209-ee1c52207000c7d70282549c73e9945bd1cec1e8-arm64`; source commit: `ee1c52207000c7d70282549c73e9945bd1cec1e8`; daemon protocol: 36. [S2]
- Bundled update metadata names GitHub owner/repo `stablyai/orca`; first-party repository and website corroborate the identity. [S2, S7]
- `orca status --json` succeeded: desktop running, runtime `ready`/reachable/connected, graph `ready`. Advertised capabilities include `orchestration.contract.v1`, launch preferences, worker stop verdict, structured read, fleet snapshot, release archive, terminal prompt delivery, terminal/worktree idempotency, and agent-session structured/resume history. Capability advertisement is not an end-to-end test of each operation.
- `orca agent-context --json` succeeded with `schemaVersion: 1`, `commandCount: 236`. Snapshot saved at [command schema snapshot](evidence/orca-command-schema.json); it contains command metadata, not secrets.

## Read-only probes and their observed results

All executable references below mean `/usr/local/bin/orca` exactly.

| Probe | Observed result | What it proves / does not prove |
| --- | --- | --- |
| `orca status --json` | exit 0, runtime ready | Current local connection and advertised version/capabilities; not lifecycle recovery |
| `orca agent-context --json` | schema v1, 236 commands | Exact installed command surface |
| `orca skills list --json` | bundled `orchestration`, `orca-cli`, etc. | Version-matched guides are available |
| `orca skills get orchestration` plus named references | exit 0 | Current lifecycle and caller obligations |
| `orca orchestration run-current --json` | exit 0, `run: null` | Current caller identity resolves; it is not bound to a Run |
| `orca orchestration run-list --limit 10 --json` | exit 0, one existing Run | Native stored Run inspection works; objective was suppressed in research output |
| `orca orchestration worker-list --limit 5 --json` | exit 0, zero workers | Fleet read endpoint works; real worker settlement not tested |
| `orca repo list --json` | exit 0, one registered repo | Orca repository discovery works |
| `orca worktree current --json` | current path `/Users/johnson.chiang/workspace/gigaxfer`, no linked issue/PR, empty git branch/head | Orca recognizes this workspace; these empty fields do not establish a usable target Git repo |
| `orca terminal list --json` | connected/writable Claude and Codex identities in current workspace | Live CLI agent presence; previews/titles were not printed |
| `orca search --index-status --json` | `enabled: false`, `phase: idle` | Session-history search is disabled; no search performed and no setting changed |
| `orca serve --help` | foreground headless runtime documented | Command availability, not successful separate server deployment |

The current environment contains `ORCA_TERMINAL_HANDLE` and `ORCA_PANE_KEY`. Without printing their values, we compared the handle to `terminal list`: it belongs to a live connected/writable Codex terminal in the current workspace. Thus this shell has a genuine existing Orca context. Research subprocesses inherit the same identity; that does not authorize multiple consumers to share its inbox.

## Capability assessment

### Programmatic dispatch: documented and exact-build source confirmed; no launch test yet

Preferred dispatch is `orchestration worker-start`, not low-level `dispatch --inject`. It composes task attempt creation, placement, agent readiness, prompt injection, and supervision. It returns exit 0 only when state is `ready`; failures include stage, effects, residual resources, and recovery actions. Do not blindly retry a nonzero start. [S3, S4, S5]

```text
orca orchestration run-create --objective <text> --json
orca orchestration task-create --spec <self-contained-brief> --deps <json-array> --run <run-id> --json
orca orchestration worker-start --task <task-id> --worktree <exact-selector> --agent claude --run <run-id> --json
orca orchestration worker-start --task <task-id> --worktree <exact-selector> --agent codex --run <run-id> --json
```

`--model`/`--effort` exist for fresh supported agents, but current guide says only pass a model when the user chose one; compare requested vs effective launch values. Otherwise inherit configured defaults. Fresh worker does not necessarily mean a new worktree or even a PTY: startup follows the user's agent tab setting. Use orchestration verbs to interact regardless of launch mode. [S3, S4]

Task specs have a bounded prompt size in the installed code. Keep the brief self-contained, with paths/version digests to substantial artifacts rather than stuffing an entire spec and diff into argv. [S6]

### Agent status: read endpoint proven; worker semantics documented

```text
orca orchestration worker-list --run <run-id> --json
orca orchestration worker-show --dispatch <dispatch-id> --json
orca orchestration worker-read --dispatch <dispatch-id> --source auto --limit 50 --json
orca orchestration task-list --run <run-id> --json
```

Fleet `projection.liveness` is agent evidence; `worker-show.observation.status` is PTY liveness. Preserve `live`, `exited`, and `unverifiable`. A live terminal can contain a dead/stuck agent. Missing/unknown status, network loss, and elapsed timeout are not proof of death. Paginate `worker-list` beyond 100 rows. [S3, S4]

### Structured results: native transport documented; delivery schema remains a gap

The installed CLI supports `--payload <json>`, or the structured flags `--task-id`, `--dispatch-id`, `--outcome succeeded|failed`, `--files-modified`, `--report-path`, and `--phase`. Raw payload and structured flags cannot be combined. Exact-build `message-payload.js` builds those JSON fields. Native task-update has a JSON result field, but workers must not manually mark tasks completed after valid `worker_done`, which settles them automatically. [S3, S5]

No native feature-result JSON schema, spec/design/head binding, TDD evidence contract, finding identity, or G1/G2/G3 evaluator was established. Those need the delivery controller's own schema. Proposed worker contract: write and atomically publish the immutable result artifact first, include attempt/SHA/artifact digests, then send `worker_done` with its real report path. The controller validates the file and evidence separately from the native execution outcome. A reviewer can report native `succeeded` while its review verdict is `changes_required`.

### Notifications: durable mailbox semantics documented; delivery not exercised

```text
orca orchestration send --type worker_done --subject <text> --body <three-sentence-summary> --task-id <id> --dispatch-id <id> --outcome succeeded --report-path <absolute-path> --json
orca orchestration check --terminal <own-handle> --run <run-id> --peek --json
orca orchestration check --terminal <own-handle> --run <run-id> --wait --timeout-ms 30000 --json
orca orchestration check --terminal <own-handle> --run <run-id> --ack <delivery-id> --json
```

A successful send proves durable enqueue, not reading/turn start. Wake/nudge is best effort. Consuming `check` returns FIFO deliveries and replays the same batch until ack; process every message before ack. Type filters are wake conditions and do not filter rows out of a delivered batch. `--peek`/`--all` are read-only. Workers must use exact IDs, executable, handle and dispatch capability in the injected preamble; do not reconstruct those arguments from persisted examples. [S3, S4]

Controller should reconcile task/dispatch state and result artifacts periodically even without notification. GitHub publishing needs a separate persistent outbox keyed by run/version/report, since Orca notification does not publish reviews or prove GitHub success. Desktop idle notifications are UI signals with different behavior for native chat; never use them as completion evidence. [S10]

### Resume and lifetime: partly documented, destructive validation deliberately deferred

Run binding and recovery commands exist:

```text
orca orchestration run-use --id <run-id> --json
orca orchestration request-show --request <request-id> --json
orca orchestration worker-start --task <task-id> --retry-of <failed-dispatch-id> --worktree <explicit-selector> --agent <agent> --json
```

`run-use` restores coordinator binding; it is not proof a worker process resumed. Recovery uses `--retry-request` with the exact mutation identity. Receipt states are `completed`, `pending`, and `absent`; absent is explicitly not proof nothing happened. A retries circuit breaker applies after three consecutive failures for the same native Task. Do not evade it by creating an unrelated task/run. [S3, S4, S6]

The first-party session-restore page documents PTYs surviving normal app quit/update/app crash in a background daemon, with warm reattachment, but host reboot/daemon crash ends processes. We did not quit/restart the app or crash any process. This latest documentation is not an observed test of 1.4.209. The installed source includes provider-specific session resume construction; there is no generic public `orca session resume` verb in the captured command schema. `orca search` can return resume commands, but history indexing is disabled locally and must not be assumed available. [S6, S9]

`orca serve --help` confirms a headless runtime can run in the foreground until Ctrl+C. Whether the local desktop control RPC remains reachable while app UI is closed was not tested. MVP should pause dispatch on runtime unavailable, preserve workers as unknown, and reconcile after reconnect. Do not start a second local runtime over the same state as a workaround without testing ownership.

### Coordinator identity: important integration constraint

Exact installed `terminal-identity.js` resolves a supplied own handle or `ORCA_TERMINAL_HANDLE`. Coordinator calls validate the environment handle and can recover it through the persisted pane identity. If no identity exists, it uses an unambiguous terminal lookup; a structured session without identity is refused specifically to prevent consuming another pane's mailbox. `run-create`, `run-use`, and `worker-start` all resolve coordinator identity. [S5, S11]

The current shell resolves successfully, but this does not prove an unrelated launchd daemon will have a valid coordinator. Recommended MVP keeps the small controller in its own Orca terminal. Only that process consumes its Run inbox. On replacement coordinator startup, use an explicit owned identity plus `run-use`, acquire the controller store lock, then reconcile before mutations. Persistent feature state must not use the terminal handle as the run's primary key; runtime handles can change.

### Worktrees: read recognition proven; create/isolation documented

```text
orca worktree list --repo <exact-selector> --json
orca worktree show --worktree <exact-selector> --json
orca orchestration worker-start --task <task-id> --worktree new-child --name <name> --agent claude --setup run --json
orca orchestration worker-start --task <task-id> --worktree new-top-level --repo <exact-selector> --name <name> --agent codex --setup run --json
```

New worktrees use agent-first creation; current/existing workspaces do not rerun setup. Worktree identity is the whole `<repo-id>::<absolute-path>` value, not repo ID alone. Branch base, Orca lineage, filesystem isolation, and orchestration ownership are distinct decisions. Existing settings can start setup hooks alongside the agent or wait for success, so do not assume readiness means setup finished. Current folder/workspace recognition does not establish that Git worktree creation will work here. [S3, S4]

Use isolated implementation worktrees for parallel editors; reviewer should inspect an isolated checkout fixed to integrated PR head and have no write authority to implementation branch. Native worker-start does not expose a reviewer read-only permission flag; enforcement through launch/config/adapter policy needs a spike.

## Minimum adapter shape (proposal)

1. Pin the absolute Orca executable and record app/runtime version/capabilities at run start. Refuse unsupported lifecycle semantics; do not import private RPC internals as the MVP public API.
2. Invoke CLI with argv arrays and parse stdout JSON plus exit status; keep diagnostic stderr separate. Store native run/task/dispatch IDs alongside delivery run/task/attempt IDs.
3. Implement discover, create-task, start-worker, observe-worker, read-result, consume/ack, and recover; route lifecycle resources only via exact Dispatch ID.
4. Own durable delivery state, schema validation, immutable evidence manifests, GitHub publication outbox, gate invalidation, retries and controller lock. Native lifecycle settlement updates execution state only.
5. On each reconcile: read current PR head/base and artifact versions; inspect expected dispatches; import valid durable result files; fetch actual CI; publish pending reports; evaluate deterministic transitions. Use mailbox only as a wake optimization.
6. On timeout: enter delivery Blocked/needs-attention and preserve uncertain worker authority; do not silently launch a competing editor. Dispatch retries only after native authoritative failed/stopped evidence. On accepted completion, reuse/release according to current native contract; archive output before release.

## Spikes required before claiming real integration

- One genuine native Run and harmless worker start in an approved target worktree, persisting exact receipt and result artifact; verify Claude and Codex both honor output contract and lifecycle preamble.
- Dedicated non-agent shell controller identity: can its Run start workers and consume its own mailbox as intended? Test `run-use` under explicit replacement identity without a second consumer.
- Simulate controller crash around task creation/start and before/after ack. Verify native request recovery plus controller outbox prevent duplicate work. Pay attention to crash before first request ID is durably captured; do not assume exactly-once from `--retry-request` documentation alone.
- Structured/native-chat workers vs PTY workers: confirm result artifact paths, release accounting, and any permissions prompt behavior on actual configured launch mode.
- Reviewer write restriction and frozen head checkout: prove no implementation branch mutation is possible through its authorized tools; detect workspace dirtiness and head mismatch anyway.
- Headless service/app quit behavior is a separate operational spike if the user requires continuing control while Orca is closed. No such continuity guarantee is proven by read-only research.
- Reboot/cold recovery: persistent evidence and task state must suffice even if agent session resume is unavailable. App upgrade changes CLI and runtime together; rerun capability compatibility checks.

## Source index

- **S1** — local `/usr/local/bin/orca` symlink; `/Applications/Orca.app/Contents/Resources/bin/orca` launcher.
- **S2** — local `/Applications/Orca.app/Contents/Info.plist`, `Resources/orca-local-build.json`, `Resources/app-update.yml`; `orca status --json`.
- **S3** — version-matched `orca skills get orchestration`; `orca skills get orca-cli`.
- **S4** — version-matched `orca skills get orchestration --reference references/coordinator-loop.md`, `references/messaging-and-gates.md`, `references/placement-and-remote.md`, `references/recovery-and-cleanup.md`.
- **S5** — installed exact-build files under `/Applications/Orca.app/Contents/Resources/app.asar.unpacked/out/cli/handlers/orchestration/`: `terminal-identity.js`, `run-handlers.js`, `worker-launch-handler.js`, `message-payload.js`, `mutation-request.js`; `out/cli/runtime/metadata.js`.
- **S6** — installed exact-build files under `app.asar.unpacked/out/shared/`: `orchestration-rpc-contract.js`, `orchestration-mutation-request.js`, `orchestration-worker-start-prompt-budget.js`, `agent-resume-launch-command.js`; command schema [command schema snapshot](evidence/orca-command-schema.json).
- **S7** — [official repository](https://github.com/stablyai/orca); identity corroborated with installed updater metadata before using the site.
- **S8** — [official CLI overview](https://www.onorca.dev/docs/cli/overview), [official orchestration guide](https://www.onorca.dev/docs/cli/orchestration). Web docs may be newer than installed version; installed help/guides take priority for exact argv.
- **S9** — [official session restore](https://www.onorca.dev/docs/model/session-restore), [ways to run](https://www.onorca.dev/docs/ways-to-run), [session history](https://www.onorca.dev/docs/agents/session-history).
- **S10** — [official notifications](https://www.onorca.dev/docs/notifications).
- **S11** — [terminal identity source pinned to installed build commit](https://github.com/stablyai/orca/blob/ee1c52207000c7d70282549c73e9945bd1cec1e8/src/cli/handlers/orchestration/terminal-identity.ts), also fetched as raw first-party source and matched to installed compiled behavior.

Research did not inspect local account credential files, runtime authentication metadata contents, terminal previews, or agent transcripts. Ancestor `/AGENTS.md`, `/CLAUDE.md`, and corresponding files under `/Users`, `/Users/johnson.chiang`, `/Users/johnson.chiang/workspace`, and the current workspace were checked; none existed at those exact paths during this probe.
