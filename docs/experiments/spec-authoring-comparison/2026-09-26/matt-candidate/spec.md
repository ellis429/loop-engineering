## Problem Statement

使用者目前需要在實作與審查 agents 之間搬運規格、追蹤 finding、要求修正，再逐一判斷測試、review 與 CI 是否適用目前的 PR。Agent 說完成、終端閒置或 CI 曾經成功，都不能證明最新交付已達成需求。通知遺失、程序重啟或未知 worker 狀態，又可能讓同一工作被重派，或讓兩個實作者同時改同一份成果。

Orca Delivery Loop MVP 要處理單一 repo、已選定 feature issue 與單一 feature PR 的交付，從新 feature 的設計與計畫，或既有 feature 的 pre-PR 交接，持續推進到有證據的 PR Pass 或可採取行動的 Blocked。Project 範圍只涵蓋 baseline／feature 引用、人工接受、相依啟動與 Retro 改善候選；完整的專案管理平台不屬於本 feature。

本文件為 2026-09-26 的 **Matt to-spec 比較草稿**。它整理已確認政策與設計候選，供比較需求表達與交接方式；測試接縫尚待確認，具體 design＋plan 的 D11 開工確認也尚未完成。

## Solution

使用者透過共同的 `orchestrate` 入口，與 Project Lead Agent、Implementer Agent 或 Reviewer Agent 直接協作。三個角色同層；Project／Feature 是工作範圍。唯一的本機 controller 依核准 plan 管理派工、版本、持久化、三 gates 與發布，agents 負責相應的需求及品質判斷。Project Lead 只有在使用者明確授權的範圍內，才能代理安排日常工作。

新 feature 先準備具穩定 AC、驗法及依賴的 design／plan，經使用者一次開工確認後依序實作。既有 feature 先唯讀查核版本、證據及原 owner，取得明確控制權交接後，只續接必要步驟。G1 核對歷史 Red 與修正的關聯、目前整合版本的 Green／regression；G1 通過後進入正式 G2 獨立 review 與 G3 必要 CI。Review／CI 問題按同一版本合併成有上限的修正批次，修正後重新驗證及覆核。

結果先保存，再發布 PR 完整 review 與原 issue 的可採取行動摘要。任何 Pass、finding closure、人工接受及恢復動作，都能追溯到適用版本和證據。三 gates 通過後交付 PR Pass package，等待人工接受；接受、實際 merge 及相依 feature 的啟動各自核對。接受後自動整理 Retro 候選，改善是否落地仍依原有權限。

以下 User Stories 的 AC 是需求驗收的可觀察目標，並非已執行測試紀錄。M13、M18、M21、M28–M32 的細部結果查核與恢復契約沿用來源設計提案作驗收細化，仍需隨 D11 的具體 design／plan 確認；格式、API 或儲存機制不因列成 AC 就成為已核准實作。Testing Decisions 區分已確認原則與待確認的測試方式。

## User Stories

1. **US-M01** — As a 使用者, I want 從同一個 orchestrate 入口準備 project、開始或接入 feature、查詢進度、恢復及提交裁決, so that 我不必在兩套交付 loop 間搬運狀態。

   **AC-M01：** 給定已選定的 repo／feature，使用者提出任一上述意圖時，回覆包含適用的 project／feature 引用、現行狀態及下一個允許動作；同一 feature 的 project 檢視與 feature 檢視引用同一 delivery run，不形成兩份可分別改動的 gate 判定。這是入口語意，不宣稱已有可用 CLI 語法。

2. **US-M02** — As a Project Lead Agent, I want 維護 project baseline、feature refs 與交付依賴, so that 每次交付都有共同契約和可辨識的需求範圍。

   **AC-M02：** 給定使用者選定的 feature，交接資料能定位其 project spec、feature spec／ticket、依賴與預期單一 PR。既有合格 baseline 可沿用；若 feature 過大，先交使用者決定拆分，不把多個獨立功能塞進本次 plan，也不新增 Project-ready 簽核 gate。

3. **US-M03** — As an Implementer Agent, I want 交接資料保留工具原生文件位置及版本, so that 我能讀到本次真正採用的契約。

   **AC-M03：** 給定規格在 issue 內文或其引用文件中，交接能讀取採用內容、實際 locator、原生檔名及 revision／digest，而不另造同義的規格或 task 檔。來源互相衝突時列出衝突與待決事項，不因修改時間較新或工具名稱而自動覆蓋。

4. **US-M04** — As a 使用者, I want 每個 AC 都有穩定 ID、情境、操作、可觀察結果與驗法, so that 我能在開工前確認要驗收什麼。

   **AC-M04：** 給定待確認的 design／plan，每項 AC 可對回 task、驗證方法及完成後的實際 evidence；尚未執行的驗法明列為計畫，不當成證據。修正程式後，原 AC 的語意及 ID 不被默默降低或重編以掩蓋缺陷。

