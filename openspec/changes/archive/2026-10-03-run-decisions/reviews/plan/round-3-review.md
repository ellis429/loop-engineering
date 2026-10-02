verdict: changes_requested

本輪核對 `8020cbd`；相對 `7c557c6` 只改 design、tasks，工作目錄無變更。以下簡稱的 `design.md`、`tasks.md` 均位於 `openspec/changes/run-decisions/`。Red 判斷是依計畫順序與契約推演，沒有執行或修改測試。

| ID | 判定 | 依據 |
|---|---|---|
| P1-04 | resolved | 三種選擇已定義實際效果；`attempted` 先撤銷再驗證、套用 A，`abandon` 清除所屬核准。`design.md:217`、`:218`、`:310`；`tasks.md:297`、`:342`。多筆 scope 疊加另見 P3-01。 |
| P1-05 | resolved | 原有測試順序修正保留；競態 Red 改驗落敗者的受控回應，write-once 不再使目標斷言提前通過。`tasks.md:101`、`:202`、`:256`、`:262`。逾時措辭另見 P3-03。 |
| P1-10 | resolved | 已明確區分程序中斷、第一個同步點失敗，以及尚無證據的 post-link fsync、`F_FULLFSYNC`、實際斷電持久性。`design.md:427`；`tasks.md:434`、`:435`。 |
| P2-01 | resolved | 恢復「history 最多領先一版」；前移位於授權、revision、mutate、物件驗證之後。連續中斷測試只截斷指定 revision 的替換。`design.md:153`、`:171`、`:186`、`:387`；`tasks.md:259`。 |
| P2-02 | resolved | 移除 effect snapshot 還原；撤銷 S 不會復活 X 對 B1 的核准，B2 必須另經 Y 批准。`design.md:305`、`:312`；`tasks.md:380`。 |
| P2-03 | resolved | 閘門移至讀完狀態後、`os.link` 前；拿掉 flock 時，輸家可因 `FileExistsError` 缺少 `already_claimed` 回應而命中指定斷言。`design.md:389`；`tasks.md:202`。 |
| P2-04 | resolved | 測試明確限於 history 暫存檔首次 fsync、link 之前；提交邊界及 link 後失敗另有定義。`design.md:178`；`tasks.md:205`。 |

其餘已解 P1 沒有因本輪退回：

| ID | 判定 | 依據 |
|---|---|---|
| P1-01 | resolved | 授權仍先於 duplicate／衝突；拆分後兩類非 owner 測試都保留。`design.md:158`；`tasks.md:260`、`:295`。 |
| P1-02 | resolved | `init --actor` 保存 coordinator identity，`claim` 才授予 token 協調權；符合固定 AC-O01、DUR-02。`design.md:116`、`:117`；`tasks.md:197`、`:200`。 |
| P1-03 | resolved | 提交仍驗證全部物件引用，包括既存引用。`design.md:169`；`tasks.md:207`。 |
| P1-06 | resolved | 參數轉送、envelope、`python -m`、prelude／barrier 自測及 smoke 的具名 Red 都保留。`tasks.md:116`、`:119`、`:120`、`:124`。 |
| P1-07 | resolved | parser／handler 分工與 status 投影契約保留。`design.md:70`、`:323`；`tasks.md:118`、`:262`、`:337`。 |
| P1-08 | resolved | SA 測試仍斷言 version、source 被保存，且不產生核准。`tasks.md:338`。 |
| P1-09 | resolved | `build`／`ci` 無 scope 的例外明文保留，subjects 與規則一致。`tasks.md:25`、`:98`、`:150`。 |

七個 task 的順序與共用檔案歸屬已同步；4.1、4.2 都能透過 `decide`／`status` 驗證，沒有新增只做一層的 task。4.1 為九個測試、4.2 為四個；3.1 仍最大，但已有超出 session 時拆分並重審的界線，沒有足夠依據另判粒度違規（`tasks.md:37`、`:279`、`:316`、`:449`）。

**P3-01**

- **嚴重度：major**
- **位置：** `design.md:312`；`tasks.md:380`
- **問題：** 新撤銷規則會清掉另一筆仍有效的 scope 限制。具體路徑：批准 P1 → `scope_change S1` → 同一 P1 再做 `scope_change S2` → 對 S2 製造衝突並選 `abandon`。此時只撤銷 S2，S1 仍 `in_effect`，但清掉 `plan.superseded_by` 的規則卻讓 P1「回到可批准」，可以不登記新版本就再次批准。
- **依據：**
  - **事實：** `scope_change` 沒有排除重複對已 superseded plan 操作的條件，且直接覆寫 `superseded_by`（`design.md:298`）。
  - **事實：** 撤銷目前 marker 所指的 S 時，直接清掉 marker 並使 plan 可批准（`design.md:312`）；既存測試只有單筆 S（`tasks.md:380`）。
  - **事實：** 固定 AC-O07、AC-O23 要求新版本被批准後才能前進（`specs/delivery-orchestration/spec.md:41`、`:61`）。
  - **推論：** 上述序列撤銷 S2，卻同時消除了未撤銷 S1 的更版限制。D9 對重登 P1 仍會因 S1 拒絕，與直接批准 P1 的結果也不一致（`design.md:284`）。
- **建議：** 清除某筆 scope 的 marker 後，仍須保留其他有效 scope 對同一 plan 的限制；統一登記、批准與 `next` 的判定。加入 S1／S2 疊加後放棄 S2 的反例，斷言舊版仍不能批准；維持「不還原核准」。

