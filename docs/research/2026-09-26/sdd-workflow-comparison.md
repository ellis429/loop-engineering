# OpenSpec、Superpowers、Matt Pocock skills：流程與口碑比較

研究日期：2026-09-26。官方來源查核：Matt `c55ee46073ed923f86ce59a5eb3b6d895095d1b7`（2026-09-18）、OpenSpec `79b6aa9c98f1e36795b2bc4ef2a8f770c6d3a777`（2026-09-25）；Superpowers 本機 6.3.0，未以較新版本行為代替本機驗證。用途：為 orca-delivery 的方法選用提供依據；不是新增 workflow 決策。官方文件／程式定義能力，使用者心得只代表其使用情境。未執行三套的同條件品質或成本 benchmark。

## 官方流程與本機查核

| 對象 | 主線與產物 | 對我們的意義 |
| --- | --- | --- |
| OpenSpec | 管理 change 及 proposal／specs／design／tasks，提供規格到實作、驗證及封存的流程。[官方 repo](https://github.com/Fission-AI/OpenSpec) | 適合作為規格／變更的持久交接來源；tasks 勾選不能直接當成三 gates 的證據 |
| Superpowers | 組合 brainstorming、writing-plans、TDD、subagent-driven-development／executing-plans 與 review 等方法。[官方 repo](https://github.com/obra/superpowers) | 適合採用具體實作與驗證方法；整套執行的派工權要與 controller 明確整合 |
| Matt Pocock | 以可組合 skills 將釐清、規格、tickets、實作與 review 串接；`to-spec` 與 `implement` 的契約不同。[官方 repo](https://github.com/mattpocock/skills) | 適合人主導需求與取捨，也可選用單一方法；不能只憑名稱視為完整交付控制器 |

### Matt：先區分 to-spec、implement、implement-spec

- `to-spec` 整理已有對話與 codebase 理解，不重新進行需求訪談。它要求檢視測試接縫並與使用者核對，依模板形成 spec，再發布到已設定的 issue tracker；規格刻意避免易過期的檔案路徑和實作碼（有決策價值的 prototype 片段為例外）。因此「會整理 spec」不等於「已幫你做完整需求探索」。 接著的 `to-tickets` 可拆垂直 slices 與依賴；不是每份 spec 都必須另跑一次冗長 planning。[官方 SKILL.md](https://github.com/mattpocock/skills/blob/c55ee46073ed923f86ce59a5eb3b6d895095d1b7/skills/engineering/to-spec/SKILL.md)
- `implement` 是短的實作方法：按 spec／tickets 工作，在事先同意的接縫盡可能使用 TDD，過程中做 typecheck／局部測試，最後跑全套測試和 code-review，commit 到目前 branch。這段契約沒有定義我們要求的 GitHub CI polling、三 gates 或持久 review/fix controller。 官方 implement 文件也說明未包含自動處理 review findings 的步驟，且 review-before-commit 與 HEAD-based diff 有可能漏看未提交修改，需在整合時核對。[官方限制說明](https://github.com/mattpocock/skills/blob/c55ee46073ed923f86ce59a5eb3b6d895095d1b7/docs/engineering/implement.md)[官方 SKILL.md](https://github.com/mattpocock/skills/blob/c55ee46073ed923f86ce59a5eb3b6d895095d1b7/skills/engineering/implement/SKILL.md)
- `implement-spec` 與單票 `implement` 不同：本輪查核的上游路徑在 `skills/in-progress`，包含依 tickets 依賴派 subagents、隔離分支／worktree、整合與 PR 收尾。若採用它，需要處理其外層派工與我們唯一 controller 的重疊，不能把它當成只執行一個 task 的替換件。[官方 SKILL.md](https://github.com/mattpocock/skills/blob/c55ee46073ed923f86ce59a5eb3b6d895095d1b7/skills/in-progress/implement-spec/SKILL.md)
- 本機 `to-spec`、`to-tickets`、`implement`、`implement-spec` 均有 user-only 呼叫設定。查閱程式不等於執行 skill；本輪未啟動任一套實作流程。自動化整合須明示方法、來源版本及改動，不能以薄封裝默默繞過呼叫限制。

### 已核對的本機狀態與推論範圍

- Orca-delivery 的 `openspec/config.yaml` 使用 `spec-driven`，`openspec list --json` 目前回傳沒有 active changes。現有設計仍在 `docs/`，不能宣稱已產生正式 OpenSpec change。
- 本機 `openspec-apply-change` 會讀實際 contextFiles、逐 task 實作及更新 checkbox；`openspec-verify-change` 檢查完整性、正確性與一致性。這些是 agent 的流程指令，不是我們三 gates 的可執行判定器。 官方流程還允許未完成 tasks 的 archive 警告及可選 verify，因此不可把「可封存」等同我們的 PR Pass。[官方 workflows](https://github.com/Fission-AI/OpenSpec/blob/79b6aa9c98f1e36795b2bc4ef2a8f770c6d3a777/docs/workflows.md)
- 本機 Superpowers 路徑版本為 `6.3.0`。其 SDD 已有進度帳本與 review 工作程序，不能說它「完全沒有狀態」；但這不等於已具備我們的外部 runtime 身份核對、GitHub checks 適用性、outbox 去重與重啟恢復。[版本化 SDD skill](https://github.com/obra/superpowers/blob/v6.3.0/skills/subagent-driven-development/SKILL.md)
- D26 已選 Superpowers TDD，加上我們明定的文件／註解 N/A 覆核政策。Matt `implement` 會接其 `/tdd`／`code-review`；整套切換需明示方法差異。不得以本研究自行更改 D26、G2 獨立性或 finding closure。

「三套現成流程都不直接等於本專案完整 controller」是依本次契約對照作出的設計判斷，並非對未讀取插件或所有版本的全面否定。

## 使用者口碑：取樣，不是勝率排名

本次於 2026-09-26 搜尋實際使用心得；優先保留有使用情境、具體優缺點的原作者文章或討論，沒有找到足以作三者客觀排名的同模型、同任務、同版本對照。以下是發文者的經驗，未獨立重跑；token／時間差異不當成普遍效能數據。Reddit 的搜尋日期與頁面相對時間有落差時，不據此推算精確發文時間。

| 對象 | 正面經驗 | 負面經驗與限制 | 原始心得 |
| --- | --- | --- | --- |
| OpenSpec | 使用者認為 artifacts 有助團隊交接；另有人搭配內部文件，在隔三週後能快速重新理解專案 | 有人嫌各 repo／開發者需維護 CLI 與 skills 版本；另有使用者同時用 OpenSpec／Superpowers，仍覺得結果與直接 coding 差異有限 | [兩者使用討論](https://www.reddit.com/r/ClaudeCode/comments/1tlp5xa/superpowers_vs_openspec_or_both/)、[隔週接續專案](https://www.reddit.com/r/ClaudeAI/comments/1pnmc68/using_openspec_for_sdd_and_asking_claude_to_keep/)、[品質與流程疑問](https://www.reddit.com/r/ClaudeAI/comments/1tptgl2/how_are_you_actually_getting_the_most_out_of/) |
| Superpowers | 有人認為先討論方案與取捨，比原生 Plan mode 更容易對齊，功能正確性與生產力改善 | 同討論有人抱怨既有專案仍重問技術棧、流程耗時；一篇以同款 travel app 試工具的文章認為整體勝過 OpenSpec，但仍耗兩個額度週期且表單有缺陷 | [正反使用者回覆](https://www.reddit.com/r/ClaudeAI/comments/1sastem/a_rave_review_of_superpowers_for_claude_code/)、[Improve & Repeat，2026-04-21](https://improveandrepeat.com/2026/04/are-superpowers-or-gsd-better-than-openspec/) |
| Matt Pocock skills | 一位從 Superpowers／其他流程轉入的作者認為文件更短、ticket 更聚焦、訪談更能找出決策；另有使用者稱 grill 後實作只需少量修整 | 同時有人花數小時回答問題和讀 spec，感到負擔；有跨 runtime 使用者遇到跳過步驟或未正確派 subagent，需調整整合 | [Jay 個人經驗，2026-08-27](https://otzslayer.github.io/essay/2026/08/27/matt-pocock-skills.html)、[grilling／wayfinder 討論](https://www.reddit.com/r/ClaudeCode/comments/1w89udt/matt_pocock_skills_grilling_and_wayfinder_how_is/)、[跨 runtime 的限制](https://www.reddit.com/r/google_antigravity/comments/1wd5sxi/any_one_using_matt_pacock_skills_in_antigravity/) |

這些報告支持「流程有用但有成本、結果受實際整合影響」的觀察，不支持「某套必定省 token／程式必定正確」。沒有用 stars、宣傳文或成功案例數量推算品質。

## 對 orca-delivery 的建議（未新增決策）

- 規格與變更紀錄沿 D07 使用 OpenSpec；本輪不重開已選 authoring 方式。
- Matt 的 grilling／domain 方法可繼續用於尚未解決的需求與架構；`to-spec` 是整理已討論內容的另一種規格入口，不要求同一 feature 再產生一份與 OpenSpec 競爭的 spec。
- 實作沿 D26 使用一套 Superpowers TDD。若選 Matt `implement` 整套，需明示處理其內建 TDD／review 與我們政策的差異，不能暗中混用兩套要求。
- OpenSpec apply、Superpowers SDD、Matt implement-spec 均有自己的執行步驟或 loop。整合時只有 controller 擁有 feature 外層派工權，局部 review 仍不取代 G2。
- 此次只研究，不安裝／執行任何 workflow，也未執行 comparative benchmark。正式 spec/design/tasks 與 controller 開發另行完成；P03 試跑不因本研究啟動。

若要在下一個新 feature 比較，固定 spec/AC、模型、工具權限與驗證環境，記錄首次 G1／review 結果、有效 blocker、修正輪次、使用者介入時間、elapsed time 與可取得的 token 用量。只比較「用了幾次 prompt」或產生多少文件沒有交付品質意義；這是未執行的評估建議。
