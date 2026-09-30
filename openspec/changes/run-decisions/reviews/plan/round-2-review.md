verdict: changes_requested

已核對 `7c557c6`，工作目錄乾淨，與 `cd1a1ba` 的差異只有指定兩份計畫。以下行號均為新版；`design.md`、`tasks.md`、`specs/` 均位於 `openspec/changes/run-decisions/`。

| Finding | 判定 | 依據 |
|---|---|---|
| P1-01 | `resolved` | `design.md:156` 明定授權先於冪等、衝突與寫入；`tasks.md:254` 補齊非 owner 重送、製造衝突及 history 領先的案例。修正另引入 P2-01。 |
| P1-02 | `resolved` | `design.md:54`、`:116` 由 init 保存 `coordinator`，claim 才授予 token；`tasks.md:196`、`:199` 分別驗證 identity 與協調權。符合 AC-O01 與 DUR-02 的分工。 |
| P1-03 | `resolved` | `design.md:167` 恢復所有物件引用的完整性檢查；`tasks.md:206` 包含新增引用不存在、既有物件遺失／毀損及普通 digest 字串。 |
| P1-04 | `partially_resolved` | `design.md:207`、`:211`～`:219` 已定義三種選擇及重送；`tasks.md:255`、`:256`、`:301` 已驗實際效果。但撤銷可能恢復不適用的核准，見 P2-02。 |
| P1-05 | `partially_resolved` | `tasks.md:105`、`:106` 已重排 t5／t2；`:199` 先交付單次 claim；`:250`、`:258` 改為精確錯誤斷言。但並行 claim 的指定突變 Red 仍不成立，見 P2-03。 |
| P1-06 | `resolved` | `tasks.md:115` 新增參數轉送測試，`:118` 改驗既存入口的 exit code 傳遞，`:119` 自測 prelude／barrier；`:123` 改為具名 envelope 檢查。 |
| P1-07 | `resolved` | `design.md:75` 明定 kind 為自由字串；`:313` 納入 decisions；`:317` 明定 approval 投影。`tasks.md:248`、`:296` 已配合修正。 |
| P1-08 | `resolved` | `tasks.md:297(b)` 明確核對兩種投影中的 SA version、source，以及仍未核准。 |
| P1-09 | `resolved` | `tasks.md:25` 明列 build／ci 不帶 scope 的例外，原 subject 因而一致。 |
| P1-10 | `partially_resolved` | `tasks.md:393`、`design.md:410` 已撤回 F_FULLFSYNC 與斷電持久性的覆蓋宣稱；但「fsync 失敗時不提交」仍超出新增測試範圍，見 P2-04。 |

**P2-01｜嚴重度：blocking**

- **位置**：`design.md:148`、`:171`、`:181`
- **問題**：取消落後現行檔的修復，卻仍只讀取領先一版的 history，會遺漏連續中斷後已提交的 revision。
- **依據**：
  - **事實**：`:148` 只回傳「下一版」；`:181` 不修復落後的 `feature.json`；`:180` 定義 history 存在即已提交。
  - **推論**：已持有 token、現行檔為 rev 2。decision X 寫完 history 3 後中斷，現行檔仍為 2；下一個 decision Y 從恢復出的 rev 3 提交 history 4，再於 replace 前中斷。此時現行檔仍為 2，依讀取規則只回 rev 3，遺漏已提交的 Y；後續提交還可能撞到既存 history 4。
  - `specs/durable-delivery/spec.md:25`、`:29`、`:33` 要求已提交 revision 可恢復。
- **建議**：重新維持「history 最多領先一版」的不變式，或明訂能驗證連續已提交 snapshot 的恢復協定；保留非 owner／拒絕路徑不寫檔。新增兩次連續中斷，再查詢及重送兩筆 decision 的測試。

**P2-02｜嚴重度：blocking**

- **位置**：`design.md:301`、`:302`
- **問題**：`effect_overwritten` 只檢查 decision 曾寫入的欄位，沒有檢查還原核准所依賴的 bindings，可能恢復舊核准並直接回報 dispatch。
- **依據**：
  - **事實**：scope_change 改的是 plan、approval（`:294`）；撤銷只比較這些欄位的 after 值（`:301`、`:302`）；有 approval 就回 dispatch（`:240`）。
  - **推論**：先批准 P1／bindings B1，再執行 scope_change S；等待批准期間登記 B2，但不更換 plan。接著對 S 製造衝突並選 abandon。plan、approval 仍等於 S 的 after，因此撤銷會還原批准 B1 的舊 approval，而目前 bindings 已是 B2；最後仍會回 dispatch。
  - `specs/delivery-orchestration/spec.md:29`、`:41` 要求變更後舊核准失效、重新批准才能往下走。`tasks.md:339` 目前只測「plan 被 P2 取代」，漏掉這條路徑。
