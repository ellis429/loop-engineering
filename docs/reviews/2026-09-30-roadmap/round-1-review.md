verdict: changes_requested

1. **ID：R1-01｜嚴重度：blocking**
   - **位置**：[docs/roadmap.md:33](/Users/johnson.chiang/workspace/loop-engineering-roadmap/docs/roadmap.md:33)、`docs/research/2026-09-30/controller-recut.md:63`
   - **問題**：Feature 3 承諾完成 R2，但 R2 所需的 orchestrate 被排在 Feature 4。研究的 task 對照漏掉 T4.1，因此目前的依賴鏈無法按順序完成驗收。
   - **依據**：【事實】[tasks.md:88](/Users/johnson.chiang/workspace/loop-engineering-roadmap/docs/design-candidate/d45-04/tasks.md:88) 明列 T4.2／R2 相依「1.2、3.1、4.1、6.1、7.1」；同檔第 86 行將 orchestrate 指派給 T4.1。`docs/decisions.md:37`（D27）要求上游接受且 merge 後才實作下游。【推論】依目前歸屬，Feature 3 需要尚未交付的 Feature 4 才能驗收。
   - **建議**：把 R2 所需的最小 orchestrate 路徑提前至 Feature 3，或將 R2 後移；補列 T4.1，重新標示 AC-O06、AC-D06 的完整成立階段。

2. **ID：R1-02｜嚴重度：major**
   - **位置**：[controller-recut.md:63](/Users/johnson.chiang/workspace/loop-engineering-roadmap/docs/research/2026-09-30/controller-recut.md:63)、`docs/roadmap.md:32`
   - **問題**：研究把整個 T7.1 歸給 Feature 2，卻未拆出依賴後續 G1、CI、review 的驗證子項；AC-D17 的完整成立點也因此被提早列為 Feature 3。
   - **依據**：【事實】[tasks.md:85](/Users/johnson.chiang/workspace/loop-engineering-roadmap/docs/design-candidate/d45-04/tasks.md:85) 的 T7.1 相依包含 T3.1、T6.1；`validation.md:212、213、216` 分別要求 review timeout、CI timeout、證據命令到限後的路由。`coverage.md:102` 將 b1–b7 全部列為 D17 的驗證。【推論】只交付 worker 管理的 Feature 2 無法完成整包 T7.1，D17 也仍需要 Feature 4 的 review 路徑。
   - **建議**：按驗證子項拆分：worker 預算歸 Feature 2，證據／CI 預算歸 Feature 3，review timeout 歸 Feature 4；同步更新跨 Feature AC 表。

3. **ID：R1-03｜嚴重度：major**
   - **位置**：[docs/roadmap.md:53](/Users/johnson.chiang/workspace/loop-engineering-roadmap/docs/roadmap.md:53)、`controller-recut.md:63`
   - **問題**：移出 12 條純 workflow AC 後，只有「指到 skill 段落」與缺口 issue，沒有驗證責任及完成點；另有六條混合 AC 的 workflow 驗證完全不在移交清單內。
   - **依據**：【事實】`coverage.md:28、42、46、49、50、53` 分別要求 O01、O15、O19、O22、O23、O26 同時具備 d／s 測試與 W 樣本。[validation.md:233](/Users/johnson.chiang/workspace/loop-engineering-roadmap/docs/design-candidate/d45-04/validation.md:233) 要求獨立 Reviewer 依 rubric 審查，第 235 行明寫「模板存在不算通過」；`docs/decisions.md:62`（D51）也採用樣本與 rubric 驗收。【推論】段落對照不能取代這些驗證，僅有 controller 測試也不能讓六條混合 AC 完整成立。
   - **建議**：移交表涵蓋全部含 W 驗證的 AC，逐項列 owner、正反例、證據位置、覆核者及完成階段；延期者明列待完成，不能僅因找到 skill 段落便視為已覆蓋。

