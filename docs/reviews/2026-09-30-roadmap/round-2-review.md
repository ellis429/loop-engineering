verdict: changes_requested

審查版本為 `50cc711`；兩個現行檔案與該 commit 相同。R1 共 **8 項 resolved、1 項 partially_resolved**。

| R1 | 判定 | 依據 |
|---|---|---|
| R1-01 | resolved | [roadmap.md:27](/Users/johnson.chiang/workspace/loop-engineering-roadmap/docs/roadmap.md:27)、第 32–33 行已安排 Feature 2 建立 orchestrate、Feature 3 執行 R2；[controller-recut.md:55](/Users/johnson.chiang/workspace/loop-engineering-roadmap/docs/research/2026-09-30/controller-recut.md:55) 補列 T4.1。 |
| R1-02 | resolved | [controller-recut.md:52](/Users/johnson.chiang/workspace/loop-engineering-roadmap/docs/research/2026-09-30/controller-recut.md:52) 按 worker、CI／證據、review 拆分 T7.1；第 88 行將 D17 完成點延至 Feature 4，符合 `validation.md:210–216`。 |
| R1-03 | resolved | [roadmap.md:59](/Users/johnson.chiang/workspace/loop-engineering-roadmap/docs/roadmap.md:59) 已涵蓋全部 18 條含 W 樣本的 AC，指定正反例、owner 來源、獨立 Reviewer、rubric、`proof.md` 與 M1 完成點。欄位錯位另列 R2-04。 |
| R1-04 | resolved | [roadmap.md:64](/Users/johnson.chiang/workspace/loop-engineering-roadmap/docs/roadmap.md:64) 至第 78 行已補 O23、G15、D23，並依 D55 修訂 O14、O18及加入唯讀專案進度視圖。 |
| R1-05 | resolved | [roadmap.md:32](/Users/johnson.chiang/workspace/loop-engineering-roadmap/docs/roadmap.md:32) 已補交接包 → `spec-to-plan` → 登記 → ◆確認開工，並引用 D55、D69；第 27、33–34 行安排後續延伸。 |
| R1-06 | resolved | [roadmap.md:20](/Users/johnson.chiang/workspace/loop-engineering-roadmap/docs/roadmap.md:20)、第 54、58 行將 R3 放在四個 Feature 接受、merge、archive 後，保留 baseline、獨立 D11 與執行責任，不再形成 Feature 4 的驗收循環。 |
| R1-07 | resolved | [roadmap.md:60](/Users/johnson.chiang/workspace/loop-engineering-roadmap/docs/roadmap.md:60)、[controller-recut.md:59](/Users/johnson.chiang/workspace/loop-engineering-roadmap/docs/research/2026-09-30/controller-recut.md:59) 已明列按接法區分的三類證據與 `none`，不再等同 preflight receipt。 |
| R1-08 | partially_resolved | [roadmap.md:84](/Users/johnson.chiang/workspace/loop-engineering-roadmap/docs/roadmap.md:84) 至第 88 行補了 hash 核對、引用清查及固定 commit，但改寫範圍牴觸核准快照保護，且漏列現行入口，見 R2-01。 |
| R1-09 | resolved | [controller-recut.md:18](/Users/johnson.chiang/workspace/loop-engineering-roadmap/docs/research/2026-09-30/controller-recut.md:18) 明確區分現存實作量與完整交付估計；第 35–44 行另列推估。唯讀重算 tracked 檔案為程式 **6,054**、測試及 fixtures **8,825** 行，合計 **14,879**。 |

以下為第 2 輪 findings。

**R2-01**

- **嚴重度：major**
- **位置：**[roadmap.md:85](/Users/johnson.chiang/workspace/loop-engineering-roadmap/docs/roadmap.md:85)–88。
- **問題：**退役清查把整個 `docs/design-candidate/d45-04/` 列為應改寫引用的現行入口，卻沒有排除受 hash 保護的候選原檔；同時漏列 `docs/README.md` 的現行接續入口。
- **依據：【事實】**[decisions.md:65](/Users/johnson.chiang/workspace/loop-engineering-roadmap/docs/decisions.md:65)（D53）及[勘誤:3](/Users/johnson.chiang/workspace/loop-engineering-roadmap/docs/design-candidate/d45-04-errata.md:3) 明定候選原檔不改。`d45-04/tasks.md:51、57` 含待清查路徑，其現行 hash 仍符合 `d11-approval.json:23`。另 [docs/README.md:25](/Users/johnson.chiang/workspace/loop-engineering-roadmap/docs/README.md:25) 直接連到待刪 proposal，第 16 行仍指定 handoff 最新段為接續依據。**【推論】**照現有分類執行，可能改壞核准快照，並留下失效或過時的現行導覽。
- **建議：**明列不可改寫的核准檔案，以外部導覽／勘誤及固定 commit 轉接；把 `docs/README.md` 納入現行入口清單。歷史 handoff 可保留，但現行導覽應改指新接續位置。

**R2-02**

