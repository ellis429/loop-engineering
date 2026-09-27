# D41／D42 與 Herdr：範圍收斂對照

日期：2026-09-27。狀態：**對照與修訂建議，非新規格核准、非實作完成或 finding closure**。

本文件對照工作目錄中的最新 D41／D42／Herdr 草案與 D40 的 88 項 AC、S1 17 項 blocking findings。它是正式 OpenSpec 修訂的輸入，不建立另一份可派工 plan／spec。使用者已確認 example 採 OpenCode＋Herdr 的方向（D43）；H-CHOICE 已依 D45 選定 Herdr 原生＋薄 controller；D46 要求在隔離目錄／worktree 重建。

> **2026-09-27 政策更新**：D47–D49 已確認離線 4h 行為、可信本機協作的信任邊界，以及本 repo 可採人工核准的版控 CI checks 政策。下表原「待確認」措辭屬政策確認前的差異盤點；具體新版設計及 checks 集合仍待審閱。最新候選見 [設計閱讀入口](/Users/johnson.chiang/workspace/loop-engineering-thin/docs/design-candidate/d45-02/README.md)，本表不因此成為實作或 finding closure 證據。

> **D50 接續**：六項精簡方向已確認，D45-02 原 H1 計畫進入修訂。下表是歷史需求對照；[新版候選](/Users/johnson.chiang/workspace/loop-engineering-thin/docs/design-candidate/d45-03/README.md) 已明示 first slice／後續切片，以及 controller／skill／人工 owner，不能以延期冒充已覆蓋。

## 目前基準與適用範圍

- 本 repo 為 `loop-engineering`，舊 `orca-delivery` 路徑為相容 symlink。
- 工作 branch `delivery/s1-controller-core`，HEAD `4ce111011fde83c3a2784402cea111e52a954b3c`。本輪採用未提交的 D41／D42 與 Herdr／目錄重整文件，不只讀 HEAD。
- 舊 PR #2 仍 open；舊程式、測試、approval 與 review 是其版本的基準，沒有因文件重整而封存或通過。
- S1 review 原始 verdict `changes_required`，17 項 open blockers；result SHA-256 `bba92f8b9f5f1a8c66a3488d16ee790b06e8490393c5e5670e466edb5c7f9a63`。原件由 `.delivery/bootstrap/bootstrap-s1-20260927/latest.json` 指向的 snapshot 保存，GitHub 發布見 PR #2／issue #1。
- 下表「保留／移交／替換」是新責任分配建議；沒有任何列等於已修復／已驗收。舊 R01–R17 一律仍 open，需適用的新程式、證據與獨立覆核才能解除。

## 新邊界：一個外層 loop，一份品質狀態

| 責任 | 已確認方向／修訂建議 | 不得推論 |
| --- | --- | --- |
| 需求與方法 | 人＋Project Lead／Implementer／Reviewer，沿 Project／Feature workflow 及原生 skills | 不因共同入口而取得相同裁決權 |
| 正常交付循環 | Orchestrate 協調 agent 呼叫工具、等待、收結果、派修；同 feature 一個 active owner | 不是 controller 內另起常駐 supervisor，也不加入第三方第二個外層 loop |
| 品質與交接判定 | 薄 controller 核對身份、版本、證據、findings、budget、允許動作 | 不執行 worker 任意 argv、不以 JSON 自述證明真實測試或身份 |
| 執行與工作空間 | 借用 runtime／git；Herdr 是待驗的 desktop 接合提案 | Worktree／clone／prompt 約束不是完整工具隔離證據 |
| 中斷處理 | 保存 pending identity，查回已有結果；不明就 Blocked／人工接管 | 不承諾全自動復原，也不把 unknown 當作可重試 |

**保留品質要求，不保留每一項舊機制。** 例如移除自建 sandbox 不等於允許 Reviewer 修改作者 branch；能力改由既有 runtime 證明，證明不了仍是缺口。移除 runner 不等於接受「已測試」文字，原始 log／版本／身份仍須核對。

## 正式 artifacts 的修訂提案

以下是每個既有 artifact 應修改的範圍；正式檔案尚未套用這輪改寫。

