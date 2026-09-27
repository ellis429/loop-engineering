# 來源與覆蓋研究

狀態：OpenSpec comparison draft 的研究筆記。來源固定於 `../baseline/`；未讀另一候選或既有工具比較。原先等待測試邊界確認，依 `../shared-input.md` 後續共同澄清改為可產出草稿；seam 仍 pending。

## 來源優先順序

1. `../shared-input.md` 及本輪共同澄清：限制比較產物與權限。
2. `../baseline/docs/decisions.md` D01–D30：已確認政策；shared-input 的最新 Ok 提供方法組合。
3. `../baseline/docs/workflow-design.md`、`workflow-contracts.md`、`file-state.md`：整合設計與具體化提案，不全部升格成已確認政策。
4. `../baseline/CONTEXT.md`：角色與交付詞彙。
5. `project-intent.md`、`experiments/pr-gating.md`、runtime 與 messaging 研究：使用情境及能力缺口，不能當已通過的 gate/E2E。

## Capability 覆蓋配置

| Capability | 已確認核心 | 情境證據重點 |
| --- | --- | --- |
| delivery-orchestration | D02–D08、D11、D17–D23、D27–D30；原生文件引用與同層角色 | 新 feature、adopt、一次開工確認、拒絕雙 loop、acceptance 不等於 merge、相依等待、Retro 候選 |
| delivery-gates | D01、D09、D10、D19、D26、D29、D30 | 歷史 Red/current Green、N/A eligibility、獨立 Reviewer、CI 非成功、版本失效、真實 E2E |
| finding-resolution | D09、D12、D13、D24、D25 | 穩定 ID、解除權限、一次爭議覆核、合併修正輪次、人工退回、PR 完整 review/issue 摘要 |
| durable-delivery | D02、D08、D13、D14、D24、D30 | 人可讀持久化、競爭 writer、通知/結果去重、unknown 操作、crash/reconcile、有界預算、adapter 能力 |

## 不轉為已確認政策的細節

- Public start/adopt/status/resume/decision + fake adapters 是待確認測試 seam；規格只要求可觀察的成果與故障語意。
- 45/30/30 分鐘 timeout、active-time 聯集/unknown interval 的具體算法、Python、YAML/JSON/JSONL 目錄布局是設計候選。
- Runtime/model、Codex 的具體定義、required checks、native completion、全工具 Reviewer 隔離、新 repo placement 尚未定案或驗證。
- Snapshot/事件修復、operation marker/read-back 等具體化需求會明標為本草稿採自設計提案的可觀察契約，未聲稱已獲 D11 批准。
- Q-TARGET 未答；P03 Retro 與 PR trial 均未開始。既有 probe 不等於真實交付。

## 自檢方法

用固定 requirement 與 AC ID 映射 D01–D30；每項以 WHEN/THEN 描述可觀察結果，避免用 enum 存在或內部函式呼叫替代驗收。CLI validate 僅證明原生結構合法，不證明政策已採用、內容完整或產品通過驗收。
