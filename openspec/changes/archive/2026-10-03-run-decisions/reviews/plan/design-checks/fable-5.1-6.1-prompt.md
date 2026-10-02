你是獨立的設計檢查者（Claude Fable 5.1），在全新 session、唯讀。不要修改任何檔案。輸出用繁體中文。

目前目錄是 loopctl 的 feature branch `feature/run-decisions` 的全新 clone。Feature 1（change `run-decisions`）的 task 1.1、2.1、3.1、4.1 已完成並通過逐 task 審查，4.2 正在複審；接下來要實作 **task 5.1（登記原生文件與開工確認）** 與 **task 6.1（範圍變更與政策核准）**。前面幾個 task 的逐 task 審查一再找到「計畫沒定義」的設計缺口（例如 I/O 錯誤的回應、同一 decision 多個衝突、計畫漏列擁有路徑），每次都要回頭改計畫。你的工作是在 5.1、6.1 開工前把這類缺口先找出來。

## 讀這些
- `openspec/changes/run-decisions/tasks.md`：共同規則、共用檔案、5.1 與 6.1 兩節全文（交付、擁有路徑、介面、測試表），以及驗收驗證中它們對到的 AC 列。
- `openspec/changes/run-decisions/design.md`：全部，特別是 D3（狀態欄位）、D4（store 契約與提交順序）、D6（衝突與解除，含「同一 identity 最多一個未解衝突」）、D7（衍生欄位、phase、blockers、next）、D8（核准後的 next）、D9（登記原生文件）、D10（決策種類與撤銷時的清除規則）、D11（status 視圖）。
- 固定的 spec：`openspec/changes/run-decisions/specs/*/spec.md`；`proposal.md`。
- 已實作的程式（5.1、6.1 會延伸它們）：`src/loopctl/{cli,store,state,next,decisions}.py`、`tests/`。用 `git log` 看各 task 的 commit。

## 找什麼
1. **計畫沒定義、但實作時一定會碰到的情況**：狀態組合、順序、錯誤路徑、與既有行為（D4 提交順序、D6 衝突、授權先於一切、讀取不寫檔、exit 6 io_error）的交互。例如：已核准時又登記同版本或不同版本、binding 角色重複、policy 與 plan 的關係、scope_change 疊加與撤銷、policy_change 撤銷、衝突發生在 approve_plan／scope_change／policy_change 上、resolve_conflict 的三種選擇對這些 kind 的效果、derive 的優先序。
2. **計畫內部或與既有程式互相矛盾的地方**：介面、欄位名、exit code、測試的預期值。
3. **5.1、6.1 測試表裡每個 Red 是否能失敗在所寫的斷言上**（以目前的程式為準）；有沒有會提前變綠或停在 setup 的。
4. **擁有路徑是否足夠**：要完成交付，是否需要改不在擁有路徑內的檔案（4.2 就是因為漏列 `cli.py` 而停下）。

## 不要做
- 不要建議擴大範圍或加新功能；只找讓 5.1、6.1 無法照計畫做完或做出錯誤行為的問題。
- 沒有依據的意見不要列。

## 輸出
先一行總結：`verdict: ready` 或 `verdict: gaps_found`。然後逐條：`ID`（G-01……）、`task`（5.1 或 6.1）、`嚴重度`（blocking／minor）、`情境`（具體的輸入與狀態 → 計畫沒說會怎樣，或會得到錯誤結果）、`依據`（檔案:行號）、`建議的最小規則`（一兩句，盡量不改既有行為）。最後列出實際讀過的檔案。
