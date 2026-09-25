# Orca Delivery

以 Orca 為入口，協調 Claude Code 實作與独立 Codex review，將選定的 feature issue 推進到具備證據的 PR Pass。

目前階段：Research / Grill。已建立獨立 repo 與 OpenSpec，尚未實作控制器，尚無真實端到端交付證據。

## 文件

- [需求意圖與已確認邊界](docs/project-intent.md)
- [決策狀態](docs/decisions.md)
- [領域詞彙](CONTEXT.md)
- [環境查核與 baseline evidence](docs/research/2026-09-25/research.md)
- [Orca 控制介面](docs/research/2026-09-25/orca-capabilities.md)
- [Skills 契約與版本查核](docs/research/2026-09-25/skills.md)
- [Feature 交接欄位草案](docs/research/2026-09-25/feature-handoff-contract.md)

## 工作層級

Project spec 定義共用契約；feature ticket 的內文或引用文件承擔 feature spec。每個可獨立驗收的 feature 對應一個 PR，implementation tasks 是該 PR 的派工單位。Review 同時對照適用的 project / feature specs。

PR Pass 必須同時滿足：G1 實作與 TDD 證據、G2 獨立 review 無未解決阻擋項、G3 必要 CI 檢查成功。結論綁定目前 PR head、review base 與適用規格版本。

MVP 的執行方式已確認為 Orca workers + 單一本機持久化控制器，從專用 Orca terminal 啟動。停止於 Ready for human acceptance；merge、close issue、release、deploy 不在預設範圍。