- **建議**：撤銷時也核對被還原效果的依賴版本，尤其 approval 的 plan／binding pins；不能恢復不適用的核准。補上只改 binding 的反例，以及 scope_change／policy_change 撤銷的正向案例。

**P2-03｜嚴重度：major**

- **位置**：`tasks.md:201`、`:398`
- **問題**：拿掉 flock 不保證讓「得勝者恰為 1」失敗；指定突變可能在該斷言仍為 Green。
- **依據**：
  - **事實**：`design.md:171` 仍以 `os.link` write-once 建立同一個 history revision，`:175` 要求 OSError 往上拋。
  - **推論**：即使八個程序都先讀到沒有 owner，也可能只有一個 link 成功，其餘因檔案已存在而失敗。因此成功數仍是 1，真正失敗的會是後面的 `already_claimed`／owner 回應斷言，或整列完全不會殺死此突變。
  - `os.link` 前睡 0.2 秒也不能保證所有程序已完成讀取；`:398` 的「不靠運氣」宣稱不成立。
- **建議**：以可控制的交錯次序驗證競態，指定真正會被破壞的公開行為，例如落敗者的受控回應與完整狀態；不要用移除 flock 推定成功數一定增加。

**P2-04｜嚴重度：minor**

- **位置**：`tasks.md:204`、`:392`；`design.md:410`
- **問題**：新增測試只能證明「第一個 fsync、history link 之前失敗」不提交，不能概括為所有 fsync 失敗都不提交。
- **依據**：
  - **事實**：`:204` 把所有 fsync 改成拋錯，因此會在第一次呼叫停止。`design.md:171` 在 history link **之後**還有目錄 fsync；`:180` 此時已定義為提交。
  - **推論**：該目錄 fsync 失敗時，命令雖失敗，history 已存在，讀取會恢復新版。
- **建議**：將聲明限縮至實測位置；若加入 link 後的同步失敗案例，預期應依提交邊界驗證恢復與冪等，不能一律要求舊版。

**突變 Red 逐一判斷**

此 commit 實際只有 **7 項**：6 個具名 pytest 測試加 dist-smoke，其中 2 項為條件式突變。`tasks.md:399` 的清單也是這 7 項；沒有另外 3 項可供核對。

下表判斷的是指定單測的預期失敗位置。這些突變不保證整套測試只有一處失敗，例如多印 stdout 也會破壞其他 CLI 測試。

| 位置／測試 | 突變判斷 |
|---|---|
| `tasks.md:107` t4 零收集 | **合理、可達。** 子 session 的 `NO_TESTS_COLLECTED` 改為 OK，會使 `ret != 0` 失敗。 |
| `tasks.md:123` dist-smoke | **合理、可達。** envelope 前多印一行，會破壞具名 envelope 的單行條件；help 的既定條件不受影響。 |
| `tasks.md:157` 單一 pytest 設定來源 | **合理、可達。** 新增 pytest.ini 直接使「沒有其他設定檔」失敗；應依既定單測命令執行，並還原檔案。 |
| `tasks.md:201` 並行 claim | **不成立。** 移除 flock 後，write-once 仍可能讓成功數保持 1；見 P2-03。 |
| `tasks.md:203` history 前中斷 | **合理、可達。** 先 replace 再中斷 link，讀取會因 history 缺失回不可信；safe lookup 得不到 revision 1，指定比較失敗。失敗值可能是 None，而非 2。 |
| `tasks.md:205` stale revision | **合理、可達。** 略過 revision 檢查後，在授權與其他前置合法時，不再拋 RevisionConflict，`pytest.raises` 失敗。 |
| `tasks.md:254` 非 owner 重送 | **合理、可達。** 至少參數 (a) 會在授權前直接回 duplicate，使 `code == 4` 失敗。其他參數也可能破壞 bytes／conflicts 斷言，不能宣稱全測試只有一個受影響斷言。 |

**其餘 Red 可達性更新**

只列新增、改寫或仍有問題的列；上表七項不重複。「可」是靜態可達性判斷，不代表已執行。

