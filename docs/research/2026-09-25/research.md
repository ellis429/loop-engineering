# Orca Delivery：環境與決策前置研究

查核日期：2026-09-25（Asia/Taipei）。狀態：Research / Grill；尚未定案設計，尚未開始 feature 實作。

## 本次保存的研究

- [Orca 身分、控制介面與生命週期能力](orca-capabilities.md)
- [Matt / Superpowers 實裝版本、契約與整合限制](skills.md)
- [本機 Orca 命令 schema 快照](evidence/orca-command-schema.json)

研究最初保存在 gigaxfer 的 reports；使用者確認獨立專案後，已搬至 orca-delivery。研究查核的 target repo 仍是候選 demo，尚未選定 demo issue。

## 已確認的任務邊界

- Orca 是使用入口，串接 Claude Code 與獨立 Codex reviewer。
- Issue → research/design → implementation plan → TDD → PR → independent review + CI → fix/re-review，直到 PR Pass 或人工裁決。
- PR Pass 必須同時具備 G1 實作/TDD 證據、G2 零未解決 blocking findings、G3 必要 CI 全通過。
- 判定必須綁定適用的 spec/design/plan、review base 和當前 PR head。Red 可來自較早版本但需可追溯；最終 Green 與 regression 適用目前 head。
- Agent 完成、Orca task done、收到通知或本機測試成功皆不等於 feature Pass。
- Reviewer 或有紀錄的人工裁決才能解除 blocking finding；實作者不能自行關閉。
- 持久化、去重、reconcile、失敗恢復、發布失敗續傳及有界 retries 是 MVP 必需。
- 本次終點是 Ready for human acceptance，不包含 auto merge、close issue、release 或 deploy。
- 真實驗收必須有 review finding → fix → re-review；mock 結果必須明標，不能充作真實證據。

### 已確認：project / feature / task 層級（使用者後續確認）

- Project spec 定義整體目標、共用契約、系統限制與跨功能保證。
- 每個 feature 需要明確的需求定義，但不要求另建一份文件。Feature ticket 內文或它連結的文件皆可承擔 feature spec。
- Feature spec 引用適用的 project spec，只補本次交付行為、範圍、驗收條件、依賴及需求增量，避免複製整份規格。
- 每個可獨立驗收的 feature / 完整功能切片對應一個 PR；implementation tasks 是該 PR 的實作與派工單位。過大的 feature 先拆成各自可驗收的 feature tickets，而不是依 DB/API/測試等技術層機械拆 PR。
- 整體流程：project spec / 整體設計 → feature ticket + feature spec → feature design → implementation plan / tasks → feature PR。
- Reviewer 同時對照 project 契約與 feature 驗收條件，審查整合後 PR 的版本。改變 project 契約必須明確提出並確認，不可在 feature spec 中默默覆寫。
- 使用 OpenSpec 時，feature change 的 spec delta 與適用 baseline 一起構成審查依據；tasks 的完成紀錄不取代行為 spec。

這次「yes」確認上述層級與交接關係；不擴張為對先前開發落點、工具選擇、runtime、human checkpoint 或品質政策的默示回答。

[Feature 交接欄位草案](feature-handoff-contract.md) 將這些已確認語意整理成可審閱範例；具体欄位名稱仍待正式 schema 設計。

## 本機與目標候選 repo

目前 cwd：`/Users/johnson.chiang/workspace/gigaxfer`。
Origin：<https://github.com/yschiang/cross-dc-xfer>。
檢查時 main HEAD：`4e9cba4cd143cbc2e583b1fda41ba885970025c0`。

沒有在 cwd 或其 ancestors 找到 AGENTS.md / CLAUDE.md。repo 有 CONTEXT.md、docs/spec.md、docs/design、docs/adr、docs/superpowers/plans，以及舊夜間任務 goal.md / reviewer.md。goal.md 是舊 P01–P03 任務的規則，不能把其中已就寢、stacked PR、兩輪限制、自行 ruling 等套用成本次已授權決策。

已有未提交使用者工作：`docs/reports/overnight-report.md` 修改、`docs/reports/pr3-a94afc2-review.md` 未追蹤。研究未改動它們。
已有六個 feature/design worktrees；不得沿用它們派送新 controller 工作。

### 語言、測試與 CI

