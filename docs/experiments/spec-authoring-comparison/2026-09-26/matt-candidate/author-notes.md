# Matt to-spec 比較草稿：作者紀錄

日期：2026-09-26。候選：Orca Delivery Loop MVP 的 Matt to-spec 原生模板版。這份紀錄說明來源、方法及覆蓋，不評比另一候選，也不替本稿評優。

## 產物與邊界

- 原生候選：[spec.md](spec.md)。保留七個原生二級 headings；40 個長編號 User Stories，各附穩定 US／AC ID 及可觀察驗收目標。Implementation Decisions 分已確認 ID-M01–M12 與設計建議 IP-M01–M06；Testing Decisions 明列接縫待確認。
- 研究覆蓋：[coverage-notes.md](coverage-notes.md)。
- 所有寫入僅在 `/private/tmp/orca-spec-comparison-20260926/matt/`；沒有修改 gigaxfer 或 orca-delivery，沒有建 issue／PR、發文、套用 label、啟動 worker 或實作。
- 沒有讀另一候選、root comparison checklist、網路口碑或先前三套比較結論；不以另一份產物反向補寫。

## 原生方法與版本

實際讀取：`/Users/johnson.chiang/.agents/skills/to-spec/SKILL.md`。

- Skill name：`to-spec`；frontmatter 有 `disable-model-invocation: true`。本次由使用者明確要求比較並選用，沒有背景擅自呼叫 user-only skill。
- Skill SHA256：`43ad9cf318e5e7d3d1fa360253a37021796dc87a0c2e595ad262661a10f85088`，3043 bytes。
- Skill 未宣告 semver；本次沒有查 upstream git commit 或網路 release，因此用實際內容 hash 識別，不捏造套件版本。
- 沒有 to-spec CLI invocation；這是讀取 Markdown workflow 後的 synthesis。工具為本 session 的本機 read／write、Python SHA256 與文件結構自檢，沒有呼叫 OpenSpec CLI、implement、implement-spec 或 to-tickets。

原版要求：研究 repo／領域詞彙；提出最高可用測試接縫並向使用者確認；依七節模板寫 spec；發布到 issue tracker 並套用 ready-for-agent。原版不做額外需求 interview，Implementation Decisions 不含具體 file paths 或 code。這些限制中，模板、廣泛 User Stories、詞彙與不嵌 paths／code 均保留。

## 共用來源版本

Baseline 來源為同次快照，SHA256 由 `../input-manifest.json` 固定；已驗證所有 11 份檔案內容吻合。產品事實以 baseline 內容及 shared-input 明列的後續確認為來源；未追開文件中的外部連結。另有一處繼承的 gigaxfer AGENTS 規則進入 Testing Decisions，來源及狀態問題如下方 provenance 補記。

| 已讀來源 | 內容 SHA256 |
| --- | --- |
| `CONTEXT.md` | `fdf18dc7f32b7a37d0052e74b395f402f279b51b5936fe025f6af2bf11803f5c` |
| `README.md` | `020c9540c3ab88ebe409e86780378d62bd0073b2e4f72f13b15ceedd560901e6` |
| `docs/decisions.md` | `2e63051992eecc441f58dc613c38a98ad8ae5dd053ce275ba011ff0f996908ac` |
| `docs/workflow-design.md` | `d069ec3f6cdb95356e0930d535aebeb349572c0b4c9cf7873bb2b1e7f4850e9a` |
| `docs/workflow-contracts.md` | `dd5660ecfbf849a4966945383e4d65f355d5fa525ffec7ed3fc664831750d5cb` |
| `docs/file-state.md` | `61e9a58388fdf19945fbe06830b8d5d2c074f24389a99677cfbe7d88eaa72648` |
| `docs/project-intent.md` | `15c3666174dc5daf3dbb12fb0981d7b30500494c48d04e9992fe34398c49493d` |
| `docs/experiments/pr-gating.md` | `060f4497428a475338224944fcc03c891b4fce6077704af13974c5047385704d` |
| `docs/research/2026-09-25/runtime-probe.md` | `68a8e8e735dfe71ef426249814bf13a2f9b35b5f75a34865e642749c56c50b01` |
| `docs/research/2026-09-25/integration-gaps.md` | `1a50209457bfd084e29b51f15c22c63f8b41116ce6567e64f4643fc7a39754c0` |
| `docs/research/2026-09-26/agent-messaging-and-opencode.md` | `88e87093adc5c76d62592c6202810472a7ee1826cdf47d8ea12eab61e037a33f` |

另外完整讀取 `../shared-input.md`，包含最新的「本輪後續一致澄清」。Baseline 沒有 D31；工具組合的後續 Ok 依 shared input 引用，不冒稱 baseline 已含 D31。來源中的 Orca 1.4.209、Claude Code 2.1.282、Codex CLI 0.153.4 及 opencode checkout 查核是既有研究時點資訊，本次沒有重新查安裝或運行版本。

## 本次方法偏離及理由

