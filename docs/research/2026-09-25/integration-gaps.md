# Orca Delivery integration gaps — bounded research, 2026-09-25

本輪以 Orca 1.4.209 安裝檔、Codex CLI 0.153.4 本機 help、既有 probe evidence 與官方文件為來源。沒有啟動 agent、建立 terminal/worktree、修改設定、送出 orchestration message 或操作使用者的既有 terminals。唯一動態 sandbox probe 是直接執行 read-only Orca CLI 查詢，不包含 LLM turn。沒有讀取 runtime metadata/auth token 的內容或 credentials 檔。

## 可直接採用的結論

1. **已證明：Codex 的 read-only sandbox 能在只加單一 Unix socket allowance 時連上 Orca。** 本機 `codex sandbox -P :read-only --allow-unix-socket <exact-socket> -- <read-only-cli>` 是正式提供的功能。相同查詢在沒有 allowance 時失敗，增加 allowance 後成功。這支持 AF_UNIX sandbox 限制為先前 IPC 失敗的主要假說。
2. **尚未證明：真正 TUI worker 能用同樣有限权限送出 `worker_done`。** `--allow-unix-socket` 是 `codex sandbox` utility 的 flag，不在已讀取的 TUI root help 中。不能直接塞入 Orca `worker-start` 或 Codex TUI argv 當成已支援。
3. **重要限制：單一 socket allowance 只限制連線目標，不限制 RPC 方法。** Orca CLI 經這個 socket 可呼叫整個 runtime API；不能因此聲稱 reviewer 只拿到 lifecycle 權限，或 reviewer 的所有工具都無法改其他工作樹。是否接受此信任邊界是設計決策。
4. 新 repo 的 repo/project/host setup **確實存在且 ready**，但 worktree inventory 仍沒有其 path，`worktree show path:<newrepo>` 仍拒絕。不能捏造完整 workspace ID，也不能從 setup ready 宣稱可派工。
5. `current` 語意存在不同 command path：一般 CLI workspace selector 會從 cwd/inventory解析；`worker-start` 把原字串送到 server，並另外解析 coordinator handle。因此 controller 必須使用經 inventory 與 returned receipt 核對過的完整 workspace identity，不能混用 shell cwd、coordinator workspace、repo ID。

## 既有 probe 的事實（非本輪重做）

讀取：

- `docs/research/2026-09-25/runtime-probe.md`
- `evidence/codex-probe-result.json`
- `evidence/probe-final-fleet.json`
- `evidence/probe-cleanup.json`

Claude 的 artifact、native settlement、release 已成功。Codex artifact 的 `status` 是 `blocked`，`run_id` 是 null；runtime CLI check/send 失敗，未偽造 native completion。Native task/dispatch 已 fence，operator 建立的 exact terminal 已關閉。結果不應升格成 feature gate 或完整 Codex integration 成功。

## A. Sandbox / IPC：事實、推論、未驗證

### 已確認本機介面

`/Users/johnson.chiang/.local/bin/codex --version`：`codex-cli 0.153.4`。

`codex sandbox --help`：

```text
Usage: codex sandbox [OPTIONS] [COMMAND]...
-P, --permission-profile <NAME>
-C, --cd <DIR>
--allow-unix-socket <ALLOW_UNIX_SOCKETS>
--log-denials
```

其中 socket flag 的 help 說明是允許 sandboxed command bind/connect 指定根路徑的 AF_UNIX sockets，可以重複指定。這個版本沒有 `sandbox macos` 子命令；`codex sandbox macos --help` 會把 `macos` 當要執行的程序，回 `sandbox-exec ... No such file or directory`，exit 71。未執行 agent。

起初使用舊 `-c sandbox_mode="workspace-write"` 搭 `codex sandbox`，解析即失敗：缺少 `--permission-profile`，exit 2。這是 utility invocation 不完整，不是 socket probe 結果。改用正式 builtin `:read-only` 才得到下面有效對照。

### Read-only 對照 probe（已執行）

先以檔案種類掃描 Orca user-data 目錄，找到本次已存在的 socket 檔案；只讀取名稱及 `lstat` 檔案種類，沒有開啟 `orca-runtime.json`。本次 endpoint 是：

```text
/Users/johnson.chiang/Library/Application Support/orca/o-24664-4f17.sock
```

