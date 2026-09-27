# Controller 開工確認表（候選 v3）

狀態：**使用者已確認（D40，2026-09-27）**。已採 v3 技術預設、三個 PR 與 private `yschiang/orca-delivery`。以下保留原提案及 hashes；正式採用紀錄見 [approval.json](../../../openspec/changes/implement-delivery-loop/approval.json)。產品驗證尚未完成。

## 1. Design＋plan 的建議預設

| 項目 | 待確認方案／主要取捨 |
| --- | --- |
| 方法 | 既有OpenSpec spec；design/tasks沿原生結構，tasks補Writing Plans欄位；Superpowers TDD依D26維持。協作者/controller掌派工，避免第二個外層loop |
| 核心 | Python 3.12 CLI、stdlib＋PyYAML、JSON/YAML狀態；無DB/daemon/dashboard |
| 平台／隔離 | POSIX設計；先在本機macOS驗證Seatbelt。Linux launcher另實測；Windows/WSL2未涵蓋。Sandbox未verified即Blocked；OpenCode＋keychain完整接入尚未驗證，Seatbelt deprecated風險保留 |
| 證據／恢復 | per-attempt clone＋CAS fast-forward、主機feature authority、分段outbox、baseline＋allowed overlay Red snapshot；Red replay額外重跑以核對可重現性，成本較高 |
| 時間與重試 | 已確認D13：4h active、3輪修正、每operation 2次額外infra retry。建議worker/review/CI timeout=45/30/30分鐘；active time取活動聯集，crash不明區間保守計入 |
| Finding／CI | 建議同finding失敗覆核達2次或resolved後reopen即Blocked；skipped/neutral預設不接受，只有明確適用policy例外 |
| 版本 | spec/design/plan等內容更新回待確認；新契約G2須重新review，無人工reuse繞過。保留N-V3-01的實作澄清與測試 |

詳細內容與逐task驗法見 [design](candidate/design.md)、[tasks](candidate/tasks.md)、[validation](candidate/validation.md)。三者是同一確認版本：

- `design.md` SHA256：`732e8a545fbc1e02b8e260b594cd923301f86a5ad8c0c806a34f19d79881ad0b`
- `tasks.md` SHA256：`2859298de5ab96a8e644ca5fa6d8a9eaa822f608e2efdf46aa94d745a2fdda02`
- `validation.md` SHA256：`6ae103b3b190ff363a05b95ce100b4e06e68f07b6155b606e200d7a37a672b12`

## 2. 交付切片

**建議3個feature PR**：S1核心／fake adapters → S2真實git/GitHub/OpenCode與隔離 → S3 orchestrate／操作文件／E2E。每片有自己的issue及驗收範圍，最終仍需完整真實finding→fix→re-review證據。

取捨：review較聚焦，但依D27，下游實作須等上游人工接受、merge並採用baseline；merge不在controller預設授權。替代單一PR可少兩次交接，但review範圍較大。確認切法後才定稿各issue的AC子集，避免把部分完成宣告為整套Pass。

## 3. GitHub目標

本機orca-delivery沒有remote。唯讀列出目前帳號yschiang的repos（limit200且未達上限，2026-09-27）未見orca-delivery；不能據此推定其他organization沒有目標。

**建議新建private `yschiang/orca-delivery`**，或由使用者指定既有owner/repo。目前尚未建立repo、ticket或PR。必要CI check名稱在確定目標與CI設定後核對；GitHub adapter實測的隔離測試repo於S2前再指定，不必為文件設計先建立它。

確認以上後：納入正式OpenSpec design/tasks/validation、依已選repo與切片建立可review的ticket及CI計畫，再派Opus按TDD實作。GPT獨立review；完成controller後才啟動cross-node-file-transfer。
