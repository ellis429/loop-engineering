# Herdr 與兩套 orchestrator：整合查核

日期：2026-09-27。狀態：官方文件與選定程式碼查核；未安裝、未執行第三方程式，沒有 runtime／E2E 通過結論。

## 結論與建議

Herdr 可承接 terminal／session 與 worktree 操作，但 delivery 的證據及 gate 規則仍由本專案負責。兩套社群 orchestrator 都值得參考；不能把它們的完成／LGTM 直接映射為本專案 PR Pass。

建議先以 Herdr 原生 CLI 建立最小能力基準，再用相同交接情境評估是否採用社群封裝。若選擇現成 controller，應替換對應責任；不在兩個 controller 內同時維護同一 feature 的狀態機。具體方案與驗證順序見 [整合設計草案](../../harness/herdr-integration.md)。

## 查核範圍與版本

| 來源 | 本次觀察 |
| --- | --- |
| Herdr | 官網現行文件；release 候選 v0.9.1，未以本機 binary 核對 API |
| alexhooi/herdr-orchestrate | GitHub API 查得 main = `bf13f4449c81da3196715263be0c8548d61d4884` |
| kylezk777/herdr-orchestrator | GitHub API 查得 main = `445d756516f76f4c172126b761ef6404f950784b` |
| 本機 | Darwin arm64；本 session PATH 找不到 herdr／herd／orch；找到 opencode 與 gh |

程式碼頁面讀取 main，另記錄同輪 API 取得的 commit，供後續固定版本重查。本次不是完整 source audit；未執行其測試。官網可能比選定 release 更新，必須以實際 binary 的 help／API schema 和 probe 校準。

