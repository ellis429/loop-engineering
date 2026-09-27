# OpenSpec author notes

本輪產物是 **comparison draft，未採用、未批准開工**。已完成 `proposal.md` 與四份 delta specs；未完成 `design.md`、`tasks.md`。Testing seams 仍 pending。本文只記本稿方法與來源，不評比另一候選。

## 方法與實際工具

- Skill：`/Users/johnson.chiang/.agents/skills/openspec-propose/SKILL.md`，metadata version `1.0`，本輪已完整讀取。
- CLI：`/Users/johnson.chiang/.local/bin/openspec`，`--version` 實際回傳 `1.13.1`。
- Schema：原生 `spec-driven`，由本側 `openspec/config.yaml` 指定；沒有改 schema。
- Planning root：`/private/tmp/orca-spec-comparison-20260926/openspec`。
- Change：`openspec new change implement-delivery-loop --schema spec-driven` 建立；命令與後續 artifacts 全部落在本側暫存 root。
- `openspec list --specs` 回傳沒有既有 specs；因此四個能力使用 `ADDED Requirements`，不是假稱修改正式 repo 的既有 specs。
- proposal、specs、design、tasks 四個 artifact 均查詢了 CLI `instructions ... --json`；只建立本輪指定的 proposal/specs。每個新增能力有原生 `Purpose`、`ADDED Requirements`、`Requirement`、`Scenario`、`SHALL` 及 WHEN/THEN。
- 研究來源為共同 `../baseline/` 快照及 `../shared-input.md`；未讀另一候選、網路口碑或先前工具比較。沒有查詢外部網站或動態 runtime。

## 有意偏離原 skill

原 openspec-propose 要完整建立 applyRequires 的 transitive artifacts。本輪依使用者比較範圍只產出 proposal＋specs；跨模組、狀態與安全恢復原本需要 design，故沒有把 design 說成 optional 並跳過，也沒有將缺失的 tasks 說成完成。這是 **partial propose**；CLI `isPlanningComplete=false`、`isComplete=false`，不稱 full propose 或 implementation-ready。

主 agent 最初發出測試接縫確認，尚未得到答覆。依共同後續澄清，本輪先產出草稿，公開 controller start/adopt/status/resume/decision 搭配 fake agent/GitHub/CI adapters 的 seam 僅為待確認建議，不是已確認 SHALL。規格仍寫已確認的可觀察結果、測試證據品質與真實 E2E 要求。沒有開始依賴該 seam 的實作或驗證。

原生 proposal 保留 Why/What Changes/Capabilities/Impact；附 draft 狀態與未決事項方便比較。規格以四個能力合併相關行為，並添加穩定 requirement ID 及 AC ID 以對應 D19。這些 ID 不是另一套 tasks 或外層 workflow。

沒有 apply、production code、產品測試、外部發布、GitHub issue/PR、worker、P03 Retro、PR trial 或強權限 workaround。正式 gigaxfer／orca-delivery repo 未由本 agent 修改。

## 政策狀態與設計具體化

D01–D30 及 shared-input 記錄的最新 Ok 是已確認政策；本文轉述不代表使用者批准此新草稿。`workflow-design.md`、`workflow-contracts.md`、`file-state.md` 明標為設計提案，本稿以下細化也保留提案狀態：

| 規格化提案 | 定位 | 尚未選定的實作 |
| --- | --- | --- |
| Artifact/result/evidence 欄位、producer 與 digest 核對 | ORC-02、GAT-02、DUR-03/04 | 欄位 schema、API、實際產品命令 |
| State/publication/acceptance 分維度、失效路由 | ORC-04/05、GAT-07 | enum 命名、store 內部結構 |
| Required check identity、分頁、attempt、衍生 snapshot 核對 | GAT-06 | repo-specific required 集合、具體 CI provider 接法 |
| Batch identity／計次、人工退回 identity | FIN-03/05 | 資料模型與 task dispatch 細節；三輪上限本身已確認 |
| Run/project authority、crash 可觀察契約、結果衝突、outbox marker/read-back | DUR-01/04/05/06/07 | JSON/YAML 的具體分工、是否採 JSONL、atomic-write／lock 實作 |
| Preflight 與 runtime results 捕捉 | DUR-03/09 | runtime/model、native completion channel、核准隔離方案 |
| Retro 證據／承接者／驗法及去重 | ORC-07 | 完整 scorecard、skill/reference 包裝；驗收後自動候選本身已確認 |