此名稱有程序/runtime 成分，**不可硬編碼為長期設定**。

精確命令（cwd 均為新 repo）：

```text
/Users/johnson.chiang/.local/bin/codex sandbox -P :read-only -C /Users/johnson.chiang/workspace/orca-delivery -- /usr/local/bin/orca status --json

/Users/johnson.chiang/.local/bin/codex sandbox -P :read-only -C /Users/johnson.chiang/workspace/orca-delivery --allow-unix-socket '/Users/johnson.chiang/Library/Application Support/orca/o-24664-4f17.sock' -- /usr/local/bin/orca status --json

/Users/johnson.chiang/.local/bin/codex sandbox -P :read-only -C /Users/johnson.chiang/workspace/orca-delivery -- /usr/local/bin/orca orchestration run-list --limit 1 --json

/Users/johnson.chiang/.local/bin/codex sandbox -P :read-only -C /Users/johnson.chiang/workspace/orca-delivery --allow-unix-socket '/Users/johnson.chiang/Library/Application Support/orca/o-24664-4f17.sock' -- /usr/local/bin/orca orchestration run-list --limit 1 --json
```

Sanitized observations:

| Query | Socket allowance | Exit | JSON evidence |
| --- | --- | --- | --- |
| status | none | 0 | `ok:true`, runtime `state:"starting"`, `reachable:false`, no app version |
| status | exact one | 0 | `ok:true`, runtime `state:"ready"`, `reachable:true`, `appVersion:"1.4.209"` |
| run-list | none | 1 | `ok:false`, error `runtime_unavailable`, message `Could not connect to the running Orca app. Restart Orca and try again.` |
| run-list | exact one | 0 | `ok:true`, returned one Run; objectives and IDs suppressed |

Both successful and unsuccessful sandbox subprocesses emitted the same Electron `task_name_for_pid ... failure (5)` diagnostic on stderr. Because the scoped query succeeded with that warning present, it is not sufficient evidence of the IPC failure cause. No lifecycle mutations were attempted. The tests did not write a canary to prove read-only enforcement; they selected Codex's built-in `:read-only` profile and used only read operations.

**推論：** baseline failures plus exact-socket success strongly support a socket allowlist gap, rather than the runtime being offline. The installed Orca transport collapses socket errors into generic `runtime_unavailable`, so the original error text alone did not prove this. The probe does not establish all TUI/provider/config combinations.

### Exact installed Orca transport source

`/Applications/Orca.app/Contents/Resources/app.asar.unpacked/out/cli/runtime/transport.js`:

- Selects `unix` or `named-pipe` transport from metadata.
- Calls Node `net.createConnection(transport.endpoint)`.
- Socket `error` becomes generic `runtime_unavailable` with the message seen in the probe; OS error detail is discarded.
- After connection, CLI itself performs the existing authentication handshake. No need for controller code to extract or relocate the authentication token.

`runtime/metadata.js` and `shared/runtime-bootstrap.js` establish that the bundled CLI loads its own normal user-data metadata. We inspected **program code**, not the metadata file's values.

### Named permission profiles: documented but not a proven TUI recipe

Official OpenAI documentation supports named filesystem/network profiles and a per-path `network.unix_sockets` allowlist. It also explicitly says profiles do not compose with legacy `--sandbox`/`sandbox_mode`; the legacy setting wins when present. [O1, O2]

One in-memory command-line config attempt using a dotted key containing the full socket pathname was rejected by Codex's override parser before any query: `unknown variant ... expected allow or deny`, exit 1. It should **not** be copied as a working recipe. The failure is consistent with the CLI treating dots in the socket path as override path separators. We stopped instead of continuing configuration experiments.

No global or project config was changed. A narrow scan of `~/.codex/config.toml` found no named permission profile sections; this is only that file, not a complete effective-config audit.

**最小後續測試（未執行）：** define a session-only named profile as one structured TOML table value passed through argv, or a task-local approved profile file, extending `:read-only` and allowing exactly the current socket. First validate it with the non-agent `codex sandbox -P <profile> -- orca orchestration run-list` query, then separately run one bounded TUI worker with explicit delivery IDs. Do not combine with `--sandbox workspace-write`, enable global network access, or use an all-sockets allowance. Passing utility validation is prerequisite evidence only, not proof of reviewer isolation.

