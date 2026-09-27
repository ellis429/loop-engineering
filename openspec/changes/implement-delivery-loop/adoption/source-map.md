# Source map：D53 採用的正式 specs

> 由 `.delivery/w1/compose.py` 的操作紀錄產生（T0.1 第 3 步）。每一處變更都以錨點從固定來源擷取原文，錨點必須恰好命中一次。沒有列出變更的單位是正式原文不變。

## 來源

| 來源 | sha256 |
| --- | --- |
| D45-02 spec-delta（`docs/design-candidate/d45-02/spec-delta.md`） | `7ebd8d014f5765cc35767a6a4372f4871d70f1af4ef72c3cb940da11a2c18565` |
| D45-04 spec-delta（`docs/design-candidate/d45-04/spec-delta.md`，revision-16 文字，D53 核准快照） | `81ce7366894349d9d56493ddd1c01901a641746897c7cdf9d8aaced87e6e284b` |
| 組合規則 | D45-04 spec-delta §12 |

## 各檔組合前後

| Spec | 組合前 sha256（正式原文） | 組合後 sha256 |
| --- | --- | --- |
| `delivery-orchestration` | `a54c18f808079dfe8d2c032a574eda5411916566124909ca4149fa4a46161c25` | `8eaafa4d14e135456727ec31f20645d3768894ce5b0865a7968b8ccc904f1a7f` |
| `delivery-gates` | `a8d68b7c03e45a55da796f8b223d7534266010af534e8c0506f36f66b0218d91` | `7cdf2ee0b1bd4f0be007169d6d0599e1e9320bef2a486e4ebd9285a550907a5f` |
| `durable-delivery` | `f873aae0d549f5f8e11cfcca801cf78610aa970d071c09fcd5776f814ca5a9f6` | `ace2b0e5b18f7c7b905a3a445975a92d317c101a3a5349507026b5c70b7db468` |
| `finding-resolution` | `2f37c77709d526b2259b2285c99617fe8d4a2768cb318ccf860dec8a8b6c8629` | `e46512eb6061717adf7b54b48a6d6e2b285cc37f29167a4401594adc0f939cb2` |

## 裁定（不改語意）

- D45-04 spec-delta §1 的取代範圍寫「以下五段」，但引文實有六段（外部寫入、PR ensure 的身份、人工處理 unknown、Branch 歷史、唯讀觀察、讀取失敗預算）；依意圖取整段引文。
- 在正式 THEN 末尾追加文字時，原句沒有句末標點者補「。」，只改標點。
- AC-D07 THEN：D45-02 把「resume/reconcile」換成「orchestrate 經 controller 讀回核對」；照字面會成為「讀回核對 核對 assignment」，組合時去掉重複的「核對」（source-map-review-01 SM-02）。
- 延後註記只寫「[延後] 由後續切片負責」，不指定 S2；只有來源原文明寫 S2 的條文（DUR-02 平行 writer、AC-G15、AC-O23、AC-D23）保留 S2（source-map-review-01 SM-01）。

## delivery-orchestration

