# 比較方法與限制

本次比較為同一 feature 的兩份規格草稿：Orca Delivery Loop MVP。兩個獨立 sub-agent 收到相同來源快照與相同補充決策，使用父 agent 相同的預設 model/reasoning；沒有指定不同模型，也沒有測量成本或效能。作者不讀另一份草稿。主 agent 先固定 18 項行為檢核，再閱讀產物。

- OpenSpec：使用本機 CLI 1.13.1 的 spec-driven schema，只生成 proposal＋specs。design/tasks 屬下一階段，沒有用「尚未生成 plan」扣分。
- Matt：使用本機 to-spec 的七段模板生成 spec。沒有另跑 grilling／to-tickets／implement，沒有發布 GitHub 或標 ready-for-agent。
- Testing seams：公開操作作為主要測試邊界是待確認提案。兩版都只是比較草稿；不能把候選 testing seam 當已確認設計。原版 to-spec 的確認後發布流程尚未完成。
- D31：使用者先前同意 OpenSpec／Writing Plans／Superpowers TDD／唯一 controller 的組合；此次比較不自行撤回決策，也不把 Matt 版升格為另一份權威規格。
- 未進行 coding／tests／真實 agent-GitHub E2E；OpenSpec validate 若通過只表示結構檢查通過。
- 同一輸入下產物也受 prompt、模型與當次生成影響；以下結論只描述這兩份實際稿，不代表任一工具普遍更優。

來源資料原始 bytes 保存在 source-snapshot.tar.gz，input-manifest.json 提供逐檔 SHA256；shared-input.md 保存共同工作 brief，method.json 保存技能雜湊與環境方法資料。完整內容供溯源，可先閱讀比較結論與兩份規格。

## 觀察到的環境限制

兩個 agents 是獨立對話上下文，但仍繼承 runtime 的 repo 指示。Matt 作者確認其上下文含 gigaxfer AGENTS，並有規則混入 Orca 的已確認 Testing Decisions；來源與處置保留於其 author-notes 和比較 R02。因此只能稱「相同明示產品輸入」，不能稱無其他上下文的嚴格受控實驗。此發現應改善目標 repo／規則適用性的交接，不直接歸因於某個 skill。