**P3-02**

- **嚴重度：major**
- **位置：** `design.md:163`、`:225`；`tasks.md:296`
- **問題：** Blocked 狀態下，未知 `cid` 的錯誤契約互相矛盾。這是本次合併複審新發現的既存問題，並非拆 task 才引入。
- **依據：**
  - **事實：** D4 第 4 步規定：已有未解衝突，而 `resolves` 不在其中，就拋 `TransitionConflict`（`design.md:163`）。
  - **事實：** kind 的有狀態檢查在其後執行（`design.md:94`、`:165`）；D6 與 4.2 測試卻要求未知 `cid` 回 exit 1 `unknown_target`（`design.md:225`；`tasks.md:296`）。
  - **推論：** run 有衝突 K 時，以合法 token 解除不存在的 Kx，會先回 exit 3，無法到達 `unknown_target`。指定 Red 的 `code == 0` 可以失敗，但完整 Green 契約不能照現有順序同時成立。
- **建議：** 明定未知／已解除 `cid` 與一般 Blocked 檢查的優先序，同步 D4、D6、4.2 測試及依賴契約；相關檢查仍須在授權之後、寫入之前。

**P3-03**

- **嚴重度：minor，不阻擋**
- **位置：** `design.md:389`、`:390`；`tasks.md:440`
- **問題：** 「3 秒逾時後繼續」不能保證拿掉 lock 後所有程序一定讀到同一版。
- **依據：**
  - **事實：** gate 允許未等齊 n 個程序就放行（`design.md:389`）。
  - **推論：** 若其他程序尚未到達就逾時，第一個程序可能先完成 claim，晚到者正常得到 `already_claimed`；因此新的 Red **可達**，但不是文件所稱的必然競態。
- **建議：** 收斂「一定一起搶」的措辭；保存突變 Red 時，同時記錄 gate 到達數及放行原因，證明該次確實施加了競態。

只列本輪有變動的 Red 可達性：

| 測試／位置 | 判斷 |
|---|---|
| `…concurrent_claims_leave_one_owner…`，`tasks.md:202` | **可達。** 無 flock 時，搶同一 history 檔的輸家缺少受控回應，精確 `result` 比較失敗；不再誤用得勝者數量。逾時限制見 P3-03。 |
| `…failed_sync_before_the_link…`，`:205` | **可達。** 尚未加入 fsync 時 claim 成功，`code != 0` 失敗；測試範圍已正確限縮。 |
| `…consecutive_interruptions…`，`:259` | **可達。** 尚無前移時，兩次中斷留下 feature=2、history=4，load 只回 3，`revision == 4` 失敗。修正後 wrapper 允許前移 revision 3，只截斷 revision 4。 |
| `…non_owners_cannot_resend`，`:260` | **突變可達。** 授權移到冪等之後，原樣重送回 duplicate／exit 0，`code == 4` 失敗。 |
| `…same_decision_id_with_other_content…`，`:294` | **可達。** 4.1 僅處理相同 payload，不同內容尚不會回 Blocked，`code == 3` 失敗。 |
| `…non_owners_cannot_create_conflicts`，`:295` | **突變可達。** 授權移後，錯誤 token 的不同內容先製造衝突並回 exit 3，`code == 4` 失敗。 |
| `…resolve_conflict_can_keep_the_original`，`:296` | **Red 可達。** 尚無解除例外時回 exit 3，`code == 0` 失敗；但 Green 的未知 cid 案例有 P3-02。 |
| `…take_the_attempted_content_or_abandon_it`，`:297` | **可達。** 前列只完成 original 時仍保留 reason `a`，`reason == "b"` 失敗。 |
| `…conflict_on_an_applied_approve_plan…`，`:342` | **可達。** 4.2 只標 voided，尚未清核准，abandon 的 `approval is None` 失敗。 |
| `…undoing_a_scope_change…`，`:380` | **可達。** 尚未加入 scope 清除規則時，marker 仍是 S，`next.blockers == ["plan_not_approved"]` 失敗。新案例涵蓋原 B2 反例，但漏掉 P3-01 的多筆 scope。 |
| `…undoing_a_policy_change…`，`:383` | **可達。** 尚未加入 policy 清除規則時仍為 approved，abandon 的 `policy.status == "not_approved"` 失敗。 |

實際核對過的檔案：

- 本 change：[design.md](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/openspec/changes/run-decisions/design.md)、[tasks.md](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/openspec/changes/run-decisions/tasks.md)、[proposal.md](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/openspec/changes/run-decisions/proposal.md)。
- 固定 specs：[durable-delivery](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/openspec/changes/run-decisions/specs/durable-delivery/spec.md)、[delivery-orchestration](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/openspec/changes/run-decisions/specs/delivery-orchestration/spec.md)、[delivery-gates](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/openspec/changes/run-decisions/specs/delivery-gates/spec.md)。
- 規則：[spec-to-plan/SKILL.md](/Users/johnson.chiang/.claude/skills/spec-to-plan/SKILL.md)、[config.yaml](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/openspec/config.yaml)、[decisions.md](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/docs/decisions.md)。
- 高層設計：[design.md](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/docs/design-candidate/d45-04/design.md)、[validation.md](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/docs/design-candidate/d45-04/validation.md)、[tasks.md](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/docs/design-candidate/d45-04/tasks.md)、[勘誤](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/docs/design-candidate/d45-04-errata.md)。
- [現況研究 research.md](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/docs/research/2026-09-30/run-decisions/research.md)。