| 單位 | 來源 |
| --- | --- |
| banner | replace banner：D45-02 §0.1＋D45-04 §12＋tasks T0.1 |
| Purpose | replace：D45-04 §12 [R16]<br>replace：D45-02 L34 |
| ORC-01 | replace in requirement text：D45-02 L40<br>append to requirement text：D45-04 L144 |
| AC-O01 | edit THEN：D45-02 ORC-01 AC-O01 |
| AC-O02 | replace THEN：D45-02 L45 |
| AC-O18 | edit THEN：D45-02 ORC-01 AC-O18<br>add slice note：D45-04 §9 |
| AC-O19 | 正式原文不變 |
| ORC-02 | 正式原文不變 |
| AC-O03 | 正式原文不變 |
| AC-O04 | 正式原文不變 |
| ORC-03 | 正式原文不變 |
| AC-O05 | 正式原文不變 |
| AC-O06 | replace THEN：D45-02 L52 |
| AC-O07 | 正式原文不變 |
| ORC-04 | 正式原文不變 |
| AC-O08 | add slice note：D45-04 §9 |
| AC-O09 | append to THEN：D45-02 L58<br>add slice note：D45-04 §9 |
| ORC-05 | append to requirement text：D45-04 L154 |
| AC-O10 | 正式原文不變 |
| AC-O11 | 正式原文不變 |
| ORC-06 | append to requirement text：D45-04 L155＋§9「O12、O13 由 skill 與人核對」 |
| AC-O12 | 正式原文不變 |
| AC-O13 | 正式原文不變 |
| ORC-07 | 正式原文不變 |
| AC-O14 | add slice note：D45-04 §9 |
| AC-O15 | replace whole scenario：D45-04 L156 |
| ORC-08 | replace in requirement text：D45-02 L64 |
| AC-O16 | 正式原文不變 |
| ORC-09 | 正式原文不變 |
| AC-O17 | 正式原文不變 |
| ORC-10 | 正式原文不變 |
| AC-O20 | 正式原文不變 |
| AC-O21 | 正式原文不變 |
| ORC-11 | 正式原文不變 |
| AC-O22 | 正式原文不變 |
| AC-O23 | replace THEN：D45-04 L151 |
| ORC-12 | 正式原文不變 |
| AC-O24 | 正式原文不變 |
| AC-O25 | 正式原文不變 |
| AC-O26 | 正式原文不變 |
| AC-O27 | 正式原文不變 |
| AC-O28 | 正式原文不變 |

## delivery-gates

| 單位 | 來源 |
| --- | --- |
| banner | replace banner：D45-02 §0.1＋D45-04 §12＋tasks T0.1 |
| Purpose | replace：D45-04 §12 [R16]<br>replace：D45-02 L78 |
| GAT-01 | replace in requirement text：D45-02 L84 |
| AC-G01 | 正式原文不變 |
| AC-G02 | 正式原文不變 |
| AC-G03 | 正式原文不變 |
| GAT-02 | append to requirement text：D45-02 L90 |
| AC-G04 | replace WHEN：D45-02 L99 |
| AC-G05 | append to THEN：D45-04 L74 |
| GAT-03 | append to requirement text：D45-04 L47 |
| AC-G06 | append to THEN：D45-04 L70 |
| AC-G07 | replace THEN：D45-02 L111（D45-04 §3 沿用） |
| AC-G08 | edit THEN：D45-04 §3 AC-G08 |
| GAT-04 | replace in requirement text：D45-02 L117 |
| AC-G09 | 正式原文不變 |
| AC-G10 | replace WHEN：D45-02 L121 |
| GAT-05 | replace whole requirement text：D45-02 L125<br>append to requirement text：D45-04 L86 |
| AC-G11 | edit WHEN：D45-02 GAT-05 AC-G11 讀法 |
| AC-G12 | 正式原文不變 |
| GAT-06 | replace whole requirement text：D45-04 L96（全文） |
| AC-G13 | replace THEN：D45-04 L114 |
| AC-G14 | append to THEN (with bullets)：D45-04 L119 |
| AC-G15 | replace whole scenario：D45-04 L116 |
| GAT-07 | 正式原文不變 |
| AC-G16 | replace THEN：D45-02 L155 |
| AC-G17 | append to THEN (with bullets)：D45-04 L75 |
| AC-G18 | replace THEN：D45-02 L157 |
| GAT-08 | append to requirement text：D45-02 L161 |
| AC-G19 | replace WHEN：D45-02 L167 |
| AC-G20 | 正式原文不變 |

## durable-delivery

