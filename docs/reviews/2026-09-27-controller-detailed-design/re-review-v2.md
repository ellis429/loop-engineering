# Controller design v2 覆核

**changes_required**：原 9 項中 8 項 verified、DR-04 still_open；新增 DR-10。僅剩 DR-04、DR-10 為本輪 confirmed blocking。

Verified 是設計層解除原反例，不是產品 G2 或實測通過。固定來源 hashes、逐項依據與限制見 re-review-v2.json。

| ID | 狀態 | 覆核結果 |
| --- | --- | --- |
| DR-01 | verified | OS launcher 成為實際拒寫邊界；verified 需負例通過及相符 dispatch receipt；未通過時 implementer 不派工、G2 unknown。原先 clone/env/事後比較可升格的反例已排除。 |
| DR-02 | verified | VersionSet 明確不含時間，採用內容與 observation 分離；相同 body 重讀與 restart 不改 key，測法已涵蓋。 |
| DR-03 | verified | 不可變 evidence 與當前 assessment 已分離；首次 PR binding 有 R-unaffected，新 base 有 R-base 重驗及新 assessment，原先保留舊 G1 key 而不能 Pass 的反例已解除。 |
| DR-04 | still_open | temp index 已解 untracked 新測試遺失，但 copy worker index 保留已 stage 的排除/scope 外內容；後續 pathspec 排除不會移除既有 index entry，仍不符合本修正承諾的 snapshot 範圍。 |
| DR-05 | verified | 選定 per-attempt clone＋controller 唯一 writer＋CAS fast-forward，列 integration operation、T0/A 對應及 ref 查回；原先兩種 branch 模型矛盾與中斷後無整合判準已解除。 |
| DR-06 | verified | 新增跨 clone 可查的 host authority locator 與 runs lineage；另一 clone 被拒、遺失 state Blocked、feature 預算累計，排除原 repo-local registry 繞過。 |
| DR-07 | verified | session 與 prompt 分段持久化；session marker 不再等於 prompt accepted，messages 查回及未知 prompt 的停止/fencing 路徑已具體化，故障矩陣核對外部呼叫次數。 |
| DR-08 | verified | 候選 M 發現、fetch/parents 映射、依 head/merge policy 查相應 SHA 均已定義；測法含 H 無 check、M 有 check 與舊 base M。 |
| DR-09 | verified | blob 檔案/目錄同步與 snapshot 提交屏障已定義，缺引用 Blocked；process kill、呼叫順序及 power-loss 驗證範圍分開，原先只 link 即供 snapshot 引用的缺口已補。 |

## 待修正

### DR-04 — temp index 的初始內容可繞過 scope/exclude 篩選（P1 / blocking）

**位置：** reviewed-v2/design.md:193–197；reviewed-v2/tasks.md:31–39

**依據：** GAT-02 / AC-G04：source snapshot 與實際 evidence 可核對；DUR-03 / AC-D05：scope 不符的成果不可採為 evidence；DUR-09：credentials 不寫入交接；v2 design.md:194、196 自身的 exclude／scope 承諾

**反例：** worker index 已有 staged outside.txt，或已 stage 的 .env（即使之後加入 ignore/exclude）。第193行完整複製 index；第194行只對 scope.paths 且非 exclude 的檔案執行 add，並不移除已存在的 outside.txt/.env entry。因此 write-tree/commit-tree 仍會保存它們。第196行 scope_violation 在 commit 已建立後才檢查，不能使『scope 外檔案不進 snapshot』成立；在 scope 內但被 exclude 的 staged 檔案，也不一定觸發 scope_violation。現有 probe 的 untracked .env 成功排除不能覆蓋此反例。

**修正：** 明定基準 tree 與允許 overlay，不能直接信任整份 worker index 作最終候選；在 write-tree/commit-tree 前驗證候選 tree 的差異及 excluded entry，拒絕或清除不應保存的 staged 新增／修改，並保留 baseline 外部程式所需內容。明定 snapshot.exclude 對 baseline 已 tracked 檔案的處理。補 staged out-of-scope、staged excluded/ignored、mixed staged/unstaged 的真 git 反例，確認不建立含禁止新增內容的 snapshot，worker index/worktree 不變。

**驗證缺口：** task 1.2 與 AC-G07 只列一般 scope_violation/.env 排除，沒有驗證由初始 index 帶入且 pathspec 不更新的 entries。

### DR-10 — R-reuse 與不完整依賴集合可使新契約直接取得舊 G2 clean（P1 / blocking）

**位置：** reviewed-v2/design.md:168–185；reviewed-v2/tasks.md:77–82；reviewed-v2/validation.md:80–80

**依據：** GAT-07 / AC-G17：spec/design/AC 改變須要求 Reviewer 讀新契約，plan/skill/policy 變更須評估適用性；GAT-05 / AC-G11：目前版本的適用獨立 review 才能使 G2 通過；D01、D11、D19、D38

**反例：** H 已在 spec S1 得 G2 clean。S2 新增一條 AC，而 adopt_binding decision 附 reuse:{gate:g2,reason:...}；第178行允許直接推導 G2 passed 到新 key，未要求獨立 Reviewer 讀 S2，三 gates 便可在同 key Pass。另一條相同根因路徑是已採用 skill digest 或 controller_version 改變：G2 dependency 沒有 skill/controller，G1 也沒有 controller，R-unaffected 因交集為空直接沿用；第185行『不派該 assignment』不能使既有 assessment 失效。這不是一般人工 closure 指定 finding 的政策。

**修正：** 明定每種 gate 的可沿用邊界：spec/design/AC 改變不可僅憑一般 reuse decision 把舊 G2 verdict 變成新契約的 clean；須有 Reviewer 對新契約的適用 assessment/review。補齊 skill/controller 版本的影響評估規則與理由，不能因 dependency table 漏欄位默認 unaffected；若保留人工例外，必須明確沿既有政策裁決且不可偽裝成未執行的 G2。測法加入 S1 clean→S2新增AC＋reuse、skill/controller更新→不得無評估直接Pass。

**驗證缺口：** 目前 AC-G17 只驗 candidate＋awaiting_approval；沒有驗採用新 binding 後不可略過新契約 review，task 2.1 也未覆蓋遺漏的 version dependencies。

## 驗證邊界

隔離已改為 OS 機制＋負例證據＋dispatch receipt 才可 verified；OpenCode、keychain、Linux 能力仍待測，缺能力維持 Blocked，故未把待測本身視為原 DR-01 未解。Git/dispatch/CI/持久化的產品驗證同樣未執行。

本輪沒有改原 review.json/md 或 frozen artifacts，沒有派子代理、改 repo 或公開發文。

DR-04 補充佐證：協作者以假資料在 tmp git repo 重現已 stage 的 `.env.fake` 通過 exclude 後仍在 tree；見 `review/staged-exclude-probe.json`（hash 已綁定於 JSON）。此為小型設計 probe，非產品 gate evidence。
