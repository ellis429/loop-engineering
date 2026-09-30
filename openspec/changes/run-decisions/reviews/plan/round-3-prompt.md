第 3 輪複審（同一個 session，最後一輪；仍然唯讀：不修改檔案、不 commit、不寫 GitHub）。

作者已依第 2 輪修正，HEAD 是 `8020cbd`（`git diff 7c557c6 8020cbd` 只改 `openspec/changes/run-decisions/design.md` 與 `tasks.md`）。spec 固定不變。主要改動：history 最多領先一版的不變式恢復（授權通過後才 roll forward）；核准只能由建立它的 decision 產生，撤銷不還原核准，移除 effect snapshot 與 `effect_overwritten`；並行 claim 改用子程序 prelude 的閘門與落敗者回應斷言；fsync 聲明限縮；4.1 拆成 4.1 與 4.2，共 7 個 task。

請複審整份合併清單：
1. P1-04、P1-05、P1-10 與 P2-01～P2-04 逐條判定 `resolved`、`partially_resolved` 或 `not_resolved`，附依據（檔案:行號）；其餘已 resolved 的 P1 確認沒有因本輪退回。
2. 本輪修正是否引入新問題：新測試（連續兩次中斷、反例與撤銷案例、閘門競態、4.2）的 Red 是否能失敗在所寫的斷言上；roll forward 與「讀取不寫檔」「授權先於一切」是否一致；拆 task 後的 blocking edges 與介面是否正確；是否仍符合固定 spec。
3. 只列有變動的 Red 可達性列。

輸出格式同前：第一行 `verdict: clean` 或 `verdict: changes_requested`；判定表；新 finding 用 P3-01……；最後列核對過的檔案。沒有依據的意見不要列；minor 且不影響開工的問題請標明「不阻擋」。
