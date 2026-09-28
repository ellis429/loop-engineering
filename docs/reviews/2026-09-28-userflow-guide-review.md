# Review：使用指南角色、兩層流程與交接圖

任務 ID：`userflow-guide-review-20260928-01`。依 [交接指示](../handoffs/2026-09-28-userflow-guide-review.md) review 並改善 [使用指南](../workflow/user-guide.md)。日期 2026-09-28。

這是文件呈現的 review，不是 controller、example 或任何產品 gate 的驗收。

## 輸入

- 指南修改前 sha256 `24bc6bf95d1770c165e174de46cd12df1a2853be5f8c95635db44454dc1466f6`。
- 對照：[overview](../workflow/overview.md)、[contracts](../workflow/contracts.md)、[decisions](../decisions.md)（到 D53 與 Q-STACK）、[Project Lead SA](../workflow/project-lead-sa.md)、[controller handoff](../handoffs/2026-09-27-controller-design.md) 最新段、[research-codebase skill](../../skills/research-codebase/SKILL.md)。
- 視覺化工具：使用者指定 [diagram-design](https://github.com/cathrynlavery/diagram-design) skill，commit `cea465e7f5ea1043d8dab21a99f2dd3f7f661beb`，已依使用者同意安裝到 `~/.claude/skills/diagram-design`。

## 發現

| # | 發現 | 影響 | 處理 |
| --- | --- | --- | --- |
| F1 | 角色圖的人與 Agent 外觀相同，只靠名稱區分；Lead（人）出現兩個節點 | 讀者難以一眼分出誰決定、誰執行 | 改為全貌泳道圖與「人／Agent／機制 × Project／Feature」對照表；各圖統一配色 |
| F2 | 「Lead（人）」與「Project Lead Agent」名稱相近，指南沒有直接說明差別 | 容易把 Agent 的建議當成人的決定 | 新增一段說明：Lead 做決定，Project Lead Agent 分析並整理文件 |
| F3 | Use case 1 是六個方框的直線，沒有 grill 往返與「可進入 Design」的判斷點 | 看不出 research → SA／grill → 高層設計 → roadmap 的反覆與人的確認 | 重畫：research 與 SA 分開，grill 回到 Lead，加入兩個人的確認點 |
| F4 | Use case 3 單張圖 13 個節點，主線與 review-fix loop 混在一起；多條箭頭沒有標交接物 | 讀者抓不到人只在開工與驗收兩處介入 | 拆成主線圖與 review-fix loop 圖；每條箭頭標交接物或退回原因 |
| F5 | 指南沒有明寫「Reviewer 不直接修改被審 branch」 | 交接要求保留的邊界不夠顯眼 | 在角色段、泳道圖註記、review-fix 圖節點三處寫明 |
| F6 | Use case 4 的圖本身沒有標示「目標情境」，只靠前一段文字 | 圖被單獨截取時會像已可用的 stacked gating | 圖內加「待 Q-STACK 確認與實作，現在不可用」的框；新增現行 D27 與目標並排對照圖；箭頭改為 base 關係，不暗示未定的開工順序 |
| F7 | 交接只有表格，沒有流程圖 | 看不出交接物的順序與誰收 | 新增交接鏈圖，箭頭標交接物；表格保留 |
| F8 | 工具表的研究列寫「Matt 的 research」 | 與使用者 2026-09-28 指定的 HumanLayer research-codebase 不符 | 研究列改指 `skills/research-codebase`，SA／grill 列保留 Matt 方法 |
| F9 | 「現在做到哪裡」寫「D11 開工確認尚未完成」 | 已過期：D53 已核准 revision-17 的 design＋plan | 改為 D53 已核准、下一步建立文件分支與 worktree、產品未實作 |
| F10 | `docs/README.md` 的「目前進度」仍寫 revision-14、D11 未確認 | 同 F9，入口頁狀態過期 | 使用者 2026-09-28 要求一起更新；改為 D53 已核准 revision-17、下一步 T0.1、產品未實作 |

## 修改

| 檔案 | 內容 |
| --- | --- |
| [docs/workflow/user-guide.md](../workflow/user-guide.md) | 依 F1–F9 修改；新增「一張圖看全貌」；七張 Mermaid 圖共用人／Agent／關卡／機制配色 |
| [docs/workflow/user-guide-visual.html](../workflow/user-guide-visual.html) | 新增圖解頁：全貌泳道圖、stacked PR 現行與目標對照。是兩張 SVG 的來源 |
| [docs/workflow/user-guide-roles.svg](../workflow/user-guide-roles.svg)、[user-guide-stack.svg](../workflow/user-guide-stack.svg) | 依 skill 的 export 程序從圖解頁匯出，供指南內嵌 |
| [README.md](../../README.md) | 只補圖解頁的入口連結 |
| [docs/README.md](../README.md) | 補圖解頁入口連結；依使用者要求更新「目前進度」（F10） |

交接要求保留的規則逐條核對後仍在：G1 先於送審、G2 與 G3 獨立並行、結果適用最新版本、Reviewer 不改被審 branch、PR Pass／人工接受／merge 分開、每個 feature 一個協調 loop、Orca 選配且角色不綁 runtime、D27 現行與 Q-STACK 待決、D11 不新增逐 task 簽核。

未修改產品程式、tests、正式 OpenSpec、controller 候選、gigaxfer、`project-lead-sa.md` 或 `docs/harness/overview.md`。

## 驗證

- diagram-design 的 `self_check.py`：圖解頁通過，0 項問題。
- diagram-design repo 的 `verify-geometry.py`：0 項問題。
- 兩個 SVG 以 `xmllint` 解析通過。
- 以 headless Chrome 渲染圖解頁、兩個 SVG，以及指南內七張 Mermaid 圖（Mermaid 11，逐張單獨渲染），全部無錯誤，並逐張看過截圖的可讀性。
- 指南、README、docs/README 與圖解頁的相對連結全部可解析。

GitHub 上的實際顯示沒有驗證，因為本次沒有 push。

修改後 sha256：

```text
user-guide.md          40099cd2617c4d7c564f8d4e406dfbefb94cac8a518ddb8d29272cff8d1708f2
user-guide-visual.html de7931ba2f2f37737e8f0ec93496651b639ab8b0200e9bc848c8f872fa076a4e
user-guide-roles.svg   d2f1ffb2066634378def692b1d91c0e5d36f1cc8d954d25bb5a51dad5e82946a
user-guide-stack.svg   b207b678256bcee3467cf4682c4ea746a029be0d5231f549a02f7542b21c1a0c
```

## 假設與未決

- **配色**：skill 第一次使用要選品牌配色。先採用 skill 預設配色，使用者於 2026-09-28 回覆「先預設」確認。要換品牌色時改 skill 的 style guide 再重新匯出。
- **維護成本**：SVG 是從圖解頁匯出的副本。改圖時要先改 HTML，再重新匯出兩個 SVG，否則兩者會不一致。
- **Q-STACK 與 Q-DEMO-PEOPLE** 仍待使用者回答；圖只呈現目標，不代表已批准。
## 後續：spec 結構與兩個 skill（2026-09-28）

同一天的後續討論，產生兩個使用者確認的決策：

- **D54**：Spec 的位置、格式與回流採 OpenSpec。SA 七項是檢核表，放進 proposal 與 spec delta 的四個位置；人確認照意思排列的摘要，放檔案由 Project Lead Agent 負責。
- **D55**：Project Lead 有自己的 `project-lead` skill；`orchestrate` 只跑單一 feature loop，控制方向由 Project Lead 往下。修訂 D17 與 D28。

D53 核准的第一片只管單一 feature，adopt 與 delegate 已回 `unsupported`，Retro 與 Project Lead 委派已延後，所以兩個決策都不需要改 Herdr session 正在實作的規格。

使用者再提議把使用指南依角色拆成三份，經評估後同意三項調整：兩層介面只在總覽定義一次、拿掉 Use case 編號、刪除總覽裡重複的交接鏈圖並把交接表移到交接契約。

| 檔案 | 內容 |
| --- | --- |
| [user-guide.md](../workflow/user-guide.md) | 改為總覽：角色、控制方向、兩層介面、文件位置、工具、演練路線與進度 |
| [user-guide-project-lead.md](../workflow/user-guide-project-lead.md) | 新增：進入 SA、完成 project level、spec 放哪與確認摘要、交出 feature、收尾、goal 與 stacked |
| [user-guide-feature-builder.md](../workflow/user-guide-feature-builder.md) | 新增：收到交接包後的詳細設計、TDD、PR、review-fix loop、PR Pass 與交回的結果 |
| [skills/project-lead/](../../skills/project-lead/SKILL.md) | 新增 skill 草稿，尚未演練 |
| [project-lead-sa.md](../workflow/project-lead-sa.md)、[contracts.md](../workflow/contracts.md)、[overview.md](../workflow/overview.md) | 依 D54、D55 更新；交接表移到契約的「角色交接摘要」 |
| [openspec/config.yaml](../../openspec/config.yaml) | 加入 proposal、specs、design 的 per-artifact rules |
| [CONTEXT.md](../../CONTEXT.md) | 新增 Lead、Feature Builder、Orchestrate、交接包 |
| 圖解頁與兩個 SVG | 泳道標題改為 Feature Builder，重新匯出 |

這些修改在從 origin/main 開出的 `docs/project-lead-skill` 分支。PR #3 合併後，原工作目錄的文件已不是權威版本；PR #3 之後新增的修改，包括 Workflow builder 的 research-codebase skill 與兩處來源說明，都原樣帶進這個分支。

未決：`orchestrate` 與 ADE 層 Orchestrator 同名，改名另議；專案進度視圖列入 S2；project-lead skill 需要實際演練；Q-STACK 與 Q-DEMO-PEOPLE 仍待回答。

### 獨立 review 第 1 輪

審查者：GPT-6 Astra，reasoning xhigh，經 `codex exec -s read-only` 開獨立 session；作者是 Claude。結果 `changes_requested`，8 項 blocking，逐項核對後都成立：

| ID | 問題 | 修正 |
| --- | --- | --- |
| R-01 | D55 把開工確認放進交接包，但 design＋plan 是 feature loop 裡才產出；授權模式因此無法啟動 | D55 (3)(4)、總覽、Project Lead 指南、skill、CONTEXT 改為：交接包不含開工確認；授權模式可啟動 loop，loop 停在 design＋plan 等人確認，Project Lead 不能代批 |
| R-02 | 總覽的 PR Pass 驗收包與 Blocked 漏了 run ID | 兩者都列 run ID；skill 收件時核對 run ID 與版本 |
| R-03 | Retro 被綁在 merge 之後，與 D28「人工驗收後」不符 | 拆開：接受後整理 Retro、提出下一個 feature；merge 核實後才 archive |
| R-04 | skill 的 delta 標題寫成 `## ADDED`，OpenSpec 1.13.1 解析不到 | 寫出完整四種標題 |
| R-05 | decisions 與 contracts 仍有「orchestrate 負責 Retro 或 project artifact index」的殘留 | 改為 project-lead；overview 同類殘留一併修正 |
| R-06 | CONTEXT、contracts、README 仍允許 ticket 內文承載 feature spec | 依 D54 改為 OpenSpec change 承載、ticket 只保存摘要與引用；D04 加註 |
| R-07 | skill 要求每輪把答案都寫進 CONTEXT | 依內容分流：需求進 spec、待決進 proposal、共用詞彙才進 CONTEXT |
| R-08 | 兩個 README 仍說正式 change 在 scope revision pending | 改為現況：D53 採用、第一片實作中、PR #2 仍未合併 |

作者自審另找到一項：總覽的控制方向圖讓 PR Pass 驗收包經 Project Lead 轉交，和介面表不一致；改為直接交驗收人，副本給 Project Lead。

### 獨立 review 第 2 輪

同一模型、新的唯讀 session。R-01、R-02、R-04、R-07、R-08 判定 fixed，無新發現。R-03、R-05、R-06 在其他段落還有殘留，已修正：

- **R-03**：總覽演練步驟與 Feature Builder 指南仍寫「驗收並 merge 後」才 Retro；改為接受後 Retro、merge 後 archive。
- **R-05**：`overview.md` 的 Retro 段與 D17 router 段、`harness/overview.md` 的 project orchestrate 相關四列仍屬舊分工；改依 D55，兩份設計文件開頭各加 D54／D55 註記。
- **R-06**：`CONTEXT.md` 的 Feature ticket 定義仍寫「包含或引用其 feature spec」；改為只保存摘要並引用。

### 獨立 review 第 3 輪

同一模型、新的唯讀 session，只覆核 R-03、R-05、R-06：三項都 fixed，沒有新發現，`VERDICT: clean`。這是文件覆核，不是產品 gate。

### 獨立 review 第 4、5 輪：roadmap 規則與 D56

第 3 輪之後新增了 D56、roadmap 規劃規則（SA 指引、skill、Project Lead 指南與參考文件）、狀態文字，以及把指南裡的「Phase 0」改成「專案骨架 F0」。同一模型、新的唯讀 session 審查這些新增內容：

- **第 4 輪** `changes_requested`：R-01（blocking）skill 把 roadmap 步驟排在 SA 人工確認之前，與 SA 指引的順序相反；R-02（nonblocking，main 上既有）`docs/README.md` 連到不存在的 `src/delivery/`、`tests/`。審查者上線核對了參考文件的五個出處，沒有誇大。
- **修正**：roadmap 步驟移到第 5 步之後，成為「5a. Project level: high-level design and roadmap」，並明寫先完成或沿用高層設計；README 那列改為純文字並說明舊程式所在的分支。
- **第 5 輪** `clean`：兩項都 fixed，沒有新矛盾。
