# Fixing the PR Bottleneck：使用者提供的演講摘要

收錄日期：2026-09-26。使用者將本摘要歸於 Matt Pocock 的《Fixing the PR Bottleneck》。未提供原始影片 URL、完整逐字稿或版本；本文整理所貼內容，未獨立觀看或核實講者原話。這是參考材料，不是對其每項做法的採納或執行授權。

## 問題與三層品質控制

來源認為 agent 加速產生程式碼後，PR 審查能力成為瓶頸；產出速度必須配合品質控制，否則人與 codebase 都承受更多返工。

| 層次 | 來源主張 |
| --- | --- |
| Automated checks | 先以 lint、type checks、tests 做低成本檢查；綠燈可能掩蓋只重述實作、對結構過敏或過度 mock 的無效測試 |
| Automated review agent | 將實作與 review context 分開；累積團隊自己的 coding-standards.md，降低無關誤報；建議 reviewer 直接 commit fixes |
| Human review | 區分易復原的 two-way door 與難以復原的 one-way door，依後果調整 review 深度；以小圖、Mermaid 或行為摘要協助理解 |

Deep Modules 是來源建議的測試設計方向：以簡單介面包住複雜實作，測試可觀察行為，降低對內部結構的耦合。來源的「只消耗 CPU、不消耗 Token」應限於確定性檢查本身；產生、維護、診斷檢查仍可能使用 agents 與人力。

## Retro 的回饋方向

來源希望人類審查同時改善產生程式碼的系統，讓重複意見逐步轉成自動檢查、review 規範或更好的代理環境。Retro 輸入包括 session 與 PR 紀錄，改善方向包括 AGENTS.md 導航、steering/skill 精簡，以及工具的 token 成本。

「不再寫第二次相同評語」是改善目標，不保證一條新規範能永久消除問題。是否有效仍需觀察真實再犯、漏檢、誤報與 review 成本。

## 與我們流程的對照

| 觀點 | 已有或建議的處理 |
| --- | --- |
| 三層品質控制 | 檢查／agent／人是責任層次；G1／G2／G3 是 PR Pass 的獨立證據條件，不能一對一替換 |
| 檢查綠燈可能誤導 | G1 要追溯行為與 Red/Green；G2 抽查 AC 和測試有效性；G3 核對真正必要 CI，三者互補 |
| Deep Modules | 沿用介面行為與可測試設計；仍需辨識實際 failure modes，不能把設計形式當成測試品質保證 |
| 獨立 review context | 沿用 Reviewer Agent；它需讀 spec/design/AC、完整 PR diff 及必要 codebase context，不假定只看 diff 就夠 |
| 規範只給 reviewer | 調整為 Implementer 可取得實作必要規範，細緻 review rubric 按需載入；保留現有 repo 檔名 |
| Reviewer 自行 commit | 不採為 G2 行為；Implementer 修正、Reviewer 獨立覆核，避免審查與修正混在同一角色 |
| Two-way / one-way door | 新增人工 review 深度的設計候選；低風險也維持必要 gates，高風險在 design / plan 就釐清 |
| 視覺摘要 | 建議加入既有 PR Pass package，只在有助理解時畫圖，不為每個簡單修改新增文件 |
| Retro 自動寫新規範 | 本機 Matt retro 實際先呈現候選，且為明確呼叫型；修改與驗證需按我們的 scope / policy 處理 |

本機 retro 的來源、hash、呼叫限制與具體輸出見 [雙層 Retro 查核](dual-loop-retro.md)。我們的接入候選見 [品質層次與人工審查](../workflow/history/orchestrate-workflow-draft.md#品質層次與人工審查補充提案)，已確認政策仍以 [decisions.md](../decisions.md) 為準。