| Artifact | 擬議修改 | 保留的來源／限制 |
| --- | --- | --- |
| proposal | 修正「沒有程式／尚待 design」的過期敘述；把 controller 實際派工改為 orchestrate 呼叫工具，說明 Herdr 候選與遷移影響 | 動機、四個 capability、三 gates、D11、OpenCode 預設、無自動 merge 維持 |
| specs（四份） | 88 個 AC ID 不刪除；明確寫執行者移交，標出需要裁決的可靠性／信任邊界，而非追加互相矛盾的 override 段 | 尚未批准的範圍縮減不能直接成為 SHALL；H2 未驗項目不標完成 |
| design | 由指定 Implementer 沿新邊界完成單一權威狀態、窄 CLI、operation/result、工具接法及停止／恢復設計 | 不直接採用未覆核的 thin-design 候選；精確 API／檔案配置須先處理下方設計缺口 |
| tasks | 在新版 design 可執行後重排 H0／H1／H2；每項有依賴、scope、AC、驗法與 evidence | 舊已勾 tasks 保存在版本／快照，不移植為新版完成狀態；H3 只作後續 roadmap，不混入第一切片 |
| validation（配套文件） | AC → 方法／環境／通過標準／證據位置依新責任更新；fake／native／E2E 分列 | 舊 227 tests、CI 與 review 只證明其歷史版本，不能複製為新版 Pass |

`approval.json`、歷史 review 原件及證據封存維持原樣；新版文件採用與 D11 開工確認是不同事件。OpenSpec 的 planning complete 只表示檔案存在，不是新 scope 可開工。

## 88 項 AC 對照

「移交」表示執行責任由 controller 轉給 orchestrate／既有工具，controller 仍驗證相同品質條件。「能力待證」表示需要真實 profile／環境證據；「待確認」是對原先承諾的可見差異，不能由此表自行批准。

### delivery-gates

| AC／原情境 | 處理 | 主要責任 | 新接法必須驗證的行為 |
| --- | --- | --- | --- |
| AC-G01 正常交付 | 保留 | controller | G1 先於正式 G2；同版本三 gates 均成功且必要發布完成才可 Pass。 |
| AC-G02 單一 gate 失敗 | 保留 | controller | 任一 gate fail 阻止 Pass；review／CI 不互相取代。 |
| AC-G03 Review 執行成功但無法裁決 | 保留 | controller | 執行 succeeded＋verdict blocked 保持 unknown，不消耗程式修正輪。 |
| AC-G04 摘要與證據不一致 | 保留 | controller＋Reviewer | 逐項核對 log、stdout/stderr digest、exit、身份、snapshot；摘要不夠。 |
| AC-G05 驗證與程式分離引用 | 移交 | 工具捕捉＋controller | 程式與 evidence 分別綁定版本，不要求文件 commit 自我引用。 |
| AC-G06 不同 SHA 的有效 Red 與 Green | 保留 | controller＋Reviewer | 歷史 Red 可早於 H，需同 task／修正 lineage；Green／regression 適用 H。 |
| AC-G07 缺歷史或錯誤的 Red | 保留 | controller＋Reviewer | 環境錯誤、事後 replay 或缺歷史 Red 均不能冒充 test-first。 |
| AC-G08 整合回歸失敗 | 移交 | Implementer／驗證工具＋controller | 整合 H 的 regression 失敗必須拒絕 G1，即使各 task 測試成功。 |
| AC-G09 純文件 N/A 通過 | 保留 | 獨立 Reviewer＋controller | 固定 diff 的 N/A eligibility 先驗身份／model／權限再免除適用 TDD。 |
| AC-G10 行為變更或待核對的 N/A | 保留 | controller | 行為設定與未完成 eligibility 不可自我豁免。 |
| AC-G11 有效獨立 review | 移交／能力待證 | orchestrate＋runtime＋controller | 真實獨立 session、核准 model、完整 diff 與 findings 覆核證據可核對。 |
| AC-G12 局部 review 或隔離無法證明 | 移交／能力待證 | runtime 權限＋controller | 驗證所有可用工具邊界；prompt／clone／pane 名稱不能證明隔離。 |
| AC-G13 非成功 check 與空集合 | 保留 | GitHub 查詢＋controller | 空集合、unknown policy、缺項及非成功不通過；例外僅核准 skipped／neutral。 |
| AC-G14 舊成功不能蓋過新 attempt | 保留 | GitHub 查詢＋controller | 完整分頁、可信 app/context、目前 attempt；舊 success 不蓋過新 pending。 |
| AC-G15 衍生整合 snapshot | 保留 | GitHub／git＋controller | CI merge snapshot 有可核對 head/base 映射才可採用。 |
| AC-G16 舊結果晚到 | 保留 | controller | 晚到 H1 只入歷史，不解除 H2 的 gates／findings／budget。 |
| AC-G17 Base 或規格改變 | 保留 | controller＋Reviewer | base／規格變更重新判適用性，不默默沿用舊 clean。 |
| AC-G18 Pass 前後發生 push | 移交 | 工具重新觀察＋controller | Pass 前讀回版本與必要 checks；任何差異取消本次判定，不用快取有效期代替。 |
| AC-G19 模擬通過但 adapter 缺證據 | 保留 | 驗收報告 | fake、真實能力、完整 E2E 分列；OpenCode／Herdr 缺項不能借用其他接法證據。 |
| AC-G20 真實 review 沒有 finding | 保留 | Reviewer＋驗收報告 | 沒有成立 finding 就標該展示未覆蓋，不造 blocker；完整 demo 尚未完成。 |

