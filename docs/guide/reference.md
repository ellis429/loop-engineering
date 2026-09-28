# Loop Engineering 使用指南：參考

[使用指南](user-guide.md)照流程講每個活動；這裡放要查才看的細節，順序跟流程相同。以下各圖使用同一套顏色：

```mermaid
flowchart LR
    H["人的工作與決策"]:::human
    A["Agent 工作"]:::agent
    G["需人批准的關卡"]:::gate
    M["協調與核對機制"]:::mech
    classDef human fill:#e9ebef,stroke:#7a8399,color:#2d3142
    classDef agent fill:#ffffff,stroke:#2d3142,color:#2d3142
    classDef gate fill:#fdf0ea,stroke:#eb6c36,color:#2d3142
    classDef mech fill:#f5f5f5,stroke:#4f5d75,stroke-dasharray:4 3,color:#2d3142
```

## 需求是怎麼問出來的

用於 A1 Project SA 與 B2 Feature SA。

Agent 不是想到什麼問什麼。它**先搭骨架，再由上往下問**：

1. **搭骨架**：骨架就是 SA 的七項（問題與目標、範圍、角色與情境、行為與規則、例外與限制、驗收、待決）。Agent 根據問題描述和研究先寫成草稿，每一格都標「假設」。
2. **由上往下確認**：從目標開始請你確認或修正；上一層定了，才問下一層。每個問題都對得回骨架的某一格。
3. **邊問邊寫**：你答完，Agent 就把那一格改成確認過的內容，寫進對應的文件。已經確認過的內容直接沿用，只核對適用性、追問差異。

以下是示意的例子，不是 cross-node-file-transfer 實際的問答紀錄。假設手上只有一段問題描述：「交易要用到前一站在別的 DC 產生的檔案，希望故障時交易不停擺。」

### Project SA：骨架到能力與 roadmap

```text
1. 問題與目標    某個 DC 故障時，其他 DC 的交易仍拿得到需要的檔案       （假設）
2. 範圍與不做    Ready 後的檔案不可修改；不支援跨部署範圍同步             （假設）
3. 角色與情境    App 發布檔案 → 送到需要它的 Node → 對方交易讀取 → 故障後補齊（假設）
4. 行為與規則    從情境的每一步拆出能力：發布、同步、讀取、對帳與恢復、運維（假設）
5. 例外與限制    不可靜默遺失；本地交易不被其他 Node 阻塞               （假設）
6. 驗收          milestone 的驗收方向，例如「發布後能在指定 Node 讀到」 （假設）
7. 待決          災難時容許的損失；DC 與 Node 的對應
```

由上往下問，每一層的答案決定下一層：

| 骨架 | Agent 問（附選項與建議） | 你的回答決定什麼 |
| --- | --- | --- |
| 1 目標 | 故障時要保證什麼：交易一定拿得到檔案，還是可以等待後重試？ | 系統的核心保證 |
| 2 範圍 | 第一版要不要支援檔案寫完後再修改？ | 「不做」清單 |
| 3 情境 | 端到端是這四步嗎？有沒有漏掉的角色或步驟？ | 能力要從哪些步驟拆 |
| 4 能力 | 每一步背後的能力這樣切，對嗎？ | roadmap 的分組與順序 |
| 5 限制 | 暫時故障一定要恢復；永久毀損要不要保證零損失？ | 每個 Feature 都要守的限制 |

「各 DC 自己持有副本，還是缺檔時向共用 DC 取」這類方案比較，等目標與限制確認後，在高層設計裡做。Project 層到這裡產出目標、範圍、情境、能力清單、共用限制與驗收方向，加上高層設計和 roadmap。**每個 Feature 的具體需求與 AC 這時還沒寫進 spec。**

### Feature SA：骨架到需求與 AC

排到「Finalize 協議」時，從 Project 情境裡「App 發布檔案」這一步搭這個 Feature 的骨架：

```text
1. 目標        App 寫完的檔案，什麼時候算可以交給同步              （假設）
2. 不做        掃描 ingest、跨 Node 同步（之後的 Feature）
3. 角色與流程  App：開始寫 → 寫入 → 宣告完成 → 看到結果          （假設）
4. 規則        宣告完成的方式；結果有哪幾種                        （假設）
5. 例外        宣告時 crash 或回應遺失；寫到一半放棄；太久沒動作   （假設）
6. 驗收        主流程與每個例外各一個可驗收的 Scenario
7. 待決        太久沒動作的時限
```

| 骨架 | Agent 問 | 產出 |
| --- | --- | --- |
| 4 規則 | 「宣告完成」要明確呼叫一個動作，還是 `close()` 就算？ | 需求：依回答寫下觸發方式，例如「必須明確呼叫 Finalize，`close()` 不算」 |
| 4 規則 | 宣告完成後，App 要能分辨哪些結果？ | 需求：例如成功、失敗、尚待確認三種結果 |
| 5 例外 | 宣告時 crash、回應遺失，App 重試會怎樣？ | Scenario：可查證是否已接受，重試不形成重複 |
| 5 例外 | 寫到一半放棄，或太久沒動作？ | 需求：放棄的動作，以及逾時後的清理與紀錄 |
| 6 驗收 | 這些 Scenario 夠不夠證明這個 Feature 可以用？ | AC 清單 |

