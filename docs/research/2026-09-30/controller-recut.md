# 薄 controller 重切：測量與 AC 對照

日期：2026-09-30。用途：[roadmap](../../roadmap.md) 把薄 controller 重切成四個 Feature 與「M1 驗收」的依據。本文只記錄現況與推導，不核准任何切法。

## 來源

| 來源 | 版本 |
| --- | --- |
| 需求輸入：`openspec/changes/implement-delivery-loop/specs/`（四份 capability） | `main@a1d8906` |
| AC 驗證對照：`docs/design-candidate/d45-04/coverage.md`（88 條 AC 的驗證欄） | `main@a1d8906` |
| 執行表與驗法：`docs/design-candidate/d45-04/tasks.md`、`validation.md` | `main@a1d8906` |
| 既有實作：本機 branch `delivery/thin-controller` | `fcefecc`（未 push） |

## 既有實作的現況

`delivery/thin-controller` 從 W1 起點 `96edd1c` 之後共 68 個 commit，完成 T1.1、T1.2、T2.1、T2.2、T2.3、T3.1、T6.1、T7.1；之後另一個 session 用 Astra 與 Sol 做了逐 task 審查與修正。T5.1 派出後停下，沒有 commit；T4.1、T4.2、T4.3、T5.1、T6.2、B1、R3 都沒做。

在 `fcefecc` 實測的檔案行數：`src/loopctl/` 6,054 行，`tests/` 8,825 行，共 14,879 行；549 個測試。這是目前的實作量，不是完整交付的大小。

| 模組 | 行數 | 模組 | 行數 |
| --- | ---: | --- | ---: |
| `gates`（G1 約 560、G3 與發 PR 路徑約 570） | 1,126 | `evidence` | 328 |
| `observe` | 620 | `decisions` | 264 |
| `writes` | 578 | `tools/herdr` | 227 |
| `cli` | 557 | `budget` | 215 |
| `assignments` | 528 | `tools/evidence` | 209 |
| `preflight` | 440 | `next` | 110 |
| `tools/gh` | 364 | `state` | 90 |
| `store` | 359 | 其他（`clock`、`__init__`） | 39 |

依賴方向：`next` 匯入幾乎所有模組；`gates` 匯入 `assignments`、`store`、`writes`、`evidence`、`observe`。所以 `next` 與 `gates` 是每個 Feature 都會延伸的檔案，其餘模組各屬一個 Feature。

## 四個 Feature 的大小估計

程式行數由上表的模組歸屬推估。Feature 4 與 orchestrate skill 沒有既有實作，依 design §9–§11 的範圍估。測試約為程式的 1.5 倍（既有實作的比例）。

| Feature | 主要模組 | 程式 | 含測試 |
| --- | --- | ---: | ---: |
| 1 人工決策與下一步 | `store`、`state`、`next`、`decisions`、`cli`（部分）、專案骨架、CI | 約 1,000–1,300 | 約 3,000 |
| 2 派工與結果回收 | `writes`、`assignments`、`observe`（worker）、`budget`（worker 部分）、`preflight`、`tools/herdr`；orchestrate skill 的入口 | 約 2,300–2,500 | 約 5,500 |
| 3 TDD 證據、PR 與 CI | `evidence`、`gates`（G1、G3）、`observe`（pr、ci）、`budget`（證據與 CI 部分）、`tools/gh`、`tools/evidence` | 約 2,000 | 約 5,000 |
| 4 獨立審查與 PR Pass | `findings`、`gates`（G2、Pass）、`publish`、`assignments`（review 與 correction） | 約 1,700–2,000（推估） | 約 4,500–5,000 |

照 D53 的做法，全部做完是一個約 8,000 行程式、19,000 行左右（含測試）的 PR；其中約 4,000 行是未實作部分的推估。

## AC 對照方法