5. **US-M05** — As a 使用者, I want 直接與任一同層角色協作並保留重要決策權, so that 角色名稱不會變成未授權的指揮鏈。

   **AC-M05：** 給定使用者直接向 Implementer 或 Reviewer 提供資訊，controller 仍核對原 plan、scope、派工權與版本。沒有明確代理授權的 Project Lead 不能批准開工、改 scope 或代替最終接受；與 Reviewer 討論也不自動形成正式 G2 結論。

6. **US-M06** — As a 使用者, I want 在每個 feature 的 design＋plan 完整時確認一次, so that 後續日常實作可以依已核准範圍進行。

   **AC-M06：** 給定尚無適用版本開工確認的 feature，系統呈現 detailed design、task 依賴、scope、task→AC、驗法及風險，且不派實作。收到明確確認後保存 actor、來源、理由及版本，再依 plan 派工；沉默或 timeout 不等於批准。範圍內正常修正不逐 task 重問批准。

7. **US-M07** — As an Implementer Agent, I want 發現 scope／spec／AC 變更、設計缺陷或需人裁決時停在正確邊界, so that 我不會自行改掉使用者要的結果。

   **AC-M07：** 給定實作或修正需要改動上述契約，run 保存問題、影響、證據與待決事項並交使用者；取得指定版本的明確裁決後才更新 design／plan 及相關驗法。新增需求保留為候選 feature，除非使用者明確決定併入目前範圍。

8. **US-M08** — As a Project Lead Agent, I want 相依 feature 的實作等到上游接受且 merge 後開始, so that 新工作不會基於尚未整合的成果。

   **AC-M08：** 給定上游僅 PR Pass，或已 accepted 但尚未 merge，下游可準備 spec／design，實作不派發並顯示等待原因。只有核對上游指定版本的人工接受、GitHub merge 事實及本次 baseline 確實包含依賴成果後，才允許相依實作；不自動 merge。

9. **US-M09** — As a 使用者, I want 既有 pre-PR feature 先唯讀查核並明確交接 owner, so that 原 session 的成果可以安全接續。

   **AC-M09：** 給定既有 session／feature，adopt 先呈現原 owner、workers、未提交變更、既有外層 loop、repo／issue／branch／head／base、規格及證據。原 owner 尚未交出派工權、仍有未知 writer、base 或必要來源不明時，保存缺口且不派競爭 writer。已有適用 D11 確認與成果就沿用，缺確認則回規劃／等待批准，不重做整個 feature。

10. **US-M10** — As an Implementer Agent, I want 既有證據缺失如實呈現, so that 接手不會把事後摘要偽裝成當時的 TDD。

    **AC-M10：** 給定 pre-PR ready 通知但缺歷史 Red 原始資料，G1 顯示 missing 及可補項目；目前重跑 Green 不能補成歷史 test-first 證據。無法取得必要歷史證據時轉交 Blocked／裁決；通知或 plan 的預期輸出均不被認作 G1 成功。

11. **US-M11** — As a controller 操作者, I want 同一 feature 只有一個有效 controller 與 writer, so that 換 run ID 或重啟不會產生競爭修改。

    **AC-M11：** 給定同一 repo＋feature 已有有效控制權，再以另一 run ID 開始或恢復不能取得第二個派工權。派工前核對實際 worktree 的 writer ownership；外部查詢失敗或 timeout 不被當作舊 worker 已停止。確認舊執行權解除後，才能派替代實作者。

12. **US-M12** — As an Implementer Agent, I want implementation tasks 依核准依賴序列執行並由單一 owner 整合, so that 最終 PR 有可核查的交付版本。

    **AC-M12：** 給定多個可派 tasks，同一 run 的實作並行度為一，依賴未滿足的 task 不被派發；可預先研究不等於授權並行寫入。各 task 的 commit／證據可追到整合版本，task 本身成功不直接產生整合 G1 或 PR Pass。

13. **US-M13** — As a controller 操作者, I want 收到可驗證的 assignment／result／evidence, so that gate 不依賴 agent 自述或通知。

    **AC-M13：** 給定完成訊息或原生 runtime message，只有核對 run／task／attempt、角色、實際 repo／head／base、採用文件版本及可讀取的 evidence 後，才能更新對應結果。測試證據含命令、環境、snapshot、時間、exit code、原始輸出及 producer；摘要、idle、input accepted 或 JSON 格式正確均不能單獨通過 gate。

14. **US-M14** — As a 使用者, I want G1 同時證明歷史 Red lineage 與目前整合版本 Green, so that 我能判斷 TDD 過程及現況都可信。

    **AC-M14：** 給定行為變更，Red 可早於最終 head，但必須追到同一 task／AC 與後續修正，且失敗原因對應該行為；無關語法或環境錯誤不算有效 Red。最終 Green／regression 必須適用目前整合 head。只有綠燈、測試總數或子 task 通過時，G1 不得被判定 passed；不要求 Red 與 Green 在同一 SHA。

