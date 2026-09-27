# 同題規格比較：Orca Delivery Loop MVP

日期：2026-09-26。兩個獨立 agents 使用此相同輸入；不讀取另一個候選或既有三套評價。用繁體中文；保留工具原生 headings。

## 使用者任務
以已確認的需求與設計資料，各產生一版 feature 規格：OpenSpec 原生格式、Matt to-spec 原生格式。比較「同一 feature 的需求表達與交接」，不是同條件模型性能 benchmark。只產生規格文件；不做 implementation，不對外發文、不建立 ticket、PR、不更動 gigaxfer、不啟動 P03 trial。

Feature：單一 repo／issue／PR 的 delivery controller MVP，支援 project/feature 共用 orchestrate 入口。Project 只需 baseline/feature refs、人工接受、相依啟動與 Retro 候選的薄層；Feature 完整包含新 feature 與既有 pre-PR adopt、三 gates、bounded finding→fix→re-review、持久化與 crash/reconcile。不要把整個未來平台放進本 feature。

## 權威與狀態
baseline/ 是同一次讀取的來源快照，input-manifest.json 保存 SHA256。先讀 decisions.md、workflow-design.md、workflow-contracts.md、file-state.md、CONTEXT.md，再按需讀 runtime 與 trial 證據。決策為已確認，設計建議及未決事項仍保留其狀態；不把建議默默升格。

來源快照之後，使用者已對以下組合回覆 Ok：OpenSpec 管 spec/design/tasks；Writing Plans 的方法銜接 OpenSpec tasks；Superpowers TDD 管實作；自有 orchestrate＋唯一 controller 管派工、狀態、三 gates；Matt 釐清/domain 方法按需使用；Matt implement/implement-spec 僅作參考，不直接啟動外層 loop。這次要求比較兩版文件，不撤回上述既有選擇。

D11 一次 design+plan 開工確認仍未完成。D18 PR trial 暫停；D22 P03 Retro 未開始。Q-TARGET 未回答；runtime/model 具體設定與 native completion/隔離等仍有實證缺口。不要自行選 P03 PR、模型或強權限 workaround。不要聲稱已有 controller/code/tests 或真實 E2E。

## 共用測試邊界
建議：從 controller 的公開 start/adopt/status/resume/decision 等操作，透過可控制的 fake agent/GitHub/CI adapters，驗證可觀察狀態、派工、發布、重啟行為；另用真實 E2E 證明 adapters/完整交付。原 to-spec 要使用者先確認 seams；主 agent 已發出確認問題，尚待回覆。兩方先 research 與製作 coverage notes，收到主 agent 確認通知後再生成最終規格。不得將 pending 確認寫成已決定。

## 自檢基準（兩方相同）
保留三 gates、Red 歷史追溯/current Green、版本失效、check 非成功狀態、reviewer 獨立且不改作者 branch、穩定 finding/closure/dispute、先保存後發布/去重、外部 unknown/crash/ownership/budget、AC可驗證、原生檔名引用、同層角色、D11人工邊界、accepted與merged區分、Retro只候選、暫停trial以及未決選型。不要新增用戶沒授權的 gates/自動 merge或close。

## 產出規則
所有寫入限制 /private/tmp/orca-spec-comparison-20260926/<your-side>/；來源快照唯讀。主 agent 最後寫入 orca-delivery。每方除了原生規格，產生 author-notes.md：實際skill/CLI版本、方法偏離、未決事項、需求覆蓋映射、耗時/工具資訊能取得才寫，不編造 token數或成本。每條已確認要求須可定位；合理合併，不需照來源逐字重複。不要替主 agent比較或給自家方案優勝評分。遇到上下文衝突送訊息，不自行改政策。

## 本輪後續一致澄清

使用者要的是可比較的規格草稿，並未批准實作。測試邊界確認問題已提出但仍未回答；兩方可產出 comparison draft，Testing Decisions／notes 將 seam 明列為待確認提案，不升格成已確認政策。Matt 原版先確認再發布的完整流程未完成；本次有意只交草稿且不發布。OpenSpec 本次只交 proposal＋specs，不交 design/tasks。兩個 agents 均已收到相同澄清；未開始任何依賴該 seam 決策的實作或驗證。
