# 薄 controller：D47–D49 政策確認後的設計候選

> **2026-09-27 後續狀態：D50 已接受六項精簡方向，本版 H1 切片進入修訂，暫不作開工提案。** 下文的 ready_for_human_review 是 review-09 對固定版本的一致性結論，不包含後續最小範圍審核。見[過度設計審核](/Users/johnson.chiang/workspace/loop-engineering/docs/reviews/2026-09-27-thin-controller-overengineering.md)。


**H1 候選已完成獨立文件覆核，沒有未解阻擋；尚未 D11、未開始產品實作。**

先看 [本次採用與開工確認範圍](approval-scope.md)；[最新審查](review.md) 與 [結構化結果](review-result.json) 均為 `ready_for_human_review`，不是產品 G2。

先讀 [實作計畫](tasks.md) 的切片與相依，再讀 [驗證與 CI 候選](validation.md)。

- [設計](design.md)：orchestrate 協調、controller 核對狀態／gates、工具做有限次外部操作；無常駐 supervisor。
- [四份 spec 的修改提案](spec-delta.md)：對回正式 OpenSpec，尚未採用。
- [88 AC／17 findings 對照](coverage.md)：105 個唯一列；全部為計畫驗證，舊 findings 仍 open。
- [清理與選擇性提取](cleanup-map.md)：新目錄重建；不帶入整套舊 src／tests。
- [三項已確認政策](policy-approval.json)：D47–D49；不包含具體 checks、完整 design／plan 或 D11。

H1 是 controller 核心與 fake／真 git 驗證，可透過 bootstrap 協調驗收其本身的 PR；H2 才是真實 runtime／GitHub／自動 loop，H3 是 cross-node-file-transfer 的完整示範。H2／H3 目前是能力與驗收範圍，尚非可直接派工的完整計畫。

Spec、design、plan 分段審查共提出 D45-S01–S10；經 Opus 修正及原 Reviewer 覆核，全部 verified，D45-R01–R06 維持。最新覆核核對 11 個文件的 hashes 與 105 個唯一對照 ID。作者文件中的「待覆核」保留提交當時狀態，以最新 review 為準。

[發布對照](publication-manifest.json) 綁定固定候選與發布版本；只調整本機來源連結。[舊版候選](../d45-01/README.md) 保留歷史。本目錄沒有產品程式碼。
