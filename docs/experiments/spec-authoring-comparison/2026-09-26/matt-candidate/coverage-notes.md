# Matt to-spec 研究與覆蓋紀錄

日期：2026-09-26。本次只有比較草稿；未批准實作，也未完成原版先確認接縫再發布的完整流程。

## 研究進度

已完整讀取 shared-input、11 份 baseline、input-manifest，以及指定的本機 to-spec skill。11 份 baseline 的 SHA256 全部符合 manifest。未讀另一候選、既有比較結論或網路口碑，沒有重新執行能力 probes、修改 repo 或啟動 runtime。

Skill 內容 SHA256：`43ad9cf318e5e7d3d1fa360253a37021796dc87a0c2e595ad262661a10f85088`。檔案沒有宣告 semver，不推定 upstream release。原版使用七節模板、長編號 user stories、禁止具體路徑／code，要求先確認最高可用測試接縫再寫 spec 並發布。

## 接縫與本輪澄清

共用提案：從 controller 公開 start／adopt／status／resume／decision 操作進入，以可控制的 fake agent／GitHub／CI adapters 驗證可觀察狀態、派工、發布及重啟。真實 adapters 與 finding → fix → re-review 另外取得真實 E2E 證據。

主 agent 已提出確認問題，但使用者尚未回答；未把接縫寫成已決。Shared input 末段及主 agent 最新指示允許先產 comparison draft，Testing Decisions 明列待確認。此澄清取代本輪初始「先等確認才產出」的等待安排，沒有替使用者批准接縫或 D11 design＋plan。

## 覆蓋群組與草稿定位

| 群組 | 來源 | Spec 定位 |
| --- | --- | --- |
| 共同入口、project 薄層、refs、原生文件、AC | D04–D08、D17、D19 | US／AC-M01–M04；ID-M01、M03 |
| 同層角色、design＋plan、scope／AC 人工邊界 | D11、D20、D23 | US／AC-M05–M07；ID-M02 |
| 相依 feature、人工接受、merged 與 baseline | D03、D27 | US／AC-M08、M34；ID-M10 |
| Pre-PR adopt、控制權、歷史證據缺口 | D15–D18；contracts 控制權；trial | US／AC-M09–M11、M40 |
| 實作序列、單一整合 owner、assignment／result | D01、D08、D13；contracts 派工與結果 | US／AC-M11–M14；IP-M04 |
| G1、Red lineage／current Green、N/A 先後 | D01、D26 | US／AC-M14–M15；ID-M04 |
| G2 獨立、作者 branch、blocking 與執行狀態 | D09、D12、D20、D23、D30 | US／AC-M16–M17、M24；ID-M05 |
| G3、check 來源與版本、非成功狀態、CIT | D01、D29；intent 5；contracts gate | US／AC-M18–M19；ID-M05 |
| 新 head／base／artifact 失效、Pass 前重查 | D01、D19；contracts gate | US／AC-M20–M21、M34；ID-M06 |
| 批次、stable findings、closure、一次 dispute | D09、D12、D24、D25 | US／AC-M22–M25；ID-M07 |
| 4h／3 rounds／2 extra retries、重啟不重置 | D13；contracts 預算 | US／AC-M26–M27；ID-M08；IP-M05 保留計時未決 |
| JSON／YAML 可讀狀態、結果先保存、去重 | D09、D14、D24；file-state | US／AC-M28–M29；ID-M09；IP-M02–M03 標建議 |
| Registry 權威、PR 全文／issue 摘要、outbox | D24；contracts 發布 | US／AC-M24、M30–M31；ID-M07、M09 |
| Unknown／crash／corruption／ownership | D08、D13、D14；contracts 恢復；file-state | US／AC-M11、M27–M33；IP-M02–M03 |
| 人工退回原 AC、同 run／預算／finding | D03、D09、D11、D13；contracts finding | US／AC-M34–M35 |
| 接受後 Retro 候選、user-only、P03 未開始 | D21、D22、D28 | US／AC-M36–M37、M40；ID-M11；IP-M06 |
| Skills／唯一外層、runtime／model 解耦 | D02、D07、D26、D30；shared-input 後續 Ok | US／AC-M37–M38；ID-M12 |
| Fake／真實證據、真實 finding 循環、paused trial | D10、D11、D18、D22、Q-TARGET；research／trial | US／AC-M39–M40；Testing Decisions；Further Notes |

## 保留的狀態區分

- 已確認政策：D01–D30 與共用輸入明列的後續工具組合 Ok；D11 具體開工確認仍未完成。
- 設計建議：Python CLI、YAML／JSON／JSONL 分工、schema／enum、鎖與 journal 細節、active time 計算法、45／30／30 分 timeout、Retro scorecard，均留在 Implementation Decisions 的 IP-M01–M06 候選段及 Further Notes。
- 待決或待實證：主要測試接縫、G2 Codex runtime／model 定義、具體 adapters／權限、repo required checks、skipped／neutral 明確政策、Q-TARGET、native completion、隔離、workspace discovery。
- 尚無 controller、產品測試或真實 E2E；AC 描述可觀察的目標，Testing Decisions 是驗證計畫，不報通過。