- **嚴重度：minor**
- **位置：**[controller-recut.md:108](/Users/johnson.chiang/workspace/loop-engineering-roadmap/docs/research/2026-09-30/controller-recut.md:108)–109；[roadmap.md:33](/Users/johnson.chiang/workspace/loop-engineering-roadmap/docs/roadmap.md:33)–34。
- **問題：**G19、D22 的中間驗證階段及相關需求輸入未同步。
- **依據：【事實】**研究第 59 行與 roadmap 第 60 行要求 Feature 2 建矩陣，Feature 3、4 與 R3 各補證據；跨階段表卻只列 `2 → V`。G19 屬 `GAT-08`、D22 屬 `DUR-09`，但 Feature 3 漏列兩者，Feature 4 漏列 `DUR-09`。其餘 Feature 1、2 的相關需求輸入與案例對照一致。
- **建議：**兩條跨階段對照改為 `2 → 3 → 4 → V`，並補齊上述需求輸入。首先驗證與最終完成的數字不需因此改動。

**R2-03**

- **嚴重度：minor**
- **位置：**[roadmap.md:74](/Users/johnson.chiang/workspace/loop-engineering-roadmap/docs/roadmap.md:74)–78。
- **問題：**M2 清單漏掉 D57 留給 S2 的逐 task review 強制機制待決事項。
- **依據：【事實】**[decisions.md:69](/Users/johnson.chiang/workspace/loop-engineering-roadmap/docs/decisions.md:69)（D57(4)）明列「controller 是否強制這一步屬 S2 範圍」。目前清單包含 Q-STACK 等待決事項，卻未承接此項；Feature 4 的整組 G2 不等於逐 task review。**【推論】**後續重切可能遺失這項已指定階段的決策。
- **建議：**補列「是否由 controller 強制逐 task 獨立 review（D57(4)，待決）」。這不代表已決定實作，也不要求提前至 M1。

**R2-04**

- **嚴重度：minor**
- **位置：**[roadmap.md:59](/Users/johnson.chiang/workspace/loop-engineering-roadmap/docs/roadmap.md:59)。
- **問題：**Workflow 樣本列缺少一個表格分隔欄，責任欄位錯位。
- **依據：【事實】**表頭有五欄，此列只有四欄；「照 §3 各組的 owner」落在 AC 欄，獨立 Reviewer 說明落在 Owner 欄，審查欄為空。
- **建議：**把 AC 清單分到獨立欄位，恢復內容／AC／Owner／審查的對應。

核對後未列為 finding 的結論：

- Feature 2 的派工、保存結果及去重匯入具有獨立可觀察的驗收終點；逐 Feature 延伸 orchestrate，可合理承接拆分後的 T4.1／T7.1。沒有具體依據判定它必須等 Feature 3 才能驗收。D57 明定 PR 大小看結構，約 5,500 行本身不足以證明過大。
- M1 驗收的 docs PR 用於彙整證據；R3 仍選取另經 D11 的真實 Feature。此安排本身與 D57、D58 相容，未發現具體產品行為因此漏入現況 spec。
- 原 R1 所指出的 M2 能力缺漏與 D55 調整均已補齊；新增遺漏限於 R2-03 的待決事項。

AC 全量重算結果如下，與研究報告一致：

| 階段 | 首先驗證 | 完成 |
|---|---:|---:|
| Feature 1 | 23 | 9 |
| Feature 2 | 15 | 7 |
| Feature 3 | 13 | 12 |
| Feature 4 | 20 | 31 |
| V：M1 驗收 | 11 | 23 |
| 延後 S2 | 6 | 6 |
| **合計** | **88** | **88** |

88 個 ID 無遺漏或重複，跨階段 AC 為 **29 條**。上述是規劃歸屬計數；O23、G15、D23 仍保留明列的 M2 部分，不能據此宣稱整條完成。

實際核對的檔案與證據：

- 第 1 輪 `review-1.md`；`174fbd6 → 50cc711` 的兩檔差異及兩檔現行全文。
- `docs/decisions.md` 指定各決策、`skills/project-lead/SKILL.md` §5、`docs/guide/user-guide.md` A3。
- `openspec/changes/implement-delivery-loop/specs/` 下四份 `spec.md`、`adoption/source-map.md`；`openspec/config.yaml`。
- `docs/design-candidate/d45-04/` 的 `coverage.md`、`tasks.md`、`validation.md`、`design.md`、`d11-approval.json`；`docs/design-candidate/d45-04-errata.md`。
- `README.md`、`docs/README.md`、`docs/validation/implement-delivery-loop.md`、`docs/handoffs/2026-09-27-controller-design.md`。
- `loop-engineering-thin@fcefecc` 的 tracked 檔案行數、`src/loopctl/next.py`、夜間迴圈 `morning-report.md`／`ledger.md`、T3.1 attempt-4 的測試紀錄。

逐案抽查 **31 條 AC**，核對 scenario、coverage 驗證欄、案例／task 與階段歸屬：

- O01、O02、O06、O11、O16、O19、O22、O23、O26。
- G01、G06、G08、G11、G12、G13、G15、G17、G19、G20。
- D06、D12、D13、D14、D15、D16、D17、D22、D23。
- F07、F11、F12。

全程唯讀，未修改、建立或刪除檔案，未執行 commit、push、GitHub 寫入或產品測試；549 tests 僅核對既有紀錄，未重跑。