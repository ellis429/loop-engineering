# Roadmap 規劃：業界做法整理

收錄日期：2026-09-28。整理「roadmap 該切多細」的常見做法，以及 agentic coding 下的修正，作為 [Project Lead SA 指引的 roadmap 規則](../workflow/project-lead-sa.md#roadmap-怎麼規劃)的背景。來源已於收錄日核對連結與關鍵說法；這是參考材料，採用的規則以 SA 指引為準。

起因：cross-node-file-transfer 規劃 roadmap 時，Lead 問「roadmap 是持續演化的文件，何時該切到多細？M1 能不能先切細，反正會再改？」。

## 傳統做法的共同核心：越近越細

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

## Agentic coding 下的修正

上面的做法以「越近越細」為準，理由是遠期會變、細化要花人力。Agent 寫 spec 很便宜之後，Lead 追問什麼做法真正適用，以下是查到的依據：

| 觀察 | 出處 | 對我們的影響 |
| --- | --- | --- |
| 實作變便宜後，困難集中在「決定什麼才算正確，並可靠地檢查」；code、測試與不變式成形後，詳細 build plan 應該縮小 | [Dispatches from O'Reilly: The right amount of spec for agentic development](https://stackoverflow.blog/2026/08/21/dispatches-from-o-reilly-the-right-amount-of-spec-for-agentic-development/) | 貴的是人的確認，不是寫 spec 本身 |
| Agent 把 spec 當真相，照著它描述的系統寫，不照實際的程式；人會察覺過時，Agent 不會 | [Your spec was right on day one](https://jsmastery.com/blogs/your-spec-was-right-on-day-one-by-day-30-it-s-lying-to-your-agent-)、[Spec drift](https://paelladoc.com/blog/spec-drift/) | 依賴程式現況的細節寫太早，會主動誤導 Agent |
| 分析 3,180 個 Copilot coding agent 的 PR：範圍清楚、內容自足的 issue，合併率高約 16% | [What Makes a GitHub Issue Ready for Copilot?](https://arxiv.org/html/2512.21426v1) | 以 ticket 直接交給 Agent 的小工作，ticket 本身要像規格 |
| Spec 驅動的工具把 spec 放在 repo；spec-kit 打算把「tasks 轉成 issue」移出核心，視為專案管理而非規格流程 | [github/spec-kit](https://github.com/github/spec-kit)、[issue #4421](https://github.com/github/spec-kit/issues/4421) | Ticket 是追蹤，不重寫 spec |

所以我們把「越近越細」改成**看穩定度**：穩定的需求可以先寫細；依賴程式現況的部分，到要做時才寫。

## 我們採用的版本

Roadmap 只有 milestone 與 feature 兩層；feature 是能單獨驗收的交付，每個受影響的 repo 一個審得動的 PR（D57、D61）。寫到多細分成幾種內容，成本差很多：

| 內容 | 包含 | 對應業界做法 |
| --- | --- | --- |
| Roadmap 上的 feature | 名稱、一句範圍、依賴、對應需求輸入的哪幾條 | Story map 上的切片；DEEP 裡較粗的 backlog 項目 |
| Feature spec | Proposal、spec delta、帶 ID 的 AC | Refine 到 ready 的項目 |
| 詳細設計與 plan | Design、tasks | Sprint 或週期內的工作拆解 |

- Feature 標「近期」或「暫定」，作用和 Now／Next 相同：讓讀者分得出哪些已經要做、哪些只是目前的判斷。
- 暫定升為近期就開 change 做 SA；change 寫好且通過驗證，相當於通過 Definition of Ready。
- 切法還沒有依據的 milestone 先只寫交付能力，相當於 Later；遠期但穩定的需求，仍可先在需求輸入裡寫細。
- 每個 feature 驗收後重看 roadmap，相當於定期 refine。

**什麼情況下，當前 milestone 可以整個列出 feature**：切法有依據時，例如有既有實作或穩定的設計，而且需要全貌來規劃平行、依賴或 demo。cross-node-file-transfer 的 M1 就是這種情況，它的 feature 來自 gigaxfer 已實作過的計畫。沒有依據時先只寫 milestone 的交付能力。