| 單位 | 來源 |
| --- | --- |
| banner | replace banner：D45-02 §0.1＋D45-04 §12＋tasks T0.1 |
| Purpose | replace：D45-04 §12 [R16]<br>replace：D45-02 L175<br>replace：D45-02 L175 |
| DUR-01 | replace in requirement text：D45-02 L183 |
| AC-D01 | 正式原文不變 |
| AC-D02 | append to THEN：D45-02 L187 |
| DUR-02 | replace in requirement text：D45-02 L191<br>append to requirement text：D45-04 L34 |
| AC-D03 | replace THEN：D45-02 L199 |
| AC-D04 | append to THEN：D45-02 L201<br>append to THEN (with bullets)：D45-04 L40 |
| DUR-03 | append to requirement text：D45-02 L204 |
| AC-D05 | 正式原文不變 |
| AC-D06 | edit WHEN：D45-02 DUR-03 AC-D06<br>edit THEN：D45-02 DUR-03 AC-D06 |
| DUR-04 | 正式原文不變 |
| AC-D07 | edit THEN：D45-02 DUR-04 AC-D07 |
| AC-D08 | 正式原文不變 |
| DUR-05 | 正式原文不變 |
| AC-D09 | 正式原文不變 |
| AC-D10 | replace whole scenario：D45-04 L129 |
| AC-D11 | 正式原文不變 |
| DUR-06 | append to requirement text：D45-04 L16（取代 D45-02 追加段；六段引文） |
| AC-D12 | edit WHEN：D45-02 DUR-06 AC-D12 |
| AC-D13 | 正式原文不變 |
| DUR-07 | 正式原文不變 |
| AC-D14 | replace THEN：D45-02 L244 |
| AC-D15 | 正式原文不變 |
| DUR-08 | replace in requirement text：D45-02 L250<br>replace in requirement text：D45-04 L164（D53 核准 E）＋§10 首句 |
| AC-D16 | 正式原文不變 |
| AC-D17 | replace whole scenario：D45-02 L258 |
| DUR-09 | replace in requirement text：D45-02 L265 |
| AC-D18 | 正式原文不變 |
| AC-D19 | 正式原文不變 |
| AC-D20 | edit THEN：D45-02 DUR-09 AC-D20<br>add slice note：D45-04 §8 |
| AC-D21 | edit WHEN：D45-02 DUR-09 AC-D21 |
| AC-D22 | edit WHEN：D45-02 DUR-09 AC-D22 |
| AC-D23 | replace whole scenario：D45-04 L138 |
| AC-D24 | add slice note：D45-04 §8 |

## finding-resolution

| 單位 | 來源 |
| --- | --- |
| banner | replace banner：D45-02 §0.1＋D45-04 §12＋tasks T0.1 |
| Purpose | replace：D45-04 §12 [R16]<br>replace：D45-04 §12 [R16]<br>replace：D45-02 L278 |
| FIN-01 | 正式原文不變 |
| AC-F01 | 正式原文不變 |
| AC-F02 | 正式原文不變 |
| FIN-02 | 正式原文不變 |
| AC-F03 | 正式原文不變 |
| AC-F04 | 正式原文不變 |
| FIN-03 | append to requirement text：D45-02 L280 |
| AC-F05 | append to THEN：D45-02 L286 |
| AC-F06 | 正式原文不變 |
| AC-F07 | 正式原文不變 |
| FIN-04 | replace in requirement text：D45-02 L291 |
| AC-F08 | 正式原文不變 |
| AC-F09 | 正式原文不變 |
| AC-F10 | 正式原文不變 |
| FIN-05 | 正式原文不變 |
| AC-F11 | 正式原文不變 |
| AC-F12 | 正式原文不變 |
| FIN-06 | replace in requirement text：D45-02 L299<br>append to requirement text：D45-02 L305 |
| AC-F13 | 正式原文不變 |
| AC-F14 | 正式原文不變 |
| FIN-07 | 正式原文不變 |
| AC-F15 | 正式原文不變 |
| AC-F16 | 正式原文不變 |

## 檢查

- requirements：36；AC：88（唯一 88）。
- 沒有對應到任何單位的操作：無。
- 操作總數：82。
