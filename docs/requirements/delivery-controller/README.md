# 需求輸入：薄 controller（loopctl）

四個 capability、36 條 requirement、88 條 AC。這是需求輸入，不是 OpenSpec 的現況 spec：每個 Feature 開 change 時，把它要實作的 requirement 從這裡帶進自己的 spec delta（D57、D58）。切法與每個 Feature 帶哪些 requirement，見 [roadmap](../../roadmap.md)。

| 檔案 | 內容 |
| --- | --- |
| [`specs/delivery-orchestration/spec.md`](specs/delivery-orchestration/spec.md) | ORC-01～12 |
| [`specs/delivery-gates/spec.md`](specs/delivery-gates/spec.md) | GAT-01～08 |
| [`specs/durable-delivery/spec.md`](specs/durable-delivery/spec.md) | DUR-01～09 |
| [`specs/finding-resolution/spec.md`](specs/finding-resolution/spec.md) | FIN-01～07 |
| [`adoption/source-map.md`](adoption/source-map.md) | 四份 spec 由哪些來源組成 |

## 來源

- 依 D75 從 `openspec/changes/implement-delivery-loop/` 原樣搬來，內容未改，五個檔案的 sha256 與搬移前相同。那個 change 已退役（刪除、不 archive），最後存在的版本是 [`a1d8906`](https://github.com/yschiang/loop-engineering/tree/a1d8906/openspec/changes/implement-delivery-loop)，其中的 proposal、design、tasks、approval 與 adoption 審查紀錄都在那裡。
- D53 核准的組成方式與 hash 綁定見 [`d11-approval.json`](../../design-candidate/d45-04/d11-approval.json)；核准後的更正見[勘誤](../../design-candidate/d45-04-errata.md)。
- 文中的「S1」「第一片」指 D53 的單一切片；重切後對應 roadmap 的 M1。延後到 S2 的部分列在 roadmap 的「延後到 M2」。
