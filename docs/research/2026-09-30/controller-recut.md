# 薄 controller 重切：測量與 AC 對照

日期：2026-09-30。用途：[roadmap](../../roadmap.md) 把薄 controller 重切成四個 Feature 的依據。本文只記錄現況與推導，不核准任何切法。

## 來源

| 來源 | 版本 |
| --- | --- |
| 需求輸入：`openspec/changes/implement-delivery-loop/specs/`（四份 capability） | `main@a1d8906` |
| AC 驗證對照：`docs/design-candidate/d45-04/coverage.md`（88 條 AC 的驗證列） | `main@a1d8906` |
| 執行表：`docs/design-candidate/d45-04/tasks.md` | `main@a1d8906` |
| 既有實作：本機 branch `delivery/thin-controller` | `fcefecc`（未 push） |

## 既有實作的現況

`delivery/thin-controller` 從 W1 起點 `96edd1c` 之後共 68 個 commit，完成 T1.1、T1.2、T2.1、T2.2、T2.3、T3.1、T6.1、T7.1；之後另一個 session 用 Astra／Sol 做了逐 task 審查與修正。T5.1 派出後停下，沒有 commit；T4.1、T4.2、T4.3、T5.1、T6.2、B1、R3 都沒做。549 個測試。

程式行數（`src/loopctl/`，共 6,054 行；測試 8,825 行）：

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

各 task 新增的行數：

| Task | 程式 | 測試 |
| --- | ---: | ---: |
| T1.1 | 613 | 1,165 |
| T2.1 | 622 | 356 |
| T2.2 | 375 | 672 |
| T2.3 | 1,694 | 1,325 |
| T3.1 | 1,033 | 1,261 |
| T6.1 | 1,086 | 1,563 |
| T7.1 | 213 | 561 |
| 逐 task 審查後的修正 | 611 | 1,938 |
| **合計** | **6,054** | **8,825** |

依賴方向：`next` 匯入幾乎所有模組；`gates` 匯入 `assignments`、`store`、`writes`、`evidence`、`observe`。所以 `next` 與 `gates` 是每個 Feature 都會延伸的檔案，其餘模組各屬一個 Feature。

## 四個 Feature 的大小估計

程式行數由上表的模組歸屬推估；F4 沒有既有實作，依 design §9–§11 的範圍估。測試約為程式的 1.5 倍（既有實作的比例）。

| Feature | 主要模組 | 程式 | 含測試 |
| --- | --- | ---: | ---: |
| 1 人工決策與下一步 | `store`、`state`、`next`、`decisions`、`cli`（部分）、專案骨架、CI | 約 1,000–1,300 | 約 3,000 |
| 2 派工與結果回收 | `writes`、`assignments`、`observe`（worker）、`budget`、`preflight`、`tools/herdr` | 約 2,300–2,500 | 約 5,500 |
| 3 TDD 證據、PR 與 CI | `evidence`、`gates`（G1、G3）、`observe`（pr、ci）、`tools/gh`、`tools/evidence` | 約 2,000 | 約 5,000 |
| 4 獨立審查與 PR Pass | `findings`、`gates`（G2、Pass）、`publish`、`assignments`（review 與 correction）、orchestrate | 約 1,700–2,000 | 約 4,500–5,000 |

整個薄 controller 當一個 PR（D53 的做法）是 6,000 行程式、近 15,000 行含測試，跨四個 capability、17 個 task；D57（2）要求一個 Feature 一個 PR 做得完，太大就拆。

## AC 對照方法

1. 從 `coverage.md` 每條 AC 的驗證欄取出案例代號（`s`、`d`、`o`、`w`、`g`、`h`、`b`、`r`、`p`、`u`、`t`、`f`，以及 R1–R3、W-A–W-F），依執行表對到 task。
2. task 對到 Feature：T1.1、T2.1、T2.2 → 1；T1.2、T2.3、T7.1 → 2；T3.1、T6.1、T4.2（R2）→ 3；T5.1、T6.2、T8.1（R3）→ 4；T4.3（W-A–W-F）→ workflow。
3. 「首先驗證」是第一個碰到該 AC 的 Feature；驗證欄跨幾個 Feature 的 AC，到最後一個 Feature 才完整成立。

結果（88 條）：

