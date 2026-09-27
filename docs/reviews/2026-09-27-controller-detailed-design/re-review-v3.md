# Controller design v3 覆核

**Verdict: clean。最終未解 confirmed blocking：0。**

DR-04、DR-10 本輪 verified；先前 8 項 verified 結論保留。這是固定快照的設計文件覆核，不是產品 G2、三 gates 通過或 D11 開工批准。

| ID | 結論 | 依據 |
| --- | --- | --- |
| DR-01 | verified | 保持 v2 已驗證的 OS launcher／負例套件／dispatch receipt 門檻及 fail-closed 路徑；v3 未修改相關規則。 |
| DR-02 | verified | Binding/observation 分離、不含時間的 VersionSet 保留；移除 adopt_binding.reuse 沒有改變同內容重讀的穩定性。 |
| DR-03 | verified | Immutable evidence/current assessment 分離、pre-PR→PR 的 G1 R-unaffected 與 base 的 R-base 保留；v3 完整矩陣仍支持原轉移。 |
| DR-04 | verified | 不再複製 worker index；從 HEAD baseline 建立 temp index，overlay 採工作樹內容並先分類 scope/exclude。Staged .env.fake 不從 index 帶入；staged out-of-scope 在 add/tree/commit/ref 前拒絕。Tracked excluded 的未修改保留與修改拒絕已明定，controller 匯入再查 tree 差異。原 untracked 遺失與 staged 排除繞過反例均已解除。 |
| DR-05 | verified | Per-attempt clone、controller 唯一整合 writer、CAS／T0-A 查回未改；新 snapshot 仍使用 parent 與 integration lineage，未恢復直接寫 author branch。 |
| DR-06 | verified | Host authority locator、跨 clone 拒絕、run lineage 累計及不可讀 Blocked 未改。 |
| DR-07 | verified | Dispatch session/prompt 分段持久化、訊息 marker 查回、未知時停止/fencing 路徑未改。 |
| DR-08 | verified | Head/merge source discovery、parents mapping、按 source SHA 查詢未改；v3 改為重新觀察 G3，未失去合法 M checks 的取得路徑。 |
| DR-09 | verified | Durable blob/file-directory sync、snapshot 引用屏障及恢復引用完整性未改；小型 probe 未被升格成 power-loss 證据。 |
| DR-10 | verified | 移除 R-reuse 及 adopt_binding.reuse，schema 拒絕舊欄位；spec/design/plan等 binding 或 pinned skill 變更使 G2 stale，必須取得讀過當前 digests 的新契約 Reviewer verdict。完整欄位×gate矩陣與 unknown→stale 補掉遺漏依賴；controller 更新重算 assessment，不能直接 R-unaffected 沿用。原 S1 clean→S2＋reuse 與 skill/controller 欄位漏列反例均解除。 |

## 本輪關鍵依據

- DR-04：design.md:214–247、task 1.2、validation AC-G06/G07/D05。HEAD baseline＋allowed overlay 排除原 staged-index 漏洞，拒絕在新增 snapshot 物件前發生，並定義 baseline tracked excluded 的處理。

- DR-10：design.md:161–206、262–270，tasks 2.1/2.3/2.10，validation AC-G11/G17。reuse 路徑已移除，新契約須新獨立 Reviewer verdict；矩陣缺欄位 fail-closed，skill/controller 更新有明定處理。

## 非阻擋澄清

建議實作時明定 method_changed 是供 G2 判斷方法適用性的 evidence 註記，還是會影響 G1 資格；目前依 G1 確定性核對／G2 語意審查的既有分工，可先完成 G1 再由 G2 審查該註記，未證明存在依賴循環。

保留在實作交接，補 skill更新→G1確定性核對→新契約G2 的狀態機測試；若實作選擇使 method_changed 阻擋 G1，須提供前置 eligibility 或重驗路徑，不能等待尚不可派發的正式 G2。此建議不要求本輪新增修正批次。

## 範圍與限制

已比較 v2→v3 的 design/tasks/validation 改動與 finding-responses，未發現它們破壞先前 verified 結論。來源 hashes 與逐項位置詳見 re-review-v3.json。

所有產品驗證仍未執行；tmp git probe 僅作設計佐證。Runtime／隔離待測能力維持 fail-closed，不據此宣稱已通過。GitHub目標、切片及D11仍待適用決策。所有舊報告與凍結草稿保持原狀。
