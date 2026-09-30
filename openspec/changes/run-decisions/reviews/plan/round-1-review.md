verdict: changes_requested

以下 `design.md`、`tasks.md`、`proposal.md`、`specs/` 均指 `openspec/changes/run-decisions/`。本次是唯讀的靜態計畫審查；沒有修改檔案、執行實作測試或寫入 GitHub。

**P1-01｜嚴重度：blocking**

- **位置**：`design.md:144`、`design.md:152`
- **問題**：token 檢查安排在 `mutate` 裡，但 store 在呼叫 `mutate` 前就處理冪等與衝突。非 owner 使用已存在的 decision ID、改動 reason，即可觸發新的 conflict revision，把 run 變成 Blocked；完全相同的 payload 則可能直接取得成功的 duplicate 回應，略過 token 核對。
- **依據**：**事實**：`design.md:144` 先處理 transition，`:147` 才執行 mutate，`:152` 把有狀態檢查放在 mutate，`:165` 又明確排除 token 於 payload。`specs/durable-delivery/spec.md:17`、`:21` 要求非 owner 的寫入被拒且狀態不變。**推論**：依所列順序，衝突提交可以先於授權檢查發生。
- **建議**：在同一把 lock 內，先核對 owner，再處理冪等、衝突及任何修復寫入；補上錯誤／缺少 token 對「相同重送、不同內容重送、history 領先」的測試，斷言 `not_owner` 且 bytes、revision、conflicts 不變。

**P1-02｜嚴重度：major**

- **位置**：`tasks.md:186`、`tasks.md:324`
- **問題**：AC-O01 的驗收被改寫了。spec 要求 `init` 後保存協調者 identity；計畫卻要求 `init` 後 `owner = null`，把 identity 延到另一個 `claim` 命令才保存。
- **依據**：**事實**：`specs/delivery-orchestration/spec.md:8`、`:9` 的 WHEN／THEN 明確連在一起；`design.md:54` 的 init 沒有 identity 輸入，`:105` 的 owner 只由 claim 寫入。`tasks.md:324` 直接以 claim 取代原 THEN。
- **建議**：讓 init 保存協調者 identity，並把它與 claim 所授予的協調權區分；若要維持目前流程，必須交 Project Lead 改 spec，不能把目前測試算作 O01 通過。

**P1-03｜嚴重度：major**

- **位置**：`design.md:154`、`design.md:344`
- **問題**：刪除提交時的物件引用檢查，理由不足以維持原不變式。「本次先 put_object」只能保證本次新增物件，不能保證狀態先前引用的物件仍存在、可讀且完整。例如登記 plan 後物件遺失，`approve_plan` 仍可只憑 metadata 提交核准。
- **依據**：**事實**：高層 `docs/design-candidate/d45-04/design.md:87` 明定提交時檢查物件引用；`validation.md:77` 的 s6 要求引用缺失時拒絕提交。現計畫明確移除此檢查，且 `tasks.md:272` 只有成功讀回案例。**推論**：後續沒有讀取該物件的提交，無法靠 `get_object` 補足檢查。
- **建議**：保留提交時的引用完整性檢查，補上缺失、毀損物件的拒絕測試；同步安排 store 的 owned paths。若要降低此保證，交 Project Lead 裁定高層設計變更。

**P1-04｜嚴重度：major**

- **位置**：`design.md:181`、`tasks.md:237`
- **問題**：目前 `resolve_conflict` 只能解除封鎖，尚未實現 AC-D10 的「選定其一或放棄」。保留原 decision 有效，再用新 ID 重送另一份內容，不等於選定另一份；例如已生效的 `approve_plan` 發生內容衝突，解除後用新 ID 重送仍會被 `already_approved` 拒絕。
- **依據**：**事實**：`specs/durable-delivery/spec.md:33` 要求人以 decision 選定內容；`design.md:181` 保留原內容有效，`:250` 拒絕已核准狀態的另一筆 approve；`tasks.md:237` 只驗解除封鎖及另一筆一般 decide 可寫入。**推論**：現有測試即使全部通過，也不能證明「改採嘗試內容」成立。
- **建議**：明定選擇、原 decision 的有效性及重送語意，測試保留原內容、採用另一份、放棄三條路徑；若產品只需要解除封鎖，應交 Project Lead 調整 spec。新增 kind 的命名本身合理，問題在效果契約。

**P1-05｜嚴重度：major**