### 是否已有正式 lifecycle-only controller bridge？

**已查到：** Orca version-matched guide requires dispatched workers to send their own `worker_done` with injected Task/Dispatch identity, exact CLI/caller/capability, and outcome. Native success report is an execution settlement. Generic MCP registration is documented by Orca; it is not documentation of an Orca lifecycle-only MCP bridge. [R1, R2]

**沒有在本次有界來源集合中找到：** sandbox-safe lifecycle-only IPC endpoint, a worker report spool that native Orca automatically settles, or a documented controller API that may impersonate worker completion. Do not interpret this as proof that no such product feature exists anywhere; it is currently **unestablished** for installed 1.4.209.

**設計選項（尚未定案）：** a new tightly scoped bridge could accept only current-attempt status/result references and preserve the sandbox around code commands, but it would be a new adapter to design and verify, not existing Orca functionality. It must not expose arbitrary CLI argv, broad RPC, credential reads, arbitrary report paths, or coordinator impersonation. Persisting a result artifact and reconciling it remains valid delivery behavior, but must not fabricate native `worker_done`/completed. If strict reviewer tool isolation is mandatory, choose a controller-owned execution/result channel with an explicit contract rather than quietly broadening Orca RPC access.

## B. Repo/project/workspace placement

### 本輪 read-only inventory 事實

```text
orca repo list --json
orca project list --json
orca project setups --json
orca worktree list --limit 100 --json
orca worktree show --worktree path:/Users/johnson.chiang/workspace/orca-delivery --json
```

Relevant sanitized rows:

```json
{
  "repo_id": "9001fee3-01b2-4854-9846-87b8e256941d",
  "project_id": "repo:9001fee3-01b2-4854-9846-87b8e256941d",
  "setup_id": "9001fee3-01b2-4854-9846-87b8e256941d",
  "host_id": "local",
  "path": "/Users/johnson.chiang/workspace/orca-delivery",
  "kind": "git",
  "setup_state": "ready",
  "setup_method": "imported-existing-folder"
}
```

All list calls returned exit 0. No matching new-repo worktree row appeared. `worktree show` returned exit 1 / `selector_not_found`. Its recovery says to list exact inventory values and explicitly warns that a bare repository ID is not a worktree ID.

The project/host setup exists; another `repo add` or setup metadata rewrite is not justified by this evidence. `kind:git` is correct for this feature repository; re-registering it as a plain folder to bypass Git would not validate Git worktree delivery.

### Correct command shape and identity checks

From installed `out/cli/worktree-project-target.js`, `handlers/project.js`, `selectors.js`, and `handlers/orchestration/worker-launch-handler.js`:

- `repo add --path <absolute-path>` registers repo metadata; `project setup-existing-folder --project <id> --host local --path <absolute-path> --kind git` imports host setup. `project setup-create` is independent setup metadata, not proof a workspace was opened or a worktree discovered.
- Ordinary `worktree create` accepts **either** `--repo <selector>` **or** `--project ... --host ...` / `--project-host-setup <id>`, never both.
- Project routing chooses a ready host setup and translates it to the exact repo selector.
- `worker-start` does not expose project/host-setup convenience flags; its creation route takes `--repo` plus `--worktree new-top-level|new-child`. For an existing workspace, give its exact discovered selector.
- `worker-start` CLI passes `current` unchanged to the runtime and separately resolves the caller; regular workspace CLI selectors normalize `current` through cwd and inventory. This explains why moving shell cwd must not be used to claim coordinator/workspace migration.
- A terminal receipt's full worktree identity must match dispatch placement, not merely have the same filesystem path. Same-path main/folder/suffixed workspace records need not be interchangeable.

**Future creation shapes, not executed this round:**

```text
orca worktree create --project-host-setup 9001fee3-01b2-4854-9846-87b8e256941d --name <approved-name> --base-branch <explicit-base> --agent <agent> --json

orca orchestration worker-start --task <task-id> --worktree new-top-level --repo id:9001fee3-01b2-4854-9846-87b8e256941d --name <approved-name> --base-branch <explicit-base> --agent <agent> --json
```

These are alternatives, not two sequential launches. The setup policy must be reviewed before real execution. Existing-terminal reuse should pass the exact worktree identity returned when that terminal was created, after verifying path/head/base against assignment; never synthesize `<repo-id>::<path>` when no returned inventory/receipt confirms it.