- Maven 多模組 Java 專案：`gigaxfer-core`、`gigaxfer-sync-service`，compiler release 21。
- `.github/workflows/ci.yml` 的 `test` job 在 Ubuntu + Temurin 21 執行 `mvn -B -ntp verify`，觸發為 pull_request 與 push main。
- 另有 Pages workflow，不能未經政策判定就當作每個 PR 的必要 check。
- 本機預設 `/usr/local` Java 17 執行失敗：`Bad CPU type in executable`。
- repo 的環境指引已有正確 arm64 toolchain；實測 `/opt/homebrew/bin/mvn -version` 為 Maven 3.9.16 / Java 27 / aarch64，`/opt/homebrew/bin/git --version` 為 2.55.0。
- 子行程可指定 `/opt/homebrew/bin` 與 `/opt/homebrew/opt/openjdk/libexec/openjdk.jdk/Contents/Home/bin`，無需修改使用者 shell 設定。本機 JDK 27 不等於 CI 的 Java 21 runtime 驗證。
- 已在上述 main HEAD 以正確 toolchain 執行 baseline。首次 `mvn -o -B -ntp verify` 在 Spring Boot repackage 失敗，原因是兩個 plugin dependencies 未快取；測試本身無失敗。接著執行與 CI 相同的 `mvn -B -ntp verify`，31.625 秒 BUILD SUCCESS，132 + 70 = 202 tests，Failures / Errors / Skipped 皆 0，兩個 module 成功。此為現況基線，不是本次 feature 的 TDD 或 CI 證據。
- 原始 logs：[offline log](evidence/maven-offline.log) 與 [successful verify log](evidence/maven-verify.log)。本機執行 Java 27，CI Java 21 的差異仍保留。

### GitHub 權限與實際讀取

`gh` 2.101.0，keyring 登入，OAuth scopes 包含 repo/workflow。只記錄能力，不保存 token。
Repository API 回傳 pull/push/triage/maintain/admin 為 true。

已成功讀取：repository metadata、open issues、open PRs、issue comments、PR reviews、Actions workflows、head 的 check-runs 與 commit statuses。

PR #11 head `2a0ab7f5d08f6b7a9e04eb085ea1bbd234101ca7` 有 github-actions 的 `test` completed/success，且 API check-run head_sha 相符。這是既有 PR 的環境證據，不是本次 gate 證據。
`main` required_status_checks API 回 Branch not protected，rules API 回空陣列。必要 checks 必須以明確 repo policy 設定，不能把沒有保護規則或空 check list 當 success。
commit statuses API 在 statuses=[] 時回 state=pending，而 Checks API 有成功 check；adapter 必須分清兩種來源。