15. **US-M15** — As an Implementer Agent, I want 純文件／註解變更有受覆核的 TDD N/A 路徑, so that 非行為變更能用合適檢查交付。

    **AC-M15：** 給定附理由、diff 與必要檢查的 N/A 申請，由 controller 派獨立 Reviewer 先核對 eligibility，再判整體 G1，之後才正式 G2。eligibility 接受只豁免適用範圍的 Red／Green，不豁免必要驗證、G2 或 G3；未確認時 G1 未決。設定、migration、test code 依實際行為判定，Implementer 無權自行豁免，eligibility 不算 review clean。

16. **US-M16** — As a 使用者, I want G2 由 controller 派出獨立 Reviewer assignment／session, so that 最終審查具有清楚的責任與隔離。

    **AC-M16：** 給定 G1 已通過的固定版本，正式 G2 assignment 由 controller 發出，符合既有獨立 Codex review 要求，並可核對 reviewer/session identity。Reviewer 可讀碼與隔離驗證、提交結果及 logs，但不能修改被審查 branch 或自行更新 gate。Implementer 自派的局部 review subagent 不能代替 G2；Codex 的 runtime／model 定義仍待決。

17. **US-M17** — As a Reviewer Agent, I want 依 spec／AC、design、完整 PR diff 及工程規範判斷 blocking, so that 交付品質不被執行成功訊息取代。

    **AC-M17：** 給定 reviewer task 成功執行但 verdict 為 changes required，G2 仍不通過。違反 spec／AC、可證明的正確性／安全缺陷及必要驗證缺失為 blocking；風格／命名偏好不 blocking，severity 用於排序。Reviewer 無法下結論時保留未決原因並 Blocked，不把它當 clean 或逕自啟動新一輪 correction。

18. **US-M18** — As a 使用者, I want G3 核對 GitHub 真正必要的 checks, so that agent 的 CI 摘要不會誤放行 PR。

    **AC-M18：** 給定明示且已與 repo 規則核對的 required checks，逐項核對名稱／來源、實際 source 版本、head／base 關係及目前 attempt。空集合、缺項、同名未知來源或無法核對 integration snapshot 關係時，不可推論成功。舊 success 不能蓋過目前 pending／failed；資料分頁不能讓必要項目漏查。

19. **US-M19** — As a 使用者, I want CI 非成功狀態有明確理由, so that 我能分辨等待、失敗與未知。

    **AC-M19：** 給定 required check 為 missing、pending、cancelled、timed out、unknown 或 stale，G3 不通過並指出該項理由。Skipped／neutral 只有在明確 policy 允許且能證明適用時才可接受；未決 policy 不默認成功。CIT 不納入本輪，也不新增第四個 gate。

20. **US-M20** — As a Reviewer Agent, I want head、base 或契約改變時重評證據適用性, so that 舊結論不會被移植到新交付。

    **AC-M20：** 給定已保存 review／CI／Pass 後發生新 head、base／merge-base、spec／design／AC、plan／skill／policy 變更，保留歷史並標明受影響 gate 失效原因。新 head 重新取得適用 G1 最終驗證、G2 與 G3；其他變更如沿用證據，須保存適用理由。歷史 Red 可保留 lineage，不能只改 policy 消除 blocker；需 D11 裁決的變更先回規劃／等待批准。

21. **US-M21** — As a 使用者, I want 宣告 PR Pass 前再核對真實版本, so that 我拿到的是對明確交付版本有效的品質結論。

    **AC-M21：** 給定三 gates 看似通過，Pass 轉移前再讀 PR head／base 及適用 artifacts。若觀察改變或舊結果晚到，放棄該次 Pass、reconcile 並呈現所需驗證；只有三 gates 同時適用目前版本且通過才保存 Pass、觀察時間及依據。後續 push 使當前 Pass 失效，舊 Pass 仍可追溯，不宣稱跨外部讀取具有全域原子性。

22. **US-M22** — As an Implementer Agent, I want 同版本 review 與 CI 問題合併為一批修正, so that 我不會收到互相競爭的派工。

    **AC-M22：** 給定 G1 通過，正式 G2 與 G3 可並行；正常情況收齊同版本結果才產生唯一 correction batch。Review 尚未完成而 CI 失敗時可收集診斷，除明確中止／timeout 路徑外不先派第二批修正。批次包含 findings、CI failures、scope、AC、驗法及依賴；新 head 先重過 G1，再取得最新 review／CI。

23. **US-M23** — As a Reviewer Agent, I want 每個 finding 有穩定身份和完整修正歷史, so that 改名、移動行號或換輪次不會洗掉問題。

    **AC-M23：** 給定同一語意 finding 跨修正存在，保留 stable ID、來源、blocking／severity、位置、依據、預期、狀態、fix commits 及覆核 evidence。位置相同或文字相似本身不足以自動合併問題；可追溯每次關聯判斷。Implementer 對批次內每個 finding 提交 fix submitted 或 disputed 及證據，缺回應時結果不完整。

24. **US-M24** — As a 使用者, I want blocking finding 只有經 Reviewer 覆核或明確人工裁決才能解除, so that 自述修好不會直接變成 review clean。

    **AC-M24：** 給定 Implementer 宣稱已修正、GitHub thread 被關閉或留言稱可接受，本機 JSON finding registry 仍保持原阻擋，直到 controller 匯入具有來源、actor、版本及理由的合法覆核／裁決。PR／issue 討論是證據來源及發布紀錄，不是第二套權威 finding 狀態；未解 blocking 不為零時 G2 不可通過。