| 歸屬 | 數量 | AC |
| --- | ---: | --- |
| 1 人工決策與下一步 | 23 | D01、D02、D03、D09、D10、D11、D13、D16、D17、F07、F11、G13、O01、O02、O03、O05、O07、O11、O15、O19、O22、O23、O26 |
| 2 派工與結果回收 | 12＋2 | D04、D05、D06、D08、D12、D18、D19、D21、D23、G11、G12、O06；另有 G19、D22（見下） |
| 3 TDD 證據、PR 與 CI | 13 | D15、G01、G04、G05、G06、G07、G08、G09、G10、G14、G15、G16、G17 |
| 4 獨立審查與 PR Pass | 20 | D07、D14、F01、F02、F03、F04、F05、F06、F08、F09、F10、F13、F14、F15、F16、G02、G03、G18、G20、O10 |
| 只由 workflow 樣本驗證 | 12 | F12、O04、O12、O13、O16、O17、O20、O21、O24、O25、O27、O28 |
| 延後 S2 | 6 | D20、D24、O08、O09、O14、O18 |

AC-G19（模擬通過但 adapter 缺證據）與 AC-D22（兩種接法分別驗證）在 `coverage.md` 只由 `proof.md` rubric 驗證，沒有對應的測試案例。兩者要求的是「每個 profile 分開報告能力與缺口、未驗證不冒稱通過」，是 preflight 報告的行為，所以歸到 2。

### 跨 Feature 的 AC

| AC | 經過的 Feature | 標題 |
| --- | --- | --- |
| AC-G13 | 1 → 2 → 3 → 4 | 非成功 check 與空集合 |
| AC-D12 | 2 → 3 → 4 | 發文成功但回應遺失 |
| AC-D13 | 1 → 2 → 3 | Unknown 無法安全重試 |
| AC-D16 | 1 → 2 → 3 | Infra retry 用盡 |
| AC-D17 | 1 → 2 → 3 | Active budget 到限與恢復 |
| AC-O02 | 1 → 4 | 拒絕第二個外層 loop |
| AC-O11 | 1 → 4 | 接受後的新版本 |
| AC-F07 | 1 → 4 | 三輪已用完 |
| AC-F11 | 1 → 4 | 首次驗收退回 |
| AC-D06 | 2 → 3 | 只有原生 assistant message |
| AC-O06 | 2 → 3 | 核准後按 plan 前進 |
| AC-G11 | 2 → 4 | 有效獨立 review |
| AC-G12 | 2 → 4 | 局部 review 或隔離無法證明 |
| AC-D15 | 3 → 4 | 恢復時版本已改 |
| AC-G01 | 3 → 4 | 正常交付 |
| AC-G06 | 3 → 4 | 不同 SHA 的有效 Red 與 Green |
| AC-G08 | 3 → 4 | 整合回歸失敗 |
| AC-G17 | 3 → 4 | Base 或規格改變 |

這 18 條在第一個 Feature 只成立一部分（例如 1 只記錄延長輪次的人工決策，三輪用完轉 Blocked 要到 4 才有）。OpenSpec 的 scenario 在 change archive 時必須已經成立，所以 roadmap 的規則是：每個 Feature 的 spec delta 只寫它結束時成立的部分；原 AC 由最後一個 Feature 補齊（前面已 archive 的 requirement 用 MODIFIED）。

## 時間估計的依據

夜間迴圈實測（`loop-2-3/morning-report.md`）：T2.1–T3.1 共 48 個驗證案例，agent 時間 2 小時 39 分，牆鐘 2 小時 51 分；high 每案例約 1.4–2.0 分鐘，xhigh 約 3.7–4.6 分鐘。之後的逐 task 審查與修正又加了 611 行程式與 1,938 行測試。

新流程每個 Feature 另外多出 feature-to-spec、計畫審查、G2 審查與三次人工確認（spec、開工、驗收）；人的等待時間無法由這些資料推估。以每個 Feature 約 1.5 個工作日、R3 約 1 個工作日計，四個 Feature 依序做完約 7 個工作日。

## 事實、推論與未知

- 事實：上面的行數、task 完成狀態與 AC 的驗證欄。
- 推論：模組歸屬與大小估計；F4 沒有既有實作，估計誤差最大。
- 未知：新流程下 G2 panel 的時間與修正輪數；人工確認的等待時間。