這些細節描述可驗收行為而不指定內部 class、library 或執行步驟。它們是本次供比較的擬議契約，不是新簽核政策或已通過的能力。

## 已確認需求覆蓋映射

檔案代稱：

- **O**：[delivery-orchestration/spec.md](openspec/changes/implement-delivery-loop/specs/delivery-orchestration/spec.md)
- **G**：[delivery-gates/spec.md](openspec/changes/implement-delivery-loop/specs/delivery-gates/spec.md)
- **F**：[finding-resolution/spec.md](openspec/changes/implement-delivery-loop/specs/finding-resolution/spec.md)
- **D**：[durable-delivery/spec.md](openspec/changes/implement-delivery-loop/specs/durable-delivery/spec.md)
- **P**：[proposal.md](openspec/changes/implement-delivery-loop/proposal.md)

每列可按 requirement 或 AC ID 搜尋定位；一個已確認要求可由多個能力共同滿足。

| 決策 | 內容 | 規格位置與情境 |
| --- | --- | --- |
| D01 | 三 gates、版本證據、歷史 Red/current Green | G:GAT-01/02/03/07；AC-G01–08、AC-G16–18 |
| D02 | Workflow/controller/skills/adapters 分工 | O:ORC-01/08、D:DUR-01/03/09；AC-O02/O16、AC-D05/18 |
| D03 | PR Pass 終點與不自動 merge/close/release/deploy | O:ORC-05；AC-O10/O11；P:What Changes |
| D04 | Project/feature spec 與 ticket 層級 | O:ORC-02；AC-O03/O04 |
| D05 | 單 feature/PR、task 派工、過大先拆 | O:ORC-02；AC-O03 |
| D06 | 獨立 orca-delivery repo | P:Impact；本稿只在暫存 planning root，不修改該正式 repo |
| D07 | 採 OpenSpec、可接受 to-spec 來源但不雙重 authoring | O:ORC-02/08；AC-O03/O16；P:Capabilities |
| D08 | Orca lead、單一本機 controller、workers、terminal start/resume | O:ORC-01、D:DUR-01/02/07/09；AC-O02、AC-D03/14/18 |
| D09 | Reviewer／人工 closure、通知不是成功 | G:GAT-01/02、F:FIN-01/02、D:DUR-04；AC-G03/G04、AC-F03/F04、AC-D07/D08 |
| D10 | 真實 finding→fix→re-review、mock 分開 | G:GAT-08；AC-G19/G20；F:FIN-03/04 |
| D11 | 一次 design+plan 確認與語意變更回人 | O:ORC-03、G:GAT-07、F:FIN-04/05；AC-O05–07、AC-G17、AC-F09/F12 |
| D12 | Blocking 準則與 severity 分離 | F:FIN-01；AC-F01 |
| D13 | 4h／3輪／infra+2、序列實作、review+CI並行 | F:FIN-03/04、D:DUR-08、G:GAT-01；AC-F05–10、AC-D16/D17 |
| D14 | JSON/YAML 與恢復／去重 | D:DUR-01/04–07；AC-D01/D02、AC-D07–15 |
| D15 | 既有 gigaxfer session 試用方向 | O:ORC-04/07；AC-O08/O09/O15；P:What Changes |
| D16 | pre-PR adopt G1→PR→gating | O:ORC-04、G:GAT-01；AC-O08/O09、AC-G01 |
| D17 | 共用 orchestrate、project/feature兩層 | O:ORC-01/05–07；AC-O01/O02、AC-O10–15 |
| D18 | PR trial 暫停，下一 feature 全流程 | O:ORC-03/04/07；AC-O05/O08/O15；P:What Changes |
| D19 | 穩定 AC、驗法/證據、原生文件版本、不降低 AC | O:ORC-02/03/08、G:GAT-02/07；AC-O03–07/O16、AC-G04/G05/G17 |
| D20 | 統一三角色名稱 | O:ORC-01、G:GAT-05；AC-O01/O02、AC-G11/G12 |
| D21 | Retro 與必要 Replanning | O:ORC-07；AC-O14/O15 |
| D22 | P03 Retro 未啟動、非接管 | O:ORC-07；AC-O15；P:What Changes |
| D23 | 同層協作、明確代理、唯一派工 | O:ORC-01、D:DUR-02；AC-O01/O02、AC-D03/D04 |
| D24 | JSON finding authority、先保存、PR/issue、outbox/reconcile | F:FIN-01/02/06、D:DUR-01/04/06/07；AC-F02–04/F13/F14、AC-D07/D08/D12–14 |
| D25 | 一次獨立爭議覆核、不另計輪、不能重置 | F:FIN-04；AC-F08–10 |
| D26 | Superpowers TDD、獨立 N/A eligibility | G:GAT-03/04、O:ORC-08；AC-G06–10、AC-O16 |
| D27 | 上游 accepted+merged+baseline 才實作 | O:ORC-06；AC-O12/O13 |
| D28 | 人工驗收後 Retro 候選、明示方法、非自動落地 | O:ORC-07/08；AC-O14–16 |
| D29 | CIT 暫不處理、保持必要 CI | G:GAT-06；AC-G13–15；P:What Changes |
| D30 | Runtime/model 解耦、不默認 model-only G2/opencode | D:DUR-03/09、G:GAT-05；AC-D05/D06/D18/D19、AC-G11/G12 |
| 最新 Ok | OpenSpec＋Writing Plans＋TDD＋orchestrate/controller＋Matt按需 | O:ORC-08；AC-O16；P:What Changes |