4. **ID：R1-04｜嚴重度：major**
   - **位置**：[docs/roadmap.md:21](/Users/johnson.chiang/workspace/loop-engineering-roadmap/docs/roadmap.md:21)、`controller-recut.md:70`
   - **問題**：M2 遺漏 O23、G15、D23 的延後部分，研究卻把三條 AC 分別列入 Feature 1／2／3。M2 的 Retro op、Project Lead 委派也仍沿用 D55 前的範圍。
   - **依據**：【事實】[tasks.md:172](/Users/johnson.chiang/workspace/loop-engineering-roadmap/docs/design-candidate/d45-04/tasks.md:172)、第 175、176 行明列「只停受影響工作」、「整合 SHA 映射」、「D23 的 OpenCode-only 變體」延期；`coverage.md:50、75、108` 同樣保留未完成部分。`docs/decisions.md:67`（D55）已將 O14 改由 skill 承接、O18 縮為授權啟動 run 的紀錄，並新增 S2 唯讀專案進度視圖。
   - **建議**：補齊 M2 能力清單並套用 D55；AC 對照明列「M1 部分成立 → M2 補齊」，不要只計六條整體延期 AC。

5. **ID：R1-05｜嚴重度：major**
   - **位置**：[docs/roadmap.md:34](/Users/johnson.chiang/workspace/loop-engineering-roadmap/docs/roadmap.md:34)
   - **問題**：唯一承接 orchestrate 的 Feature 4 只串 `plan-to-code`、`to-pr`，沒有安排從交接包進入 `spec-to-plan` 並等待開工確認的路徑。
   - **依據**：【事實】[docs/decisions.md:81](/Users/johnson.chiang/workspace/loop-engineering-roadmap/docs/decisions.md:81)（D69）要求 orchestrate 依序呼叫三個 skill，「在 ◆確認開工停下」；第 67 行（D55）明定交接包不含開工確認。舊 `design.md:12` 才是從已批准的 plan 出發。
   - **建議**：補列三段串接及人工停點的歸屬；若刻意維持舊入口，應明列延期範圍及需要 Lead 修訂的決策。

6. **ID：R1-06｜嚴重度：major**
   - **位置**：[controller-recut.md:63](/Users/johnson.chiang/workspace/loop-engineering-roadmap/docs/research/2026-09-30/controller-recut.md:63)、同檔第 102 行；`docs/roadmap.md:20`
   - **問題**：研究把 T8.1／R3 算入 Feature 4，並要求最後一個 Feature 補齊原 AC；roadmap 卻又把四個 Feature 完成 archive 與 R3 分列為 M1 條件。兩份文件沒有一致區分 Feature 4 自身驗收與合併後的真實示範。
   - **依據**：【事實】[validation.md:260](/Users/johnson.chiang/workspace/loop-engineering-roadmap/docs/design-candidate/d45-04/validation.md:260)、`tasks.md:163–164` 要求 R3 在 bootstrap accepted、merged、baseline 登記後，以另經 D11 選定的新行為執行。【推論】若 R3 是 Feature 4 自身 AC 的必要完成證據，便形成「先驗收 merge 才能取得驗收證據」的循環。
   - **建議**：把 R3 明列為四片合併後的 M1 驗證階段，保留獨立 D11、baseline 與證據責任；對 G01、D14、G20 等分列產品驗證及 R3 證據，不在 Feature 4 archive 時宣稱後者已成立。

7. **ID：R1-07｜嚴重度：minor**
   - **位置**：[controller-recut.md:77](/Users/johnson.chiang/workspace/loop-engineering-roadmap/docs/research/2026-09-30/controller-recut.md:77)
   - **問題**：G19、D22 可以由 Feature 2 首先承接，但將兩者等同「preflight 報告的行為」縮窄了原驗收契約。
   - **依據**：【事實】[validation.md:248](/Users/johnson.chiang/workspace/loop-engineering-roadmap/docs/design-candidate/d45-04/validation.md:248) 要求 `proof.md` 對每項能力分列 `fake／profile-probe／real-E2E`，按接法分開，未執行格標 `none`；`design.md:182` 的 preflight receipt 並不包含這份完整驗收矩陣。
   - **建議**：明列 Feature 2 建立並覆核矩陣，後續 Feature 與 R3 更新各自證據；不必等全部實測才建表，但不能只交付 preflight receipt。