25. **US-M25** — As an Implementer Agent, I want finding 反證有一次獨立覆核機會, so that 有根據的爭議可被釐清並在必要時交人。

    **AC-M25：** 給定 disputed 及可重現反證，controller 沿原 finding／batch 派獨立 Reviewer 覆核一次。仍有 blocking 爭議即 Blocked 並交使用者雙方依據，不自動換 reviewer 再試。此次釐清不另計 correction round，重啟、重複通知、換 session 或措辭不重置次數；若有新 head，先有適用 G1。Scope／spec／AC 或設計變更直接依 D11 回人。

26. **US-M26** — As a 使用者, I want 交付及修正有持久化上限, so that loop 不會無限消耗時間或靠重啟繞過限制。

    **AC-M26：** 給定同一 run，主動執行最多 4 小時、最多 3 輪 correction；每批開始派修才增加一輪，不按 finding、subagent 或 CI job 分別計輪。到限停止新派工、處理仍存活工作的執行權並保存 Blocked、已用額度及下一步。重啟、人工退回或改 run ID 不能重置預算；增加 budget 需明確人工裁決。Active time 的精確計算法及 resume 細節仍待 design 確認。

27. **US-M27** — As a controller 操作者, I want infra 失敗有界重試並先釐清外部結果, so that 暫時失敗不會變成重複副作用。

    **AC-M27：** 給定單一 infra 操作失敗，最多允許 2 次額外重試，保留原 operation 與 attempts；未知結果先 reconcile。診斷為程式／測試缺陷時回 correction 流程，不能偽裝成 infra retry。Worker／review／CI timeout 使用待核准設定，達限先核對是否已停止或安全解除執行權，不能直接重派未知 writer。

28. **US-M28** — As a controller 操作者, I want 設定與狀態是可直接閱讀的 JSON／YAML, so that 我能在沒有額外 dashboard 時檢查交付。

    **AC-M28：** 給定已開始或已停止的 run，直接閱讀保存狀態即可找到目前 phase、三 gates 的理由、blockers、版本、已用預算、待發布項目及下一步。Controller 更新狀態後，讀者取得完整舊版或完整新版，不取得半份狀態；無法解析或不相容的狀態不可被覆寫成空白新 run。具體格式分工及儲存布局仍屬設計提案。

29. **US-M29** — As a controller 操作者, I want 結果先完整保存再匯入，而且重複結果可去重, so that 通知順序不會破壞權威狀態。

    **AC-M29：** 給定結果已保存但通知遺失，resume 可核對 assignment／版本／digest／evidence 後匯入一次。相同 result 重複到達不重複更新 finding、計輪或派工；同一 attempt 的結果內容衝突時保留原件並 Blocked，不以最後寫入者覆蓋。Workers 只能交自己的結果，不能自行改 run／gate／finding authority。Implementer 與 Reviewer 的正式交手經 controller，不直接傳訊或互相呼叫；交接通知只帶已保存 result 的識別／位置，不承載權威 finding、verdict 或回應。

30. **US-M30** — As a 使用者, I want PR 有完整 review、原 issue 有可採取行動的摘要及連結, so that 我能從原工作入口追到交付問題和處置。

    **AC-M30：** 給定核對完成的 review result，先持久化，再經 outbox 發布完整 PR review 及原 issue 摘要／連結；發布紀錄能對回 run、review／result、head／base／spec 版本及 finding IDs。發文失敗保留已完成 review，只重試發布，不重做 review、不假稱已發布，也不以 GitHub 帳號能否按 approve 決定 G2 clean。

31. **US-M31** — As a controller 操作者, I want 外部寫入結果 unknown 時依 operation marker 查回, so that 我不會在恢復時重貼 review 或重派工作。

    **AC-M31：** 給定發文或派工前已保存 operation，外部成功但回應遺失時，reconcile 以原 identity／marker／receipt 查回並讀回驗證。已存在的結果不重做；查不到且無法證明可安全重試時保留 unknown／Blocked。重複通知只喚醒核對，不自行形成第二次 mutation；不宣稱本機檔案可提供跨 GitHub／Orca 的 exactly-once 保證。

32. **US-M32** — As a controller 操作者, I want crash 後恢復最小必要工作並保留診斷, so that 已完成成果不會重跑或遺失。

    **AC-M32：** 給定 controller 在保存、匯入、派工或發布邊界中斷，resume 先讀持久化 state、核對 ownership，再讀 workers／PR／artifacts／results／outbox、重評版本並續接必要步驟。通知缺失不阻止找回已保存結果；損壞或矛盾資料顯示具體錯誤及恢復條件，不默默跳過或將全部 tasks 重設 pending。精確 crash window 與 journal 修復策略在 design 中選定。

