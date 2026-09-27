# 2026-09-26 變更請求套用回報

範圍：僅 orca-delivery 文件。來源為使用者交付的 274 行 `change-request-2026-09-26.md`；已先完整讀取並以引文核對。未修改 gigaxfer，未操作原 Looper 或 GitHub，未啟動 PR gating 或 P03 Retro；未安裝 runtime、未開始 controller／skill 開發。

後續更新（2026-09-26）：使用者重新討論角色層級後明確回覆「同意」，D23 已採三角色同層協作、使用者可直接與任一角色合作、明確授權才由 Project Lead 代理安排。原始 1A 的固定指揮鏈提案未採用。其後使用者回覆「1-5 ok；6 先不管他」，已將五項推薦政策記為 D24–D28、CIT 暫緩記為 D29；下表保留原始修改範圍，決策處理列已更新為目前狀態。使用者另撤回「改用 model」的誤輸入；未採用 model-only G2 決策。後續「不綁定底層」記為 D30 的核心／adapter 解耦原則，具體 runtime/model 政策仍待選定。

2026-09-27 角色修訂：本回報以下保留 2026-09-26 的套用歷史。當時「同層協作」的概括措辭已由 [D23](../../decisions.md) 修訂為專案協調／功能交付的責任交接、依授權劃分決策權，以及 runtime 不綁固定父子關係；現行定義見 [角色與控制權](../../workflow-design.md#2-角色與控制權)。

## 修改檔案

| 檔案 | 本輪修改 |
| --- | --- |
| [workflow-design.md](../../workflow-design.md) | Controller 派獨立 G2 session、檔案交接步驟、逐 finding 回應；補 Adopt、G1 缺證據、版本失效、各階段 Blocked、人工退回預算與來源；統一狀態名及 feature 選定者 |
| [workflow-contracts.md](../../workflow-contracts.md) | Result producer／原生 messages 捕捉、完整修正回應、blocked verdict、失效後 phase、人工驗收 findings 與輪次、依 D17 明示單一入口 |
| [file-state.md](../../file-state.md) | Project registry、feature identity lock、worktree lease、run lock 與跨檔 reconcile 次序 |
| [decisions.md](../../decisions.md) | 補記 D01 原始歷史 Red／最新 Green 語意；Q-TDD 只留方法與例外選擇；對齊 Q-RETRO 建議、未決清單、現行設計入口與已被 D15 取代的 Q-DEMO |
| [orchestrate-workflow-draft.md](../../orchestrate-workflow-draft.md) | 派工交唯一 controller、D13 依序實作標示、完整入口／Retro reference、Q-ID 對照、舊 Retro 建議與稱謂／錯字 |
| [loop-engineering.md](../../loop-engineering.md) | 現行入口與 V1–V6 次序、feature/run 鎖、錯字；保留早期研究推導的定位 |
| [project-intent.md](../../project-intent.md) | 依 D18 暫緩 PR 試用、D22 等待 P03 Retro 指示、未決事項與錯字 |
| [workflow-gap-review.md](../../workflow-gap-review.md) | 未決清單補齊 Q-NEXT、Q-RETRO |
| [pr-gating.md](../../experiments/pr-gating.md) | Controller／Reviewer 名稱及「這些」錯字 |
| [CONTEXT.md](../../../CONTEXT.md) | 領域描述擴充為已確認的 project／feature 兩層與驗收／Retro |
| [README.md](../../../README.md) | 角色入口指向現行設計，新增 runtime 研究入口 |
| [agent-messaging-and-opencode.md](agent-messaging-and-opencode.md) | 新增固定版本來源、查核結果、請求中的過度斷言與實證缺口 |
| 本回報 | 保存已套用／未套用範圍及新發現衝突 |

D23 後續同步檔案：`decisions.md`、`workflow-design.md`、`workflow-contracts.md`、`orchestrate-workflow-draft.md`、`CONTEXT.md`、`README.md` 與本回報。

## 原提案取捨與後續決策

| 請求項目 | 處理與原因 |
| --- | --- |
| 1A：原始固定指揮鏈提案 | 原提案未採用；後續使用者確認同層協作，已記為 D23 並同步角色文件與 Controller 詞條。未禁止 orchestrator 別名，D17 未改 |
| D08「Orca lead agent」是否等於 Project Lead | 未確認，未建立同義映射 |
| 1B：disputed 先覆核一次才 Blocked | 後續已採 D25：經 controller 交獨立 Reviewer 覆核一次，仍有 blocking 爭議則 Blocked 交人；沿用原 batch、不另計修正輪次。超過一次仍未授權 |
| 1C：Q-RUNTIME、採用 opencode 及 G2 Codex 的 runtime/model 定義 | D30 僅確認核心與底層實作解耦；使用者已撤回 model-only 的誤輸入，G2 runtime/model 定義與是否採用 opencode 仍待選定。未新增 Q-RUNTIME 問題列、選定新 adapter 或啟動 V4；各實證缺口留研究檔 |
| DEC-03：Q-CIT 列及跨文件 Q-CIT 引用 | 使用者後續要求第 6 項先不處理，已記 D29；不新增 Q-CIT 問題列或 gate，G3 仍為必要 CI |
| 其他既有未決政策 | 後續五項推薦已獲「1-5 ok」：Q-PUBLISH → D24、Q-TDD → D26、Q-NEXT → D27、Q-RETRO → D28；與 D25 一併同步設計及執行契約 |

## 新發現衝突與採取的修正

1. **D23 原措辭 vs D11／D17：** Project Lead「決定 scope、接受或退回」可能被讀成取代使用者的變更裁決與最終接受。先提出限定授權範圍的版本；使用者後續改選同層協作，已由 D23 明確記錄，人工裁決權沿用 D11／D17。
2. **Orca 未綁定 Run 並非不能傳訊：** 固定版本有 unbound terminal-to-terminal 測試；群組也有 `@worktree` 例外。研究檔保留這些限定，未照抄概括敘述。
3. **背景結果不是保證等父回合結束後才送：** opencode source 直接提交 synthetic prompt；busy runner 的採用時機與 request 對應需實測。Process-local background registry 的限制不代表所有 session/messages 都不持久化。
4. **檔案交接與 runtime messages 不衝突：** 禁止 agent 以 peer message 當權威交手，不禁止 adapter 讀原生 assistant messages 並先落檔。Producer／IDs／digest 不等於語意驗證已通過。
5. **Q-PUBLISH 不重開 D09：** 當時待選的是 finding 狀態的權威儲存來源，後續已由 D24 選本機 JSON；解除阻擋的角色權限維持 D09。
6. **人工退回未必已有 accepted：** 使用被退回的交付版本，不要求不存在的 accepted 版本；沿用原 run／三輪上限，首次退回也有可用路徑。
7. **Provider 文件有內部落差：** 固定版本 Anthropic 文件同時提及 Pro/Max 登入及不再內建該 plugin。研究保留 API key 路徑與矛盾說明，未宣稱已完成登入或測試。

原始碼／官方文件連結集中在 [runtime 研究](agent-messaging-and-opencode.md)。本輪僅作文件核對；mock、runtime E2E 或三 gates 的驗證均未執行。