| `tasks.md` 行號 | 測試縮寫 | 判斷 |
|---|---|---|
| 105 | t5 xfail／xpass | 可；已移到 t2 之前，指定 xfail 參數。 |
| 106 | t2 非平台 skip | 可；指定一般 skip，不再與前列 xfail 混淆。 |
| 115 | 參數轉送與 handler envelope | 可；safe lookup 可在沒有派送時取得 None，失敗於 received.repo。 |
| 116 | 每命令一個 envelope | 可；骨架自測可容納尚未填入 handler 的空輸出。 |
| 117 | usage JSON | 可；SystemExit 與空 stdout 的 helper 契約已補明。 |
| 118 | python-m 與 in-process 相同 | 可；入口存在，測的是回傳值沒有成為程序 exit code。 |
| 119 | prelude／barrier 自測 | 可；忽略 prelude 時 code 為 0，指定比較應為 9。barrier 部分是同列的額外 Green 契約。 |
| 196 | init planning run | 可；Green 已包含 coordinator identity。 |
| 197 | status human | 可；新增 coordinator 顯示不改指定 Red。 |
| 198 | init 不覆寫 | 可；新增 actor 變體不改指定 Red。 |
| 199 | 單次 claim 與 token | 可；token 缺值可失敗於格式斷言，沒有依赖未完成的 claim setup。 |
| 200 | 未 init 的 run | 可；前列已交付 claim，next 仍可保留 stub。 |
| 202 | history 後中斷 | 可；新加唯讀／拒絕不修復的斷言，但漏掉 P2-01 的連續中斷。 |
| 204 | fsync 失敗 | 可；但只涵蓋第一個同步點，見 P2-04。 |
| 206 | 物件引用缺失／毀損 | 可；(a) 不需要先成功提交物件引用，能到達指定 raises 斷言。 |
| 248 | decision provenance | 可；status 已提供 decisions。 |
| 250 | missing fields | 可；指定缺 source 的精確結果，消除缺 actor 提前 Green 的問題。 |
| 251 | token | 可；已明定使用新的 decision。 |
| 253 | 不同內容造成衝突 | 可；同時保存兩份完整 payload。 |
| 255 | 保留 original | 可；未實作解除時 exit 3，指定 exit 0 失敗。 |
| 256 | attempted／abandon | 可；把所有選擇當 original 時，reason 不會變成 b。 |
| 257 | budget extension | 可；指定 invalid_target 內容，優於只比 exit 1。 |
| 258 | unsupported | 可；指定頂層 adopt 的完整結果，避開 parser 已回 exit 2 的問題。 |
| 294 | 原生文件登記 | 可；safe lookup 容納尚未登記的 plan。 |
| 296 | 版本與待批准視圖 | 可；Green 已分開兩種投影。 |
| 297 | 校準版人工批准 | 可；指定 (d) 的 Red 未改，(b) 已補 SA 保存斷言。 |
| 299 | dispatch | 可；前列仍未要求這個 next 值。 |
| 301 | 已生效 approve_plan 的衝突 | 可；4.1 只標 voided，abandon 後 approval 仍存在，指定斷言會失敗。 |
| 337 | scope_change | 可；明確觀察狀態檔的 approval。 |
| 339 | effect_overwritten | 可；無條件還原會使 abandon 回成功。此案例本身有效，但不足以涵蓋 P2-02。 |

`init --actor` 與 claim 的新分工符合固定 spec；identity 是紀錄，token 才是協調權，沒有額外授予批准權。

task 3.1 現有 13 個具名測試、4.1 有 11 個，撤銷效果則分散於 4.1～6.1。僅凭數量不足以判定一定超過一個 session，因此不新增規模 finding。`tasks.md:401`～`:405` 已改成超出時拆垂直切片並重新審查，修正了上一版「內部重排即可」的問題；P2-01、P2-02 定案後仍應重新估量。

**本輪實際重新核對的檔案**

- [design.md](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/openspec/changes/run-decisions/design.md)
- [tasks.md](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/openspec/changes/run-decisions/tasks.md)
- [delivery-orchestration/spec.md](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/openspec/changes/run-decisions/specs/delivery-orchestration/spec.md)
- [durable-delivery/spec.md](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/openspec/changes/run-decisions/specs/durable-delivery/spec.md)
- [openspec/config.yaml](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/openspec/config.yaml)：design／tasks 規則。
- [指定的 spec-to-plan/SKILL.md](/Users/johnson.chiang/.claude/skills/spec-to-plan/SKILL.md)：第 2、3 節。

另核對上述兩份計畫的 `cd1a1ba → 7c557c6` 完整差異；未修改檔案或寫入 GitHub。