- **位置**：`tasks.md:14`、`tasks.md:102`、`tasks.md:189`、`tasks.md:190`
- **問題**：部分 Red 說明與「前面的測試已 Green」互相衝突：
  - `:189` 已要求另一個 run 完成 claim；`:190` 卻仍以 claim 是「八個都成功的 stub」作為 Red。若前者真的驗證 setup，後者便不能再假設 stub。
  - t2 完成後，拒絕非 `only_on` skip 的實作可能已使 xfail 失敗；t5 的指定 Red 因而提前 Green，但它沒有標示突變。
  - `:233` 缺 actor 的參數，在前一個 actor 檢查完成後，`code == 1` 已成立；`:239` 未知 kind 若被 parser 拒絕，`code == 2` 也已成立。
- **依據**：**事實**：上述順序與斷言均出自各測試列；`:16` 又規定未標突變而提前 Green 必須停下。`docs/decisions.md:80`（D68）要求 Red 證明對應行為。**推論**：照此執行會遇到錯誤前置、提前 Green，或失敗在後面的其他斷言。
- **建議**：先交付並驗證單次 claim，再用缺少競態保護作並行 Red；t5 明定已有 skip 政策下的處理；缺欄位及 unsupported 改以精確錯誤內容作 Red，並指定會失敗的參數案例。

**P1-06｜嚴重度：major**

- **位置**：`tasks.md:105`、`tasks.md:112`、`tasks.md:116`
- **問題**：共用骨架雖然先做且有自測，但缺少「參數確實轉送」的自測；目前的 envelope 測試允許 handler 完全忽略輸入。此外，`python -m` 的 Red 明列為缺少 `__main__.py`，dist-smoke 的 Red 是找不到命令、exit 127，仍屬缺入口造成的失敗。
- **依據**：**事實**：指定的 `/Users/johnson.chiang/.claude/skills/spec-to-plan/SKILL.md:41` 要求骨架自測驗證參數轉送及輸出契約；`:71`、`:72` 排除缺命令、缺模組的 Red。`tasks.md:109` 至 `:112` 沒有參數轉送斷言。
- **建議**：補上 handler 收到完整解析參數的骨架測試，以及 `cli_proc` 注入接縫的自測；先提供可呼叫入口，再讓 Red 失敗於輸出／轉送契約。打包檢查也應有具名斷言，不能只記錄 shell 找不到命令。

**P1-07｜嚴重度：major**

- **位置**：`design.md:62`、`design.md:108`、`design.md:261`；`tasks.md:231`、`tasks.md:274`
- **問題**：介面與預期 Green 有三處未對齊：
  - parser 核對 kind 選項，且 argparse 錯誤一律為 `usage`；後面卻要求任意未知 kind 回 `unsupported`。
  - status 的欄位清單沒有 `decisions`，但 provenance 測試要求從 status 讀取它。
  - 狀態檔未核准時的 `approval` 是 `null`；status 則是 `{status: not_approved, plan_version: V}`。測試再要求「feature.json 相同」，字面上無法同時成立。
- **依據**：**事實**：分別見 `design.md:78`、`:81`、`:108`、`:261`，以及 `tasks.md:239`、`:231`、`:274`。
- **建議**：統一 parser／handler 的錯誤分工，補齊 status 契約，並把狀態檔與 status 的驗證寫成各自的明確投影；不要要求不同表示法直接相等。

**P1-08｜嚴重度：major**

- **位置**：`tasks.md:275`、`tasks.md:332`
- **問題**：O26 的對應測試只驗登記 SA 後仍等待批准，沒有斷言 SA 的版本與確認來源已保存。驗收表卻宣稱兩者已被驗證。
- **依據**：**事實**：`specs/delivery-orchestration/spec.md:69` 的 THEN 同時要求保存版本、来源及不取代開工確認；`:275(b)` 只斷言 phase。`:272` 的文件登記案例也沒有 SA。
- **建議**：在 SA 案例直接從 status／狀態檔核對 version、source，並保留「沒有 approval」及後續人工批准的斷言。

**P1-09｜嚴重度：minor**

- **位置**：`tasks.md:92`、`tasks.md:142`
- **問題**：`build: ...` 與 `ci: ...` 缺少 scope，不符合本計畫自行訂定的 commit subject 格式。
- **依據**：**事實**：`tasks.md:23` 要求 `<type>(<scope>): <祈使句>`，沒有列例外。七個 subject 都未超過 72 字元，其餘格式無此問題。
- **建議**：例如改成 `build(loopctl): ...`、`ci(loopctl): ...`，或明確寫出適用的 scope 例外。

**P1-10｜嚴重度：minor**

