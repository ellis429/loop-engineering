# Planning preflight：工具與實作模型

日期：2026-09-27。只查能力、版本與本機技能來源；未建立 worker、未提交模型推理任務、未修改產品程式或 GitHub。此報告不是 TDD／gate／E2E 證據。

| 查核 | 觀察 | 限制 |
| --- | --- | --- |
| `/usr/local/bin/orca --version` | 1.4.212，exit 0；stderr 有 Electron codesign `task_name_for_pid` 診斷 | 舊 1.4.209 probe 不自動適用新版；本次未測 live dispatch |
| `orca orchestration worker-start --help` | 支援 Claude 的 opaque `--model <id>`，`--effort` 需同時指定 model；不能與重用 `--terminal` 合併 | CLI surface 不證明帳號可用該模型或實際 model 一致 |
| `worker-read --help` | `auto`／`transcript`／`terminal` 與分頁 cursor；cursor 綁定 source | 要核對 source 切換；不是 completed 證據 |
| Claude Code | `/Users/johnson.chiang/.local/bin/claude` 2.1.283；支援 model、stream-json、json-schema、print／resume | 本輪未登入或更改帳戶設定，不輸出 credentials |
| Claude model discovery | 依 Orca bundle `claude-model-list-probe.js` 發 `list_models` control request，exit 0／success，回 `default`、`opus`、`claude-fable-5-1[1m]`、`sonnet`、`haiku`，均未標 disabled | 沒有提交 user prompt／API turn；catalog 的 `opus` family alias 不足以證明 Opus 5.5 的實際執行 |
| Opus 5.5 正式 ID | `claude-opus-5-5`，來源見下方官方文件 | 派工時需驗證帳號實際可用、原生回報 model 與指定一致；未通過就明列缺口，不 fallback |
| OpenSpec | 1.13.1；repo schema 為 spec-driven；instructions 指向 change 內 design.md／tasks.md | instructions 不等於 artifacts 已完成或已批准 |
| Python | shell 的 python3 是 3.10.10；`uv python list --only-installed` 查到已裝 cpython 3.12.13 | uv 需讀取其 cache，本次依 sandbox 流程取得讀取授權；未下載 Python 或改全域版本 |
| GitHub remote | orca-delivery 的 `git remote -v` 無輸出 | 後續真實 PR／CI 需選定及設定目標；本輪未建立 remote／issue／PR |

官方來源：[Claude Opus 5.5](https://platform.claude.com/docs/en/models/opus-5-5/overview)。本機命令和已安裝原始碼優先用來界定當前 CLI surface；官方 model ID 不能取代實測。

本機 skill 內容以 [skill fingerprints](skill-fingerprints.json) 記錄，不推定 Matt 安裝版本號。Superpowers 路徑含 6.3.0；Writing Plans 的原生交棒是 subagent-driven-development／executing-plans，與單一 controller 的接合需明示改動。OpenSpec 的 apply 原生會遍歷 tasks；派工時需以允許 task IDs／scope 作明示受限入口，不能讓每個 worker 自行跑整份 plan。

查閱 grill-with-docs、code-review、TDD 等是比較其契約，未在本輪啟動它們的 interview、subagents 或 implementation 流程。兩個選型問題已向使用者提出；controller 實作者指定 Opus 5.5 已明確，但不因此視為 Q-METHOD 或 G2 runtime 已回答。
