verdict: changes_requested

token 保存說明與既有契約一致（`design.md:128`、`:436`）；tasks、固定 spec、測試與驗收文字均未改動。但人工還原新增了不安全的回退語意。

**P5-01**
- **嚴重度：major**
- **位置：** [design.md:157](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/openspec/changes/run-decisions/design.md:157)
- **問題：** 「取最後可信快照、刪除較新 history」可能丟失已提交的 decision；`status` 回 exit 0 不能證明恢復正確。例如較新的 `scope_change` history 損毀，依此回退到舊的 approved 快照，便會復活已撤銷的核准。另存備份不會阻止現行狀態發生這個回退。
- **依據：** **事實**：新增步驟允許回退、刪除，並以 exit 0 判定完成（`design.md:156`、`:157`、`:158`）；固定 spec 要求已提交 revision 可恢復且不重複生效（`specs/durable-delivery/spec.md:25`、`:33`），scope 變更後舊核准失效（`specs/delivery-orchestration/spec.md:41`）。**推論**：上述操作不能視為不改變既有語意的說明。
- **建議：** 改為保全資料、停止寫入並交人處理；不能確認最新已提交狀態時，不指示回退或刪除較新 history。若要正式支援人工回退，須另由 Project Lead 決定恢復契約及驗證方式。