### delivery-orchestration

| AC／原情境 | 處理 | 主要責任 | 新接法必須驗證的行為 |
| --- | --- | --- | --- |
| AC-O01 直接與 Implementer 協作 | 保留 | orchestrate／人 | 直接交付 feature 可準備 design；沒有 D11 不得派實作。 |
| AC-O02 拒絕第二個外層 loop | 移交 | orchestrate＋controller | 同 feature 另一協調者遭拒；局部 review 不更新 G2。 |
| AC-O18 授權 Project Lead 協調與委派 | 移交 | Project Lead／人＋orchestrate | 明確授權可提出委派，controller 核對後由工具執行，仍需 D11。 |
| AC-O19 入口與 runtime 關係不授予決策權 | 保留 | orchestrate＋controller | runtime 的父子顯示不新增角色權限或替代 reviewer 獨立性。 |
| AC-O03 引用既有文件 | 保留 | controller | 原生檔名可引用，snapshot／digest 可核對；不另造 spec。 |
| AC-O04 權威來源衝突 | 保留 | 角色 agent＋人 | 衝突有來源與版本；語意不明不派工，controller 不替人選需求。 |
| AC-O05 新 feature 尚未批准 | 保留 | controller | 缺適用批准時所有實作 prepare／dispatch 路徑均被拒。 |
| AC-O06 核准後按 plan 前進 | 移交 | controller 核准、orchestrate 派工 | 使用真實 approve_plan 入口後可取得第一個合法 assignment。 |
| AC-O07 需求變更不混入修正 | 保留 | controller＋Project Lead／人 | scope_change 保存影響並使舊批准失效，不 crash、不偷偷修改 AC。 |
| AC-O08 已實作 pre-PR 接入 | 保留／切片待排 | orchestrate＋controller | 既有成果接入從 G1 開始；H2 若只驗新 feature，不宣稱 adopt 已完成。 |
| AC-O09 Adopt 缺口 | 保留 | controller | 缺歷史 Red／批准／base 或有未知 writer，不能以 adopt 略過。 |
| AC-O10 Pass 尚未接受或 merge | 保留 | controller＋人 | Pass、accepted、merged 分欄，無自動 merge／關票。 |
| AC-O11 接受後的新版本 | 保留 | controller | V2 不繼承 V1 acceptance；保存 V1 歷史與失效原因。 |
| AC-O12 上游 accepted 但未 merge | 保留至 Q-STACK 決定 | controller | 上游未 merge 時不派依賴實作；stack 目標不是現行豁免。 |
| AC-O13 Merge 與 baseline 都適用 | 保留至 Q-STACK 決定 | controller＋GitHub 查詢 | 核對 accepted、merged 與 adopted baseline 三者，再套自身 D11。 |
| AC-O14 重複接受事件 | 移交 | orchestrate／Project Lead＋controller | 同 acceptance identity 只登記一次 Retro，缺證據如實列明。 |
| AC-O15 暫停的 P03 試用 | 保留 | orchestrate | 不因本次文件收斂啟動 gigaxfer／P03／cross-node 專案。 |
| AC-O16 Skills 交回 controller | 移交 | orchestrate＋controller | skills 交回 result；只有 orchestrate 維持外層 loop，user-only 不隱式呼叫。 |
| AC-O17 另一 repo 的規則混入草稿 | 保留 | 角色 agent＋controller | 外 repo 規則必須有適用來源，不能由 cwd 自動升為政策。 |
| AC-O20 從 project 分析拆出 features | 保留 | Project Lead | Project baseline 能追到研究、domain、高層設計與 milestones／features。 |
| AC-O21 單一 feature 的聚焦分析與交接 | 保留 | Project Lead | Feature 聚焦差異、引用適用 baseline；重要未知回人。 |
| AC-O22 Project Lead 提供初步 tasks | 保留 | Implementer＋人 | 任務草案經校準後只有一份執行 plan，D11 綁定具體版本。 |
| AC-O23 詳細設計發現跨 feature 影響 | 保留 | Implementer→Project Lead／人 | 跨 feature／AC 影響留痕，未受影響工作依原批准繼續。 |
| AC-O24 專案與功能的分析深度 | 保留 | Project Lead | Project 與 feature SA 深度不同，後者可追溯 baseline 與 AC。 |
| AC-O25 文件齊全但需求仍有阻擋 | 保留 | Project Lead／人 | 模板填滿但核心歧義未解，不得標 SA ready。 |
| AC-O26 適用 SA 確認與開工確認分開 | 保留 | Project Lead＋controller | SA ready 的確認不可當作 design＋plan 開工批准。 |
| AC-O27 研究發現與使用者描述衝突 | 保留 | Project Lead／人 | 現況與需求衝突分開；prototype／環境修改另核授權。 |
| AC-O28 功能驗收與業務成果分開 | 保留 | Project Lead／Reviewer | 功能符合 AC 與業務改善量測分開，不捏造量化成果。 |

