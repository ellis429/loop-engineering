# durable-delivery Specification

## Purpose
run 狀態的持久化與可信度：每個 repo＋feature 一份人可閱讀的現行狀態、唯一的協調權、中斷後讀到完整的舊版或新版、手改與不可信狀態的偵測，以及預算調整只記錄人工裁決。派工、外部寫入與預算計時由後續 Feature 加入（需求輸入：`docs/requirements/delivery-controller/`）。

## Requirements

### Requirement: DUR-01 人可閱讀且單一的現行狀態

設定與執行狀態 SHALL 以人可閱讀的 JSON／YAML 保存，不以 SQLite 取代。同一 repo＋feature SHALL 只有一份現行狀態；歷史只是紀錄，不是另一份現行狀態。使用者 SHALL 可以從狀態檔或 `status` 直接讀到目前階段、owner、plan／spec／design 的版本、核准、三 gate 的狀態與理由、blockers 與下一個允許的動作。狀態只能經 controller 的命令改變；手改 SHALL 可被偵測，而且永不當作決策。每筆人工 decision SHALL 保存決策者、來源、理由與影響。系統只有一套生效的狀態與 CLI 入口。

#### Scenario: AC-D01 直接檢視狀態
- **WHEN** 使用者打開 run 的狀態檔，或執行 `status`（含 `--human`）
- **THEN** 不讀歷史就能看到目前階段、owner、plan／spec／design 的版本、核准狀態、三 gate 的狀態與理由（尚未評估的 gate 標明未評估）、blockers 與 `next` 會回報的下一步

#### Scenario: AC-D02 手動修改不是決策
- **WHEN** 有人直接修改狀態檔（例如把 gate 改成 passed、改 phase 或刪除 decision），沒有經過 controller 的命令
- **THEN** 下一次讀取偵測到手改並回報，不把手改值當成批准或 gate 結果，也不覆寫原檔；合法的 decision 只能經 `decide` 產生，並保存決策者、來源、理由與影響

### Requirement: DUR-02 唯一派工權與安全重派

同一 repo＋feature SHALL 同時只有一個持有協調權的呼叫者；run ID、session 或 clone 不同，SHALL NOT 產生第二份協調權。協調權以 `claim` 取得的 token 表示，狀態只保存 token 的 digest；每個寫入命令 SHALL 核對 token。沒有協調權的呼叫者 SHALL 只能讀取狀態。

#### Scenario: AC-D03 兩個 run 搶同一 feature
- **WHEN** 兩個呼叫者同時對同一 repo＋feature 執行 `claim`
- **THEN** 恰好一方取得協調權；另一方收到已被持有的結果與目前 owner，之後仍可讀取狀態，但任何寫入命令都因 token 不符被拒，狀態不變

### Requirement: DUR-05 Crash 後讀到完整可核對狀態

已提交的狀態更新 SHALL 在支援的本機檔案系統上持久恢復；讀者只能看到完整的舊版或新版，SHALL NOT 讀到半份現行狀態。每次更新 SHALL 先寫入歷史，再原子替換現行狀態，並核對 revision；同一 transition identity 重複提交 SHALL 不重複生效，內容不同時 SHALL Blocked，並由人工 decision 解除。狀態缺失、無法解析、schema 不相容或衝突時，SHALL 說明具體原因與現存檔案，保留原資料，SHALL NOT 建立空 run。系統 SHALL NOT 以事件重放作為第二份現行狀態來源；未驗證的共享磁碟或多主機 writer 不宣稱受支援。

#### Scenario: AC-D09 State 提交前後 crash
- **WHEN** 更新狀態的命令在提交前或提交後被中斷，之後再次讀取或執行命令
- **THEN** 讀到完整的舊版或新版；已提交的 revision 可恢復，被中斷而未提交的變更不被接受

#### Scenario: AC-D10 歷史尚未完成
- **WHEN** 現行狀態更新時被中斷，或同一 transition 被重複提交
- **THEN** 已提交的 revision 可恢復而且不重複生效；未提交的變更只保留作診斷；同一 transition identity 內容不同時 run 進入 Blocked，保留兩份內容，直到人以 decision 選定其一或放棄

#### Scenario: AC-D11 無法信任的 state
- **WHEN** 讀取時遇到狀態缺失、無法解析、schema 不相容或衝突
- **THEN** 顯示具體原因與現存的檔案清單，原檔內容不變；`init` 不覆寫既有狀態，也不建立空 run 抹去歷史

### Requirement: DUR-08 有界時間與操作重試

調整預算（`budget_extension`）SHALL 只能由人工 decision 記錄，目標為 `active`、`rounds`、`attempts:<unit>` 或 `ci_wait:<H>` 之一，並附理由；記錄 SHALL NOT 改動政策檔 `workflow.yaml`，也 SHALL NOT 重置任何計數。等待、新 session 或新的 run ID SHALL NOT 自動重置預算。

#### Scenario: AC-D25 預算調整只記錄人工裁決
- **WHEN** 人以 `budget_extension` 對四種目標之一記錄延長，或 agent 身分、缺少理由、未知目標的請求送進來
- **THEN** 前者各寫入一筆附決策者與理由的 decision，`workflow.yaml` 與其他計數都不變；後三者被拒，狀態不變