Issue/PR/comment/review 寫入權限依 scopes 與 repo permissions 可用，但此階段未做寫入測試。需要在使用者選定的 issue/PR 上做實際發布並記錄 URL，不能宣稱已驗證寫入。
OAuth token 可以讀 checks，但不能建立/更新 check-runs；[GitHub Checks REST 文件](https://docs.github.com/en/rest/checks/runs) 對此有限制。MVP 讀取 CI、發布 PR review COMMENT 和 issue 摘要即可，不需新建 GitHub App。
同一 GitHub 帳號的 reviewer session 不代表不同帳號；現有 reviewer.md 使用 `gh pr review --comment`，不能以 GitHub APPROVED 狀態當獨立 reviewer clean 的唯一表達。

### 現有交付腳本的可沿用與缺口

`scripts/review-patrol.sh` 已使用新 Codex process、拋棄式 detached worktree、固定 reviewer 指示、PR review COMMENT，並按 head SHA 避免已審版本重審。
現有 README / goal / reviewer.md 記錄 Claude implementation + Codex review 的人工交接流程。

缺口（靜態讀碼觀察，尚未以測試證明）：

- 只用 free-text VERDICT 和 comment 計數；沒有 typed outcome、穩定 finding registry 或 reviewer resolution evidence。
- 沒有持久化結果與 transactional publication outbox；發布失敗後會清除暫存 worktree，下次可能重做 review。
- 無單一 controller lock；trigger 與 patrol loop 可同時重審/重貼。
- 去重只比 head，不涵蓋 base/spec/design 變動。
- 取 PR head、diff、history 的多次 GitHub API 讀取未鎖定單一版本快照。
- 既有未驗 AC 可放 nonblocking 的規則不能默認沿用；本次品質政策待 grill。
- 固定兩輪 review、無界基礎設施重試與旧 goal 的 stacked delivery 與本次需求不同。

不要在新 controller 運作時同時啟動舊 patrol loop / Claude /loop / Ralph 外層循環。

## Agent runtime

- Claude Code：`/Users/johnson.chiang/.local/bin/claude` → native 2.1.282。`claude auth status` 顯示 claude.ai first-party 登入 / Max。
- 本機 help 有 `-p`、`--output-format json|stream-json`、`--json-schema`、`--resume`、`--session-id`、工具 allow/deny、permission mode、`--worktree`。
- Codex：`/Users/johnson.chiang/.local/bin/codex` → standalone CLI 0.153.4。`codex login status` 顯示 ChatGPT 登入。
- 本機 `codex exec` 及 `codex exec resume` 均有 `--json`、`--output-schema`、`--output-last-message`。CLI 可以獨立於目前 ChatGPT/Codex app conversation 執行；不能把當前 UI agent 等同 CLI worker。
- Codex 支援 read-only/workspace-write sandbox；reviewer 能否在隔離副本執行所有必要測試要做實際 spike，不能只靠 flags 宣稱隔離完整。
- 目前只驗證 binary/help/auth 狀態，未驗證新 worker 真正 inference、schema result、resume 或取消後恢復。
- Claude user settings 啟用 Superpowers、Ralph 與 Orca hooks；新工作需控制不啟動既有外層 loop，不修改使用者全域設定。

官方對照：[Codex non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode)、[Claude Code programmatic execution](https://code.claude.com/docs/en/headless)。CLI help 是 installed-version 的依據，官方網站可能隨新版變動。

## 第一輪 grill（待回答，不是既定決策）

### 使用者後續補充：spec 來源

使用者提出可用 `to-spec` 或 OpenSpec 產生 spec。將兩者列為可接受的上游規格產出方式；這不表示已選定其中之一，也不表示 MVP 必須自動操作兩套 authoring workflows。

- `to-spec`：綜合已討論的需求與 codebase context，確認測試介面後產出 spec；原 skill 會發布至設定的 tracker。需保留 user-only invocation 與發布契約。
- OpenSpec：本機 CLI 1.13.1，目前 repo 已設 `spec-driven`，無 active changes。預設可產出 proposal、capability spec delta、design 與 tasks。執行使用所選 root 的 CLI paths/instructions，不憑慣例猜位置。
- 建議單次 feature 選一套權威 spec/plan；OpenSpec 的 change delta 要連同適用的 baseline 提供 reviewer，不能單靠 delta 代表完整需求。已有 design/tasks 時先校對與補足可派工契約，避免再維護一份會漂移的同義 plan。
- 不論 authoring 來源，交接需帶可讀取內容、版本／digest、scope、acceptance criteria 與批准的決策；issue、task、review 結果引用同一適用版本。這沿用已確認的版本綁定要求。
- 上游流程可表達為：需求討論／grill → to-spec 或 OpenSpec → 確認規格／拆票 → 選定 issue → delivery loop。單一 feature 可直接使用 spec issue，只有需要分拆時再用 to-tickets，避免為同一交付單位重複開票。
- 仍待決定：本次 orchestrator 自身 spec 採哪一條路、開發落點、human checkpoint 與原第一輪問題。這次補充沒有授權替任意現有 issue 改 scope，也沒有取消原三 gates。

上述為研究與整合方向紀錄；此回合未執行 `to-spec` 發文或建立 OpenSpec change。

### 已確認：開發落點、規格工具與執行方式

使用者以「all ok」接受本輪三個建議：

1. 專案獨立位於 `/Users/johnson.chiang/workspace/orca-delivery`。第一個真實 demo repo/issue 另外選定。
2. 本次 project / feature 規格使用 OpenSpec；ticket 引用對應版本。可接收 to-spec 來源不等於 MVP 自動操作兩套 authoring 流程。
3. 使用 Orca lead agent + 單一本機小型持久化 controller，controller 掌 policy 與 gates，Orca supervised workers 掌執行。先從專用 Orca terminal 啟動可恢復 process。

下一輪已提出但待回答：feature 開工前的 design+plan 人工確認、blocking 標準、時間/修正/基礎設施重試上限。後續尚需 TDD 細節、publication/finding authority 以及 demo target。

## 可行方案比較（比較時的建議；後續已選小型 controller + Orca workers）

| 方案 | 優點 | 代價／不適用處 | MVP 建議 |
| --- | --- | --- | --- |
| 只有 lead agent + skills/聊天記憶 | 最快啟動 | SHA、gate、重複事件、restart recovery 仍依 agent 自律，無法滿足已確認驗收 | 排除 |
| 小型持久化 controller + Orca supervised workers + lead agent | 沿用已存在的 task/dispatch/session/worktree；只補 deterministic delivery policy | 需處理 Orca coordinator 身分、API 可用性與 typed evidence 外部儲存 | 優先 spike |
| 小型 controller 直接呼叫 Claude/Codex CLI，Orca 僅入口 | CLI schema/resume 可直接掌握，可獨立於 Orca 控制面 | 要自行做 process supervision、UI 可見性、通知、session/worktree 管理 | 第一方案不可行時再評估 |
| 通用 durable workflow engine（如大型 scheduler） | 狀態/重試基礎設施完整 | 多一套部署與 state ownership；單一 repo/issue MVP 尚無需要 | 延後 |
| 在 Superpowers SDD 外再包 review/fix loop | 可沿用完整方法流程 | 既有內外 retry/裁決/finish 會互相控制；不能保證同一 gate policy | 不直接疊加 |

Orca 原生 Run 不自行排程：小控制器只擁有 feature policy，Orca 保留 execution state，兩者需以 IDs 對應，不能把 Orca done 升格成 PR Pass。Orca terminal caller identity 是實際整合前提；第一個可執行版本建議在專用 Orca terminal 前景啟動 controller，之後才驗證獨立 service 模式。

最小可行資料保存可考慮 SQLite + immutable result/evidence files + publication outbox；這是待 design 比較的實作選項，不是已確認需求。GitHub 是對人發布的 review 紀錄，結構化 finding authority 的選擇仍待 grill。

### 設計前必做的有界 spike

1. 建立專用 run/task，分別起一個低成本 Claude 與 Codex worker，產出 contract-shaped result 並驗證 id/SHA/schema；不使用既有工作中的 terminal/worktree。
2. worker done 後保留結果，先不消耗 mailbox；測試 controller reconcile 可收回結果，重複通知不重派。
3. 記錄 runtime 的 session id 與 dispatch id；中斷 controller 後重新綁定合法 coordinator，恢復同一工作。
4. 驗證 reviewer 在獨立 detached copy 的 source 沒變動，測試產物不污染 implementation branch。
5. 在已選 issue/PR 發布實際 review 與摘要，讀回 marker/result digest/head/URL；失敗則只重試 outbox。

以上是原始 spike 清單；後續已開始 Run/Task/Dispatch 的真實 probe，具體完成程度與缺口見 [runtime-probe.md](runtime-probe.md)。尚未執行的項目不以文件支援代替實際能力證據。

## 下一輪待決定（依第一輪答案調整）

- 選定單一 feature issue；#12 為真實 feature，但依賴未合併的 #11、範圍大且已有 worktree，不能擅自接管。#8 小而獨立但屬 follow-up fix，不能未經同意就當 feature demo。
- Finding blocking 定義、未驗 AC 規則、爭議裁決與 authoritative structured registry。
- TDD 行為/任務粒度，Red 的 snapshot+test+failure 證據，非行為變更 exemption。
- PR 詳細 review + issue actionable summary 的呈現方式。
- 必要 checks 與 skipped/neutral 規則；CI / review 的同版本聚合與 timeout。
- Correction rounds、infra retries、時間/用量預算、並行度、常駐/resume。

## 驗證缺口

- 真實 Orca dispatch/result 已開始驗證，詳見 [runtime probe](runtime-probe.md)；resume/idempotency、專用 controller caller identity 和 app lifecycle 仍需 spike。
- GitHub 寫入與 read-after-write 尚未實測。
- 未選 issue、未批准 design、未實作 controller、未跑假 adapter 驗收、未跑真實 E2E。

研究不能被誤標為交付完成。