33. **US-M33** — As a 使用者, I want 執行、品質、發布、接受及整合事實分開呈現, so that 我知道每種「完成」真正代表什麼。

    **AC-M33：** 給定 review 執行成功但仍有 findings、CI 尚未完成、發文失敗或外部狀態未知，status 分別顯示執行結果、gate／verdict、publication、human acceptance 及 integration 事實。任何未知項目都不因另一維度成功而變成功；Blocked 顯示原因、證據、owner／待決事項及最小恢復條件。

34. **US-M34** — As a 使用者, I want PR Pass package 明確交回人工接受, so that 品質結論不會越過我的最終交付決定。

    **AC-M34：** 給定目前版本三 gates 通過，package 包含範圍、版本、AC 對應 evidence、findings 處置、CI 及發布狀態，並標示 ready for human acceptance。接受紀錄綁定 code／spec／design 版本；PR Pass、accepted 與 GitHub merged 分開，系統不自動 merge、close issue、release 或 deploy。新版本的人工接受重新 pending，歷史接受仍保留。

35. **US-M35** — As a 使用者, I want 驗收退回原 AC 缺陷時沿原 run 修正, so that 退回不會遺失既有 finding 或刷新修正額度。

    **AC-M35：** 給定人工驗收發現原 AC／核准設計未達成，保存被退回版本、actor、來源、時間、可重現差異及 stable finding；首次退回不需先有 accepted 紀錄。既有問題沿用 ID，重複回饋去重；當前 Pass 失效並重評相關 gates。先查原 run 剩餘預算再派修，三輪到限即 Blocked，closure 仍遵守獨立覆核或明確人工裁決。

36. **US-M36** — As a Project Lead Agent, I want 人工接受後自動整理有證據的 Retro 改善候選, so that 下一個 feature 能利用本次交付的新知。

    **AC-M36：** 給定對指定版本的人工接受事件，orchestrate 依該接受 identity／版本去重整理執行、review／CI 及人工回饋，Project Lead 彙整候選的證據、事實或假設、改善、承接者、驗法及適用版本。重啟或重複接受不重複產出；無足夠改善時不造待辦。候選不自動改 code、spec、架構或 gate policy，也不成為新增 PR gate；跨 feature 影響才提出 Replanning。

37. **US-M37** — As an Implementer Agent, I want skills 提供方法而由唯一 controller 維持外層交付, so that task 細節和 feature gates 不會由不同 loops 競爭決定。

    **AC-M37：** 給定已核准 assignment，OpenSpec 承接 spec／design／tasks，Writing Plans 方法銜接 task 計畫，Superpowers TDD 承接實作，skills 將結果及證據交回 controller。局部 task review 不取得 G2 或 Pass 權；Matt implement／implement-spec 只供參考，不啟動第二外層 loop。保留固定版本 skill refs 及 user-only 呼叫限制；自動 Retro 明示整合方法和差異，不暗中呼叫原版 user-only skill。

38. **US-M38** — As a controller 操作者, I want 核心品質契約與 runtime／model 分離, so that 替換底層工具不會改變交付承諾。

    **AC-M38：** 給定採用或變更 adapter 設定，角色、gates、assignment／result 與 ownership 契約維持，runtime 與 model 各自記錄核准設定及實際身份。Preflight 核對版本、正確 workspace／branch、工具權限、登入及結果通道；能力不足時列具體 Blocked，不默默換工具、放寬 sandbox、轉移 credentials 或降低 Reviewer 隔離。選用 opencode 或 model-only G2 均未被本規格批准。

39. **US-M39** — As a 使用者, I want fake adapter 測試與真實交付證據分開, so that 可控故障測試不會被當成端到端驗收。

    **AC-M39：** 給定驗證報告，逐項標明證據來自 fake／模擬、真實 adapter probe 或真實 feature。完整真實驗收須包含已核准目標上的有效 finding → fix → re-review、stable finding ID、兩版 head 對應及最新三 gates 證據；若未出現真實 finding，據實記 clean，不能虛構循環已驗證。現有 probe 不宣稱 controller 或完整 E2E 已完成。

40. **US-M40** — As a 使用者, I want 本次比較稿保留 trial 暫停及未決選型, so that 文件產出不會擅自接管既有工作。

    **AC-M40：** 給定本次規格生成，不啟動任何 runtime worker、PR gating 或 Retro。現有 gigaxfer pre-PR 試用依 D18 暫停；Q-TARGET 的 feature／session／版本及原 owner 仍需重查與確認。P03 已選為首次 Retro 試用對象，依 D22 等明確開始；這不等於選定 P03 PR、批准完整流程或解除原 Looper 的控制權。

## Implementation Decisions

**已確認的決策。** 以下是產品與工作流程約束，具體介面或資料布局仍由 design／plan 落實。