Agent 把確認後的骨架寫成這個 Feature 的 proposal 與 spec（需求加上帶 ID 的 Scenario），交給你一頁摘要確認。

需求就這樣一個 Feature 接一個累積，每一條都追得到骨架的哪一格、當時的問答和你的原話。手上有現成需求文件（客戶規格、上游專案的 spec）時，它讓骨架草稿更完整：已確認的部分直接沿用，只核對是否適用這次的 Feature、追問差異。

### 開始與接續一次 SA

有三個時機會進入 SA：開新專案或匯入既有專案、選定下一個 feature、新證據推翻原本的需求。開一個 agent session，這樣說：

> 請用 project-lead skill，做〈project／某個 feature〉的 SA。Repo 在〈路徑〉，既有資料在〈位置〉。我想解決的問題是〈一兩句〉。

只要給四樣：哪一層、repo 在哪、既有資料、想解決什麼。第四樣講不清楚也沒關係，Agent 會先問。

進去之後：

1. **Agent 先研究，不先問問題**：用 research-codebase 查現況，交一份摘要，分清事實、推論和未知。
2. **每輪問你 1–3 題**：每題附為什麼現在要決定、選項、影響與建議。
3. **邊問邊寫**：每輪告訴你改了什麼、還剩哪些阻擋。
4. **提出「可進入 Design」**：附一頁摘要。
5. **你確認或退回**：確認後才進入高層設計；這不是開工批准。你同時是 Feature Builder 時，feature 的這一步併入開工確認，spec、design、plan 一起看一次。

中途離開不影響進度，答案都已寫進文件。下次說「接續〈project／feature〉的 SA」，Agent 會先讀文件，已確認的不重問。

## 專案基準要回答什麼

用於 A1–A3。

以未來的 `cross-node-file-transfer` 演練為例：

> 請用 project-lead skill 準備 cross-node-file-transfer。先核對可沿用的 gigaxfer 需求、領域、設計與 roadmap，保留來源版本；把 `docs/spec.md` 依能力拆成需求輸入（不放進 `openspec/specs/`），先給我拆法對照表。只釐清差異與阻擋問題，最後交出專案基準、milestones 與第一個 feature 的建議。

```mermaid
flowchart TD
    A["Lead<br/>給目標、既有資料與限制"]:::human
    R["Project Lead Agent<br/>Research：現況與程式依據"]:::agent
    S["Project Lead Agent<br/>SA／domain／grill"]:::agent
    C{"Lead<br/>需求足以進入 Design？"}:::gate
    D["Project Lead Agent<br/>高層設計與技術取捨"]:::agent
    M["Project Lead Agent<br/>roadmap、milestones、features"]:::agent
    F{"Lead<br/>確認專案基準與第一個 feature"}:::gate
    A -->|目標與來源| R
    R -->|研究報告：事實、推論、未知| S
    S -->|每輪 1–3 題| A
    S -->|摘要與可進入 Design 的理由| C
    C -->|仍有阻擋| S
    C -->|確認| D
    D -->|元件責任與限制| M
    M -->|baseline 與 roadmap 草案| F
    F -->|需要調整| M
    classDef human fill:#e9ebef,stroke:#7a8399,color:#2d3142
    classDef agent fill:#ffffff,stroke:#2d3142,color:#2d3142
    classDef gate fill:#fdf0ea,stroke:#eb6c36,color:#2d3142
```

Research 記錄「目前如何運作」，研究報告不是已批准的 spec。Spec 說「要達成什麼」，design 說「如何達成」。

專案基準（project baseline）要能回答以下問題：

| 內容 | 位置 |
| --- | --- |
| 為誰解決什麼問題、哪些不做 | project intent 或 `mission.md` |
| 共用領域語言 | `CONTEXT.md` |
| 還沒實作的需求原文 | 需求輸入，記錄來源版本；匯入時依能力拆開 |
| 跨 feature 的共用限制 | 實作前在 project intent 列出並指向輸入；第一個讓它成立的 feature 把它帶進 spec |
| 已經做好的行為 | `openspec/specs/<能力>/spec.md`，只由 archive 寫入，新專案開始時是空的 |
| 架構、技術棧與重要取捨 | 既有 system design、ADR 或 `tech.md` |
| Milestones、features、順序與完成條件 | roadmap |
| 如何 setup、build、test；工程規則與必要 CI | repository 指引、scripts、CI 設定 |

交接時保存採用的路徑與版本。已確認的需求可以沿用；新 example 的程式必須留下自己的驗證證據。需要先建立專案骨架（測試、CI、工程規則，常稱 Sprint 0 或 bootstrap）時，把它當作第一個 feature，和其他 feature 一樣用 ticket 編號。

完成這個階段，代表已有足以展開近期工作的基準與 roadmap，不要求提前寫完所有未來 features 的 spec。

## Roadmap 要切多細

用於 A3。

Roadmap 只有兩層：milestone 和 feature。Feature 是能單獨驗收的交付，每個受影響的 repo 一個審得動的 PR；task 寫在 feature 裡，不上 roadmap。Roadmap 會一直改，所以問題不是「切得越細越好」，而是哪些東西值得先寫：