來源：[Herdr release](https://github.com/herdrdev/herdr/releases/tag/v0.9.1)、[alexhooi commit](https://github.com/alexhooi/herdr-orchestrate/commit/bf13f4449c81da3196715263be0c8548d61d4884)、[kylezk777 commit](https://github.com/kylezk777/herdr-orchestrator/commit/445d756516f76f4c172126b761ef6404f950784b)。

## 1. Herdr 原生能力

官方 CLI 有 workspace／worktree、agent start／get／read／prompt／wait；多數命令回傳 JSON。Agent 啟動需要可用 shell pane；可選 kind 包含 opencode、claude、codex。CLI 的 session/socket 必須明確綁定，不能用 pane 名稱推定跨 server 身分。[CLI reference](https://herdr.dev/docs/cli-reference/)

重要限制：

- prompt 的回覆不保證該任務已完成；wait 不追蹤個別任務／turn。
- idle／done 是輸入就緒狀態；blocked 是辨識到提示介面，unknown 不是完成。
- timeout 或 stalled 不證明 prompt 未送達，不可因此盲目重送。

因此結果必須包含本次 assignment／attempt 身分及版本，由檔案交接並核對；terminal 狀態只輔助觀察。[Agent automation](https://herdr.dev/docs/agent-automation/)

Detach 可保留正在執行的程序；server restart 不保留原程序。原生會話恢復依賴 integration 提供的 session reference；恢復畫面不代表工作已完成。[Session state](https://herdr.dev/docs/session-state/)

worktree create 可指定 branch／base／path；workspace close 和 worktree remove 是不同操作。這讓本專案能保留展示用 checkout，而不用接收其他框架的自動清理政策。[Worktrees](https://herdr.dev/docs/cli-reference/#worktrees)

## 2. alexhooi/herdr-orchestrate

有價值的做法：orchestrator skill 搭配 Python CLI、JSON ledger、lane 身分、獨立 review 及 findings JSON。README 明示 PR 模式的 land 不負責強制 review gate，因此它不是本專案三 gates 的現成替代品。[README](https://github.com/alexhooi/herdr-orchestrate/blob/bf13f4449c81da3196715263be0c8548d61d4884/README.md)

直接採用的差異：

- Skill 要求身在 Herdr pane，並指定角色／模型路由、子 lane 委派和 watch 規則。
- Reviewer 預設使用 tab lane；本專案仍需檢查獨立 checkout／工具權限。
- close 會清除所擁有的 worktree；本專案預設保留。
- merge／scratch 模式、完成判準、severity 路由不能直接變成我們的政策。

這些來自其 [SKILL.md](https://github.com/alexhooi/herdr-orchestrate/blob/bf13f4449c81da3196715263be0c8548d61d4884/herdr-orchestrate/SKILL.md)，本次僅研究，未啟用該 skill。

程式碼抽查：`deliver()` 包含再次送 prompt 的迴圈；`KIND_ARGS` 固定若干 runtime 的 model／permission 預設；`pretrust()` 會處理使用者 trust stores；`cmd_close()` 含 checkout 清理。若作為依賴，需先驗證 timeout 時的重送語意，並改成符合已核准 profile 及保留 worktree 的行為。[bin/herd](https://github.com/alexhooi/herdr-orchestrate/blob/bf13f4449c81da3196715263be0c8548d61d4884/herdr-orchestrate/bin/herd)

評估：適合借用小型 CLI／assignment 與 findings 的操作設計。要保留整包，需維護相當程度的行為調整；目前不建議直接安裝它作為外層 orchestrate。

## 3. kylezk777/herdr-orchestrator

有價值的做法：Rust CLI 管理檔案狀態、events、phase、baseline 與角色綁定；提供 OpenCode skill 安裝路徑；structured callbacks 與 submission unknown 的處理接近本專案所需的檔案交接。其 phase LGTM 與後續 dispatch 分開；Operator 的 commit 規則及角色分工與本專案不同。[README](https://github.com/kylezk777/herdr-orchestrator/blob/445d756516f76f4c172126b761ef6404f950784b/README.md)

具體查核：`scope::check_scope()` 的 missing-tests 判斷檢查 required tests 存在時 Tests Run 文字是否為空。這是報告完整性檢查，不是 exit code、Red／Green lineage 或目前 SHA 的測試證據驗證。[scope.rs](https://github.com/kylezk777/herdr-orchestrator/blob/445d756516f76f4c172126b761ef6404f950784b/src/scope.rs)

Controller skill 要求使用者明確要求 herdr-orch control 才載入、經 CLI 修改狀態，並保留 agent／model／argv／cwd／trust 的明確授權及禁止盲重試等規則。不能把「考慮這套工具」當成啟用授權，也不把其模型預設套到本專案。[Controller skill](https://github.com/kylezk777/herdr-orchestrator/blob/445d756516f76f4c172126b761ef6404f950784b/skills/orch-conversational-controller/SKILL.md)

評估：兩套之中，它更接近「skill＋檔案 controller」的結構，值得作為替代底座的首要對照。若採用，需驗證如何把 G1/G2/G3 與版本核對接入同一權威狀態更新。未查得可直接掛入我們三 gates 的現成擴充契約；不能先假設加一層 wrapper 即可完成。

## 4. 對照選項

| 方案 | 可省下 | 必須補／調整 | 目前建議 |
| --- | --- | --- | --- |
| Herdr 原生＋既有 orchestrate／薄 controller | 自建 terminal、session supervisor、worktree UI | 窄 transport 接法、交接及 gate 規則 | 第一個能力基準與設計預設 |
| 包裝 alexhooi herd | lane 管理、watch、findings 操作 | 工作流、重送、profile、PR gates、review 隔離、清理 | 方法參考；暫不整包採用 |
| 以 kylezk777 orch 作 controller 底座 | phase／event／baseline／角色交接 | 三 gates、PR／CI、commit 政策、版本／finding 契約 | 首要替代方案，需同題實測 |
| 兩套一起包在既有 controller 外面 | 暫時共用更多命令 | 重複狀態、控制權與恢復規則 | 不採用此堆疊方式 |

這是適配成本的設計判斷，不是效能 benchmark。未以模組數／README 行數推斷維護成本，也未驗證作者聲稱的實戰效果。

## 5. 固定版本試驗的共同標準

三方案使用相同 spec／AC、角色、結果格式與保留 worktree 要求，比較：

1. 能否以既有 runtime／model profiles 執行，而不另套一組預設。
2. 正確回收本次 attempt 的檔案結果；idle、舊結果及 timeout 不會放行或重派。
3. Reviewer 不修改被審 branch；修正由 Implementer 承接並由 Reviewer 覆核。
4. 三 gates 可獨立核對；PR／issue 發布有可查回身分，失敗只重試發布。
5. 一個 feature 只有一個協調者及一份 gate/finding 權威狀態。
6. 記錄必要 patch、額外依賴、安裝步驟與維護介面，再決定採用。

若 kylezk777 底座符合以上標準且所需修改比原生薄接法少，可改採它；不得以降低 AC 換取少寫程式。

## 本機設計基準

Git HEAD：`4ce111011fde83c3a2784402cea111e52a954b3c`。以下採用工作目錄中的未提交修訂，不能只用 HEAD 代表本文所讀基準：

| 文件 | SHA-256 |
| --- | --- |
| docs/project-intent.md | f6ea1c7af109c045b67af5640caa9086b70e12c5d3d5ed44420ee5f32bb87068 |
| docs/decisions.md | 45f7903e2342129519a5c904104396110741c4714f0e8f730cd2f90cdf2b79ef |
| docs/workflow-contracts.md | d449020a996e23b67e89f4870fa48232f12ed57bf089aec6c125a26cee5ec91e |
| openspec/changes/implement-delivery-loop/design.md | 61c4dce1c1d0bc43418a6e586dad85ad55d58a18528e7d483fa4dcc50eaca482 |

本輪依 research skill 的一手來源及落地研究紀錄做法，由目前協作者自行查核；遵循本側邊對話禁止派遣 sub-agent 的限制，未使用其背景委派步驟。