- **ID-M01 — 範圍與權威分工（D02、D04–D08、D17）。** 使用獨立 Orca Delivery repo；一個可獨立驗收 feature 對應一個 issue／PR，implementation tasks 是派工單位。Workflow 定義規則，controller 執行與持久化，skills 提供方法，adapters 操作工具。MVP 為 Orca lead agent＋單一本機小型持久化 controller＋Orca workers，從專用 Orca terminal 啟動與 resume；project 僅保留本稿定義的薄層。
- **ID-M02 — 同層角色及人工邊界（D11、D20、D23）。** Project Lead、Implementer、Reviewer 同層協作；只有明確授權才有 Project Lead 代理安排。Controller 擁有唯一派工及確定性核查權，不擔任 agents 的主管。每 feature 的 design＋plan 一次人工確認；契約變更、設計缺陷與未解阻擋爭議回人。
- **ID-M03 — 需求及證據交接（D01、D19）。** AC 有穩定 ID 與可觀察結果，附驗法及實際證據映射，併入 D11 確認。保留工具原生檔名、實際位置及採用內容版本；規格衝突由人決定。結果及證據要能追溯 task／attempt 與適用交付版本。
- **ID-M04 — G1（D01、D26）。** 採 Superpowers TDD，歷史 Red 追溯同一 task／修正，最終 Green／regression 適用目前整合 head。非行為 N/A 先由獨立 Reviewer 核對 eligibility，再完成 G1、進正式 G2；沒有自我豁免。
- **ID-M05 — G2／G3（D01、D09、D12、D29、D30）。** G1 通過才正式送 G2；controller 派獨立 Codex Reviewer，不能由 Implementer 的 subagent 取代，Reviewer 不改作者 branch。G2／G3 可並行；required CI 真正成功與零未解 blocking 缺一不可。Codex 的 runtime／model 定義待決，CIT 不列入本輪。
- **ID-M06 — 版本與結果維度（D01、D03、D19）。** Gate／Pass 與人工接受綁定適用版本；執行成功、review verdict、publication、acceptance、merged 為不同事實。變更時保留歷史、重評適用性，不移植舊成功。
- **ID-M07 — Finding／爭議（D09、D12、D24、D25）。** 本機 JSON registry 是 finding 權威，stable IDs 與歷史保留；解除 blocking 需 Reviewer 覆核或明確人工裁決。反證只獨立覆核一次，沿原 batch 不另計輪，仍有爭議即 Blocked。
- **ID-M08 — 預算與派工（D13）。** 實作並行度一；同版本 review／CI 結果形成修正批次，最多三輪 correction、每 infra 操作最多兩次額外 retry、每 run 主動執行最多四小時。恢復或人工退回不刷新額度；精確計時及 timeout 預設尚未核准。
- **ID-M09 — 保存與發布（D09、D14、D24）。** MVP 用人可讀 JSON／YAML 持久化；先保存結果，再透過 outbox 發布及 reconcile。PR 保存完整 review，原 issue 保存摘要／連結。通知只喚醒 controller，GitHub 討論匯入後依 closure 權限更新本機權威；發布失敗只重試發布。Runtime results／logs 不自動提交版控，分享證據另保存去敏副本；credentials 沿用既有認證，不寫入 assignment 或規格。
- **ID-M10 — 人工接受與相依啟動（D03、D27）。** 交付終點 PR Pass／ready for human acceptance，不自動 merge、close、release、deploy。下游相依實作需核對上游指定版本已接受、實際 merge 且 baseline 包含成果；等待時可準備 spec／design。
- **ID-M11 — Retro（D21、D22、D28）。** 人工接受後自動去重整理改善候選；Project Lead 彙整證據，改善落地遵守既有 scope／權限，必要才 Replanning。原版 Matt user-only 限制保留，整合方法與輸出契約須明示。P03 提前試用仍等明確開始。
- **ID-M12 — 方法及底層邊界（D07、D30、共用輸入的後續確認）。** OpenSpec 管 spec／design／tasks，Writing Plans 方法銜接 tasks，Superpowers TDD 管實作，自有 orchestrate＋唯一 controller 管外層。Matt 釐清／domain 方法按需使用，implement／implement-spec 不直接啟動外層 loop。Runtime 與 model 分開設定，由 adapter 接入；具體選型及能力實證未完成。

**供 D11 審議的設計建議，尚非核准實作。** 它們說明如何可能滿足上述行為，不是額外 gates；名稱、schema 與枚舉也不是已存在 API。

