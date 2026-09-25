# Orca Delivery

從一個已選定的 feature issue 到 PR Pass 的交付協作領域。

## Language

**Project spec**:
整體目標、共用契約、系統限制與跨功能保證的權威需求集合。

**Feature spec**:
引用 project spec，定義單次交付的可觀察行為、範圍、驗收條件與依賴的需求集合；可位於 feature ticket 內文或其引用文件。

**Feature ticket**:
追蹤一個可獨立驗收功能切片的 issue，包含或引用其 feature spec。
_Avoid_: Task ticket（用於指稱 feature 時）

**Implementation task**:
Feature plan 中具有 scope、依賴與驗證條件的派工單位，多個 tasks 可共同交付一個 feature PR。

**Delivery run**:
針對一個已選定 feature ticket，從規劃、實作到 PR Pass 或需要人工裁決的持續交付紀錄。

**Attempt**:
同一 implementation、review 或診斷 task 的一次執行；重試產生新的 attempt，保留先前紀錄。

**Orca Dispatch**:
Orca 指派給 worker 的一次具有效執行權的 task attempt，與 delivery attempt 以識別碼對應。

**Gate evidence**:
可讀取、可追溯且適用於指定交付版本的驗證紀錄，是 gate 判定依據。

**Blocking finding**:
尚未經 reviewer 覆核解除或人工明確裁決、會阻止 review clean 的問題。

**Correction round**:
同一適用版本的 review / CI 結果整理成修正批次後，經修正、驗證與重新審查的一輪。

**PR Pass**:
目前交付版本同時滿足實作/TDD、獨立 review 與必要 CI 三個 gates 的品質結論。
_Avoid_: Agent done、CI green（用於指稱全部通過時）

**Blocked**:
交付需要人工決策或外部條件變更才能正確續行的狀態，包含具體原因、證據與待決事項。