1. **Pending seam draft。** 原版要求先確認測試接縫，再完成 spec。主 agent 已提出問題但未獲使用者回覆；共用輸入最新澄清要求先交可比較草稿。故 Testing Decisions 明示接縫為提案，沒有把它算成已確認或聲稱完整原版 workflow 已完成。未開始任何依賴此決策的實作或驗證。
2. **未 publish、未 ready-for-agent。** 本輪明確只產比較文件、不建票、不對外發文。因而省略發布與 label，沒有要求 issue tracker setup，也沒有用「skill 原版會發布」推定授權。這是任務範圍差異，不是假裝發佈成功。
3. **快照研究替代重新探索 live repo。** 使用同一批指定來源保證輸入一致。Baseline 明確標示 controller 尚未實作，因此沒有杜撰既有 modules 或測試 prior art；probe 只作能力現況，不作產品通過紀錄。
4. **增加可追溯驗收 ID。** 在原生 User Stories 中附 AC，並在 Testing Decisions 映射驗法，滿足已確認 D19。未增加額外頂層規格 headings，未插入 OpenSpec requirement/scenario 模板或實作路徑。
5. **設計候選另標。** 原版 Implementation Decisions 主要記已作決策；來源同時含尚待 D11 的 design 提案，故在同節明確分出 IP 候選，不把 Python、檔案布局、timer／timeout 或 runtime 設定升格。Solution 亦明列 M13、M18、M21、M28–M32 的設計衍生驗收細化仍待 D11，避免 AC 形式被誤讀為對機制的批准。

## 已確認決策逐條定位

US 與 AC 共用 M 編號；例如 M14 指 US-M14 及 AC-M14。ID 指 Implementation Decisions 的已確認項。

| 決策 | 規格定位 | 保留的要點 |
| --- | --- | --- |
| D01 | M13–M21；ID-M03–M06 | 三 gates、證據適用、歷史 Red lineage／當前 Green、版本失效 |
| D02 | M37；ID-M01、M12 | Workflow／controller／skills／adapters 分工，唯一外層 |
| D03 | M08、M34；ID-M10；Out of Scope | PR Pass 與接受／merge 分開，無自動 merge／close／release／deploy |
| D04 | M02–M03；ID-M01、M03 | Project 共用契約、feature ticket 可承擔 feature spec |
| D05 | M02、M12；ID-M01 | 單 feature 單 PR，tasks 派工；過大先拆 |
| D06 | ID-M01 | 獨立 Orca Delivery repo；spec 不嵌具體路徑 |
| D07 | M37；ID-M12；Out of Scope；Further Notes | 正式選擇 OpenSpec，本次 Matt 比較不要求雙 authoring workflows |
| D08 | M11、M28–M32；ID-M01 | Orca lead＋本機持久化 controller＋workers；專用 terminal 啟動／resume |
| D09 | M13、M24、M29–M31；ID-M05、M07、M09 | 解除須覆核／裁決，通知不是成功證據 |
| D10 | M39；Testing Decisions | 真實 finding→fix→re-review，fake 與真實分開 |
| D11 | M06–M07、M09、M25；ID-M02；Further Notes | 一次具體 design＋plan 開工確認與後續人工邊界 |
| D12 | M17、M23–M24；ID-M05、M07 | Blocking 定義、偏好不 blocking、severity 排序 |
| D13 | M12、M22、M26–M27、M35；ID-M08 | 4h、3 輪、2 次額外 infra retry、實作序列／review＋CI 並行 |
| D14 | M28–M32；ID-M09；IP-M02–M03 | JSON／YAML 可讀保存；布局及 journal 細節仍候選 |
| D15 | M09–M10、M40；Further Notes | 既有 gigaxfer session pre-PR 方向，未擅選實驗目標 |
| D16 | M09–M10、M14–M22、M40 | 原實作完成後 G1→PR→review／CI→修正覆核，不重做初始工作 |
| D17 | M01–M02、M34–M37；ID-M01 | 共用 orchestrate、Project／Feature 範圍與交接 |
| D18 | M40；Out of Scope；Further Notes | PR trial 暫停，先流程／skills；未接管 |
| D19 | M03–M04、M07、M20；ID-M03；Testing Decisions | AC 穩定 ID、驗法／證據、原生檔名／實際 refs、不得降 AC |
| D20 | M05、M12、M16–M17；ID-M02 | 三角色統一名稱及職責 |
| D21 | M36；ID-M11 | Execution Retro 與必要 Replanning；不包進整個未來平台 |
| D22 | M40；Further Notes | P03 首次 Retro 對象已選，尚待明確開始 |
| D23 | M05、M11、M16；ID-M02 | 同層、明確代理授權、唯一 controller、G2 獨立 |
| D24 | M24、M28–M31；ID-M07、M09 | JSON registry 權威、PR 全文／issue 摘要、先保存 outbox／reconcile |
| D25 | M25；ID-M07；Testing Decisions | 一次獨立反證覆核、原 batch 不增輪、重啟不重置、仍爭議回人 |
| D26 | M14–M15、M37；ID-M04、M12 | Superpowers TDD、N/A eligibility 先於 G1／正式 G2、無自我豁免 |
| D27 | M08、M34；ID-M10 | 接受＋實際 merge＋採用 baseline 才啟動相依實作 |
| D28 | M36–M37；ID-M11；IP-M06 | 接受後去重產候選、不自動落地、不隱式呼叫 user-only |
| D29 | M19；ID-M05；Out of Scope | CIT 暫不處理、不新增 gate |
| D30 | M16、M38；ID-M05、M12；Further Notes | 核心與 runtime／model 解耦，不默認 model-only G2／opencode |
| Shared-input 後續 Ok | M37；ID-M12；Further Notes | OpenSpec＋Writing Plans 方法＋Superpowers TDD＋唯一 controller，Matt 方法按需 |