## Testing Decisions — 待確認

建議用公開 start/adopt/status/resume/decision 操作及可控制的 fake agent/GitHub/CI adapters，觀察狀態、派工、發布與重啟；這可穩定製造 stale result、push race、unknown request 與 crash，不須 production 測試後門。此 seam 尚待使用者確認，沒有選定實作 API／測試框架，也沒有執行這些測試。

規格內 69 個 AC 情境描述預期外部結果，後續 plan 應將它們對應具體驗法與證據。真實 adapters/全流程另驗；fake 成功不能填補 Reviewer 隔離、native completion、workspace placement 或真實 finding loop 的缺口。必要環境問題如實記錄，不降低驗收。

## 未決事項與限制

1. **D11 未完成**：沒有完整 design/tasks，更沒有對具體版本的開工確認。
2. **Testing seam pending**：上述公開操作／fake adapters 邊界尚未確認。
3. **Runtime/model 待選與待驗**：Codex 的 runtime/model 定義、具體 adapters、native lifecycle、全工具 Reviewer 隔離、新 repo placement 尚未證明；本稿不採 opencode 或強權限 workaround。
4. **Repo required checks 待固定**：空集合及未知不能成功；skipped/neutral 只有明確 policy 才接受，沒有替使用者選例外。
5. **Timeout/active time 待設計確認**：4h/3輪/+2 已確認；45/30/30min、wall-clock 聯集、crash unknown interval 算法只是候選，未寫成確定預設。
6. **產品實作選擇未定**：Python、檔案布局、JSONL、schema/API/命令及 lock／durability 細節留給 design；支援本機的證據不能推出共享磁碟／多主機支援。
7. **Trial 暫停**：Q-TARGET 未答；不自行把 P03/issue #12/p03-ingest 選為目標；P03 Retro 等明確開始，PR trial 等恢復與原 owner 交接。
8. **沒有產品執行證據**：既有探測只代表快照記錄的能力；這些文件不證明 controller/code/tests/E2E 存在。

## 驗證與工具紀錄

- 原生命令：`openspec validate implement-delivery-loop --strict --json`，`valid=true`、`issues=[]`；見 [validation.json](tool-records/validation.json)。此驗證只證明草稿的 OpenSpec 結構合法。
- 最終狀態見 [status-final.json](tool-records/status-final.json)：proposal/specs done；design ready、tasks blocked；planning incomplete。
- 結構自檢與來源 digest 核對見 [draft-audit.json](tool-records/draft-audit.json)：四個 capability、31 requirements、69 unique AC scenarios，沒有 design/tasks，來源快照與共同 manifest 一致。
- 原始 artifact instructions 與分段 status 存於 `tool-records/`；工具版本另存 `cli-version.txt`。
- 無可用完整 token、成本或可靠活躍耗時統計，不編造數值。CLI validation 的 `durationMs` 只代表該命令的 validator 時間，不代表寫作總耗時。