1. 從 `coverage.md` 每條 AC 的驗證欄取出案例代號（`t`、`s`、`d`、`f`、`o`、`w`、`g`、`h`、`b`、`r`、`p`、`u`，以及 R1–R3、W-A–W-F），`b1–b7` 這類範圍展開成各案例。
2. 以案例為單位對到階段，不以整個 task：
   - T1.1 的 `t`、T2.1 的 `s`、T2.2 的 `d` → 1；其中 `d3` 屬 T2.3 → 2，`d7b` 屬 T6.2 → 4。
   - T1.2 的 `f` 與 R1、T2.3 的 `o`、`w` 與 `b0` → 2。
   - T7.1 依案例拆開：`b1`（active 時間與到期 stop）、`b2`（worker 逾時）、`b5`（延長 active）→ 2；`b4`（CI 等待）、`b6`（`attempts` 與 `ci_wait` 延長）、`b7`（證據命令到限）→ 3；`b3`（review 逾時）→ 4。
   - T3.1 的 `g`、T6.1 的 `h`、R2 → 3；`h7` 的 G2 格子依勘誤 E-3 屬 4。
   - T5.1 的 `r`、T6.2 的 `p`、`u` → 4。
   - T4.1（orchestrate）→ 2，因為 R2（T4.2）依賴它，而 R2 在 3。
   - R3 與 W-A–W-F → 「M1 驗收」（下表的 V）。
3. 「首先驗證」是第一個碰到該 AC 的階段；「完成」是最後一個。`coverage.md` 階段欄只寫 S2 的 AC 另列。

AC-G19、AC-D22 的驗證欄只有 `proof.md` rubric（`validation.md` §4）：每項能力分列 `fake`、`profile-probe`、`real-E2E`，依接法分開，未執行的格子標 `none`。preflight receipt 只是其中一格，所以矩陣在 2 建立，3、4 與 R3 各自補上證據，完成點是 V。

## 結果

| 階段 | 首先驗證 | 完成 |
| --- | ---: | ---: |
| 1 人工決策與下一步 | 23 | 9 |
| 2 派工與結果回收 | 15 | 7 |
| 3 TDD 證據、PR 與 CI | 13 | 12 |
| 4 獨立審查與 PR Pass | 20 | 31 |
| V M1 驗收 | 11 | 23 |
| 延後 S2 | 6 | 6 |
| **合計** | **88** | **88** |

各階段首先驗證的 AC：

- 1：D01、D02、D03、D09、D10、D11、D13、D16、D17、F07、F11、G13、O01、O02、O03、O05、O07、O11、O15、O19、O22、O23、O26。
- 2：D04、D05、D06、D08、D12、D18、D19、D21、D22、D23、G11、G12、G19、O06、O16。
- 3：D15、G01、G04、G05、G06、G07、G08、G09、G10、G14、G15、G16、G17。
- 4：D07、D14、F01～F06、F08、F09、F10、F13～F16、G02、G03、G18、G20、O10。
- V：F12、O04、O12、O13、O17、O20、O21、O24、O25、O27、O28（只由 workflow 樣本驗證）。
- S2：D20、D24、O08、O09、O14、O18。其中 O08、O18 在 1 只驗 `d8` 的拒絕，`coverage.md` 註明不算覆蓋。

另有 3 條在 M1 只成立一部分，其餘延到 S2：O23（只停受影響工作）、G15（整合 SHA 映射的正向）、D23（OpenCode-only 變體）。

### 跨階段的 AC