### durable-delivery

| AC／原情境 | 處理 | 主要責任 | 新接法必須驗證的行為 |
| --- | --- | --- | --- |
| AC-D01 直接檢視狀態 | 保留 | controller | 人可讀單一現行 JSON 狀態；project 只引用，不複製 gate authority。 |
| AC-D02 手動修改不是決策 | 保留／信任邊界待定 | controller | gate 從證據重算、decision 留來源；不承諾可抵抗有同等主機權限者整套偽造。 |
| AC-D03 兩個 run 搶同一 feature | 移交／設計待定 | orchestrate owner＋controller | 同 repo＋feature 不同 run 也不能取得第二個許可；鎖與 budget 必須同一權威。 |
| AC-D04 Worker 狀態 unknown | 保留 | orchestrate＋runtime＋controller | unknown 不等於 stopped；停止證據不明即 Blocked，禁止競爭 writer。 |
| AC-D05 結果未符合派工 | 保留 | controller | assignment／result ID、scope、實際 cwd／版本不符保留原件但拒絕採用。 |
| AC-D06 只有原生 assistant message | 移交 | runtime 讀回工具＋controller | 保留原生 session/message 與 digest；assistant 訊息不冒充 task completion。 |
| AC-D07 結果存在但通知遺失 | 移交 | orchestrate reconcile＋controller | 漏通知／重啟後已保存 result 可匯入一次，不重派 task。 |
| AC-D08 重複與衝突結果 | 保留 | controller | 同 ID 同 bytes 無副作用；不同 bytes 保存衝突且 Blocked。 |
| AC-D09 State 提交前後 crash | 保留／承諾收斂 | controller | 本機中斷後只有完整舊／新 JSON；保留登記與 evidence，不承諾任意斷電或共享磁碟。 |
| AC-D10 歷史尚未完成 | 替換機制／待確認 | controller | revision snapshot 取代事件重放候選；事件同 ID 衝突仍拒絕，歷史缺口停止或可證補齊。 |
| AC-D11 無法信任的 state | 保留 | controller | 缺失／損壞／未知 schema 不能建立空 run 或重置 budget。 |
| AC-D12 發文成功但回應遺失 | 移交 | orchestrate＋GitHub 工具 | 依既有 marker 查回已發布內容，保存 receipt；不可重做 review 或重貼。 |
| AC-D13 Unknown 無法安全重試 | 保留 | controller 核對＋orchestrate | 不知道有無執行就 Blocked；沒有 marker 不是安全重試證明。 |
| AC-D14 Controller restart | 移交／承諾收斂 | orchestrate resume＋controller | 已完成結果沿用；無法確認 clone／worker／owner 的部分停下交人，不承諾全自動修復。 |
| AC-D15 恢復時版本已改 | 保留 | controller＋外部觀察 | 恢復先比對 head/base/spec，再失效 gates／acceptance，不沿用舊 Pass。 |
| AC-D16 Infra retry 用盡 | 保留 | controller＋單次工具呼叫 | 同操作最多初次＋2次重試，create／query 等不能在 helper 偷重試；用盡 Blocked。 |
| AC-D17 Active budget 到限與恢復 | 保留／計時接法待定 | orchestrate／runtime＋controller | 等待 worker／CI 也計時；換 session/run 不歸零；非長駐 controller 的到限停止能力需 probe。 |
| AC-D18 正確 workspace 與設定 | 移交 | Herdr／runtime 工具＋controller | requested 與 observed placement/model 不符即拒絕；input accepted 不是派工完成。 |
| AC-D19 能力缺口與替換 | 保留 | preflight＋controller | 能力不足回報最小缺口，不自動換 profile、放權或把研究當實證。 |
| AC-D20 僅有 OpenCode 的部署 | 保留／實測待排 | OpenCode 接法 | 保留公司只有 OpenCode 的路徑；Herdr 不應新增成所有環境的硬依賴。 |
| AC-D21 Runtime 身份不取代共用身份 | 保留 | transport 轉接＋controller | 共用 run/task/attempt 與外部 handle 分欄，不能為另一 runtime 偽造原生 IDs。 |
| AC-D22 兩種接法分別驗證 | 保留 | 各接法驗收 | Herdr／OpenCode-only／Orca 各自留證；未選用的不要求開發，不能共用通過標記。 |
| AC-D23 未選用的接入故障 | 保留 | profile preflight | 未選用工具缺失不阻斷本 profile，也不默默 fallback。 |
| AC-D24 同一 runtime 的不同角色與模型 | 保留／能力待證 | runtime＋controller | 同 OpenCode 不同角色可用不同核准模型；獨立性仍須身份與工具能力證據。 |

