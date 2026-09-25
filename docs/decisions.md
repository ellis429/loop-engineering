# 決策狀態

日期：2026-09-25。此文件記錄確認來源，不替代正式 spec。建議尚未得到回答時，不當成已授權政策。

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

## 已提出，待回答

| ID | 建議 | 主要取捨 |
| --- | --- | --- |
| Q-HUMAN | 每個 feature design+plan 開工前確認一次；之後 scope/spec/AC 變更、設計缺陷或阻擋爭議回到人 | 增加一次人工等待，避免方向錯誤一路實作 |
| Q-BLOCKING | 違反 spec/AC、可證明的正確性/安全缺陷、必要驗證缺失皆 blocking；偏好性建議不 blocking；severity 排優先順序 | 需可讀取依據；不以固定 severity 門檻掩蓋違反 AC |
| Q-LIMITS | Run 主動執行 4h、最多 3 輪 correction；每個 infra 操作額外重試 2 次；實作序列、review+CI 並行；worker/review/CI 45/30/30min | 到限保存狀態轉 Blocked；成本先記錄可得用量，不假稱精確美元硬上限 |

## 下一個決策前緣

- TDD 方法、行為/任務的證據粒度、非行為變更的 exemption 與相應驗證。
- Review 詳情與 issue 摘要的發布方式、finding 的權威來源及人工裁決入口。
- 第一個真實 demo repo/feature issue，及是否已有適用 CI。現有 gigaxfer issues 僅作候選，不擅自接管進行中的 worktrees。

## 可由設計自行處理的實作細節

持久化引擎、語言、檔案安排與內部介面由設計比較後提出，需滿足已確認的行為、恢復及證據契約。技術建議不提前寫成使用者已指定的偏好。