- **IP-M01 — 模組接縫。** 以入口 router、controller 核心、檔案 store／finding registry／outbox，以及 Orca、git、GitHub／CI adapters 分工。公開 start／adopt／status／resume／decision 操作提供主要驗證入口；具體語言及函式介面未定。本機 Python CLI 是來源中的候選。
- **IP-M02 — 檔案一致性。** 建議 YAML 保存設定，排版 JSON 保存 run／assignment／result，JSONL 保存事件；run snapshot 集中同一 run 的可變權威，project 只引用 run identity／revision。單一 writer、repo＋feature 控制鎖及實際 worktree lease 配合完整 snapshot 的 flush／atomic replace；不可覆寫的 evidence 先保存再引用。鎖、檔案布局及平台 durability 需實測。
- **IP-M03 — 恢復設計。** 建議 snapshot 帶 pending history，event IDs 去重；尾筆中斷保留診斷後恢復，中段損壞／同 ID 衝突停為 Blocked。外部 operation 在 mutation 前保存 identity、payload digest、marker，完成後保存 receipt／read-back；不能由此宣稱外部 exactly-once。跨 project／run 恢復先 reconcile run，再更新 project refs。
- **IP-M04 — 結構化契約。** 建議 assignments 明列 schema／run／task／attempt／角色、核准 runtime／model、repo／worktree／branch、issue／PR、版本、scope／tools、依賴、AC、skill refs、結果位置與 budget；results 回實際 identity／版本、execution status、verdict／findings、evidence 及待決事項。原生 messages 可由 adapter 捕捉保存原文與來源 digest，不授予通知權威或偽造 native completion。
- **IP-M05 — 計時與 timeout。** 來源建議以 worker、CI wait 及 controller 交付操作的 wall-clock 聯集計 active time，等待人時暫停但存活 worker 繼續計，crash unknown interval 保守計入；worker／review／CI 的 45／30／30 分只是未核准預設。精確算法、恢復語意及 budget extension 操作要在 design／plan 明確呈現，不由本稿拍板。
- **IP-M06 — Retro 輸出。** 來源建議首輪有據時選一至三項改善，列來源、原因、owner、驗法與落地版本；具體 scorecard schema／skill 包裝未定。候選數量不構成驗收 gate，也不要求沒有改善時產出形式性待辦。

## Testing Decisions

**已確認的驗證原則與必要行為。** 測試驗證公開可觀察行為：適用版本的狀態、實際派工、發布內容／次數、保存證據及重新啟動後的結果。不能只測 enum、重述實作步驟、依 agent 摘要判定，或為測試新增 production hooks。預期有根據的 Red／Green 過程、integration regression、獨立 review，以及真實 finding → fix → re-review；缺證據時如實失敗或列未涵蓋，不放寬斷言、加 sleep／retry 掩蓋問題或排除 flaky 測試。

**待使用者確認的主要測試接縫。** 建議從 controller 公開 start／adopt／status／resume／decision 操作進入，以可控制的 fake agent、GitHub、CI adapters 和正式時間依賴製造版本變更、遺失／重複通知、crash 及未知結果，觀察狀態、派工及發布。這是最高層的共同接縫提案，尚未成為已確認 Testing Decision；具體 public API、adapter 注入方式與故障注入位置須進 design／plan。若實作後需要補較低層測試，應由無法在此層觀察的契約缺口說明，不預先建立大量私有方法測試。

**覆蓋計畫，尚未執行。** 下表是 AC→驗法→預期 evidence 的草案；fake 測試不能代替真實 adapter 與完整交付驗收。

| 待驗範圍 | AC | 建議操作與應保存的可觀察證據 |
| --- | --- | --- |
| 共同入口、project refs、角色、開工確認 | M01–M07 | 用同一 feature 經各入口讀取、嘗試未批准派工、提交指定版本裁決；保存狀態輸出、artifact refs、拒絕／允許的派工紀錄，證明 scope 變更回人 |
| 相依啟動與 adopt／ownership | M08–M12 | 分別提供 accepted 未 merge、錯 baseline、未知 writer、缺 D11／缺 Red，再補齊合法證據；保存等待原因及實際 dispatch 次數，驗證只接續必要步驟且實作並行度一 |
| 結果證據、G1、N/A | M13–M15 | 提供僅摘要、無效 Red、有效歷史 Red＋當前 Green、舊 Green、未確認及接受的 N/A；保存 G1 理由、evidence refs、eligibility assignment 與正式 G2 先後關係 |
| Reviewer 獨立、G2 blocking 分類 | M16–M17、M24 | 提供 controller／Implementer 各自建立的 review、changes required、風格建議、必要驗證缺失及非授權 closure；保存 gate 結果、角色 identity、finding 歷史。真實隔離另驗所有可用工具不能修改作者 branch |
| Required CI、版本適用與 final Pass | M18–M21 | 控制缺項、分頁、來源不符、舊 success／新 pending、各非成功狀態、integration SHA 關聯；在 Pass 前改 head／base／artifact，保存逐 check 理由、失效及 reconciliation 結果 |
| 批次、穩定 finding、closure／爭議 | M22–M25 | 讓 review／CI 以不同順序完成、逐 finding 提交 fix 或反證、移動位置、重送相同結果並重啟；保存 batch／round、stable IDs、覆核次數、缺回應及未解爭議的 Blocked |
| 預算、infra retries、狀態維度 | M26–M27、M33 | 使用待核准計時契約的可控制時間，測三輪修正、兩次額外 infra retry、四小時到限與重啟；保存已用額度、停止新派工及 unknown writer 處理。精確時間斷言待算法確認 |
| 持久化、通知、外部 unknown 與 crash | M28–M32 | 在保存／replace／匯入／mutation／receipt 邊界控制中斷，重送相同及衝突 result，模擬外部成功但失回應、損壞狀態及雙 controller；保存重啟後狀態、實際副作用次數、read-back 及錯誤診斷。細部 journal cases 依選定設計補入 |
| 人工接受、退回、Retro | M34–M36 | 對同版本接受／退回、新 head、重複接受事件操作；保存 acceptance 歷史、同 run finding／預算、候選產出次數及沒有自動 merge／改規範的外部操作紀錄 |
| Skills／runtime／真實接入 | M37–M40 | Dry run 檢查結果回到唯一 controller、skill refs 及限制；真實測 requested／actual runtime/model、workspace、native lifecycle、權限與發布 read-back。恢復試用另需目標及 owner 確認 |

