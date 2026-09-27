# Controller 詳細設計審查（design-02）

日期：2026-09-27。狀態：**v3 review clean；未解 confirmed blocking = 0；D40 已記錄 D11 核准**。這是文件審查，不是產品 G2、PR Pass、實作驗收或開工批准。

## 現行候選與下一步

- [Design v3](2026-09-27-controller-detailed-design/candidate/design.md)
- [Tasks v3](2026-09-27-controller-detailed-design/candidate/tasks.md)
- [88 AC validation v3](2026-09-27-controller-detailed-design/candidate/validation.md)
- [Implementer result](2026-09-27-controller-detailed-design/candidate/result.json)／[finding responses](2026-09-27-controller-detailed-design/candidate/finding-responses.json)
- [開工確認表](2026-09-27-controller-detailed-design/approval.md)

候選文件保留 Opus 原始 bytes，與覆核 hashes 一致；不是與 OpenSpec 平行維護的另一套規格。確認設計、切片及必要目標後，沿 OpenSpec 原生 design→tasks 順序納入正式 change，候選留作凍結審查證據。現行 OpenSpec proposal/specs 仍是需求權威；正式 [design](../../openspec/changes/implement-delivery-loop/design.md)／[tasks](../../openspec/changes/implement-delivery-loop/tasks.md) 與 [validation](../validation/implement-delivery-loop.md) 已採用；只更新核准／切片與狀態標記，凍結候選不變。

## 審查與修正歷程

| 版本 | 結論 | 處理 |
| --- | --- | --- |
| v1 | 9 blocking（DR-01–DR-09） | Opus 依同一批 finding 修正 |
| v2 | 8 verified；DR-04 still_open；新增 DR-10 | 再交 Opus 集中修正 snapshot 範圍與證據沿用 |
| v3 | DR-01–DR-10 verified；未解 blocking 0 | 保留 N-V3-01 非阻擋實作澄清；D40 已核准 |

[初審](2026-09-27-controller-detailed-design/review-v1.md)、[v2覆核](2026-09-27-controller-detailed-design/re-review-v2.md)、[v3最終覆核](2026-09-27-controller-detailed-design/re-review-v3.md) 與對應 JSON 保存各版 hashes、反例與 closure。完整 [v1–v3 固定快照](2026-09-27-controller-detailed-design/design-02-v1-v3.tar.gz) 含輸入、三版輸出及派工／修正回執；既有 v1 archive 保留。

修正涵蓋 Reviewer OS 隔離、版本穩定性及重綁、Red snapshot、單一整合策略、跨 clone authority／預算、分段 dispatch、merge CI source、blob 持久化屏障及新契約強制獨立 review。

## 已核對與限制

協作者核對三版輸出 hashes、88個AC索引無缺漏，並以真 git 暫存 repo 重現 stash 漏 untracked、staged exclude 未排除兩個反例。Opus 提供修正算法及 macOS sandbox 小型 probe；這些不是產品實測或完整 E2E。

Native transcript 選取的50則 assistant model 欄位均為 claude-opus-5-5；[觀察紀錄](2026-09-27-controller-detailed-design/model-observation.json) 僅證明 client 收到的 model metadata，不獨立證明本機 proxy 上游路由。獨立 GPT reviewer 只讀固定快照，未修改作者產物；此文件 review 不是未完成 controller 的自動 G2。

N-V3-01：實作時依 G1 確定性核對／G2 語意審查的分工，明定 method_changed 的語意並補狀態機測試；若選擇使該註記阻擋G1，就須提供前置 eligibility／重驗路徑，避免等待尚不可派發的G2。這是非阻擋澄清，不自行增加gate。

Runtime／隔離、Linux、keychain、真實GitHub checks及power-loss等能力仍依文件列出的範圍驗證；缺能力不宣稱成功。沒有產品程式、ticket／PR、CI或E2E成果。Gigaxfer及cross-node-file-transfer未修改／啟動。