- **位置**：`tasks.md:365`
- **問題**：宣稱 `F_FULLFSYNC` 等行為已由 task 3.1 覆蓋，超過列出的測試能證明的範圍。中斷測試攔截的是 `os.link`／`os.replace`；即使移除 fsync，這些測試仍可能通過。
- **依據**：**事實**：`tasks.md:191`、`:192` 沒有同步呼叫或順序斷言；`design.md:148` 則承諾檔案、目錄同步及 Darwin 的 `F_FULLFSYNC`。**推論**：目前只能證明所測程序中斷點的恢復，不能證明同步契約已受測試保護。
- **建議**：補上平台適用的同步順序／失敗路徑測試，或限縮覆蓋聲明；保留 `design.md:353` 已揭露的斷電測試限制。

逐一核對 **42 個具名測試及 1 個 dist-smoke Red** 如下。「可」表示計畫存在到達指定斷言的合理路徑，並非已執行通過；巢狀欄位比較須以安全的缺值觀察到達斷言，不能先拋出 KeyError／TypeError。名稱縮寫均可由 `tasks.md` 行號唯一定位。

| Task／行號 | 測試縮寫 | 指定 Red 判斷 |
|---|---|---|
| 1.1／99 | t1 only_on | 可；子 session 的返回值比較失敗，Green 還須驗 skip／pass 數 |
| 1.1／100 | t2 非平台 skip | 可 |
| 1.1／101 | t4 零收集 | 可；已明列突變 |
| 1.1／102 | t5 xfail／xpass | 不保證；t2 可能已使指定 xfail Red 變綠，見 P1-05 |
| 1.1／103 | t6 平台不符 | 可 |
| 1.1／109 | help 命令清單 | 可；空 main 已可呼叫，失敗在輸出 |
| 1.1／110 | 每命令一個 envelope | 可；helper 必須容納空 stdout |
| 1.1／111 | usage JSON | 可；需把 SystemExit 與空 stdout 正規化 |
| 1.1／112 | python-m 與 in-process 相同 | 不合 D68；指定原因是缺模組，見 P1-06 |
| 1.1／116 | dist-smoke | 不合 D68；只有缺命令的 exit 127，見 P1-06 |
| 2.1／148 | required check 宣告 | 可；已指定缺檔 helper |
| 2.1／149 | pull_request job | 可；已指定缺檔 helper |
| 2.1／150 | pytest 單一設定來源 | 可；已明列突變 |
| 3.1／186 | init planning run | Red 可；Green 違反 O01，見 P1-02 |
| 3.1／187 | status human | 可 |
| 3.1／188 | init 不覆寫 | 可；測的是拒絕回應而非崩潰 |
| 3.1／189 | 未 init 的 run | 前置未成立：需要先有真實 claim，見 P1-05 |
| 3.1／190 | 並行 claim | 所寫的 stub 前提不成立；須改競態 Red，見 P1-05 |
| 3.1／191 | history 後中斷 | 可 |
| 3.1／192 | history 前中斷 | 可；已明列突變 |
| 3.1／193 | stale revision | 可；已有提前 Green 的突變安排 |
| 3.1／194 | untrusted state | 可；須確保有效 setup 後才注入損壞 |
| 3.1／195 | manual edit | 可 |
| 4.1／231 | decision provenance | Red 可；status 的 Green 契約不一致，見 P1-07 |
| 4.1／232 | only human actors | 可 |
| 4.1／233 | missing fields | 部分可；缺 actor 的 `code == 1` 已綠，見 P1-05 |
| 4.1／234 | coordinator token | 可；但漏掉 P1-01 的重送／衝突路徑 |
| 4.1／235 | decision 重送一次生效 | 可 |
| 4.1／236 | 同 ID 不同內容 | 可 |
| 4.1／237 | resolve conflict | Red 可；Green 不足以驗 D10 的選擇，見 P1-04 |
| 4.1／238 | budget extension | 可；已指定 `rounds:+2` 參數 |
| 4.1／239 | unsupported | 頂層 stub 可；未知 kind 的 exit 2 可能已綠，見 P1-05、07 |
| 5.1／272 | 原生文件登記／讀回 | 可 |
| 5.1／273 | 不可讀文件 | 可；測的是受控拒絕回應 |
| 5.1／274 | 版本與待批准視圖 | Red 可；狀態檔 Green 表示法有衝突，見 P1-07 |
| 5.1／275 | 校準版人工批准 | 可；明確指定 (d)，但 (b) 漏 O26 保存斷言 |
| 5.1／276 | 缺 bindings | 可 |
| 5.1／277 | 核准後 dispatch | 可；前列只要求 approved，尚未要求 dispatch |
| 5.1／278 | 已核准文件變更 | 可 |
| 6.1／311 | scope change | 可；已指定「已核准」參數 |
| 6.1／312 | 只有新版可批准 | 可；以本 task 才加入 superseded 檢查為前提 |
| 6.1／313 | policy digest 核准 | 可 |
| 6.1／314 | 核准後 policy 改動 | 可 |

