# 比較檢核表（生成前固定）

評估對象是本次兩份生成稿，不推論工具的普遍勝率；相同來源、同一父層模型預設、獨立上下文，不指定不同 model 或 reasoning。未做 token／速度 benchmark。

- C01：兩層工作範圍、三角色同層、唯一 controller、明確授權才代理安排。
- C02：一個 feature 一個 PR；task DAG／scope／AC／artifact版本可交接；原生檔名不強改。
- C03：D11 design+plan一次批准；新scope/spec/AC與設計缺陷回人；無auto merge/close/release/deploy。
- C04：Adopt先核owner／未知writer與既有證據，不重做已核准成果；P03 trial暫停。
- C05：G1先於G2；G2/G3並行，三者同版本成立才Pass；執行成功與gate verdict分開。
- C06：歷史Red可早於head，finalGreen/regression適用整合head；缺歷史證據不偽造。
- C07：純文件N/A需獨立eligibility先於G1，設定／migration／testcode依行為。
- C08：G2獨立assignment/session完整diff，作者branch唯讀；局部review不取代G2。
- C09：required checks空集合／missing／pending／cancelled／unknown／來源／attempt／衍生SHA適用性。
- C10：head/base/spec/design/plan/policy失效與Pass前刷新，accepted版本不可移植。
- C11：穩定finding、localJSON權威、closure僅reviewer或human、dispute一次覆核。
- C12：同版本review/CI收齊合併批次，三輪correction、infra各兩次extra retry、4hactive不重置。
- C13：先持久化後發布，PR詳細＋issue摘要連結、outbox／duplicate／unknown read-back。
- C14：assignment/result身份與evidence來源/digest可核對；結果衝突非最後寫入者獲勝。
- C15：restart/reconcile、ownership/locks、防第二run、通知遺失不重做、corruptstate不可空白初始化。
- C16：Projectaccepted與merged區分，相依feature只準備不提早實作；Retro候選一次且不自動改規範。
- C17：runtime選型／timeout／check例外等未決保持未決，不把skill效果或probe當實證。
- C18：fake故障測試與真實finding→fix→re-review E2E分開，成功／失敗皆可觀察。

標示：明確＝可直接找到規則及可觀察結果；部分＝有方向但缺可判定條件或重要分支；缺漏＝找不到；衝突＝與共同baseline相反。逐項附原文位置，不用檔案數或長度充當品質。

除coverage外比較：讀者快速理解、需求/設計/待決分離、AC可直接轉測試、任務拆分需補的資料、版本修改影響定位。後兩項只看規格交接，不因其中一方未生成plan而扣分。
