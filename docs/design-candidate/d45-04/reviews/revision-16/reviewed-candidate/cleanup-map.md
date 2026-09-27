# Cleanup map（候選 design-04；revision-16）

> **作者提交狀態**：revision-16；目前的 review 狀態以 [README](README.md) 為準。revision-15 只更新驗證引用、提取紀錄的擁有方式，並說明新 lineage 不含舊碼；提取規則不變。

> 來源：舊 S1 的 `src/delivery/`，commit `4ce1110`；另有未覆核的 `5d334d5`，只作參考。逐項的原始碼缺陷證據沿用 `review-09/cleanup-map.md` §3。
> 相對於 outputs-03，本版只改驗證引用與 AC audit 的注意事項，D50 的刪減不變。revision-10 另外移除了逐測試 owner 核對的 script。revision-12 只更新驗證引用；新的 `tests/conftest.py` 測試政策是新寫的 test-only 設定，不從舊碼提取，也不是逐測試 registry。

## 1. 規則

- **單一入口**：新樹只有 `loopctl` 一套入口（D46）。
  - 不反向 import 舊碼、不使用舊的 PYTHONPATH、不建立 `legacy/`。
  - `import delivery` 必須失敗。
  - 以乾淨安裝的 smoke 確認（dist-smoke）。
- **舊碼的取得方式** [R15]：新 branch 從 `origin/main` 出發，lineage 不含 `4ce1110`（tasks T0.1）；需要參考舊碼時以 `git show 4ce1110:<path>` 讀取，不 checkout 舊 branch 到新 worktree。
- **提取的紀錄單位**：一次提取 commit，或一條行為規則，由做提取的 task 追加到 `docs/implementation/extraction-log.md`（只追加自己的一節；tasks 共用檔案表）。每筆記錄：
  - 來源 commit 與路徑；
  - 適用的舊 findings；
  - 改動理由；
  - 新的驗證，引用 validation 矩陣的列 ID。
- **不採用**：
  - 逐 symbol 的 manifest；
  - 逐測試案例的 hash 表；
  - 每個模組都要有生產 caller 的硬 gate（caller 盤點只當 review 的輔助）。
- **依賴方向要保留**：核心不 import `subprocess` 或 tools，這條以測試固定。
- **舊測試**：
  - 逐案評估；合格的行為案例可以改寫帶入；
  - 舊的 pass 數不當新證據；
  - 必要測試依 validation §0 執行：本機適用的套件是 G1 的條件；遠端必要的 CI 由 G3 判定。
- **舊碼通過測試不等於正確**：AC audit 對舊程式實際重現了 S1-R11：`evaluate_g1([], …)` 回 passed。任何 gate 規則的提取，都必須先以 g4 這類新反例驗證。
- **刪除舊碼不等於關閉 finding**：17 項 S1 findings 各自仍 open。

## 2. 第一片的行為去向

| 舊模組 | 第一片 | 新驗證（矩陣列） |
| --- | --- | --- |
| `store` | 取用原子寫入與 link 協定；改為 history-first＋typed refs | s1–s3、s6 |
| `versions` | 取用 VersionSet 與依賴矩陣；G3 一律重新觀察 | h6、h7、u2 |
| `gates` | 取用 G1、G2、G3 的判定；修正 R11、R13、R14、R15、R17；Red 要求 scope、對應到 attempt 的捕捉紀錄、lineage 三項資格，改變行為的修正也需要 Red；Green 在 H 的乾淨 checkout；G3 只認 head、只認 PR 事件，每個 run 取最新 attempt、同一 H 的 run 都計入 | g1–g15、g3b、r1、h1–h5、h4a–h4e、h12 |
| `findings`、`correction` | 取用 registry 與 batch 規則；修正 R16；文件缺陷可列為修正項 | r2–r10、r13、r14 |
| `budget` | 取用區間聯集與 gap 計入；新增角色 timeout 路徑 | b1–b6 |
| `results` | 取用身份核對、去重、衝突處理 | w6、w7 |
| `runner` | 取用 snapshot 與 junit 分類；只接受 `command_id` | g3、g9 |
| `decisions`、`cli`、`controller` | 重寫；未支援的 kind 回 `unsupported` | d1–d6、d7a、d8–d10、s7 |
| `publication` | 重寫發布順序、內容與讀回；Pass package 由狀態投影 | p1、p4、p5、p7 |
| `integration` | 第一片不帶入：單一 worktree 序列執行；平行 writer 留到 S2 | — |
| `retro` | 延後到 S2 | — |
| `loop`、`outbox`、`authority`、`events`、`resume`、`sandbox`、`__init__` | 不帶入（D41、D50）；歷史保留在 Git 與 PR #2 | — |