切片方面，六個 task 沒有明顯的純技術層切分；骨架先做、依賴無循環、owned paths 與共用檔案順序已有列出。D69 effort、D72 預設模式及不同模型 Reviewer 的安排符合規則。單一 session 的規模估計沒有足夠反證可判不合格，但 `tasks.md:373` 的「超出就內部重排」不能取代 D71 必要時拆成更小垂直切片的要求。

20 個 AC 都有映射及證據位置；主要缺口是 O01、O26，以及 D03、D10 上述反例。其餘 16 個 AC 已列出對應的可觀察行為與驗收入口，仍須先修正相關 Red 與介面契約問題。範圍、平台、網路需求、風險及執行上限都有記載。

`next = dispatch` 的決定合理：`proposal.md:27` 已確認核准後回報派工，`:79` 把名稱與欄位留給 design；`design.md:213` 也綁定 plan 與 approval。`resolve_conflict` 作為獨立 kind 同樣在 `proposal.md:80` 授權的 design 決策內，但效果須修正 P1-04。

**第 7 點四個問題的判斷**

| 問題 | 判斷 | 依據 |
|---|---|---|
| (a) claim token 遺失無法恢復協調權 | **可接受但須揭露的風險**；若要新增恢復能力，再交 Project Lead 訂 spec | 高層 `docs/design-candidate/d45-04/design.md:88` 本來就是明文只回一次、保存 digest；現行 DUR-02 未定義收回／重發協定。`design.md:350` 已揭露。不能因此宣稱 token 遺失後可恢復操作。 |
| (b) `human:x` 由呼叫者自稱 | **可接受的風險** | `specs/delivery-orchestration/spec.md:13` 明定接受條件就是 actor 格式；高層 design `:6` 採可信本機協作。沒有依據要求本 Feature 新增身分驗證。這不豁免 P1-01 的 token 核對。 |
| (c) init 應保存 identity，卻由 claim 保存 | **計畫缺陷** | 固定 AC-O01 的 THEN 明確；見 P1-02。只有要保留目前設計時，才需要 Project Lead 改 spec。 |
| (d) 已核准時登記變更回 `scope_change_required` | **可接受的設計決定** | `specs/delivery-orchestration/spec.md:29` 要求變更經 scope_change；`design.md:238` 拒絕變更、保持狀態，讓 caller 先完成該流程。它沒有把新內容套進舊核准。 |

**實際核對過的檔案**

- [指定的 spec-to-plan/SKILL.md](/Users/johnson.chiang/.claude/skills/spec-to-plan/SKILL.md)：第 2、3 節及獨立審查規則。
- [openspec/config.yaml](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/openspec/config.yaml)
- [docs/decisions.md](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/docs/decisions.md)：D11、D13、D50、D52、D53、D57、D68、D69、D71、D72、D75。
- 本 change 的 [design.md](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/openspec/changes/run-decisions/design.md)、[tasks.md](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/openspec/changes/run-decisions/tasks.md)、[proposal.md](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/openspec/changes/run-decisions/proposal.md)。
- 三份固定 spec：[delivery-orchestration](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/openspec/changes/run-decisions/specs/delivery-orchestration/spec.md)、[delivery-gates](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/openspec/changes/run-decisions/specs/delivery-gates/spec.md)、[durable-delivery](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/openspec/changes/run-decisions/specs/durable-delivery/spec.md)。
- 高層設計的 [design.md](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/docs/design-candidate/d45-04/design.md)、[validation.md](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/docs/design-candidate/d45-04/validation.md)、[tasks.md](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/docs/design-candidate/d45-04/tasks.md) 相關段落，以及 [勘誤](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/docs/design-candidate/d45-04-errata.md)。
- [現況研究 research.md](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/docs/research/2026-09-30/run-decisions/research.md)。
- 唯讀參考 `loop-engineering-thin@fcefecc` 的 [store.py](/Users/johnson.chiang/workspace/loop-engineering-thin/src/loopctl/store.py)、[cli.py](/Users/johnson.chiang/workspace/loop-engineering-thin/src/loopctl/cli.py)、[tests/conftest.py](/Users/johnson.chiang/workspace/loop-engineering-thin/tests/conftest.py) 相關段落；未把舊測試或舊審查當成本次證據。