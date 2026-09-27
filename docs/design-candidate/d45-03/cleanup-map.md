# Cleanup map（D50 候選 design-03）

> 來源為舊 S1 的 `src/delivery/`，commit `4ce1110`；另有未覆核的 `5d334d5`，只作參考。逐項的原始碼缺陷證據沿用 [D45-02 cleanup map](../d45-02/cleanup-map.md) §3，本文不重述。

## 1. 規則

- **新樹只有 `loopctl` 一套入口**（D46）：
  - 不反向 import 舊碼、不用舊的 PYTHONPATH、不建立 `legacy/`；
  - 以 `import delivery` 必須失敗的測試，加上乾淨安裝的 smoke 來確認。
- **提取的紀錄單位是「一次提取 commit」或「一條行為規則」**：寫入 `docs/implementation/extraction-log.md`，每筆記錄：
  - 來源 commit 與路徑；
  - 適用的舊 findings；
  - 改動理由；
  - 新的驗證（Red／Green 證據）。
- **不採用**：逐 symbol 的 manifest、逐測試案例的 hash 表、每個模組都要有生產 caller 的硬 gate。模組的 caller 盤點只當 review 輔助。
- **依賴方向要保留**：核心不 import `subprocess` 或 tools。這條以測試固定。
- **舊測試逐案評估**：
  - 合格的行為案例可以選擇性改寫帶入；
  - 平台專屬的案例退役；
  - 舊的 pass 數不當新證據。
- **刪除舊碼不等於關閉 finding**：17 項 S1 findings 各自仍 open，要經新證據與獨立覆核才能關。

## 2. 第一片的行為去向

| 舊模組 | 第一片 | 新驗證（task） |
| --- | --- | --- |
| `store` | 取用原子寫入與 link 協定；改為 history-first＋typed refs | 2.1 |
| `versions` | 取用 VersionSet 與依賴矩陣；G3 一律重新觀察 | 6.1、6.2 |
| `gates` | 取用 G1／G2／G3 的判定；補 R11、R13、R14、R15、R17 | 3.1、5.1、6.1 |
| `findings`、`correction` | 取用 registry 與 batch 規則；補 R16 與文件缺陷的修正資格 | 5.1 |
| `budget` | 取用區間聯集與 gap 計入 | 7.1 |
| `results` | 取用身份核對、去重、衝突處理 | 2.3 |
| `runner` | 取用 snapshot 與 junit 分類；只接受 `command_id` | 3.1 |
| `decisions`、`cli`、`controller` | 重寫：只支援第一片的 decision kinds，其餘回 `unsupported` | 2.2 |
| `publication` | 重寫發布順序與 marker 查回 | 6.2 |
| `integration` | 第一片不帶入：單一 worktree 序列工作，不需要跨 worktree 整合；CAS 規則留到 S2 平行 writer | — |
| `retro` | 延後到 S2 | — |
| `loop`、`outbox`、`authority`、`events`、`resume`、`sandbox`、`__init__` | 不帶入（D41／D50），歷史保留在 Git 與 PR #2 | — |
