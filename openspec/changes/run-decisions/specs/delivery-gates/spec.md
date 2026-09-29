## ADDED Requirements

### Requirement: GAT-06 必要 CI 與非成功狀態

必要 check 的集合 SHALL 宣告在 repo 根目錄的政策檔 `workflow.yaml`（不是 GitHub workflow），列明 check 的名稱、app 與 workflow；政策 SHALL 經人工 `policy_change` 核准，並綁定政策檔的 digest。範例名稱不構成核准。本 repo 的必要 check 是 `unit-linux`（D53）。

本機測試與每個必要 CI job SHALL 套用同一套收集、skip 與失敗政策：收集數為 0、任何不是由 `only_on` 在非所屬平台產生的 skip、xfail 與 xpass，都 SHALL 使測試 session 失敗；skip reason 的文字 SHALL NOT 作為平台條件的證據。

#### Scenario: AC-G21 本機與 CI 同一測試政策
- **WHEN** 測試 session 收集到 0 個測試，或出現不是由 `only_on` 在非所屬平台產生的 skip，或出現 xfail、xpass
- **THEN** 本機與 `unit-linux` 的測試 session 都以失敗結束；兩者執行同一個測試命令，政策來自同一份設定

#### Scenario: AC-G22 必要 check 政策需要核准
- **WHEN** `workflow.yaml` 宣告了必要 check，但沒有綁定目前 digest 的人工 `policy_change`，或檔案內容在核准後被改動
- **THEN** `status` 顯示政策未核准或 digest 不符，不把宣告的集合當成已核准的政策；人以 `policy_change` 記錄目前的 digest 後才視為核准