### finding-resolution

| AC／原情境 | 處理 | 主要責任 | 新接法必須驗證的行為 |
| --- | --- | --- | --- |
| AC-F01 分類 review 意見 | 保留 | Reviewer＋controller | 問題依 spec／正確性／驗證分類 blocking；severity 不自動代替政策。 |
| AC-F02 保持 identity | 保留 | Reviewer 匹配＋controller | 同問題維持 stable ID；controller 不以文字相似自行合併。 |
| AC-F03 修正尚未覆核 | 保留 | controller | fix_submitted 或 GitHub thread resolved 都不能解除 blocker。 |
| AC-F04 有證據解除 | 保留 | 獨立 Reviewer／人＋controller | closure 帶來源、版本與 evidence，仍需其餘 G2 條件成立。 |
| AC-F05 CI 先失敗仍收齊 review | 移交 | orchestrate＋controller | 同版本 review／CI 收齊才派一批修正；等待／timeout 有明確路由。 |
| AC-F06 完整回應批次 | 保留 | controller | batch 每項 finding 都有 fix_submitted／disputed 回應，缺項拒絕完整完成。 |
| AC-F07 三輪已用完 | 保留 | controller | 三輪用完拒絕第四輪；換 run 不重置，有新裁決才可調整。 |
| AC-F08 Reviewer 接受反證 | 移交 | orchestrate＋獨立 Reviewer | 一次反證覆核接受後依 finding 權限解除，計數不當作新修正輪。 |
| AC-F09 爭議仍在或重送 | 保留 | controller | 爭議仍在交人；重送／restart 不再抽一次結論。 |
| AC-F10 反證伴隨新 head | 保留 | controller＋orchestrate | 反證伴隨新 head 先重驗 G1，再覆核及 CI。 |
| AC-F11 首次驗收退回 | 保留 | 人＋controller | 尚未 accepted 也可退回原 AC 缺陷，失效 Pass，沿同一 budget。 |
| AC-F12 新需求或規格錯誤 | 保留 | Project Lead／人 | 新需求或錯誤 spec 回規劃，不改 AC 來掩飾失敗。 |
| AC-F13 完整 review 與摘要 | 移交 | orchestrate＋GitHub 工具 | PR 完整 review、issue 行動摘要與連結均可查回同一 result／版本。 |
| AC-F14 發文失敗 | 保留 | controller＋orchestrate | 發文失敗保存 review；只處理原 publication，unknown 不盲重貼。 |
| AC-F15 連續修正仍留下同一 blocker | 保留 | Reviewer＋controller | 連續相同 blocker 達既定門檻提前 Blocked，不只等三輪耗盡。 |
| AC-F16 已解除的 blocker 再次出現 | 保留 | Reviewer＋controller | resolved 再出現時沿 ID reopen、保留舊 closure 歷史並阻擋新版本。 |