8. **ID：R1-08｜嚴重度：minor**
   - **位置**：[docs/roadmap.md:66](/Users/johnson.chiang/workspace/loop-engineering-roadmap/docs/roadmap.md:66)
   - **問題**：退役方案刪除 change，卻沒有安排更新現存入口及歷史引用；「留在 Git 歷史」不足以讓目前的連結繼續可用。
   - **依據**：【事實】[README.md:7](/Users/johnson.chiang/workspace/loop-engineering-roadmap/README.md:7) 連到將被刪除的 design、tasks；`docs/handoffs/2026-09-27-controller-design.md:112` 連到 proposal；`docs/decisions.md:50` 連到舊 approval。D53 核准快照另存於 `d11-approval.json:12–28`，原樣搬移四份 spec 本身不會改變內容 hash。
   - **建議**：退役步驟加入引用清查：現行入口指向新需求輸入，歷史引用改為固定 commit；保留可定位的 superseded 快照及 source-map，並驗證搬移前後 hash。

9. **ID：R1-09｜嚴重度：minor**
   - **位置**：[controller-recut.md:35](/Users/johnson.chiang/workspace/loop-engineering-roadmap/docs/research/2026-09-30/controller-recut.md:35)、同檔第 43、58 行
   - **問題**：task 行數表的逐列加總不等於合計；後文又把尚未完成的實作大小寫成整個 controller PR 的大小。
   - **依據**：【事實】第 35–42 行相加為程式 **6,247**、測試 **8,841**，不是第 43 行的 **6,054／8,825**。唯讀重算 `fcefecc` 的實際檔案則得到 **6,054／8,825**；第 16 行也明列 T5.1、T6.2 等尚未完成。【推論】表格混用了新增量與現存量，不能直接作為完整交付大小的測量。
   - **建議**：補上各 task 的 commit 範圍及新增／刪除／淨增口徑；把 14,879 行標為目前實作量，未完成部分另列估計。

核對後未列為 finding 的結論：Feature 1 的登記、人工決策、唯讀狀態與中斷恢復具有獨立可觀察行為，不能僅因沒有派工就判為水平切；ADDED 後以 MODIFIED 擴充符合 D58 與 `openspec/config.yaml:17`。D61 的解讀已明列待 Lead 決定，尚未冒充既定決策。E-1／#9、E-2／#11、E-3／#12 的對應正確。M1 保留「Blocked 或沒有 finding，R3 維持 open」也符合原驗法。

**實際打開核對的檔案**

- `docs/roadmap.md`、`docs/research/2026-09-30/controller-recut.md`。
- `docs/decisions.md`，包含指定的 D27、D53、D54、D57、D58、D61、D62、D63、D65、D67、D69、D71、D73、D74。
- `skills/project-lead/SKILL.md` §5、`docs/guide/user-guide.md` A3、`docs/references/roadmap-planning.md`。
- `openspec/changes/implement-delivery-loop/specs/` 下四份 `spec.md`、`adoption/source-map.md`、`approval.json`。
- `docs/design-candidate/d45-04/` 下 `coverage.md`、`tasks.md`、`validation.md`、`design.md`、`d11-approval.json`、`reviews/revision-17/publication-manifest-at-d11.json`；以及 `docs/design-candidate/d45-04-errata.md`。
- `openspec/config.yaml`、`.agents/skills/openspec-sync-specs/SKILL.md`、`README.md`、`docs/validation/implement-delivery-loop.md`、兩份 controller／Herdr handoff。
- `loop-engineering-thin@fcefecc`：`src/loopctl/`、`tests/` 的檔案行數，`src/loopctl/next.py`，本機 task 收件紀錄、T5.1 停止紀錄、`.delivery/bootstrap/thin-s1/loop-2-3/morning-report.md` 及 Git 歷史。

**AC 核對清單**

全表核對 **O01–O28、G01–G20、D01–D24、F01–F16，共 88 條**，ID 無遺漏或重複。逐项追查「驗證欄 → task → Feature」的重點清單：

- O01、O02、O06、O11、O12、O13、O15、O16、O19、O22、O23、O26。
- G01、G06、G08、G11、G12、G13、G15、G17、G19、G20。
- D04、D06、D12、D13、D14、D15、D16、D17、D18、D19、D22、D23。
- F07、F11、F12。

全程未修改檔案，未執行產品測試或任何 GitHub 寫入。GitHub API 連線失敗，因此無法確認提供清單以外是否另有 open issue；549 個測試也未重新執行驗證。10/16 仍是排程提案，實測的 2 小時 39 分不能直接證明每個 Feature 1.5 工作日及 R3 一日的假設。