**被驗證的模組。** 主要觀察 controller 的派工／gate／finding／budget 行為、檔案 store 與 outbox 的跨重啟行為、入口及 project refs 的交接；runtime／GitHub／CI adapters 另做真實 integration 驗證。Reviewer 的實際隔離與 native completion 不能由 fake adapter 測試聲稱成立。

**Prior art 與目前限制。** 指定 baseline 明確表示 controller 尚未實作，沒有可引用為已通過的 controller test suite。既有 2026-09-25 probes 提供 Claude 的 dispatch、artifact、native completion 及 release 證據；Codex 只有可讀取的 blocked artifact，native completion 未通。後續狹窄 socket 查詢證明 utility 連線，沒有證明真正 TUI worker 的完成或所有工具隔離；新 repo workspace discovery 也仍有缺口。這些可作 adapter 驗證案例的來源，不能當成 G1／G2／G3 或本 feature 的 E2E。

真實 feature 驗收須在恢復試用、選定目標及完成交接後，另外保存真實 finding→fix→re-review、最新版本三 gates、PR／issue 發布及至少一次遺失通知或重啟恢復的證據。目前沒有這些執行成果。

## Out of Scope

- 實作本比較稿、建立 implementation tasks／tickets、發布 issue／PR、套用 ready-for-agent label，或把草稿視為 D11 開工批准。
- 多 repo swarm、分散式／多主機 writers、新 dashboard、全面 workflow framework，或完整 mission／research／roadmap／scaffolding 平台；本次 project 只交付 Solution 所列薄層。
- 自動 merge、close issue、release、deploy，新增 CIT gate，或把 Retro、發布狀態及 Project-ready 變成額外品質 gates。
- 並行 implementation writers、自動擴張 scope、降低 AC、覆蓋 finding 歷史，或以換 run／session／reviewer 重置預算與爭議次數。
- 替第三方 runtime 決定內部儲存技術、默認採用 opencode／model-only G2、用強權限繞過 native completion 或 Reviewer 隔離缺口。
- 自動維護 OpenSpec 與 Matt 兩套正式 authoring workflows；這次 Matt 文件僅為比較候選，不撤回已確認的工具組合。
- 恢復 gigaxfer PR gating 試用、啟動 P03 Retro、選定 P03 PR，或接管原 session／Looper。
- 聲稱精確美元硬上限、shared-network filesystem durability 或尚未執行的真實 E2E 已通過。

## Further Notes

- **草稿及方法狀態。** 本稿保留 to-spec 原生七節格式及長編號 User Stories；主要測試接縫仍是待確認提案。原版要求先確認 seams 再完成 spec 並發布；本次依比較範圍先交草稿、不發布，沒有完成原版完整流程。成為可執行規格前需確認接縫與具體 design／plan；發布若要進行也需另有明確任務，不能由本稿推定。
- **已確認選擇。** 正式工作流程仍以 OpenSpec 的 spec／design／tasks、Writing Plans 方法、Superpowers TDD 及自有 orchestrate＋唯一 controller 組合為準。Matt 釐清／domain 方法按需使用，implement／implement-spec 不啟動外層 loop。
- **待定 execution design。** 需選定 controller 語言、public API、檔案／鎖／durability 細節、runtime adapters、G2 Codex 的 runtime／model 定義及可驗證隔離。不得從 runtime 名稱推定實際 model，或從可替換性推論已符合 G2。
- **待定政策實例。** Repo-specific required checks／來源、skipped／neutral 的明確接受政策、worker／review／CI timeout、active time 計算法及 budget resume 操作，應在具體 design／plan 呈現。45／30／30 分 timeout、wall-clock 聯集算法及 Python CLI 都是候選，並未批准。
- **待取得的能力證據。** 真正 Codex native completion、Reviewer 全工具隔離、正確新 repo workspace／worktree placement、真實發布 read-back 及跨重啟接續，仍需有界實證。環境不足應保存限制及恢復條件，不把另一角色的成功 probe 當成通過。
- **Trial 狀態。** D18 PR 試用維持暫緩；Q-TARGET 未回答，恢復前重查 feature／session／head／base／證據及控制權。D22 選定 P03 作首次 Retro 試用不等於開始，屆時只回顧實際已完成階段。
- **可追溯性。** 每一 AC 的來源、原生 skill 內容識別、共用快照驗證與本次方法偏離另記在配套 author notes；本 spec 不嵌入具體程式路徑或 code snippets。所有驗法在此都是計畫，沒有宣稱已存在 controller、測試或完整交付成果。