## S1 17 項 findings：遷移不能代替覆核

前五項涉及要替換的執行／恢復機制；其安全或一致性要求仍保留。後十二項直接涉及正常流程、品質與交接，薄 controller 仍須修正或證明新的路徑正確。

| Finding（均仍 open） | 處理方向 | 原問題 | 新責任／解法方向 | 解除前所需的驗證 |
| --- | --- | --- | --- | --- |
| S1-R01 | 替換執行路徑 | Controller 執行 worker 提供的 Red argv | controller 不執行 argv／測試；既有工具依核准命令及 runtime 權限捕捉證據，再交 controller 核對。 | 惡意 result argv 不會被 controller 執行；測試工具的允許／拒絕範圍另留真實 probe。 |
| S1-R02 | 替換恢復路徑、保留上限 | Session-create 的 recovery 可越過重試上限 | 單次工具呼叫返回 receipt；controller 計同操作全部嘗試，unknown 交查回／Blocked。 | create／查詢連續失敗最多允許範圍內嘗試，無 helper 內部遞迴重試。 |
| S1-R03 | 替換歷史機制、保留衝突拒絕 | 同 event ID 不同內容被覆蓋 | 提議縮為 revision snapshots＋明確 operation/result identity，不引入第二份事件 authority。 | 相同 identity 不同內容必須保留衝突；讀入舊 history 不能靜默抹去其中一份。 |
| S1-R04 | 替換提交機制、保留可追溯性 | State 已提交但 transition history 遺失 | 現行提交保存完整 transition ID／內容；history 不作第二個判定來源。 | 在 state/history 邊界中斷仍可識別變更；無法補齊則顯示缺口，不捏造完整歷程。 |
| S1-R05 | 移交 workspace 操作、收斂恢復承諾 | Clone 存在但未登記時無法續行 | 先登記 worktree/clone operation，再交工具執行；已存在查回身份，未知就人工接管。 | 中斷後不重建競爭 checkout、不吞錯；確定匹配才採用，不確定回報具體接管資訊。 |
| S1-R06 | 保留核心修正 | Binding digest 被誤認為 blob reference | 文件版本 digest、檔案 locator 與 evidence reference 明確分型。 | 使用真正 sha256 值走 start／record／inspect 完整入口，不以 P1 等 placeholder 掩蓋。 |
| S1-R07 | 保留核心修正 | approve_plan 後仍無法派工 | 校準者與 plan provenance 保存在 plan；approval 只引用適用版本，不能覆蓋丟失來源。 | 從未批准開始，輸入可核對人工批准，再取得第一份合法 assignment。 |
| S1-R08 | 保留核心修正 | 更換 run 可重置 feature budget | 同 repo＋feature 保留單一權威 owner／budget；resume/adopt 不另建零預算。 | 四小時／三輪耗盡後，新 session/run 仍被拒；舊 state 不可讀就 Blocked。 |
| S1-R09 | 保留要求、執行能力待證 | Worker／CI 等待期間不執行預算限制 | 計時涵蓋活躍等待；orchestrate 在有界觀察中檢查，工具提供可核對停止能力。 | 等待跨限不得繼續派工；離線期間是否可到時停止需真實 probe，不能用下一次 CLI 才發現冒充硬時限。 |
| S1-R10 | 保留核心修正 | scope_change 對正常 state crash | 初始 schema 與 decision 路徑一致，保留提案及待批准版本。 | 從公開建立入口執行 scope_change，不 crash，舊批准不能用於新 scope。 |
| S1-R11 | 保留核心修正 | Adopt 使用空 tasks 集合繞過 G1 | 驗完整核准 task／AC 集合，不只驗本次建立的 integration entries。 | 已實作 adopt＋缺 Red 不得 Pass；若 H2 不含 adopt，須列未驗，不關此 finding。 |
| S1-R12 | 保留交接修正 | Fix／re-review 缺 finding 內容與依據 | Assignment 附完整可讀 finding snapshot/reference、AC、舊 review 與 fix evidence。 | 只憑 assignment 與其引用就能完成 fix／覆核；不能靠 fake 私下提供答案。 |
| S1-R13 | 保留核心修正 | Red 輸出／身份／exit 矛盾仍放行 | 逐項驗 stdout、stderr、producer、task/attempt、exit、snapshot；replay 不能補正假歷史。 | 每項獨立污染都被拒；有真實 Green 也不能掩蓋錯誤 Red。 |
| S1-R14 | 保留路由修正 | CI policy 不可讀被當程式修正 | 區分 policy_unknown、infra_failure 與可修程式缺陷。 | Required rules 403／unknown 時 G3 unknown＋Blocked，修正輪數不增加。 |
| S1-R15 | 保留核心修正 | N/A eligibility 未驗獨立 producer/model | N/A 與正式 G2 共用身份／核准 profile／權限核對。 | Implementer 或未核准 model 的 eligibility 必須被拒，即使後續 G2 clean。 |
| S1-R16 | 保留核心修正 | 已 resolved 的同一缺陷再現卻不 reopen | Reviewer 確認 matches 與依據後重新開啟 stable ID，closure 留歷史。 | 新版本再現立即阻擋且套 recurrence 規則，不能維持 resolved。 |
| S1-R17 | 保留核心修正 | 非成功例外可放行 failure 且無批准 | 僅適用且明確核准的 skipped/neutral 例外可接受。 | failure/cancelled/unknown 永不因白名單 Pass；無批准 skipped/neutral 亦拒絕。 |

