# 產生 AI Agent 重建備份（Prompt A — 可重複下達）

> 這是「Prompt A」：一份穩定、可以重複下達的產生指令，本身不含大量原始碼
> 或規則全文。把這份檔案整份貼給任何一個已經載入
> `~/claude-workspace/.claude/CLAUDE.md`（透過 `~/.claude/CLAUDE.md` 的
> `@import`）的 Claude session 當作一則訊息，就能觸發它產生最新版的
> 「Prompt B」——依日期版本化、包含完整重建內容的快照檔案。
>
> 固定位置：`~/claude-workspace/dev/init-prompt/generate_backup_prompt.md`
> 本檔案只在「產生流程的邏輯本身」有變動時才需要修改，平常規則/dev
> 工具/skill 有變動時不必同步更新這份檔案。

## 給收到這則訊息的 Claude 的指令

請依照 workspace 主規則檔（`~/claude-workspace/.claude/CLAUDE.md`）
「八、備份與重建機制」章節的完整規格執行；若因故無法存取那份規則檔，
改用下方「備援複本」章節的精簡版本執行，兩者精神一致。

### 執行步驟
1. **重新掃描目前實際檔案系統狀態**，不得憑記憶回填、不得沿用先前產生
   過的舊版 Prompt B 內容當作已經是最新狀態。掃描範圍：
   - `~/.claude/CLAUDE.md` 與 `~/claude-workspace/.claude/CLAUDE.md`
   - `~/claude-workspace/.claude/memory/*.md`
   - `~/claude-workspace/.claude/wrappers/*`
   - `~/claude-workspace/dev/**`（排除 `.venv/`、`node_modules/`、
     `__pycache__/`、快取型暫存資料夾、`.DS_Store`、單次查詢用的
     暫存輸入檔）
   - `~/.claude/skills/{使用者個人建立的 skill}/SKILL.md`
   - `~/Library/LaunchAgents/com.claudeworkspace.*.plist`
   - `~/claude-workspace/README.md`
2. 逐項嵌入完整內容（規則檔、memory、wrapper script、dev/ 原始碼、
   skill、plist、README 皆為**完整內容**，不是摘要），並排除機密與
   可重抓資料（見下方「一律排除」）。
3. 以今天日期（ISO 8601、+08:00 時區）為檔名前綴，寫入新檔案：
   `~/claude-workspace/dev/init-prompt/backups/{YYYY-MM-DD}_backup_prompt.md`
   （同一天內重複產生則覆寫當天那份，不動更早的歷史版本——這樣使用者
   可以保留多個時間點的快照）。
4. 依「紀錄義務」寫入 `logs/activity_log.jsonl`（topic 填 `general` 或
   `dev`）與 `memory/dev.md` 索引更新（記錄本次涵蓋的專案清單與本次
   版本檔案位置，不需要把 Prompt B 全文複製進 memory）。
5. 完成後告知使用者本次版本檔案位置，並詢問是否要透過 SendUserFile／
   下載等方式取得一份存放在這台機器以外的地方（雲端硬碟、Email 附件
   等）——這份檔案的意義就在於「離開這台機器也要能用」。傳送前依
   「終端機權限與資安邊界」b 項，先讓使用者知道會包含哪些內容類別
   （不需要逐字念出全文）才能送出。

### 一律排除（不寫入 Prompt B，也不得要求使用者貼明文）
- `logs/activity_log.jsonl`、`logs/archive/`（累積型日誌，重建後重新
  開始記錄即可）
- `data/{topic}/` 底下可重抓的歷史資料（股價、新聞、universe 快取等，
  用 dev/ 對應腳本重新抓取即可）
- `outbox/`（一次性產出，本來就會自動 3 天清除）
- 各專案 `.venv/`、`node_modules/`、`__pycache__/`、快取/冷卻狀態檔
  （由套件管理器重建或自然重新累積）
- Keychain 內密鑰明文（`telegram-bot-token`、`telegram-chat-id` 等）：
  一律由使用者在新機器上手動重新輸入，Prompt B 只能提醒步驟
- `claude_desktop_config.json`（本來就只在使用者確認後才建立，且不含
  明文）
- 訓練/模型用大型資料檔、螢幕截圖、`.DS_Store` 等系統雜項檔案

---

## 備援複本（若 workspace CLAUDE.md 無法存取時使用）

Prompt B 至少必須包含以下 11 個部分，逐項完整嵌入（非摘要）：
1. 目錄結構總覽
2. `~/.claude/CLAUDE.md` 完整內容
3. `~/claude-workspace/.claude/CLAUDE.md` 完整內容
4. `.claude/memory/` 底下所有 `*.md` 完整內容
5. `.claude/wrappers/` 底下所有 wrapper script 完整內容
6. `dev/` 底下所有專案原始碼（逐檔，附相依套件安裝方式）
7. `~/.claude/skills/` 底下個人 skill 的 `SKILL.md` 完整內容
8. `~/Library/LaunchAgents/` 底下 `com.claudeworkspace.*` plist 完整內容
9. `README.md`
10. 排除項清單（見上方「一律排除」，並說明原因）
11. 重建步驟 Checklist（建目錄 → 寫入兩份 CLAUDE.md → 寫入 memory →
    寫入 wrappers 並 `chmod +x` → 依專案建立 venv/npm 並安裝套件 →
    寫入 dev/ 原始碼 → 建立 launchd plist 並 `launchctl bootstrap` →
    ⚠️ 提醒使用者手動在 Keychain 建立密鑰 → ⚠️ 確認後才建立/合併
    `claude_desktop_config.json` → ⚠️ 確認測試訊息內容後端對端測試
    Telegram 發送 → 寫回 activity_log.jsonl／memory → 向使用者回報
    完成狀態）。

---

## 維護原則
- 平常新增主題、改規則、新增/修改 dev/ 專案、新增 skill、新增 launchd
  排程時，**不需要**同步更新這份 Prompt A，避免每次小改動都觸發一次
  大量重寫；只有使用者明確要求「產生/更新備份」，或直接貼上這份
  Prompt A 時，才執行上方「執行步驟」產生新版 Prompt B。
- 若距上次備份已久、期間又有大量異動，可以主動提醒使用者「要不要重新
  產生一份備份」，但不得未經同意就自行執行。
- 若這份 Prompt A 本身的「產生流程邏輯」有變動（例如新增了必須涵蓋的
  項目類別），才需要同步更新 workspace CLAUDE.md「八、備份與重建機制」
  章節與本檔案，兩者維持一致。