### Git executable / missing inventory

Parent probe established `/usr/local/bin/git` is an unusable Intel executable on this environment and `/opt/homebrew/bin/git` works. The installed bundled runtime contains a local Git execution route selecting literal binary `git`; no `--git-binary` placement flag appears in the installed command schema. Source snippets were read from `app.asar/out/main/index.js` via bundled Electron filesystem support; no app code was modified.

**推論：** Orca runtime resolving the wrong `git` can plausibly explain both worktree creation `-86` and missing Git worktree enumeration. **尚未證明：** the exact path/environment used by the already-running runtime, or that enumeration failure is the cause of the missing inventory. Changing the controller subprocess's PATH does not by itself establish a change to the already-running app's Git execution environment.

**最小後續測試（未執行）：** issue one repo-scoped read such as `orca repo search-refs --repo id:9001fee3-01b2-4854-9846-87b8e256941d --query main --json`, and correlate only that request with a sanitized runtime error to identify executable/OS failure. Compare `git worktree list --porcelain` using the known-good absolute Git to `orca worktree list --repo id:<id> --json`. If the runtime Git route is proven bad, decide on one explicit runtime launch/environment repair; do not silently replace system Git, restart the app during other work, install Rosetta, or repeatedly re-register repo metadata. After repair, first prove exact workspace inventory, then perform one new isolated worktree probe.

## Completion boundary for this research

The sandbox utility's narrow socket access is proven; actual TUI lifecycle and reviewer least-privilege are not. The new repo registration is proven; usable workspace/worktree placement is not. These two open integration contracts should remain explicit design risks and blocked acceptance checks, not be covered by Claude's unrelated successful probe.

## 2026-09-26 coordinator follow-up

The suggested repository-scoped read was executed once. `orca repo search-refs --repo id:9001fee3-01b2-4854-9846-87b8e256941d --query main --json` exited 0 / `ok:true` but returned `refs:[]`, `refDetails:[]`, `truncated:false`. In contrast, known-good `/opt/homebrew/bin/git worktree list --porcelain` showed this repository's actual main worktree at `/Users/johnson.chiang/workspace/orca-delivery`, branch `refs/heads/main`, HEAD `f66640057546eee65fec3cd40a4ea254a6359da7`. `orca status --json` still reported the same 1.4.209 runtime ready/reachable.

This confirms a discovery discrepancy; it does not prove the Git binary root cause, since this read returned no executable error. No app restart, Git replacement, setup rewrite, or worker launch was performed. Runtime repair remains a specific implementation prerequisite.

## Sources

- **P1** — `/Users/johnson.chiang/workspace/orca-delivery/docs/research/2026-09-25/runtime-probe.md` and listed evidence files.
- **C1** — installed `codex --version`, `codex --help`, `codex sandbox --help`; exact read-only subprocess probes above.
- **R1** — `/usr/local/bin/orca skills get orchestration`; references `placement-and-remote.md`, `messaging-and-gates.md`, `low-level-topology.md`; version matched to installed 1.4.209.
- **R2** — [Orca skills/MCP documentation](https://www.onorca.dev/docs/cli/skills). This establishes generic MCP registration only.
- **S1** — `/Applications/Orca.app/Contents/Resources/app.asar.unpacked/out/cli/runtime/transport.js`, `runtime/metadata.js`, `out/shared/runtime-bootstrap.js`.
- **S2** — same installed CLI tree: `selectors.js`, `worktree-project-target.js`, `handlers/project.js`, `handlers/orchestration/worker-launch-handler.js`, `handlers/orchestration/terminal-identity.js`.
- **S3** — installed `app.asar/out/main/index.js`, local Git binary selection and runtime worktree RPC routes; minified exact-build code, so no unproven broad root-cause claim.
- **O1** — [official OpenAI permission profiles](https://learn.chatgpt.com/docs/permissions): builtin profiles, inheritance, legacy-sandbox precedence. Latest documentation is not a substitute for local 0.153.4 validation.
- **O2** — [official OpenAI configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference): `permissions.<name>.network.unix_sockets`, feature/network distinctions.

No runtime metadata, dispatch capabilities, authentication tokens, account files, full transcripts, or terminal previews are included in this report.