## 要先解掉的設計缺口

1. **許可不等於可重送的 dispatch**：重複 prepare 可以返回同 operation ID，但不能讓兩個 caller 都以為可執行。需指定只有一個 owner 能消耗的執行許可與 receipt 規則；外部 outcome unknown 就停止，不重放許可。
2. **同 feature 的唯一狀態／預算**：Herdr 草案仍以 run directory 為配置候選。須確保改 run ID 不會取得新 writer 或新 budget，不能讓 per-run lock 與 feature ownership 分成互相不同步的兩份 authority。
3. **四小時與非長駐 controller 的接合**：保留 worker／CI 等待計時；確認既有 runtime 的 deadline／停止能力，以及協調 session 離線時的行為。若只能下次呼叫才發現超時，需明示限制並裁決，不宣稱硬時限已達成，也不偷建新 supervisor。
4. **原始 TDD 與身份證據**：抓取原始 Red 的時間、task／attempt、測試／程式 snapshot、兩路 log 與 exit；後來 replay 僅為補充。Receipt／model 身份需來自可核對的 runtime 資料，不由 worker 自填 profile 就通過。
5. **Pass 前的外部觀察**：取得最新 head/base/check attempts/policy；將 observation 與本次 assessment 綁定。五分鐘快取或只讀本地 gate 值不能代替新觀察，仍不宣稱能鎖住 GitHub 的全域交易。
6. **OpenCode-only 仍是已確認需求**：Herdr 是本機接合候選，不應讓公司只有 OpenCode 的情境失效。第一切片可以只驗選定接法，但完整 change 的 AC-D20／D22／D23 不能因此勾完成；其他接入按選用範圍另列證據。
7. **G3 required policy 仍待決**：既有 403 與 CI jobs 成功是兩件事。無適用明確政策仍 Blocked；不能默認 `test` 足夠，也不能把權限缺口送成一次程式修正。