## 原始驗收情境定位

| Project intent 情境 | 本稿 AC |
| --- | --- |
| A01 正常 feature | M01–M06、M12–M22、M34 |
| A02 Finding 修正覆核 | M22–M25 |
| A03 Review clean／CI fail | M18–M19、M21–M22 |
| A04 CI green／review fail | M17、M21–M24 |
| A05 缺 TDD 證據 | M10、M13–M15 |
| A06 舊 SHA／Pass 前 push | M20–M21 |
| A07 Missing／pending／cancelled check | M18–M19 |
| A08 重複事件／遺失通知 | M29–M32 |
| A09 Crash／restart | M11、M27–M33 |
| A10 上限／爭議 | M25–M27、M33、M35 |
| A11 發布失敗 | M30–M31 |
| A12 Reviewer 隔離 | M16、M24、M38；Testing Decisions 真實隔離 |
| A13 真實端到端 | M39；Testing Decisions 真實驗收段 |

## 待決事項及未完成驗證

- 測試主要接縫的使用者確認；比較稿沒有越過此點批准實作。
- D11 具體 design＋plan 的開工確認；語言、public API、資料布局／鎖／平台 durability 均待落實。
- G2 Codex 的 runtime／model 定義、核准 execution 設定、adapter、真實 Reviewer 全工具隔離。
- Repo-specific required checks／來源、skipped／neutral 政策、timeout、active time 精確算法及 budget resume／extension 操作。
- Codex native completion、新 repo workspace discovery、真實 GitHub read-back／重啟恢復、完整 feature E2E 的實證缺口。
- Q-TARGET 未回答；D18 暫停未解除，D22 P03 Retro 未開始。不得依 baseline 中過期 head／PR 觀察直接採用目標。
- Retro 具體輸出 schema／skill 包裝尚未定；改善只作候選，沒有新增 gate 或落地授權。

## 檢查與工具紀錄

本次只做文檔及來源完整性自檢：七節標題、40 個唯一且連續的 US／AC IDs、AC→Testing Decisions 映射、已確認／建議／待決分離、無具體實作路徑或 code fences；產品測試、adapter tests、真實 E2E 均未執行。

可取得的時點是研究完整性核對在 `2026-09-26 13:02:23 UTC`；期間有等待與中斷，沒有可靠 active authoring 計時，因此不報總耗時、token 數或成本。最終機器結構檢查結果另存 `validation-notes.json`；它只是文件自檢，不能當作 feature gate evidence。

## 審校後 provenance 補記：繼承的 AGENTS 規則

主 agent 指出 Testing Decisions 第一段的 production hooks、sleep／retry、flaky exclusions 無法在共同 baseline 定位。已查明這些不是 to-spec skill 的明示規則，也不是本次 baseline 已確認的 Orca feature 決策；來源是 subagent 繼承的使用者訊息「AGENTS.md instructions for /Users/johnson.chiang/workspace/gigaxfer」，不是本次額外讀取另一份文件。

- 該訊息 §1「不為測試改 production 程式」要求不加只給測試呼叫的 hook／accessor，並以公開行為和既有正式注入點驗證。
- §3「修根因，不修症狀」禁止放寬斷言、加 sleep 或 retry 讓測試剛好通過，以及排除 flaky 測試。
- 原生 to-spec 本身只支持「驗外部行為、不驗實作細節」與選擇最高可用 seam 等原則；它沒有逐項列出上述禁令。

**狀態判斷：** gigaxfer AGENTS 是作者繼承的 repo 工作規則，並非共同快照中的 Orca Delivery 產品需求。將這些細項放入 spec 的「已確認驗證原則」超出了本次共同產品來源，不能據此認定它們已被批准為 Orca feature policy。這是來源混入及標記不夠精確，並非一項另有批准的新增政策。比較時應保留這個限制，不以該段給本稿增加已確認需求的覆蓋分數。

依主 agent 指示，保留生成的 spec 原稿，不因審校發現而重寫；此補記只修正作者紀錄的 provenance 說明。Spec 此時 SHA256 仍為 `51141cf17c2ff5c4593ffa97a7961c7bdf8183a909361434a18f916767bcc4c9`。
