# 外部 skills 的來源

這裡的 skills 原樣拉自上游，只在每個來源的根目錄放上它的 `LICENSE`，不改內容。`setup.sh --update` 會照下表的 commit 重新拉；要換版本，先改這張表的 commit。

| 來源 | repo | 上游路徑 | 本地位置 | commit | 授權 |
| --- | --- | --- | --- | --- | --- |
| mattpocock | mattpocock/skills | skills | skills/third-party/mattpocock | c55ee46073ed923f86ce59a5eb3b6d895095d1b7 | MIT，Copyright (c) 2026 Matt Pocock |
| superpowers | obra/superpowers | skills | skills/third-party/superpowers | 8ca22dba9a94f28898bbce59f2537ff4d87c747d | MIT，Copyright (c) 2025 Jesse Vincent |

OpenSpec 不在這裡：它是 CLI，它的 skills 由 `openspec init` 產生；`setup.sh` 只檢查 CLI 的版本。Superpowers 若已經以 Claude Code plugin 安裝，`setup.sh` 不會再把它的 skills 裝進 `~/.claude/skills`，避免重複。
