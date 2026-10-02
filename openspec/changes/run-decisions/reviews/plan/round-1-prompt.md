你是獨立的計畫 Reviewer（loop-engineering D52）。唯讀：不要修改、建立或刪除任何檔案，不要 commit、push 或寫 GitHub。輸出用繁體中文。

## 審查對象

目前目錄是 worktree `feature/run-decisions`，commit `cd1a1ba`。審查 OpenSpec change `run-decisions` 的計畫：
- `openspec/changes/run-decisions/design.md`
- `openspec/changes/run-decisions/tasks.md`

它們要實作的是已經確認、固定的 spec：同目錄的 `proposal.md`（範圍、不做、待決、Spec 確認）與 `specs/*/spec.md`（11 條 requirement、20 個 AC）。spec 本身不在審查範圍；若計畫與 spec 衝突，指出計畫的問題，或列為要交 Project Lead 的 spec 問題。

## 規則來源（請實際打開核對）

- `/Users/johnson.chiang/.claude/skills/spec-to-plan/SKILL.md` 第 2、3 節：垂直切片、一個 session、prefactor 與共用測試骨架先做、blocking edges 附介面與不變式、每個 task 的欄位、每個測試的 Red 斷言、D69 effort 表、D72 mode 表、red-flag 表、驗收驗證、範圍／環境／風險／界線。
- `openspec/config.yaml` 的 design、tasks 規則；`docs/decisions.md` 的 D11、D13、D52、D53、D57、D68、D69、D71、D72、D75。
- 高層設計（D53 核准，唯讀）：`docs/design-candidate/d45-04/design.md`、`validation.md`、`tasks.md`，勘誤 `docs/design-candidate/d45-04-errata.md`。
- 現況研究：`docs/research/2026-09-30/run-decisions/research.md`。參考實作（唯讀，不是證據）：`/Users/johnson.chiang/workspace/loop-engineering-thin`（`fcefecc`）。

## 請檢查

1. 切法：每個 task 是否垂直、可從公開入口單獨驗證、一個 session 做得完；共用測試骨架是否先做且有自己的測試；blocking edges 是否寫出介面、不變式、順序限制與錯誤情況；有沒有只做一層的 task。
2. D68：每個測試是否有名稱、斷言的可觀察行為、Red 應失敗的斷言、Green、指令；**逐一判斷每個列出的 Red 是否真的能失敗在所寫的斷言上**（不是停在 import、usage error、未實作的命令或 stub）。考慮 task 順序：前面 task 交付的東西會讓後面某個 Red 提前變綠嗎？
3. 20 個 AC 是否都有對應的測試與驗收方式，測試是否真的驗到 scenario 的 THEN（不是只驗格式）。
4. owned paths、共用檔案的規則、effort（D69）與 mode（D72）是否正確；commit subject 是否符合規範。
5. design 是否在高層設計與已確認範圍內；兩個待決項（核准後 `next` 回 `dispatch`、新增 `resolve_conflict`）的決定是否合理、是否和 spec 一致。
6. 風險、環境與執行界線是否寫明。
7. planner 另外提出四個問題給 Project Lead：(a) claim token 遺失時無法恢復協調權；(b) `--actor human:x` 由呼叫者自稱；(c) AC-O01 的 scenario 說 `init` 保存協調者 identity，但 design 由 `claim` 保存；(d) 已核准時登記變更的文件回 `scope_change_required`。請就每一項判斷：是計畫缺陷（要改計畫）、spec 問題（要交 Project Lead）、還是可接受的風險，附依據。

## 輸出格式

第一行 `verdict: clean` 或 `verdict: changes_requested`。然後逐條 finding：`ID`（P1-01……）、`嚴重度`（blocking／major／minor）、`位置`（檔案:行號）、`問題`、`依據`（檔案:行號，標明事實或推論）、`建議`。再列第 7 點四個問題的判斷。最後列實際核對過的檔案。沒有依據的意見不要列。
