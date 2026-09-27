# Controller bootstrap：設計交接與 runtime 修訂

## 最新狀態：候選v3已覆核，待D11

Opus已交付詳細設計、tasks與88個AC驗證對照。獨立GPT初審9項blocking，兩輪修正後共DR-01–DR-10全部verified、未解blocking 0。只有文件review完成；沒有D11批准、產品程式或產品gate。現行候選、完整歷程與最少待決項見 [設計審查與開工確認](../../reviews/2026-09-27-controller-detailed-design.md)。OpenSpec正式design/tasks仍未建立；下列早期派工／未收件狀態屬歷史，以本節為準。

日期：2026-09-27。本紀錄包含一次真實但失敗的設計派工及後續 D38／D39 決策；沒有 production code、最終 design／tasks、GitHub issue／PR 或產品 gate 結論。

## 依同一 workflow 建置 controller

Controller 是正式 feature 交付。Project Lead 交接既有 spec／AC 與高層設計，指定的 Opus 5.5 Implementer 承接詳細設計／最終 plan，再交使用者一次 D11 確認。其後以 Superpowers TDD 實作，由獨立 Reviewer 與真實 CI 驗證並反覆修正。第一輪由目前協作者按相同契約協調；完成的 controller 才能接受自動派工／恢復測試，不能宣稱由尚未完成的產品自行帶完。

目前 change 有多個 capabilities；設計 intake 要求評估是否拆成可獨立驗收的 feature PR，尚未決定拆分。既有 spec 仍是唯一權威。GitHub owner/repo 已詢問，尚無回答及 remote；可先做本地設計，正式 implementation 前仍需 ticket 與 D11 確認。

## 已執行的派工

- [Assignment](controller-bootstrap/assignment.json)：`implementation-design-intake`／`design-intake-01`，只讀固定輸入，未授權程式變更。
- [Prompt](controller-bootstrap/prompt.md)：請 Implementer 提出技術設計、切片、關鍵問題及部分 AC 驗法草案；不是另一份權威 spec。
- [16 份輸入的 manifest](controller-bootstrap/input-manifest.json) 與 [固定快照](controller-bootstrap/input-snapshot.tar.gz)：保存派工當時的 dirty 文件內容；它們早於 D38，不代表現行政策。
- [觀察與選取的原生回執](controller-bootstrap/evidence.json)：由協作者保存，沒有冒充模型產出的 result；原始 runtime log 留本機，不自動版控。

Claude Code 以明確 `claude-opus-5-5` 啟動；可用工具限 Read／Glob／Grep，未提供產品修改、Bash 或 GitHub 工具。最終 process exit 為 1，native result 同時回 `subtype=success` 與 `is_error=true`，文字是 `ECONNREFUSED`；只有 synthetic assistant message、沒有 model usage 或結構化設計結果。因此此任務為 failed，不能據 subtype／init model 推論完成或 Opus 身份已核對。

在與派工相同的 sandbox 外權限下，Claude 登入唯讀查詢成功。局部設定顯示 Anthropic base URL 指向本機 `127.0.0.1:8787`，socket 查核為 connection refused；未改設定、未啟動 proxy、未讀出 credential。只據此定位本機 proxy 沒有監聽，不斷言更深原因。程序已被 launcher wait 收割並保存 exit；未另重派。

這次 CLI 有內建 API retries，尚未由產品 controller 管理；不得把此 probe 當成已符合 D13 的 controller retry 證據。Adapter 設計需把 native retry 與外層操作／時間預算的關係明列並驗證。

## 使用者修訂：D38

預設由 OpenCode 執行 agents，按角色選 OpenAI／Claude models。Orca、Codex／ChatGPT 相關入口及 Claude Code 是選配。Controller 依賴抽象 runtime 契約；指定模型不等於指定同廠牌 CLI。D36 的 Opus 5.5 與 G2 獨立審查保持，精確 provider/model 與隔離能力需另核對。

D38 調整的是產品預設 runtime。其後已依使用者要求安裝 OpenCode 1.18.32，完成無推論的 session／重啟 probe；詳見 [安裝紀錄](opencode-setup.md)。模型推論與 Reviewer 隔離尚未驗證。

## 本次開發分工：D39

使用者為本次 controller 建置選擇先協調 Opus 與 GPT agents。沿用 Opus 5.5 Implementer 與獨立 GPT／Codex Reviewer，從詳細設計、plan 到實作／review／fix 留下同一套交接證據。產品 D38 不變；OpenCode 登入不是 bootstrap 設計派工前置。具體 GPT 型號與可用派工通道仍待核對，尚無成功的 Opus 設計回應。現有 Claude Code 通道的本機 proxy 未監聽，正在確認可用入口；沒有改 credentials 或繞過原路由。

## 下一個可執行交接

1. 恢復或確認可用的 Opus 5.5 派工通道，核對 requested／actual model；沒有就具體回報，不默默換模型。
2. 依 D38／D39 更新輸入 manifest／assignment，再交 Implementer 做詳細設計；沿用尚適用研究，不重做完整 SA。
3. 收斂影響設計的選型與切片；形成唯一 design、tasks 及完整 AC validation，交 D11 確認。
4. 核對 GitHub 目標、ticket／CI 與 reviewer profile 後正式實作；真實 E2E 和模擬測試分開。先測通 orca-delivery，再啟動 cross-node-file-transfer。

## 已交接 opus session（design-02）

使用者指定 Orca workspace `opus`。已核對對應 Claude terminal 畫面為 Opus 5.5／xhigh，向該 terminal 發送限於設計草稿的 assignment；Orca receipt 顯示 `input_accepted` 與 `turn_started`，後續畫面已見讀取快照。這證明派工已開始，不是任務完成、actual inference model 最終核對或 gate 通過。

- 工作包與固定輸入：`/private/tmp/orca-controller-bootstrap-20260927/opus-session-design-02/`，含 assignment、input-manifest、prompt、dispatch-receipt。
- 輸出：同目錄 `outputs/` 下的 design.md、tasks.md、validation.md、result.json；目前待收件。
- Session 的原 cwd 是 gigaxfer；assignment 只允許寫上述 outputs，不修改任何產品 repo、全域設定或 GitHub。尚未授權產品實作。
- 使用者要求代答範圍內的例行 Y／proceed；協作者核對提示再處理，D11 的具體 design＋plan 開工確認仍保留。
- 收件後核對輸入版本與完整88個AC，再交獨立GPT reviewer；不可只憑 console 完成訊息放行。
