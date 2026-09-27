# 既有設計更新與雙軸 Review

日期：2026-09-27。狀態：本次文件 review 的 findings 已由各原 reviewer 覆核解除，兩軸未解 blocking 均為 0。這不是產品 PR 的 G2，也不是 D11 開工批准；controller／orchestrate 尚未實作。

## 範圍與固定基準

依使用者要求，先更新既有設計，再 review，留下交接後才考慮 compact。另再次確認 D33：完成並測通 orca-delivery harness／controller 後，用新 workflow 從頭啟動 cross-node-file-transfer，驗證完整 Project＋Feature 流程與 member 操作；沿用適用基準，新實作留下新證據。舊 gigaxfer PR／P03 維持暫緩。

本次採已安裝 Matt `code-review` 的 Standards／Spec 雙軸方法，由 `/root/design_standards_review` 與 `/root/design_spec_review` 分開閱讀、回報與覆核。原 skill 以固定 git commit diff 及 issue 為輸入；本次明示適配為未提交的設計文件快照，需求來源使用 project-intent、已確認 decisions 與 SA 契約。沒有假稱原生 commit review、已存在 GitHub feature issue 或 G2 review。

- Git HEAD：`bc255674f47afb5d45d5a6f2067846b06dec1137`；工作樹包含既有修改及未追蹤文件，HEAD 不是這些文件的完整版本。
- 初審：snapshot-v1，48 份 Markdown／OpenSpec config 的固定內容；manifest SHA256 `01bf57d44f3ffe4b1570d0251602d8e46d1d86f9f74d88c56600ada54e90182e`。
- 覆核：snapshot-v2，同一檔案集合；manifest SHA256 `a187e22c275e01e08b82737052239af2a7daa84a989c73acc51782a064328d98`。
- 可重讀內容與每檔 hashes：[v1 archive](2026-09-27-design-review/snapshot-v1.tar.gz)、[v2 archive](2026-09-27-design-review/snapshot-v2.tar.gz)；[證據索引](2026-09-27-design-review/evidence.json) 保存 archive digest、修訂 diff 與命令結果。快照不是產品執行或 runtime evidence。

主要範圍：README、CONTEXT、decisions、project-intent、workflow-design、workflow-contracts、delivery-harness-overview、project-lead-sa、file-state、loop-engineering，以及正式 OpenSpec proposal／四份 capability specs。References／research／experiments 僅作有來源的歷史或候選，未視為另一份現行權威。

## 本次更新

- 同步 Orca 推薦選配與公司直接 OpenCode 接入；移除現行總覽及 formal spec 對 Orca terminal／專有 IDs 的必要依賴。
- DUR-09 增加 AC-D20–D22：無 Orca 部署、核心與原生身份映射、兩種接法各自驗證；保留原 AC IDs 與 G2 約束。
- [Workflow §10.2](../workflow/overview.md#102-建置-harness-本身與後續試用) 分開正式 bootstrap 與之後的完整試用：controller 實作需可追蹤 feature ticket，不依賴尚未完成的 controller 自己帶完自己；人工協調、fake tests、真實 adapter 及自動 E2E 分別留證據。
- D33 補記使用者最新確認；Q-RUNTIME／Q-PLATFORM 明列已提出而未回答的問題，未新增已確認模型或平台政策。

## Standards

**初審：STD-01｜中等｜blocking：是（限設計收斂）。**

`docs/workflow-contracts.md:186` 將 required check 的 `missing / pending / cancelled / skipped` 合列，結果寫成「只有 policy 明示接受才通過」，可能讀成四種狀態均可豁免。正式 `delivery-gates/spec.md:81、85` 及 `project-intent.md:25` 明定前三種不得成功，只有 skipped／neutral 可有明確政策例外。此表用於定義可觀察驗收結果，可能導出錯誤 gate 驗收案例，屬規範歧義。

**修正與覆核：**最小修正將其拆成兩列。原 Standards reviewer 已在 snapshot-v2 核對 `workflow-contracts.md:186–187`，確認不可成功狀態不能豁免，skipped／neutral 需明確適用 policy，與正式規格一致。另核對 decisions 的待決項與 workflow-design 修訂摘要，未發現新問題。

**結果：STD-01 verified／解除 blocking；初審 1 項，新增 0 項，未解 blocking 0。**

## Spec

**初審：SPEC-01｜P2｜blocking：是（限設計收斂）。**

`docs/workflow-contracts.md:186` 的驗收列讓不可成功的 check 狀態看似可由政策接受。需求 `project-intent.md:25` 規定 missing/pending/cancelled/timed-out/unknown/stale 不能當 success；正式 `delivery-gates/spec.md:81–85` 亦只對 skipped／neutral 開放例外。這會使依契約撰寫的驗收與 gate 實作採用不同準則。

**修正與覆核：**原 Spec reviewer 已核對 snapshot-v2 的兩列規則與需求一致；Q-RUNTIME／Q-PLATFORM 仍明列待答，未放寬 G2、承諾跨平台支援或批准開工。

**結果：SPEC-01 verified／解除 blocking；初審 1 項，新增 0 項，未解 blocking 0。**

兩軸各自保留 finding ID 與覆核結果；它們指向同一處文件歧義，未合併或跨軸重排嚴重度。本次 review 範圍內未發現其他阻擋，不表示尚未建立的 implementation design／tasks 已被 review。

## 驗證與限制

- `openspec validate implement-delivery-loop --strict --no-interactive`：通過。
- 正式 specs：86 個唯一 AC IDs（O28／G20／F16／D22）；本次只新增 D20–D22。
- Active Markdown 本機連結檢查及 `git diff --check`：通過。
- `openspec status --change implement-delivery-loop --json`：proposal／specs 存在；design 尚未建立、tasks 缺 design，`isPlanningComplete=false`。

上述是文件／結構檢查，沒有測產品程式、GitHub CI、Opus 5.5 實際推理或自主交付。覆核後僅新增本報告、快照證據、[handoff](../handoffs/2026-09-27-controller-design.md) 與 README 導覽，未再改動受審執行契約。

下一步先收斂 Q-METHOD／Q-RUNTIME／Q-PLATFORM 及可查證的環境事實，完成具體 design、唯一 plan／tasks、AC 驗證對照及 feature ticket，再依 D11 確認開工。預算、timeout、recurrence、required checks 的具體實作預設隨該設計核對；不在此次 review 代替使用者批准。
