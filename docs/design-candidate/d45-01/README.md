# D45／D46 設計候選：分段交付

最新候選與 review 請見 [D45-02](../d45-02/README.md)；本頁保留前一階段歷史。

**尚未採用為正式設計、尚未 D11、沒有產品實作或 PR Pass。** 正式規格仍在 loop-engineering；本目錄只保存可審閱的候選，不含舊 src/tests。

- [清理與選擇性提取](cleanup-map.md)：21 個舊模組的取捨；合格行為測試可逐案提取。
- 三項政策已由使用者「All ok」確認：[D47–D49](/Users/johnson.chiang/workspace/loop-engineering/docs/decisions.md)、[批准紀錄](policy-approval.json)。離線 4h 採恢復時如實處理；採可信本機協作邊界；本 repo 可用人工核准的版控 checks 政策。具體 check 集合與完整 design／plan 尚未批准。
- [原決策提案](decisions-needed.md) 保留審閱當時的歷史狀態；其中「待決」由上述批准紀錄取代。
- [設計草稿](design.md)：draft_pending_sync；其他章節仍待完整對齊。
- [初審](review-01.md)：六項 findings；經三次定點修正後，[限定覆核](review-04.md) 確認 D45-R01–R06 全部 verified。這不是完整 design clean。
- [分段結果](result.json)：spec-delta、88 AC／17 findings 對照、tasks、validation 尚待完成。作者結果中的待覆核描述是提交當時狀態，以上 reviewer 的最新結論為準。

這些是文件審查，不是產品 G2，不能用來關閉舊 S1 findings。原始候選與來源快照保存在 loop-engineering/.delivery/bootstrap/herdr-design-d45-01；[發布對照](publication-manifest.json) 記錄原始／發布雜湊。發布版本只調整來源文件連結，未產出的引用明示 pending；原始候選保持不動。

正式開發的 worktree／branch 安排仍是提案。新樹只接納選定且重新驗證的程式及必要測試，不整批複製、不掛回舊程式。沒有提交、推送、GitHub 發文、合併或產品程式修改。
