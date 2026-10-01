verdict: changes_requested

**P6-01**

- **嚴重度**：major
- **位置**：[tasks.md:211](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/openspec/changes/run-decisions/tasks.md:211)、[design.md:92](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/openspec/changes/run-decisions/design.md:92)
- **問題**：提交後 I/O 失敗的案例要求原樣重送 `claim` 回 duplicate，與既有契約衝突，無法同時滿足 Green。
- **依據**：**事實**：design.md:210 明定每次 `claim` 使用不同 transition identity，已有 owner 時回 exit 1 `already_claimed`；tasks.md:206 的既有中斷測試也採此預期。**推論**：新增測試若要求 duplicate，就必須改變既有 `claim` 行為。
- **建議**：將重送預期改為 exit 1 `already_claimed`、附目前 owner、revision 與檔案不變。D2 的 duplicate 保證限於重送同一 transition identity；decision 的驗證留在 4.1。明文 token 未成功交付的情況屬既有 #34 風險。

**P6-02**

- **嚴重度**：major
- **位置**：[design.md:91](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/openspec/changes/run-decisions/design.md:91)
- **問題**：exit 6 涵蓋所有 store I/O 錯誤，但 `committed` 只定義了 `commit` 的 history link 邊界，沒有涵蓋 `init/create`。
- **依據**：**事實**：design.md:140、209 規定 `init` 走 `create`，以 rename 發布；現行 [store.py:178](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/src/loopctl/store.py:178) 完成 rename 後，仍在 :186 同步父目錄，整條路徑沒有 `os.link`。**推論**：此處同步失敗時 run 已發布，但依新增文字無法正確判定 `committed`，可能誤報 false。
- **建議**：分別定義 `commit` 以 history link 成功、`create` 以 rename 成功為提交邊界；補上 `init` 發布前後 I/O 失敗的 envelope 與狀態驗證。

兩個新增測試的 Red 可達性如下；這是原始碼與計畫核對，未執行會寫檔的測試。

| 測試 | 判定 |
| --- | --- |
| `test_io_errors_print_an_envelope_and_say_whether_the_change_committed` | 兩個注入點皆能使未捕捉的 `OSError` 經 harness 記為 `code=None`，失敗在 `code == 6`。Red 可達；Green 有 P6-01。 |
| `test_a_rejected_command_never_creates_the_lock_file` | 可達。先收集命令結果，再優先斷言檔案集合；現行 `O_CREAT` 會重建 lock。若先斷言 `status` 的 exit 5，則會停在另一個斷言，實作時須遵守指定 Red 順序。 |

`lock_missing` 與讀取、被拒命令不寫檔一致（design.md:149、203）。D2「下次讀取會補上」宜明寫為「讀回新版，不修復 `feature.json`」，維持 D4 契約。

#36 描述準確對應審查原文的「存在檢查後、rename 前出現空目錄」競態（design.md:140；review-1/result.json:28）。依 Project Lead 本次明確決定接受風險，不另列缺陷。除上述 I/O 契約問題外，未發現對後續 task 介面的新衝突。

實際核對：指定 diff、design.md、tasks.md、durable-delivery/spec.md、review-1/result.json、src/loopctl/{cli,store,state}.py、tests/{conftest,test_state}.py、docs/decisions.md、openspec/config.yaml、指定 spec-to-plan/SKILL.md。HEAD 為 `7b6721d`，工作目錄乾淨。