# Stacked PR：目標情境（尚未決定）

這是設計文件，不是操作說明：記錄「給一個 goal，用 stacked PR 推進多個 Feature」的目標情境。它還沒決定、也還沒實作（決策紀錄 Q-STACK；現行規則是 D27：有依賴的 Feature 等上游接受並 merge 後才開始實作）。使用者現在的做法見[參考](../guide/reference.md#給一個-goal推進多個-feature)。圖的原稿是 [stacked-pr.html](stacked-pr.html)，SVG 由它匯出。

**Stacked PR 是還沒決定、也還沒實作的目標情境，現在不能這樣執行。** 現在能做的是：goal 拆成多個 feature，一個接一個推進。

先對照現行規則與目標：

![Stacked PR 對照：左為現行規則，下游等上游人工接受並 merge 後才開始實作；右為還沒決定的目標，PR C 以 PR B、PR B 以 PR A 為 base](stacked-pr.svg)

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
