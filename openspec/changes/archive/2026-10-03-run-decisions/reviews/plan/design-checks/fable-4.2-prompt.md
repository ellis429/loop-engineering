你是獨立的設計檢查者（Claude Fable 5.1），在全新 session、唯讀。不要修改任何檔案。輸出用繁體中文。

目前目錄是 loopctl 的 feature branch `feature/run-decisions` 的全新 clone（HEAD `75e6877`）。task 4.2（transition 衝突與解除）已實作，但它的**設計**在逐 task 審查時兩度被找到缺口（計畫漏列 `cli.py`；同一 decision 多個衝突保存過時內容，之後改成「同一 identity 最多一個未解衝突」）。Project Lead 要你**只審設計**，不審程式碼：找出 D6 及相關段落還沒定義、或彼此矛盾的情況，讓我們在繼續之前補齊。

## 讀這些
- `openspec/changes/run-decisions/design.md`：D3（狀態欄位，特別是 transitions、conflicts、decisions）、D4（store 契約與提交順序、Blocked 的優先序、`resolves`）、D5（transition identity 與冪等）、D6（衝突與解除全文）、D7（衍生欄位、blockers、next）、D10（決策種類與撤銷時的清除規則）、D2（exit code、io_error）。
- `openspec/changes/run-decisions/tasks.md`：4.2 一節與它的測試表；5.1、6.1 中會碰到衝突與撤銷的部分。
- 固定的 spec：`openspec/changes/run-decisions/specs/durable-delivery/spec.md`（DUR-05、AC-D10）。
- 參考：目前的實作 `src/loopctl/store.py`、`decisions.py` 只用來理解設計的落點；不要評論程式風格。

## 找什麼（設計層級）
1. D6 沒定義的狀態組合與順序：例如衝突發生在 `approve_plan`、`scope_change`、`policy_change`、`budget_extension`、`resolve_conflict` 本身；解除後再重送各種內容；兩個不同 decision id 各有未解衝突；`attempted` 的內容核對失敗；`abandon` 之後的同 id 新內容；與 D4 第 3、4 步（duplicate、rejected、open conflict、`resolves`）的優先序；讀取不寫檔、授權先於一切、io_error 的提交邊界。
2. D6 與 D10 撤銷規則、D7 的 blockers／next、5.1／6.1 的介面之間的矛盾。
3. 有沒有任何情況會讓 run 卡在一個無法解除的狀態，或讓已撤銷的核准重新生效。

## 不要做
- 不要擴大範圍、不要加新功能；沒有依據的意見不要列。

## 輸出
先一行總結：`verdict: ready` 或 `verdict: gaps_found`。然後逐條：`ID`（DG-01……）、`嚴重度`（blocking／minor）、`情境`（具體輸入與狀態 → 設計沒說會怎樣，或會得到錯誤結果）、`依據`（檔案:行號）、`建議的最小規則`（一兩句，盡量不改既有行為）、`影響的 task`（4.2、5.1 或 6.1）。最後列出實際讀過的檔案。
