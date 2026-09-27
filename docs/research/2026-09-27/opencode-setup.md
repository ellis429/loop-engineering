# OpenCode 本機準備與無推論驗證

日期：2026-09-27。本頁保留早期安裝與無推論 API 查核；以下認證／能力敘述為當時快照。後續 ChatGPT OAuth、GPT-6 Luna 真實交接與明確 session resume 已通過，見 [Herdr H0](herdr-setup.md)。Claude 本機接法另依 D44 使用 Herdr＋Claude Code；未取得產品 gate 結論。

## 安裝

使用 [官方 v1.18.32 release](https://github.com/anomalyco/opencode/releases/tag/v1.18.32) 的 Darwin ARM64 binary，下載檔 SHA256 與 release metadata 相符。安裝到 `~/.opencode/bin/opencode`，由既有 PATH 上的 `~/.local/bin/opencode` symlink 提供命令；`opencode --version` 回傳 `1.18.32`。未修改 shell rc、Claude／Codex 設定或搬移 credentials。

[安裝 receipt](opencode-setup/install-receipt.json) 保存版本、路徑與檔案 digest。

## 已實測

以 `serve --pure` 啟動 localhost 暫時服務，啟用隨機 Basic auth、禁止 agent 工具、停用分享及自動更新。密碼僅存在 process 記憶中。未發出 prompt／inference。

- `/global/health` 回傳 healthy 與正確版本。
- 讀取原生 `/doc`、provider 與 auth 方法，僅保存非機密的選取欄位。
- 建立 session，讀回 metadata 與空 messages。
- 停止 server，再啟動並讀回同一 session。
- probe 完成後停止兩個暫時 server。

[能力 evidence](opencode-setup/capabilities.json) 保存結果與 HTTP 回應 digest。實測 API 應與 [官方 server 文件](https://opencode.ai/docs/server/) 交叉核對；CLI 實際預設 port 為 0，不能直接套用文件的 4096 假設。

## 尚未證明

`auth list` 顯示 0 個保存的 credentials；runtime 另偵測到既有環境 providers，這不是已授權或可用模型的證據，未對其推論。`--pure` 查得 OpenAI 提供 ChatGPT browser／headless OAuth 與 API key 方法；Anthropic auth methods 為空，不能據此推論 API key 不支援或保證 Claude Max OAuth 可用。

catalog 有 `claude-opus-5` 等 ID，未核實 Opus 5.5；不能以近似名称替換指定模型。模型登入／推論、actual model、結構化結果、獨立 Reviewer 工具隔離及完整 delivery loop 均尚未驗證。Session 重啟讀回不等於任務自動恢復已實作。

依 D39，本次 controller 開發先協調 Opus 與 GPT agents；OpenCode 登入不阻擋這個 bootstrap。產品的 OpenCode 預設路徑仍須在 adapter／E2E 階段驗收。OpenCode 自身的儲存實作不改變 controller 採 JSON／YAML 的 D14。