以上是 design 的待解問題，不是新增已確認需求或新增 gates。前兩项可由指定 Implementer 提出最小設計；信任／計時承諾若改變既有 AC，必須對具體差異請使用者裁決。

## 下一步與確認順序

1. H-CHOICE 已依 D45 收斂：採原生 Herdr＋薄 controller 作第一條實作路徑，不引入另一套 orchestrator 或第二份 gate/finding authority。
2. H0 已完成所選版本及 Luna／Sonnet 的小型交接，見 [實測紀錄](../research/2026-09-27/herdr-setup.md)。正式 skills profile、Reviewer 權限及公司環境仍未驗證；設計應引用已保存證據與限制，不重跑廉價模型 probe 充當產品驗收。
3. 將本對照交指定 Opus Implementer，完成所選接法的正式 spec 差異、design、tasks 與 validation 候選；核對輸入是目前工作目錄基準。過期候選只可供參考。
4. 對候選做獨立 spec／standards review，修正後供使用者逐 artifact 採用；這是文件審查，不能當產品 G2。完成 D11 的版本確認後才派產品實作。
5. H1 驗核心與 fake 負例；H2 驗真實 issue → TDD → blocking finding → fix → re-review → CI → PR Pass。少任何一段就列未覆蓋。
6. 本 repo 測通最小真實 loop 後，以 OpenCode＋Herdr、orchestrate skill 與薄 controller 啟動 cross-node-file-transfer 的 Project→多 features（D43）。沿用適用的既有需求基準，新程式留下自己的 TDD／review／CI／worktrees；不把 bootstrap 由協作者搬運的成果算成產品自行協調成功。Stack 政策與真實多人方式沿 Q-STACK／Q-DEMO-PEOPLE 保留待決。

### Example repository 的安排建議

建議 `loop-engineering` 保存方法、skills、controller、安裝／示範說明及驗證證據索引；`cross-node-file-transfer` 使用獨立 repo，保存產品程式、自己的 project baseline／feature artifacts／tests、issues／PRs 與 CI。Example 引用可核對版本的本工具，驗證 member 能將機制帶到另一個專案；此處是對使用者 repo/worktree 問題的建議，尚未建立或搬動 repository。

Worktree 共用所屬 repo 的 Git 歷史：各 feature 的實作 worktrees 應從 cross-node-file-transfer 建立；Reviewer 按核准權限使用獨立 checkout／必要時 clone。Demo 保留 branches／worktrees，GitHub 與可分享證據亦保留，不以本機 checkout 作唯一歷程。實際 repo／checkout 路徑、初始化與清理須在 H3 操作計畫列明，不由本次文件更新自動執行。

## 對照初稿當時的事實（歷史快照）

以下記錄對照初稿完成時的狀態；後續 H0 實測見上方連結，D45 已採用收斂後 proposal，其餘正式 artifacts 尚待修訂。

當時未修改 `src/delivery/`、`tests/` 或舊 OpenSpec artifacts／approval；未關閉任何 finding；未安裝 Herdr、啟動新實作、修改 gigaxfer 或建立 cross-node-file-transfer。Scope 對照完整不等於新 design 已完成或 E2E 已通過。

來源：[Project intent](../project-intent.md)、[決策](../decisions.md)、[Herdr 整合草案](herdr-integration.md)、[正式 OpenSpec](../../openspec/changes/implement-delivery-loop/proposal.md)、[舊 S1 checkpoint](../handoffs/2026-09-27-controller-design.md)。
