# 決策狀態

日期：2026-09-25。此文件記錄確認來源，不替代正式 spec。建議尚未得到回答時，不當成已授權政策。

2026-09-26 補充：使用者希望建立「Loop Engineering」並詢問整套流程如何實現。已整理 [流程藍圖](loop-engineering.md)。這是整體目標的延伸說明，不視為 Q-TDD / Q-PUBLISH / Q-DEMO 的答案，也不推定授權更改 repo 名稱。

## 已確認

| ID | 決策 | 來源 |
| --- | --- | --- |
| D01 | 三 gates：G1 實作/TDD、G2 獨立 review、G3 CI；結果必須驗證證據與適用版本 | 初始 handoff |
| D02 | Workflow 定義規則、controller 執行規則與持久化狀態、skills 提供方法、adapters 操作工具 | 初始 handoff |
| D03 | 終點 PR Pass / Ready for human acceptance，不自動 merge/close/release/deploy | 初始 handoff |
| D04 | Project spec 定義共用契約；feature spec 引用它並定義本次行為與驗收，可放 ticket 內文或引用文件 | 使用者「yes」確認層級 |
| D05 | 每個可獨立驗收 feature / 完整切片一個 PR，tasks 為派工單位；過大則先拆 feature | 使用者「yes」確認層級與流程 |
| D06 | 獨立 repo：`/Users/johnson.chiang/workspace/orca-delivery` | 使用者「all ok」接受三個建議 |
| D07 | 本次規格採 OpenSpec；接受 to-spec 作未來規格來源，但不因此要求自動維護兩套 authoring workflows | 同上 |
| D08 | Orca lead agent + 單一本機小型持久化 controller + Orca workers；先從專用 Orca terminal 啟動與 resume | 同上 |
| D09 | Review findings 需 reviewer 驗證或明確人工裁決才能解除；通知不能作為成功證據 | 初始 handoff |
| D10 | 真實驗收含 finding → fix → re-review，mock 與真實證據明確區分 | 初始 handoff |
| D11 | 每個 feature 的 design+plan 開工前由使用者確認一次；後續 scope/spec/AC 變更、設計缺陷或阻擋爭議回到人 | 使用者「ok'」接受上一輪三項建議 |
| D12 | 違反 spec/AC、可證明的正確性/安全缺陷、必要驗證缺失皆 blocking；風格/命名偏好不 blocking；severity 用於排優先順序 | 同上 |
| D13 | Run 主動執行時間上限 4h、最多 3 輪 correction；每個 infra 操作額外重試 2 次；實作序列、review+CI 並行；到限保存狀態轉 Blocked | 同上 |
| D14 | MVP 採人可閱讀的 JSON／YAML 檔案保存設定與狀態，取代 SQLite 提案；持久化、恢復與去重要求維持 | 使用者「我建議用 json 或是 yaml, 讓人也看得懂」 |

## 已提出，待回答

| ID | 建議 | 主要取捨 |
| --- | --- | --- |
| Q-TDD | 沿用 Superpowers TDD；每個行為變更追溯到 task、Red 測試與歷史 snapshot，最新整合 head 有 Green/回歸；純文件/註解可附理由和檢查申請 N/A，由 reviewer 確認；設定依實際行為判定 | 保留可稽核流程，避免形式化無效 Red；agent 不可自行豁免 |
| Q-PUBLISH | 結構化 finding registry 為權威；PR 完整 review、issue 可行動摘要與連結；GitHub 可討論，解除阻擋需 reviewer 證據或 Orca 入口的明確人工裁決 | 避免 GitHub 和本機各自改狀態；需持久化發布 outbox 與 read-after-write |
| Q-DEMO | 建立 private GitHub `orca-delivery` repo 與「CLI 查詢 run 狀態、三 gates 與 Blocked 原因」feature issue；基礎完成後，用固定版本控制器交付這個獨立 feature PR | 避開 gigaxfer 在途工作；demo 真正新增可用功能，執行中的 controller 版本固定 |

## 下一個決策前緣

等待本輪 Q-TDD / Q-PUBLISH / Q-DEMO；收到答案後完成具體 spec、design 與可派工 tasks，交付一次開工前 review。

## 可由設計自行處理的實作細節

持久化採 D14 的人可讀檔案。格式分工建議：YAML 保存 workflow/gate 設定，排版過的 JSON 保存 run/assignment/result，JSONL 保存事件歷史；具體寫入與恢復設計見 [檔案狀態設計](file-state.md)。語言、檔案安排與內部介面仍由設計提出，需滿足已確認的行為、恢復及證據契約。

Design 草案會明列 worker/review/CI 45/30/30min 的 timeout 預設、只接受 required check 的 success（skipped/neutral 預設拒絕）、active time 計算及 budget resume 行為，隨具體 design 一併確認。現階段成本只記錄可得用量，不宣稱精確美元硬上限。