- **Feature 清單很便宜**：只有名稱、一句範圍、依賴，以及對應需求輸入的哪幾條。當前 milestone 的切法有依據時，可以整個列出來，方便看平行和依賴。
- **Spec 等 feature 排進近期才寫**：建立這個 Feature 的 spec、做 SA。細節看穩定度，不看遠近；依賴程式現況的部分寫太早，會過時並誤導 Agent。
- **詳細設計等開工前才做**：由 Implementer 負責。

每個 feature 標「近期」或「暫定」，讓人分得出哪些已經要做。每個 feature 驗收後回頭看一次 roadmap；改範圍或順序時記進決策紀錄。

以 cross-node-file-transfer 為例：M1 的 feature 來自 gigaxfer 已經實作過的計畫，所以可以整個列出，只有專案骨架和第一個 feature 標近期；M2 要不要做等 M1 完成再決定，所以先只寫交付能力。需求放在哪、怎麼流動，見[需求放在哪](#需求放在哪)；業界做法與出處見 [Roadmap 規劃參考](../references/roadmap-planning.md)。

## 工作層級：Milestone、Feature、Task

| 層級 | 是什麼 | 怎麼追蹤 | Azure DevOps |
| --- | --- | --- | --- |
| Milestone | 一個可以展示的成果，把幾個 Feature 歸在一起 | roadmap；GitHub milestone | Feature 或 Epic |
| Feature | 一個自成一體、能單獨驗收的交付：一份 spec、每個受影響的 repo 一個 PR、一張 ticket | ticket | PBI（Story） |
| Task | 一個 session 做得完的工作，寫在 `tasks.md` | 不開 ticket | Task |

- Feature 的結果不一定要讓外部使用者看到，由系統其他部分或工程條件觀察也可以；重點是用自己的 AC 就能驗收，不必等之後的 Feature。業務上完整的能力由 Milestone 驗收。
- Feature 在每個受影響的 repo 各一個 PR，每個 PR 都要審得動。某部分能單獨驗收，或 PR 太大，就拆成另一個 Feature。
- 一個 task 一到幾個 commit，每個 commit 自己綠燈；PR、merge、併入現況都以 Feature 為單位。
- PR 不限行數，但要審得動：每個 task 做完審一次，最後 G2 再看整個 PR。

## 多個 repo 的專案

用於整個流程。結構見使用指南的[專案的 repo 結構](user-guide.md#專案的-repo-結構)。

**清單** `repos.yaml` 放在 root，每個服務 repo 一筆：

```yaml
repos:
  - name: order-service
    url: git@github.com:acme/order-service.git
    branch: main
    path: repos/order-service
    purpose: 訂單 API
```

**同步指令**由專案提供（例如 `scripts/sync-repos`）：缺的 repo 就 clone，乾淨的就更新，有未提交修改的不動並回報。`repos/` 不進 root 的版控，也不用 git submodule。

**一個 Feature 跨 repo 時**

- spec、design、tasks 都在 root 的 `openspec/changes/<id>/`；每個 task 註明改哪個 repo。
- 每個受影響的 repo 開一個 PR（root 也算一個），都連到同一張 ticket並互相連結。
- G1、G3 在各 repo 執行；G2 對照 spec 審整組 PR；人驗收整個 Feature。
- merge 依依賴順序、提供方先；每個 PR 單獨 merge 都要安全（向後相容）。全部 merge 後才在 root 把 spec 併入現況。
- 交接包與 PR Pass 驗收包列出每個受影響 repo 的 base branch、commit 與 PR；版本以這些 commit 為準。
- 其中能單獨驗收的部分，拆成另一個 Feature。

## 需求放在哪

用於 B1–B8。**需求放在哪，看它做到哪了。**

```text
還沒開始做            決定做、正在做               做完了
OpenSpec 之外     →   openspec/changes/<名稱>/  →  openspec/specs/
（輸入、roadmap）      寫 spec、design、實作        archive 時搬進來
```

### 跟著一條需求走

以 cross-node-file-transfer 的需求 FR-02「Source Ready & Acceptance Boundary」（來源檔案什麼時候才算 Ready）為例：

1. **一開始**：它在需求輸入裡。roadmap 上只有一行：M1 的 Feature「Finalize 協議」，也就是示範專案 GitHub 上的 ticket #2。
2. **排到要做**：建立這個 Feature 的 spec，位置例如 `openspec/changes/finalize-protocol/`。Project Lead Agent 把 FR-02 中這次要做的部分寫成 spec（內容寫完並持久化才回報 Ready），人確認。Crash 後重新發現檔案的部分屬於之後的「掃描 ingest」，到時用 MODIFIED 補上。
3. **實作**：工程師帶 Implementer 寫 design 和 tasks，一個 task 一個 task 做，最後開 PR。
4. **做完**：人驗收、merge 之後 archive，FR-02 這次做完的部分搬進 `openspec/specs/file-readiness/spec.md`，從此代表「系統已經做得到」。重新發現的部分，等掃描 ingest 做完再用 MODIFIED 補進去。

所以 Agent 讀到 `openspec/specs/`，就知道系統現在做得到什麼；讀到 `openspec/changes/`，就知道接下來要做什麼。

### OpenSpec 的資料夾

```text
openspec/
├── specs/                   ← 系統現在做得到的事（做完的需求，只由 archive 寫入）
└── changes/
    ├── finalize-protocol/   ← 一個 Feature 的資料夾，進行中
    │   ├── proposal.md      ←   為什麼做、做什麼、不做什麼
    │   ├── specs/           ←   這次受影響的需求：新增、修改（寫完整新版）或移除
    │   ├── design.md        ←   怎麼做
    │   └── tasks.md         ←   分幾步做
    └── archive/             ← 做完的 Feature 資料夾；差異已經併回最上面的 specs/
```

OpenSpec 把 `changes/` 底下每個 Feature 的資料夾叫 change，和上線部署的變更無關。不改名，因為資料夾名稱是 OpenSpec 寫死的，改了工具就找不到。

### 常見問題

- **SA 會一次寫出全部需求嗎？** 不會。Project SA 問出目標、範圍、端到端情境、能力清單、關鍵規則、共用限制與 Milestone 的驗收方向，再排出 roadmap，但還不寫各 Feature 的具體需求與 AC；每個 Feature 的需求與 AC，在它排進近期、做 Feature SA 時才經研究與逐輪問答（每輪 1–3 題）寫出來。每一步問什麼、產出什麼，見[需求是怎麼問出來的](#需求是怎麼問出來的)。有現成需求文件時，它只是參考輸入，不會直接變成 spec。
- **roadmap 上還沒開始的 Feature 在哪？** 不在 OpenSpec 裡。roadmap 上一行：名稱、目標、所屬 Milestone、依賴，以及對應輸入裡的哪幾條需求。
- **為什麼不把整份需求先放進 `openspec/specs/`？** OpenSpec 定義它是現況："Specs ... describe how your system currently behaves"（[concepts](https://github.com/Fission-AI/OpenSpec/blob/main/docs/concepts.md)）。放進還沒做的需求，Agent 會以為它已經存在。
- **跨 Feature 的共用限制呢？**（容量、安全、資料不遺失）還沒實作前，project intent 列出它們並指向輸入。第一個讓它成立的 Feature 把它帶進自己的 spec；Feature SA 每次都要檢查這次碰到的行為有沒有相關限制。
- **spec 要先寫多細？** 看穩不穩定，不看遠近。穩定的需求可以先在輸入裡寫細；依賴程式現況的部分（這次的 spec 細節、design、tasks）到要做時才寫，過時的規格會誤導 Agent。
- **修 bug 也要建立 Feature 的 spec 嗎？** 不用。讓行為回到既有 spec 的修正、更新依賴、補測試，都不改需求，ticket 本身就是規格：內容自足、附 AC、範圍小。Bug 暴露出 spec 沒寫到的情況時，才建立 Feature 的 spec 補上。

### 每一步誰做、ticket 在什麼狀態

| 步驟 | 誰 | 產出 | Ticket |
| --- | --- | --- | --- |
| 1. 排進 roadmap | Project Lead Agent 提出，Lead 確認 | roadmap 上一行 | 通常還沒開；想早點讓人看到可以先開，只寫目標 |
| 2. 選中 | Lead | 建立 Feature 的 spec（`openspec new change <id>`） | 開 ticket，或把已有的 ticket 連上 spec |
| 3. Feature SA | Project Lead Agent 研究與提問，Lead 回答 | `proposal.md`、spec；`openspec validate` 通過 | 同一人兼任：就緒；不同人：待 SA 確認 |
| 4. SA 確認 | Lead | 確認紀錄、交接包 | 就緒 |
| 5. Design＋plan | Implementer | `design.md`、`tasks.md`、AC 的驗法 | |
| 6. 開工確認 | Feature Builder | 確認紀錄 | 開發中 |
| 7. 逐 task 實作 | Implementer；Reviewer 做局部 review | 每個 task 一到幾個綠燈 commit | |
| 8. PR | Implementer、Reviewer、CI | 三個 gates、PR Pass 驗收包 | 連上 PR |
| 9. 驗收、merge | 人類驗收人 | 接受紀錄；由人 merge | |
| 10. 收尾 | Project Lead Agent | `openspec archive`；更新 roadmap；Retro 候選 | 由人關閉，或 PR merge 時關閉；Agent 只在獲授權時更新狀態 |

兩個角色由同一人擔任時，第 4 步併入第 6 步：spec、design、plan 一起看一次，確認後開工。不同人擔任時分開，spec 被推翻時工程師不會白做。

## Spec 怎麼寫、放哪

用於 B2。

SA 要回答七個問題，它們是檢核表，不是七個章節：問題與目標、範圍與非範圍、角色與端到端情境、行為與業務規則、例外與必要限制、驗收條件、假設依賴與待決。Agent 把它們放進四個位置：

| 位置 | 裝什麼 |
| --- | --- |
| `proposal.md` 的 Why | 問題與目標 |
| `proposal.md` 的 What Changes 與「不做」 | 範圍與非範圍 |
| `specs/<能力>/spec.md` 的 Requirement 與 Scenario | 情境、行為與規則、例外與限制、驗收條件；每個 Scenario 就是一條帶 ID 的 AC |
| `proposal.md` 的待決與依賴 | 假設、依賴與待決 |

你確認時看到的是這樣的摘要：

```text
目標：……                          → proposal.md#why
不做：……                          → proposal.md
規則：ING-01 ……、ING-02 ……        → specs/file-ingest/spec.md
例外：AC-I03 重複寫入、AC-I04 逾時
待決：Q1 容量上限（阻擋 Design，等你決定）
版本：<commit 或檔案 hash>
```

需求 ID 每個能力一個前綴，用過不重用，archive 後也不變，讓 review 與證據能一直追溯。格式由 `openspec validate` 檢查；內容對不對由你和 Reviewer 判斷。

## 交接

用於 B3、B6、B7。兩層之間只交兩樣東西，Agent 依規則組好，你讀的是它們的重點：

| 介面 | 方向 | 你要確認什麼 |
| --- | --- | --- |
| **交接包** | Project Lead → 工程師（feature loop） | spec 的版本寫明，並附上 SA 確認紀錄；兼任工程師時，改附「併入開工確認」的註記；每個受影響 repo 的起點寫清楚；依賴的上游已接受並 merge；待決事項各有決策者；寫明誰批准開工、誰驗收。它不含開工確認：design＋plan 在 loop 裡產出後才由人確認 |
| **PR Pass 驗收包** | feature loop → 驗收人，副本給 Project Lead | 每條 AC 都有結果與證據；證據對應的是目前的版本；風險與已知限制寫明；PR、CI、review 都連得到 |

兩者的完整欄位定義在[交接契約](../workflow/contracts.md#角色交接摘要)，由 Agent 照著組。

feature loop 無法安全繼續時，改交 **Blocked**：run ID、問題、已嘗試事項、證據、可選方案與需要誰決定。

**PR Pass 不是接受，接受也不是 merge**，三者分開記錄。有依賴的 Feature 要等上游被接受並 merge 後才開始實作；以未合併 PR 為 base 的 stacked PR 還沒決定是否允許。

### 控制方向與自主程度

Project 層是人和 Agent 一來一回的對話，不需要派工或 gates；Feature 層有多個 Agent 並行，需要 controller 核對證據。所以兩層分成兩個 skill，控制只往下走：Project Lead 把交接包交給 orchestrate，orchestrate 從不呼叫 Project Lead。同一套 skill 有兩種自主程度：

| 模式 | 誰啟動每個 Feature | 適合 |
| --- | --- | --- |
| 手動 | 人拿 Project Lead 準備好的交接包，自己啟動 orchestrate | 第一版、個人使用 |
| 授權 | Project Lead 在人核准的範圍內啟動；各 Feature 的 SA 確認須先完成，或註明併入開工確認。loop 產出 design＋plan 後停下，等人確認開工，Project Lead 不能代批 | goal 模式、多 Feature 的 demo |


### 把 Feature 交出去

> 請用 project-lead skill 準備〈feature〉：補足 spec、AC、必要高層設計與依賴，引用專案基準的實際版本。交接給〈Feature Builder〉，列出已確認事項與阻擋問題。

```mermaid
flowchart TD
    A["Lead<br/>選 feature 與交付負責人"]:::human
    B["Project Lead Agent<br/>聚焦 SA：proposal、spec delta、依賴"]:::agent
    C{"Lead<br/>確認交付範圍與成功條件"}:::gate
    D["Project Lead Agent<br/>交接包與 ticket"]:::agent
    E["Feature Builder＋Implementer<br/>核對交接包"]:::human
    F["Feature loop<br/>見「做出來：工程師的細節」"]:::mech
    A -->|feature 與 baseline 版本| B
    B -->|不同人擔任：摘要與 AC| C
    C -->|確認| D
    B -.->|同一人兼任：不另確認，<br/>併入之後的開工確認| D
    D -->|spec 位置與版本、SA 確認或併入註記、base| E
    E -->|需求衝突或阻擋問題| C
    E -->|足以設計| F
    classDef human fill:#e9ebef,stroke:#7a8399,color:#2d3142
    classDef agent fill:#ffffff,stroke:#2d3142,color:#2d3142
    classDef gate fill:#fdf0ea,stroke:#eb6c36,color:#2d3142
    classDef mech fill:#f5f5f5,stroke:#4f5d75,stroke-dasharray:4 3,color:#2d3142
```

交接包的內容見上表。Ticket 連到 spec，不重貼內容。Project Lead 可以附 tasks 草案，但最終 plan 由 Implementer 校準。

**交接完成**是 Feature Builder 知道要交付什麼、能開始詳細設計；不等於已開工。啟動 feature loop 有兩種方式：

- **手動**：你把交接包交給 Feature Builder，由他啟動。
- **授權**：你明確授權 Project Lead 負責某個範圍，且該 feature 的 SA 已確認（或註明併入開工確認），Project Lead 就能自己啟動。loop 產出 design＋plan 後會停下等開工確認，Project Lead 不能代你批准。

### 跨人、跨 session 要交什麼

換人或重開 session 時，交文件位置與適用版本，再讀保存的結果。聊天可補背景，但不承擔唯一的進度與需求記憶。Implementer 與 Reviewer 不直接互傳結果，都經由保存的檔案與 orchestrate 交接；先保存結果，再發布或通知，通知只是喚醒接收者。各角色之間的交接內容見[交接契約](../workflow/contracts.md#角色交接摘要)。

## 做出來：工程師的細節

用於 B4–B6。

### 你會收到什麼

Project Lead 交給你一個交接包，內容見[交接](#交接)。缺東西或有衝突時，先回報 Project Lead 和 Lead，不要自己補需求。

feature loop 從收到交接包就開始，第一步是 design＋plan，然後停下等開工確認。交接包本身不含開工確認。

你只改這個 Feature 的 `design.md` 與 `tasks.md`，驗法寫進 validation 文件。`proposal.md` 與 `specs/` 屬於 Project Lead；需要改需求或 AC 時回去找 Project Lead 和 Lead，不在程式裡繞過。

### 完成一個 Feature，包括 PR

先看主線：人只在開工確認與驗收兩處介入，中間由 agents 跑 review-fix loop。

```mermaid
flowchart TD
    A["Feature Builder<br/>交代 Feature、目標與限制"]:::human
    B["Implementer Agent<br/>研究、詳細設計、tasks、AC 驗法"]:::agent
    C{"被授權的人<br/>一次確認 design＋plan"}:::gate
    D["Implementer Agent<br/>依序 TDD，取得 G1"]:::agent
    L["Review-fix loop<br/>見下一張圖"]:::mech
    H{"人類 Reviewer／驗收人<br/>review PR、驗證 AC 與 demo"}:::gate
    Z["記錄接受的版本<br/>Project Lead 收尾"]:::human
    Q["Project Lead 與 Lead<br/>需求、爭議、超限或未知"]:::human
    A -->|交接包| B
    B -->|design＋plan＋驗法| C
    C -->|需修改| B
    C -->|批准開工| D
    D -->|G1 通過才 push 與送審| L
    L -->|PR Pass 驗收包| H
    L -->|無法安全繼續| Q
    H -->|既有 AC 未滿足| L
    H -->|需求或 AC 改變| Q
    H -->|接受；merge 另由人決定| Z
    classDef human fill:#e9ebef,stroke:#7a8399,color:#2d3142
    classDef agent fill:#ffffff,stroke:#2d3142,color:#2d3142
    classDef gate fill:#fdf0ea,stroke:#eb6c36,color:#2d3142
    classDef mech fill:#f5f5f5,stroke:#4f5d75,stroke-dasharray:4 3,color:#2d3142
```

再看 review-fix loop：G2 與 G3 對同一組版本並行，收齊後才判定。多 repo 的 Feature 每個 repo 各有一個 PR：G3 逐 repo 跑在各 PR 目前的 head；G2 對整組 PR 的目前版本審一次；任一 PR 有新 push，整組的 G2 與 PR Pass 都要重評。

```mermaid
flowchart TD
    P["各 PR 目前的 head<br/>Implementer push"]:::agent
    R["Reviewer Agent<br/>G2：獨立 session，不改 branch"]:::agent
    T["CI<br/>G3：必要 checks"]:::agent
    J{"Orchestrate＋controller<br/>同一組版本結果收齊，三 gates 通過？"}:::mech
    X["Implementer Agent<br/>修正批次，重過 G1"]:::agent
    O["PR Pass<br/>交人驗收，不是 merge"]:::gate
    B["Blocked<br/>保存原因，交人裁決"]:::human
    P -->|review 任務| R
    P -->|觸發 checks| T
    R -->|verdict 與 findings| J
    T -->|check 結果| J
    J -->|可修正，最多 3 輪| X
    X -->|新 head| P
    J -->|全部通過| O
    J -->|爭議、到限或未知| B
    classDef human fill:#e9ebef,stroke:#7a8399,color:#2d3142
    classDef agent fill:#ffffff,stroke:#2d3142,color:#2d3142
    classDef gate fill:#fdf0ea,stroke:#eb6c36,color:#2d3142
    classDef mech fill:#f5f5f5,stroke:#4f5d75,stroke-dasharray:4 3,color:#2d3142
```

G1 缺原始證據、必要結果無法取得或出現未知執行狀態時，先保存原因並交人處理，不為了走到 PR Pass 補造證據。Implementer 對 finding 有異議時，反證先交獨立 Reviewer 覆核一次，仍有 blocking 爭議才交人。

你負責確認技術交付安排、查看進度、處理自己有權決定的問題；Agent 負責實際工作。若你被授權批准 design＋plan，由你完成開工確認，否則交指定決策者。正常已授權工作不需要每個 task 都回來簽核。

Task 是 PR 內的工作單位，一個 session 做得完，不開 ticket。一個可獨立驗收的 Feature，在每個受影響的 repo 各對應一個 PR；做 design 時發現某部分能單獨驗收，或某個 repo 的 PR 大到審不動，就提議拆成另一個 Feature，由 Project Lead 與 Lead 確認。每個 task 一到幾個綠燈 commit，完成後由獨立 Reviewer 做一次局部 review，最後 G2 再看整個 PR。

### 計畫要讓 AC 真正能驗證

每個 AC 都要有「怎麼驗、在哪裡驗、何謂通過、證據放哪」。以下只是寫法示例，並非已核准的 cross-node 功能需求：

| AC 示例 | 驗證方法／環境 | 通過標準 | 保存的證據 |
| --- | --- | --- | --- |
| 成功傳送後，目的檔案內容與來源一致 | 對採用的兩節點測試環境執行傳送，再獨立比對檔案 | 傳送成功且內容完全相符 | 測試輸出、環境資訊、適用程式版本 |
| 傳送失敗時，呼叫端不會收到成功結果 | 在受控環境製造傳送失敗，檢查公開回傳行為 | 明確回報失敗，不誤報成功 | 行為測試結果及原始 Red→Green 紀錄 |

### PR Pass 到底代表什麼

| Gate | 足以通過的證據 |
| --- | --- |
| G1：實作／TDD | 與本次行為及 task 可追溯的 Red→Green 過程，最終相關與回歸驗證適用目前整合後的 head |
| G2：獨立 Review | Reviewer 已對照 spec、design、完整 PR diff 與必要 context；未解 blocking findings 為零 |
| G3：CI | 設定要求的 checks 全部取得可接受的成功結果，且適用目前版本 |

G1 先於送審；G2 與 G3 彼此獨立，可以並行。Red 通常來自較早版本，不要求與最後 Green 同 SHA。CI 綠燈不能補上缺失的 TDD 證據，agent 的「完成」也不能當作 gate 結果。純文件或註解的 TDD N/A 須有理由與檢查，並由獨立 Reviewer 確認。

新 push、review base 或適用 spec／design 改變時，重新評估證據；過期結果不能放行。缺 check、pending、取消或未知都不算成功。

**PR Pass 表示可交給人驗收。** 不代表已被接受、已合併或已部署。人發現原需求未滿足，回修正；若是新增需求或改變 AC，先回 Project Lead 更新並確認需求，不能為了讓程式過關而反改 spec。

### 讓單一 Feature 持續跑

一個可執行的 goal 包含：交付範圍、何謂完成、允許的動作、執行限制，以及需要你回來的情況。

> 請推進〈Feature〉，以已確認的 design／plan 為準。可依計畫實作、更新 PR、執行獨立 review／CI 及修正循環。直到目前版本的三 gates 通過，整理驗收包後停下。保留 worktree，不自動 merge、close issue 或 deploy。需求／AC 或設計需改變時回來裁決；最多三輪修正、四小時主動執行時間。

Orchestrate 按授權工作，controller 核對狀態與證據。每個基礎設施操作最多額外重試兩次，和三輪程式修正分開計算；未知的執行結果先保存並停止，不反覆重派。

查進度時，你應看得到：目前 feature／PR 與版本、哪個角色正在工作、各 gate 的證據或缺口、下一步，以及是否有需要人的問題。

轉為 **Blocked** 時，agent 應交出問題、已嘗試事項、證據、可選方案與需要你決定的事。你補上決策後，再從保存的狀態核對並接續；不能只憑一句「proceed」忽略尚未解決的正確性問題。

### 你交回什麼

| 結果 | 交給誰 |
| --- | --- |
| PR Pass 驗收包（內容見[交接](#交接)） | 人類驗收人，副本給 Project Lead |
| Blocked：需求或 scope | Project Lead 與 Lead |
| Blocked：環境、權限、爭議或到限 | 有權裁決的人 |

驗收後的 Retro 與下一個 feature，以及 merge 後的 archive，都由 Project Lead 處理。依賴與 stacked PR 的規則見[交接](#交接)。

## 驗收之後：收尾

用於 B7、B8。

feature loop 回來的結果只有兩種：

- **PR Pass 驗收包**：交給你或指定的驗收人，內容見[交接](#交接)。
- **Blocked**：如果原因是需求或 scope，你和 Project Lead 分析影響、更新 spec 並記錄決策，再把新版本交回去。

你接受之後，Project Lead 會：

1. **整理 Retro 候選**：只挑 1–3 個有證據的改善，寫明來源、原因、改善、owner 與驗法。沒有證據就不寫。
2. **提出下一個 feature**：更新 roadmap、檢查依賴，讓你選。

確認 PR 已 merge 之後，再：

3. **把 spec 併入現況**（`openspec archive`）：把這個 Feature 的需求差異併回 `openspec/specs/`，從此代表「系統已經做得到」。

有依賴的 feature 等上游接受並 merge 後才開始實作；等待期間可以先準備它的 spec。Milestone 還需要自己的跨 feature 整合驗證，不能把一串 PR 綠燈直接加總成完成。

## 給一個 goal，推進多個 Feature

**Stacked PR 是還沒決定、也還沒實作的目標情境，現在不能這樣執行。** 現在能做的是：goal 拆成多個 feature，一個接一個推進。

先對照現行規則與目標：

![Stacked PR 對照：左為現行規則，下游等上游人工接受並 merge 後才開始實作；右為還沒決定的目標，PR C 以 PR B、PR B 以 PR A 為 base](stack.svg)

未來可以這樣說：

> 請用 project-lead skill 把〈已確認的 goal〉拆成可驗收的 features，提出 spec、依賴與 PR stack，讓我確認。在我授權的範圍內依序啟動 feature loop，每個 PR 都完成自己的 gates。達到 goal 後交出整組 PR、依賴順序、驗收證據與已知限制，保留 worktrees。

```mermaid
flowchart TD
    A["Lead<br/>給 goal、完成條件與執行限制"]:::human
    subgraph T["目標情境：還沒決定也還沒實作，現在不可用"]
        B["Project Lead Agent<br/>拆 features、spec 與 PR 依賴"]:::agent
        B2["Implementer Agent<br/>各 feature 的 design、plan 與驗法"]:::agent
        C{"Lead／被授權的人<br/>確認 scope、stack 政策與各 feature 開工"}:::gate
        D["PR A：base 為 main<br/>自己的 spec、TDD、review、CI"]:::agent
        E["PR B：base 為 PR A<br/>自己的 spec、TDD、review、CI"]:::agent
        F["PR C：base 為 PR B<br/>自己的 spec、TDD、review、CI"]:::agent
        G["Project Lead 彙整<br/>各 PR 最新 gates＋goal 驗證＋依賴順序"]:::agent
    end
    H{"人類 Reviewer／驗收人<br/>按依賴 review 與驗收"}:::gate
    I["回受影響 PR 的 feature loop<br/>重評下游結果"]:::mech
    A -->|goal| B
    B -->|feature spec 與依賴| B2
    B2 -->|stack 與各 feature plan| C
    C -->|核准各 feature 開工| D
    E -->|base 是 PR A| D
    F -->|base 是 PR B| E
    D -->|各自的 gates| G
    E -->|各自的 gates| G
    F -->|各自的 gates| G
    G -->|整組 PR 與驗收證據| H
    H -->|指出受影響 PR| I
    I -->|更新後的 gates| G
    classDef human fill:#e9ebef,stroke:#7a8399,color:#2d3142
    classDef agent fill:#ffffff,stroke:#2d3142,color:#2d3142
    classDef gate fill:#fdf0ea,stroke:#eb6c36,color:#2d3142
    classDef mech fill:#f5f5f5,stroke:#4f5d75,stroke-dasharray:4 3,color:#2d3142
    style T fill:#fafafa,stroke:#9aa1b1,stroke-dasharray:6 4
```

圖中的 A／B／C 只是 stack 結構示例，不是已選定的 cross-node features。每個 PR 對應一個有界、可驗收的 feature；goal 不取代各 feature 的 spec、開工確認與 gates，也不能只用最後一個 PR 通過就宣告整組完成。

**交給人 review 的內容**：goal 與達成情況、PR 依賴圖及閱讀順序、每個 PR 適用版本的 gates 與 AC 證據、整組成果的驗證方式、剩餘問題。

**與目前規則的邊界**：現行規則要求相依 feature 等上游人工接受、實際 merge、採用 baseline 後才開始實作。未來啟用 stack 前，要先確認每個 PR 的依賴與 review base、上游變動後哪些證據失效，以及人工驗收與合併順序。B 相對 A 通過，不代表 B 可以直接合併 main。這件事還沒決定。

## 查進度

你問進度時，Project Lead 應列出 roadmap 上每個 feature 的狀態：準備中、SA 已確認、feature loop 進行中（附 run ID）、PR Pass、已接受、已 merge 並 archive，或 Blocked 與原因。狀態來自文件、ticket、PR 與 controller 的唯讀狀態，不靠對話記憶。這個專案進度視圖的自動化列在 S2。

## 會用哪些 skills 與工具

| 用途 | 目前方向與界線 |
| --- | --- |
| Project 層與 Feature 準備 | [project-lead](../../skills/project-lead/SKILL.md) skill（草稿） |
| Codebase 研究 | [research-codebase](../../skills/research-codebase/SKILL.md)，改寫自 HumanLayer 的 research_codebase；記錄現況，不批准需求或決定設計 |
| SA、領域語言與 grill | Matt 的 grill-with-docs、grilling、domain-modeling，由 project-lead 按需叫用 |
| 規格 | OpenSpec；Writing Plans 與 tasks 的接合仍在驗證 |
| 單一 Feature 的 loop | `orchestrate` skill 呼叫薄 controller，第一片實作中 |
| TDD | Superpowers TDD；每個行為 task 保存可追溯證據 |
| 審查與修正 | 獨立 Reviewer，依 spec 與工程規則審查；Implementer 修正 |
| Example 執行環境 | Herdr 管 sessions 與工作區；本機 OpenAI 經 OpenCode，Claude 直接用 Claude Code；Orca 是選配入口 |
| 程式與協作紀錄 | Git branches／worktrees、GitHub issues／PRs／CI，以及可讀的執行結果與狀態 |

loop-engineering 自己開發 controller 時，預設 Opus 5.5 實作、GPT 審查；Reviewer 必須使用不同的實際模型與獨立 session。其他專案的 profile 仍需明確設定及驗證。

## 想知道為什麼

這份參考和[使用指南](user-guide.md)一樣只說怎麼做。規則本身、設計理由與取捨在內部設計文件：[決策紀錄](../decisions.md)、[交接契約](../workflow/contracts.md)、[流程設計](../workflow/overview.md)、[SA 階段契約](../workflow/project-lead-sa.md)；手冊和它們有出入時，以設計文件為準。各主題對應哪條決策，見使用指南的[對照表](user-guide.md#想知道為什麼)。
