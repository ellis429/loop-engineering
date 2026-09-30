第 4 輪複審（同一個 session；Project Lead 追加的最後一輪；仍然唯讀：不修改檔案、不 commit、不寫 GitHub）。

作者已依第 3 輪修正，HEAD 是 `020b046`（`git diff 8020cbd 020b046 -- openspec/changes/run-decisions/design.md openspec/changes/run-decisions/tasks.md`；中間的 `30cedd0` 只新增審查紀錄）。spec 固定不變。主要改動：`plan.superseded_by` 改為由所有仍生效的 `scope_change` 推導，登記、`approve_plan`、`next` 共用；`resolve_conflict` 指向非未解衝突的 cid 一律 exit 1 `unknown_target`，其餘寫入在衝突未解時 exit 3；閘門記錄到達數與放行原因。

請複審整份合併清單：
1. P3-01～P3-03 逐條判定 `resolved`、`partially_resolved` 或 `not_resolved`，附依據（檔案:行號）；確認 P1、P2 各條沒有因本輪退回。
2. 本輪修正是否引入新問題：推導規則是否在所有提交路徑一致、會不會讓既有測試（單筆 scope 撤銷、B2 反例、核准後 dispatch）的預期改變；新增或改寫測試的 Red 是否能失敗在所寫的斷言上（含新的條件式突變）；錯誤優先序是否和 4.1、4.2、5.1 的介面描述一致。
3. 只列有變動的 Red 可達性列。

輸出格式同前：第一行 `verdict: clean` 或 `verdict: changes_requested`；判定表；新 finding 用 P4-01……；最後列核對過的檔案。沒有依據的意見不要列；minor 且不影響開工的問題請標明「不阻擋」。
