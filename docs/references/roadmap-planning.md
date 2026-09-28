# Roadmap 規劃：業界做法整理

收錄日期：2026-09-28。整理「roadmap 該切多細」的常見做法，作為 [Project Lead SA 指引的 roadmap 規則](../workflow/project-lead-sa.md#roadmap-怎麼規劃)的背景。來源已於收錄日核對連結與關鍵說法；這是參考材料，採用的規則以 SA 指引為準。

起因：cross-node-file-transfer 規劃 roadmap 時，Lead 問「roadmap 是持續演化的文件，何時該切到多細？M1 能不能先切細，反正會再改？」。

## 共同的核心：越近越細

| 做法 | 出處 | 重點 |
| --- | --- | --- |
| Rolling wave planning（滾動式規劃） | PMI《PMBOK Guide》；見 [Wikipedia](https://en.wikipedia.org/wiki/Rolling-wave_planning)、[PM Study Circle 的整理](https://pmstudycircle.com/rolling-wave-planning/) | 近期工作詳細規劃，遠期只到較高層級；屬於 progressive elaboration，隨資訊增加逐步細化 |
| DEEP product backlog | Roman Pichler 與 Mike Cohn；見 [Pichler](https://www.romanpichler.com/blog/make-the-product-backlog-deep/)、[Mountain Goat Software](https://www.mountaingoatsoftware.com/blog/make-the-product-backlog-deep) | Detailed appropriately：優先的項目較細，後面的較粗；Emergent：backlog 持續變動，要定期 refine |
| Now／Next／Later roadmap | Janna Bastow，ProdPad；見 [Why I Invented the Now-Next-Later Roadmap](https://www.prodpad.com/blog/invented-now-next-later-roadmap/) | 用三個時間範圍取代固定日期，表達的是把握程度而不是交期 |
| User story mapping | Jeff Patton；見 [Story Map Concepts](https://www.jpattonassociates.com/wp-content/uploads/2015/03/story_mapping.pdf) | 先把整個旅程攤開看全貌，再橫切成 release；第一片是能走完全程的最小切片（walking skeleton） |

## 反方觀點

Basecamp 的 [Shape Up〈Bets, Not Backlogs〉](https://basecamp.com/shapeup/2.1-chapter-07)刻意不維護長 backlog，每個週期只為下一輪挑選工作：

> "Backlogs are a big weight we don't need to carry. Dozens and eventually hundreds of tasks pile up that we all know we'll never have time for."

它提醒的風險是真的：長清單會過時，還會被誤當成承諾，維護它本身也花時間。上面各做法都用某種方式控制這個風險：DEEP 只細化前段，Now／Next／Later 用分欄表達把握程度。

## 我們採用的版本

「切細」分成三個層次，成本差很多，只有第一層可以提早做：

| 層次 | 內容 | 對應業界做法 |
| --- | --- | --- |
| Roadmap 切片 | 名稱、一句範圍、依賴 | Story map 上的切片；DEEP 裡較粗的 backlog 項目 |
| Feature spec | Proposal、spec delta、帶 ID 的 AC | Refine 到 ready 的項目 |
| 詳細設計與 plan | Design、tasks | Sprint 或週期內的工作拆解 |

- 切片標「近期」或「暫定」，作用和 Now／Next 相同：讓讀者分得出哪些已經要做、哪些只是目前的判斷。
- 暫定升為近期，就開始該片的 SA；SA 確認並備妥交接包，相當於通過 Definition of Ready。
- 後面的 milestone 只列 feature，相當於 Later。
- 每個切片驗收後重看 roadmap，相當於定期 refine。

**什麼情況下，當前 milestone 可以整個切到切片層**：切法有依據時，例如有既有實作或穩定的設計，而且需要全貌來規劃平行、依賴或 demo。cross-node-file-transfer 的 M1 就是這種情況，它的切片來自 gigaxfer 已實作過的計畫。沒有依據時保持在 feature 層。