| AC | 經過的階段 | 標題 |
| --- | --- | --- |
| AC-D17 | 1 → 2 → 3 → 4 | Active budget 到限與恢復 |
| AC-G01 | 3 → 4 → V | 正常交付 |
| AC-D12 | 2 → 3 → 4 | 發文成功但回應遺失 |
| AC-D13 | 1 → 2 → 3 | Unknown 無法安全重試 |
| AC-D16 | 1 → 2 → 3 | Infra retry 用盡 |
| AC-G13 | 1 → 3 → 4 | 非成功 check 與空集合 |
| AC-D06 | 2 → 3 | 只有原生 assistant message |
| AC-O06 | 2 → 3 | 核准後按 plan 前進 |
| AC-G11 | 2 → 4 | 有效獨立 review |
| AC-G12 | 2 → 4 | 局部 review 或隔離無法證明 |
| AC-F07 | 1 → 4 | 三輪已用完 |
| AC-F11 | 1 → 4 | 首次驗收退回 |
| AC-O02 | 1 → 4 | 拒絕第二個外層 loop |
| AC-O11 | 1 → 4 | 接受後的新版本 |
| AC-D15 | 3 → 4 | 恢復時版本已改 |
| AC-G06 | 3 → 4 | 不同 SHA 的有效 Red 與 Green |
| AC-G08 | 3 → 4 | 整合回歸失敗 |
| AC-G17 | 3 → 4 | Base 或規格改變 |
| AC-D14 | 4 → V | Controller restart |
| AC-G20 | 4 → V | 真實 review 沒有 finding |
| AC-D22 | 2 → 3 → 4 → V | 兩種接法分別驗證 |
| AC-G19 | 2 → 3 → 4 → V | 模擬通過但 adapter 缺證據 |
| AC-O16 | 2 → V | Skills 交回 controller |
| AC-O01 | 1 → V | 直接與 Implementer 協作 |
| AC-O15 | 1 → V | 暫停的 P03 試用 |
| AC-O19 | 1 → V | 入口與 runtime 關係不授予決策權 |
| AC-O22 | 1 → V | Project Lead 提供初步 tasks |
| AC-O23 | 1 → V | 詳細設計發現跨 feature 影響 |
| AC-O26 | 1 → V | 適用 SA 確認與開工確認分開 |

這 29 條在第一個階段只成立一部分，例如 1 只記錄延長輪次的人工決策，三輪用完轉 Blocked 要到 4 才有。OpenSpec 的 scenario 在 change archive 時必須已經成立（D58），所以 roadmap 的規則是：每個 Feature 的 spec delta 只寫它結束時成立的部分，原 AC 由最後一個 Feature 補齊（前面已 archive 的 requirement 用 MODIFIED）；V 的部分由「M1 驗收」的紀錄補齊，不寫進 Feature 的 spec。

## Feature 1 範圍確定後的調整

2026-09-30，Project Lead 確定 Feature 1（change `run-decisions`）的範圍：`decide` 的種類跟著產生對象的 Feature 走，spec delta 只寫本 Feature 觀察得到的部分。首先驗證的階段因此改變：

| AC | 原本 | 改為 | 原因 |
| --- | --- | --- | --- |
| D13、D16 | 1 | 2 | `resolve_operation`、`resolve_read` 在 Feature 2 才有對象 |
| O02、D17 | 1 | 2 | 觸發情境（派工、主動時間）在 Feature 2 才存在 |
| G13 | 1 | 3 | 觸發情境是 G3 判定 |
| F07、F11、O11 | 1 | 4 | 輪次效果與 `accept`／`return` 在 Feature 4 |

Feature 1 另外新增五個 AC：D25、G21、G22、O29、O30，說明見該 change 的 proposal。上方各表維持重切當時的推導，不回頭改寫。

## 時間估計的依據

夜間迴圈實測（`.delivery/bootstrap/thin-s1/loop-2-3/morning-report.md`，在 `fcefecc` 的 worktree）：T2.1–T3.1 共 48 個驗證案例，agent 時間 2 小時 39 分，牆鐘 2 小時 51 分；high 每案例約 1.4–2.0 分鐘，xhigh 約 3.7–4.6 分鐘。之後的逐 task 審查與修正沒有計時。

新流程每個 Feature 另外多出 feature-to-spec、計畫審查、G2 審查與三次人工確認（spec、開工、驗收）。假設每個 Feature 約 1.5 個工作日、M1 驗收約 1 個工作日，四個 Feature 依序做完再驗收約 7 個工作日；roadmap 的日期另留一週給修正輪與等待。這個假設不能由上面的實測證明。

## 事實、推論與未知

- 事實：檔案行數、測試數、task 完成狀態、`coverage.md` 的驗證欄與 `tasks.md` 的相依。
- 推論：模組歸屬、大小估計、案例到階段的對照；Feature 4 與 orchestrate 沒有既有實作，估計誤差最大。
- 未知：新流程下 G2 panel 的時間與修正輪數；人工確認的等待時間。
