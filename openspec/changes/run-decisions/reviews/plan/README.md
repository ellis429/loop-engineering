# run-decisions 計畫審查紀錄

Reviewer：GPT-6 Astra，effort xhigh，`codex exec` 唯讀沙箱；三輪在同一個 session（thread `01a0efae-9d1c-7f83-ad83-71cf8d8f25fc`，第 2、3 輪以 `codex exec resume` 接續）。native 模型、effort 與沙箱取自 codex session 檔的 `turn_context`（五輪的 turn 都是 `gpt-6-astra`／`xhigh`／`read-only`）。計畫作者：Claude Opus 5.5（planner subagent）。

| 輪次 | 審查的 commit | 時間（UTC） | 結果 |
| --- | --- | --- | --- |
| 1 | `cd1a1ba` | 2026-09-30T00:19:51Z～2026-09-30T00:30:48Z | changes_requested：1 blocking（P1-01）、7 major、2 minor |
| 2 | `7c557c6` | 2026-09-30T00:46:18Z～2026-09-30T00:54:02Z | changes_requested：P1 七項解決、三項部分解決；新增 2 blocking（P2-01、P2-02）、1 major、1 minor |
| 3 | `8020cbd` | 2026-09-30T01:03:09Z～2026-09-30T01:12:53Z | changes_requested：P1、P2 全部解決；新增 2 major（P3-01、P3-02）、1 minor 不阻擋（P3-03） |
| 4 | `020b046` | 2026-09-30T03:17:25Z～2026-09-30T03:25:06Z | **clean**：P1～P3 全部解決；P4-01 minor、不阻擋（4.2 摘要漏寫分支條件） |
| 4 補 | `779da5c` | 2026-09-30T03:26:09Z～2026-09-30T03:26:34Z | **clean**：照 P4-01 的建議改一行，Reviewer 確認沒有其他變動 |

第 3 輪後上限已到，依 spec-to-plan 第 4 步轉 Blocked；Project Lead 2026-09-30 決定「追加一輪審查」（ticket #29 留言），第 4 輪 clean。第一次開工確認以 `779da5c` 為準。

之後 Project Lead 在開工前走過計畫，design 補了兩段說明（人工處理不可信狀態、token 的保存與 #34），同一個 session 再確認：

| 輪次 | 審查的 commit | 結果 |
| --- | --- | --- |
| 5 | `e899200` | changes_requested：P5-01 major（人工還原可能回退並刪掉已提交的 decision） |
| 5 補 | `615ab12` | clean；P5-02 minor（還原後仍可能因未解衝突回 exit 3） |
| 5 補 2 | `658ac7b` | clean |

重新開工確認以 `658ac7b` 為準。

開工後，task 3.1 的逐 task 審查要求改設計（T3.1-01、T3.1-02、T3.1-03）。Project Lead 決定修 01、03，接受 02 為風險（#36）；計畫修訂後由同一個 session 確認：

| 輪次 | 審查的 commit | 結果 |
| --- | --- | --- |
| 6 | `7b6721d` | changes_requested：P6-01（提交後重送 claim 的預期與既有契約衝突）、P6-02（`init` 的提交邊界未定義） |
| 6 補 | `7537cc9` | clean |

重新開工確認以 `7537cc9` 為準。

task 4.2 的 Implementer 在 commit 前回報計畫缺口（衝突的 exit 3 只有 cli.py 能回，但 cli.py 不在 4.2 的擁有路徑；transitions 要保存 payload；attempted 的內容本身是 resolve_conflict 時要拒絕）。計畫修訂後由同一個 session 確認：

| 輪次 | 審查的 commit | 結果 |
| --- | --- | --- |
| 7 | `45beb42` | changes_requested：P7-01（新的拒絕條件沒有獨立測試）、P7-02 minor（`create` 的 transitions 項目與 D3 不一致） |
| 7 補 | `bc1e8e1` | clean |

重新開工確認以 `bc1e8e1` 為準。

task 4.2 的逐 task 審查找到 T4.2-01（同一 decision id 多個衝突保存過時內容）與 T4.2-02（回歸測試未列入）。Project Lead 選「同一個 transition identity 同時最多一個未解衝突」，計畫修訂後由同一個 session 確認：

| 輪次 | 審查的 commit | 結果 |
| --- | --- | --- |
| 8 | `48b4201` | clean |

重新開工確認以 `48b4201` 為準。

5.1、6.1 開工前，Project Lead 請 Claude Fable 5.1 xhigh 唯讀檢查設計（[4.2](design-checks/fable-4.2-result.md)、[5.1 與 6.1](design-checks/fable-5.1-6.1-result.md)；native model 讀回為 `claude-fable-5-1`），加上 Astra 對 4.2 的複審 T4.2-03。計畫修訂後由同一個 Astra session 確認：

| 輪次 | 審查的 commit | 結果 |
| --- | --- | --- |
| 9 | `9bab1ca` | changes_requested：21 條缺口與 T4.2-03 全部 resolved；P9-01 minor（4.2 的 attempt 編號） |
| 9 補 | `5a0a92f` | clean |

重新開工確認以 `5a0a92f` 為準。
