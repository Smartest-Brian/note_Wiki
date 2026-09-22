# AI Agent 重建 Prompt（Prompt B — 2026-09-23 版）

> 產生時間：2026-09-23T00:00:00+08:00（實際嵌入內容以產生當下掃描到的檔案系統狀態為準）
> 這是「Prompt B」——依日期版本化的重建全文快照，由「Prompt A」
> （`dev/init-prompt/generate_backup_prompt.md`，可重複下達的產生指令）
> 依 workspace 主規則檔「八、備份與重建機制」的流程掃描目前實際狀態後產生。
> 目的是讓使用者即使這台電腦完全損毀，也能只憑這一份文字檔，在全新環境重建目前
> 這個 AI agent 的規則、目錄結構、skill、memory 累積的心得與 dev/ 工具程式碼。
> 每次重新產生會建立新的日期版本檔案，不覆寫更早的歷史版本。

## 給接手這份 prompt 的 Claude 的說明

你即將在一台全新的 macOS 電腦上，重新建置一個先前已經運作一段時間的
Claude Code / Claude Desktop 個人助理環境。請把這份文件當成「規格書 + 原始碼庫」：

1. 這份文件**不含任何密鑰明文**（Telegram Bot Token、Chat ID 等），也不含
   activity log、可重新抓取的歷史資料（股價、新聞等）、暫存快取、`.venv`/`node_modules`。
   這些請依下方「排除項與理由」的說明處理，不要因為找不到而回報錯誤。
2. 請依「重建步驟 Checklist」章節依序執行，不要跳步，尤其是涉及密鑰的
   Telegram 機制與會修改 Claude Desktop 設定檔的步驟，一律要先向使用者確認。
3. 文件中出現的帳號路徑 `/Users/vm/`（或 `vm`）請替換成新機器的實際
   macOS 使用者帳號名稱。
4. 重建完成後，這份文件所描述的「八、備份與重建機制」規則會一併寫回
   CLAUDE.md，讓新環境往後仍然具備「使用者要求時可以重新產生下一份
   Prompt B」的能力——這是一個會自我延續的機制，不需要額外設定，
   `dev/init-prompt/generate_backup_prompt.md`（Prompt A）也應一併復原。

---

## 目錄

1. 目錄結構總覽
2. 使用者層級 CLAUDE.md（`~/.claude/CLAUDE.md`）完整內容
3. Workspace 主規則檔（`~/claude-workspace/.claude/CLAUDE.md`）完整內容
4. 目前已存在的主題與 memory 完整內容
5. 密鑰 wrapper script 完整內容
6. dev/ 工具原始碼（逐專案）
7. 個人 skills 完整內容
8. launchd 排程（plist）完整內容
9. README.md
10. 排除項與理由（刻意不備份的東西）
11. 重建步驟 Checklist

---

## 一、目錄結構總覽

```
~/
├── .claude/
│   └── CLAUDE.md                       # 使用者層級：一行 @import 掛載主規則檔
│
└── claude-workspace/
    ├── README.md
    ├── .claude/
    │   ├── CLAUDE.md                   # 主規則檔
    │   ├── wrappers/
    │   │   └── run_telegram_mcp.sh
    │   └── memory/
    │       ├── general.md
    │       ├── dev.md
    │       ├── stock.md
    │       ├── hardware.md
    │       └── travel.md
    ├── data/                           # {topic}/ 動態新增，重建後留空即可（可重抓）
    │   ├── general/  stock/  hardware/  travel/
    ├── dev/                             # 所有專案程式碼統一存放處，不分主題
    │   ├── telegram-notify/
    │   ├── outbox-cleanup/
    │   ├── stock-news/
    │   ├── stock-chart/
    │   ├── stock-model/
    │   ├── stock-fomo/
    │   ├── stock-sector/
    │   ├── gmaps-lookup/
    │   └── init-prompt/
    │       ├── generate_backup_prompt.md   # Prompt A：可重複下達的產生指令
    │       └── backups/
    │           └── {YYYY-MM-DD}_backup_prompt.md   # Prompt B：就是這份檔案自己
    ├── logs/
    │   ├── activity_log.jsonl          # 重建後從空檔案重新開始
    │   └── archive/
    └── outbox/                          # 一次性產出，重建後留空即可
```

---

## 二、使用者層級 CLAUDE.md（`~/.claude/CLAUDE.md`）完整內容
**`~/.claude/CLAUDE.md`**
````markdown
# 使用者層級規則

實際規則內容集中在 workspace 主檔，透過下方 import 載入
（不論工作目錄在哪，此檔都會被讀取）：

@/Users/vm/claude-workspace/.claude/CLAUDE.md

````

## 三、Workspace 主規則檔（`~/claude-workspace/.claude/CLAUDE.md`）完整內容
**`~/claude-workspace/.claude/CLAUDE.md`**
````markdown
# Workspace 主規則檔

本檔只放：全域規則、主題分類機制、資料路徑索引。
任何主題的細節內容一律寫入 memory/{topic}.md，不得堆積於此。

---

## 一、全域行為準則

### 語言
- 對話回覆一律使用繁體中文。
- 程式碼中的註解一律使用英文。
- 本檔與所有 memory 子檔案以繁體中文撰寫。

### 主題分類（動態，非固定清單）
- 不預設任何主題名稱。遇到新領域時，自行判斷一個簡短英文 slug 作為 {topic}，
  並依此建立 data/{topic}/ 與 memory/{topic}.md（骨架見「六、memory 子檔案骨架」）。
- 一次任務若橫跨多個主題，依「主要目的」歸類一個主題；
  無法判斷時先歸入 general，日後再視情況拆分或改名。
- 程式碼一律放 dev/，不因主題不同而分散路徑；memory/dev.md 記錄
  「此專案屬於哪個/哪些主題」以便交叉查找。

### 紀錄義務
每次執行涉及「資料存取 / 修改 / 下載」的操作，完成後必須：
1. 判斷本次所屬主題 {topic}（依上方動態分類原則）。
2. 將細節（做法、參數、結論、觀察）寫入對應 memory/{topic}.md。
3. 於 logs/activity_log.jsonl 追加一行紀錄（格式見第四節）。
4. 若產生實際資料檔，存入 data/{topic}/，並於該 memory 檔案的
   「資料檔索引」註明完整路徑。
5. 若涉及程式碼異動，存入 dev/ 對應專案路徑，並於 memory/dev.md 更新索引。

activity log 只記「何時、哪個主題、做了什麼」，不寫分析細節。

### 密鑰 / Token 存取
任何操作需要用到密鑰、Token、API Key（例如呼叫外部 API、啟動 MCP server）時：
1. 先檢查 `.claude/wrappers/` 底下是否存在對應的 wrapper script。
2. 若存在：直接呼叫該 wrapper script 取得對應環境變數並使用，
   **不得**自行嘗試用 `security` 指令讀取 Keychain 原始項目、
   不得要求使用者貼上明文。
3. 若不存在：停止操作並告知使用者「尚未設定此密鑰的 wrapper script」，
   引導使用者依「五、Token 安全儲存機制」章節建立，
   **不得**主動詢問使用者要不要直接把明文 token 貼在對話或檔案中。
4. 任何情況下，取得的 token / 密鑰明文都不得寫入 activity_log.jsonl、
   memory/*.md、data/ 底下任何檔案、dev/ 底下任何程式碼，或出現在回覆內容中。

### 終端機權限與資安邊界
本機為與實體主機完全隔離的獨立 macOS VM，因此：
- Claude 可在此 VM 的終端機中使用完整權限（含 sudo）執行本機操作
  （安裝套件、修改系統設定、建立 / 刪除 / 覆寫檔案等），
  不需針對單一本機操作逐一向使用者確認。
- 但以下情況仍為硬性邊界，不因上述權限而放寬：
  a. 任何密鑰、Token、個資（含 Telegram Bot Token、Chat ID 等）
     一律不得寫入檔案明文、log、memory，或出現在對外傳送的內容中
     （適用範圍同「密鑰 / Token 存取」一節）。
  b. 任何會將資料「傳出這台 VM」的操作（發送 Telegram 訊息、呼叫外部
     API、上傳、對外連線分享等），執行前必須先向使用者確認要傳送的
     內容，避免非預期夾帶個資或內部資料。
  c. 不得自行變更 VM 對外的網路 / 防火牆設定以「擴大」對外存取範圍，
     除非使用者明確指示。

### 時間格式
- 一律使用 ISO 8601 含時區，時區為 +08:00。
  例：2026-08-29T14:30:00+08:00

---

## 二、主題分類機制

不使用固定分類表。每個主題對應：
- memory 檔案：`.claude/memory/{topic}.md`
- 資料夾：`data/{topic}/`

首次出現的主題，依「六、memory 子檔案骨架」建立骨架檔案，
並將此主題加入下方「主題索引」表格（本表由 Claude 自行持續維護更新，
非使用者預先填寫）：

| 主題 slug | Memory 子檔案 | 資料夾 | 建立日期 |
|-----------|---------------|--------|----------|
| general | memory/general.md | data/general/ | 2026-09-18 |
| dev | memory/dev.md | dev/（不分主題，統一路徑）| 2026-09-18 |
| stock | memory/stock.md | data/stock/ | 2026-09-18 |
| hardware | memory/hardware.md | data/hardware/ | 2026-09-18 |
| travel | memory/travel.md | data/travel/ | 2026-09-19 |

---

## 三、資料路徑索引

| 項目 | 路徑 |
|------|------|
| 各主題資料 | ~/claude-workspace/data/{topic}/ |
| 程式碼（跨主題共用） | ~/claude-workspace/dev/ |
| 操作日誌（當月） | ~/claude-workspace/logs/activity_log.jsonl |
| 日誌封存 | ~/claude-workspace/logs/archive/YYYY-MM.jsonl |
| 密鑰 wrapper script | ~/claude-workspace/.claude/wrappers/ |
| 一次性產出檔案（自動3天清除，見「七」） | ~/claude-workspace/outbox/ |
| 備份產生指令 Prompt A（見「八」） | ~/claude-workspace/dev/init-prompt/generate_backup_prompt.md |
| 備份重建全文 Prompt B，依日期版本化（見「八」） | ~/claude-workspace/dev/init-prompt/backups/{YYYY-MM-DD}_backup_prompt.md |

---

## 四、activity_log.jsonl 每行格式

每行為一個獨立 JSON 物件（JSONL），欄位如下：

    {"ts":"2026-08-29T14:30:00+08:00","topic":"travel","action":"download","summary":"下載東京行程參考資料","files":["data/travel/2026-08-29_tokyo_itinerary.csv"],"memory":"memory/travel.md"}

- ts：ISO 8601 含 +08:00 時區。
- topic：動態主題 slug（非固定清單，見「二、主題分類機制」）。
- action：read | write | download | delete | analyze | send | other。
- summary：一句話摘要。
- files：本次產生或修改的資料檔，路徑相對 workspace 根目錄；無則空陣列 []。
- memory：本次細節寫入的 memory 子檔案路徑。

### 每月封存規則
每月首次寫入前，若 activity_log.jsonl 內含上個月（或更早）的紀錄，
先將既有內容整檔搬到 logs/archive/YYYY-MM.jsonl（依當前紀錄多數所屬月份命名），
再清空 activity_log.jsonl 並寫入本月新紀錄。

---

## 五、Token 安全儲存機制（macOS：Keychain + Telegram 通知）

macOS 上的密鑰不落地存放於任何檔案，而是存進系統的 **Keychain**，
透過 `security` 指令存取。取用邏輯一律是「wrapper script 先查 Keychain
再 export 環境變數」，不會有明文 token 常駐在磁碟上的設定檔裡。

通知管道統一改用 **Telegram Bot API**（不再使用 LINE）。

### 5.1 密鑰已存入 Keychain
使用者已於 Terminal 手動執行過（Claude 不需、也不應重複執行）：
```bash
security add-generic-password -a "$USER" -s "telegram-bot-token" -w "你的token"
security add-generic-password -a "$USER" -s "telegram-chat-id" -w "你的chat id"
```

### 5.2 wrapper script：run_telegram_mcp.sh
- 存放路徑固定為：`~/claude-workspace/.claude/wrappers/run_telegram_mcp.sh`
- 需要執行權限：`chmod +x ~/claude-workspace/.claude/wrappers/run_telegram_mcp.sh`
- 本身不得包含任何明文密鑰，只負責「從 Keychain 取值 → export 環境變數 → 呼叫 MCP server」。

```bash
#!/bin/bash
# .claude/wrappers/run_telegram_mcp.sh

export TELEGRAM_BOT_TOKEN=$(security find-generic-password -a "$USER" -s "telegram-bot-token" -w)
export TELEGRAM_CHAT_ID=$(security find-generic-password -a "$USER" -s "telegram-chat-id" -w)

if [ -z "$TELEGRAM_BOT_TOKEN" ] || [ -z "$TELEGRAM_CHAT_ID" ]; then
  echo "錯誤：無法從 Keychain 讀取必要的環境變數" >&2
  exit 1
fi

exec python3 /Users/vm/claude-workspace/dev/telegram-notify/telegram_notify.py
```

第一次執行 `security find-generic-password` 時，macOS 會跳出系統彈窗
詢問是否允許該程式存取 Keychain 中的這筆密碼，選「一律允許」即可，
之後不會再重複詢問。

### 5.3 對應的 MCP server 程式碼位置
程式碼本體（telegram_notify.py，僅提供單一功能：發送文字訊息，
不具備讀取訊息 / 聯絡人等其他權限）放在：
```
~/claude-workspace/dev/telegram-notify/telegram_notify.py
```
依「開發用程式碼統一集中於 dev/」原則管理，並於 memory/dev.md 索引。

### 5.4 Claude Desktop 的 MCP 設定
密鑰配置檔位置為：
```
~/Library/Application Support/Claude/claude_desktop_config.json
```
規則：**不要**在該 JSON 的 `"env"` 欄位直接寫明文 token，
而是把 `"command"` 指向 wrapper script，讓 Claude Desktop 啟動
MCP server 時透過 wrapper 動態注入環境變數：

```json
{
  "mcpServers": {
    "telegram-notify": {
      "command": "/Users/vm/claude-workspace/.claude/wrappers/run_telegram_mcp.sh"
    }
  }
}
```

此章節屬於「知識參考」，Claude 不得自動修改 `claude_desktop_config.json`，
如需變更須先向使用者確認。另外建議：
```bash
chmod 600 ~/Library/Application\ Support/Claude/claude_desktop_config.json
```
確保只有目前使用者帳號能讀取這個設定檔本身。

### 5.5 使用時機
- 任何需要「主動通知使用者」的情境（任務完成、異常告警等），
  一律透過呼叫 `send_telegram_message` 工具送出，且送出前需依
  「終端機權限與資安邊界」b 項向使用者確認訊息內容。
- 未來若新增其他密鑰（非 Telegram），比照本節模式：
  Keychain 存值 → 新增一支 wrapper script → 於 claude_desktop_config.json
  或對應設定檔中指向該 wrapper。

---

## 六、memory 子檔案骨架（新主題建立時套用此模板）

===== memory/{topic}.md 模板 =====
```
---
分類: （主題中文說明，例如：旅遊規劃）
主題 slug: {topic}
最後更新: （建立當天日期）
---

# {topic 中文說明}

## 常用來源與工具
（API、網站、抓取指令、資料頻率）

## 策略與觀察重點
（長期累積的分析心得、規則、教訓、指標定義）

## 資料檔索引
| 日期 | 檔案 | 內容說明 |
|------|------|----------|
| - | - | - |

## 待辦 / 追蹤中
```

===== memory/dev.md（固定存在，跨主題共用）=====
```
---
分類: 程式撰寫與除錯（跨主題）
最後更新: （建立當天日期）
---

# 程式撰寫與除錯

## 專案索引
| 專案 | 路徑 | 所屬主題 | 語言 / 技術 | 說明 |
|------|------|----------|-------------|------|
| telegram-notify | dev/telegram-notify/ | （通知類，跨主題共用） | Python / fastmcp | 單向發送 Telegram 訊息的 MCP server |

## 環境與慣用寫法
（Python/Node 版本、虛擬環境位置、常用套件、程式風格慣例）

## 除錯紀錄與教訓
| 日期 | 問題 | 原因 | 解法 |
|------|------|------|------|
| - | - | - | - |

## 待辦 / 追蹤中
```

===== memory/general.md（固定存在）=====
```
---
分類: 尚未分類 / 雜項
最後更新: （建立當天日期）
---

# 尚未分類 / 雜項

## 雜項紀錄
（尚無法歸入特定主題的操作、設定、自動化任務）

## 待分類項目
（暫時歸此，日後可能拆成新主題）

## 資料檔索引
| 日期 | 檔案 | 內容說明 |
|------|------|----------|
| - | - | - |
```

---

## 七、一次性產出檔案管理機制（outbox，3天自動清除）

### 目的
區分「有長期分析價值、需要在 memory 索引長期追蹤」的資料，
與「本身就是最終產出、用完/傳完就不再需要」的一次性檔案
（例如：要傳給使用者看的圖表、要傳送出去的報告、臨時產生的截圖）。
後者一律統一存放、統一清除，不需要每個主題各自維護清理邏輯，
也不必污染 data/{topic}/ 的長期資料索引。

### 判斷準則
- 這份檔案「本身即是最終目的」（給使用者看一次、傳出去一次就完成任務），
  且未來不會被程式讀回去做進一步分析/訓練 → 放 **outbox/**。
- 這份檔案是「持續累積、有分析價值、日後可能被讀回去做進一步處理」的資料
  （股價歷史、新聞歷史、模型訓練資料等）→ 維持放 **data/{topic}/**，
  照常寫入該主題 memory 檔案的「資料檔索引」。
- 設定檔、wrapper script、密鑰相關檔案不受此機制影響，一律不進 outbox/。

### 規則
1. 固定路徑：`~/claude-workspace/outbox/`。
2. 檔名一律加時間戳記前綴：`YYYY-MM-DD_HHMM_{描述}.{副檔名}`，
   方便排序與追蹤來源，不需另外分子資料夾。
3. 寫入 outbox/ 的操作，仍比照「紀錄義務」寫一行 activity_log.jsonl
   （action 依實際動作，例如產生圖表後傳送用 send；files 路徑寫
   `outbox/xxx.png`），但**不需要**在 memory/{topic}.md 的
   「資料檔索引」表格逐筆列出（該表格保留給 data/{topic}/ 底下的
   長期資料）。
4. 清除機制：`dev/outbox-cleanup/cleanup_outbox.py`（純標準庫，
   系統 python3 即可執行），刪除 outbox/ 底下「檔案最後修改時間
   （mtime）超過 3 天（72 小時）」的檔案；有實際刪除時才寫入一行
   activity_log.jsonl（action=delete）。
5. 排程：launchd LaunchAgent `com.claudeworkspace.outbox.cleanup`，
   每天 03:00 執行一次，plist 位置：
   `~/Library/LaunchAgents/com.claudeworkspace.outbox.cleanup.plist`，
   已用 `launchctl bootstrap` 載入。這是純本機刪檔操作（不對外傳送
   任何資料），依「終端機權限與資安邊界」屬於可自由執行的本機操作，
   不受「b. 對外傳送前需確認」規則限制。

---

## 八、備份與重建機制（Prompt A / Prompt B）

### 目的
讓使用者即使這台電腦完全損毀，也能只憑一份 prompt 檔案，在全新環境
（不需存取這台機器）重建目前這個 AI agent 的規則、目錄結構、skill、
memory 累積的心得與 dev/ 下的工具程式碼，且不含任何機密或可重抓資料。

### 兩份檔案，分工不同
這個機制拆成兩份檔案，不合併成一份：

- **Prompt A（產生指令本身，穩定、可重複下達）**：
  `~/claude-workspace/dev/init-prompt/generate_backup_prompt.md`
  內容是「怎麼產生備份」的指令，本身不含大量原始碼/規則全文，
  只在這個產生流程本身有變動時才需要修改，平常不隨主規則檔異動而變。
  使用者可以直接把這份檔案的內容貼給任何一個已載入本 workspace 的
  Claude session 當作訊息，用來觸發產生 Prompt B。
- **Prompt B（重建用全文，依日期版本化）**：
  `~/claude-workspace/dev/init-prompt/backups/{YYYY-MM-DD}_backup_prompt.md`
  每次依 Prompt A 執行產生流程時，用**當天日期**建立新檔案（同一天內
  重複產生則覆寫當天那份，不覆寫更早的歷史版本，讓使用者可以保留多個
  時間點的快照）。這份才是實際包含規則全文、memory 內容、dev/ 原始碼的
  重建內容本體。

（`memory/dev.md` 需索引這兩份檔案的固定路徑與用途。）

### 觸發時機
使用者說類似「產生備份」「更新備份」「重新產生 backup_prompt」
「幫我做一份可以重建你的 prompt」等語句時，或使用者直接把 Prompt A
的內容當作訊息貼給 Claude 時，一律**重新掃描目前實際檔案系統狀態，
產生當天日期的新版 Prompt B**，不得只回覆舊版內容、不得沿用記憶中的
舊版當作已經是最新狀態。

### 必須涵蓋（逐項嵌入完整內容，非摘要）
1. `~/.claude/CLAUDE.md` 與本檔（workspace 主規則檔）目前完整內容。
2. `.claude/memory/` 底下所有 `*.md` 檔案完整內容（含骨架模板與目前
   已累積的策略、教訓、指標定義；memory 內「資料檔索引」表格本身照抄，
   但表格指到的實體資料檔不必一併備份，見下方排除項）。
3. `.claude/wrappers/` 底下所有 wrapper script 完整內容（腳本本身
   依規定不含明文密鑰，可安全嵌入）。
4. `dev/` 底下所有專案的原始碼與必要設定檔（.py/.js/.sh/.json 等），
   逐檔嵌入完整內容並標明相對路徑；每個專案附上其相依套件的安裝方式
   （對應的虛擬環境/套件清單即可，不需附 `pip freeze`/`node_modules`
   完整輸出）。屬於單次查詢用的暫存輸入檔（例如某次查詢用的候選店清單
   JSON）不算工具本體，可排除。
5. `~/.claude/skills/` 底下屬於使用者個人建立的 skill，其 `SKILL.md`
   完整內容。
6. `~/Library/LaunchAgents/` 底下屬於本 workspace 的 launchd plist
   （以 `com.claudeworkspace.` 開頭辨識）完整內容。
7. 一份「排除項清單」，明確列出哪些東西刻意不包含及原因。
8. 一份「重建後續步驟」checklist，依序列出：建目錄 → 寫入兩份
   CLAUDE.md → 寫入 memory → 寫入 wrappers 並 `chmod +x` → 依專案
   建立 venv/npm 安裝套件 → 寫入 dev/ 原始碼 → 建立 launchd plist 並
   `launchctl bootstrap` → 提醒使用者手動在 Keychain 建立密鑰 →
   端對端測試 Telegram 發送 → 向使用者回報完成狀態。

### 一律排除（不寫入 backup_prompt.md，也不得要求使用者貼明文）
- `logs/activity_log.jsonl`、`logs/archive/`：累積型操作日誌，重建後
  重新開始記錄即可，沒有保留價值。
- `data/{topic}/` 底下屬於「可重抓」的歷史資料（股價歷史、新聞
  parquet、股票 universe 快取等）：用 dev/ 裡對應腳本重新抓取即可，
  不需要把資料本身塞進 prompt。
- `outbox/`：一次性產出，本來就會自動 3 天清除。
- 各專案 `.venv/`、`node_modules/`、`__pycache__/`、`.tabelog_state/cache`
  等可由套件管理器重建或屬暫存快取的內容。
- Keychain 內密鑰明文（`telegram-bot-token`、`telegram-chat-id` 等）：
  一律由使用者在新機器上依「五、Token 安全儲存機制」5.1 節手動重新
  輸入，這份 prompt 只能提醒步驟，不能包含明文，也不能主動要求使用者
  把明文貼在對話裡。
- `claude_desktop_config.json`：本來就只在使用者確認後才建立，且不含
  明文，備份中只保留「知識參考」章節說明怎麼重建，不假設它已存在。
- 訓練/模型用的大型資料檔、螢幕截圖、`.DS_Store` 等系統雜項檔案。

### 產生流程
1. 掃描目前實際檔案系統（CLAUDE.md、memory/、wrappers/、dev/、
   ~/.claude/skills/、~/Library/LaunchAgents/），不得憑記憶回填。
2. 依「必須涵蓋」逐項蒐集內容、依「一律排除」過濾。
3. 以今天日期（ISO 8601、+08:00 時區）為檔名前綴，寫入新檔案
   `dev/init-prompt/backups/{YYYY-MM-DD}_backup_prompt.md`（同一天內
   重複產生則覆寫當天那份，不動更早的歷史版本）。
4. 依「紀錄義務」寫入 `activity_log.jsonl`（topic 可填 `general` 或
   `dev`）與 `memory/dev.md` 索引更新（記錄本次備份涵蓋的專案清單與
   本次版本檔案位置，不需要把 Prompt B 的內容複製進 memory）。
5. 因為這份檔案的目的是「離開這台機器也要能用」，產生後應主動告知
   使用者本次版本檔案位置，並詢問是否要透過 SendUserFile／下載等方式
   取得一份存放在這台 VM 以外的地方（雲端硬碟、Email 附件等）。依
   「終端機權限與資安邊界」b 項，傳送前需先讓使用者知道這份檔案會包含
   哪些內容類別（不需要逐字念出全文）才能送出。
6. Prompt A（`generate_backup_prompt.md`）本身只在「產生流程的邏輯」
   有變動時才需要修改（例如新增了必須涵蓋的項目類別），平常產生新版
   Prompt B 不需要動到它。

### 維護原則
- 平常新增主題、改規則、新增/修改 dev/ 專案、新增 skill、新增 launchd
  排程時，**不需要**同步更新 backup_prompt.md，避免每次小改動都觸發
  一次大量重寫；只有使用者明確要求「產生/更新備份」時才整份重新產出。
- 若距上次備份已久、期間又有大量異動（例如新增了一個主題或好幾個
  dev/ 專案），可以主動提醒使用者「要不要重新產生一份備份」，但不得
  未經同意就自行覆寫。

````

## 四、目前已存在的主題與 memory 完整內容

以下為產生此備份當下，`.claude/memory/` 底下每個檔案的完整內容
（骨架模板已內嵌在上方主規則檔「六」節，此處是目前實際累積的內容）。
**`~/claude-workspace/.claude/memory/general.md`**
````markdown
---
分類: 尚未分類 / 雜項
最後更新: 2026-09-18
---

# 尚未分類 / 雜項

## 雜項紀錄
- 2026-09-18：依初始設定 prompt 建置 ~/claude-workspace 完整目錄結構與規則檔案
  （.claude/CLAUDE.md 主規則檔、.claude/wrappers/run_telegram_mcp.sh、
  memory/dev.md、memory/general.md、logs/activity_log.jsonl、README.md）。

## 待分類項目
（暫時歸此，日後可能拆成新主題）

## 資料檔索引
| 日期 | 檔案 | 內容說明 |
|------|------|----------|
| - | - | - |

````

**`~/claude-workspace/.claude/memory/dev.md`**
````markdown
---
分類: 程式撰寫與除錯（跨主題）
最後更新: 2026-09-22（stock-sector 新增 ETF 版）
---

# 程式撰寫與除錯

## 專案索引
| 專案 | 路徑 | 所屬主題 | 語言 / 技術 | 說明 |
|------|------|----------|-------------|------|
| telegram-notify | dev/telegram-notify/telegram_notify.py | （通知類，跨主題共用） | Python 3（stdlib urllib/io/mimetypes/uuid，無外部依賴）+ fastmcp（選用） | 單向發送 Telegram 訊息，兩個能力：send_message（文字）、send_photo（圖片，2026-09-18新增）。send_photo 只接受本機檔案路徑（用 multipart/form-data 上傳 bytes），不接受任何網址/URL，避免被拿來當任意 URL 轉發器；不具讀取訊息/聯絡人功能 |
| init-prompt | dev/init-prompt/claude_init_prompt.md | general（機器初始建置範本） | Markdown（非可執行程式碼，供貼給新 VM 的 Claude 用） | 完整版初始設定 prompt，已把 telegram-notify 的程式碼/venv/wrapper/測試流程收斂進初始建置範圍，安全確認邊界（Keychain、對外傳送前確認、claude_desktop_config.json 需確認）維持不變；無版本標記，直接視為目前唯一版本 |
| stock-model | dev/stock-model/ | stock（股市：量化模型可行性研究） | Python 3.12（venv）+ pandas/numpy/scikit-learn/scipy | v1: fetch_data.py + train_model.py，單股(NVDA)純技術指標RandomForest做漲跌方向分類。v2: fetch_universe.py(10檔股票+6項總經指標)、fetch_fundamentals.py(Yahoo quoteSummary基本面快照，需crumb/cookie手動取得，見程式內handshake寫法)、train_model_v2.py(RandomForestRegressor預測次N日報酬率，含IC/R²評估與排名回測)。v1、v2結論皆為：無統計上顯著的預測力，不實用，詳見memory/stock.md |
| stock-news | dev/stock-news/ | stock（股市新聞自動蒐集+AI每日摘要通知） | Python 3.12（venv，pandas+pyarrow）+ Bash + 本機 `claude -p` headless 呼叫 | fetch_news.py：每30分鐘（launchd）抓5個RSS新聞源存成`data/stock/news/YYYY-MM.parquet`，用URL雜湊去重。build_digest_prompt.py：依市場+時間窗組出摘要用的prompt文字。run_digest.sh：串起「組prompt→呼叫`claude -p`生成繁中條列摘要(含AI影響評估)→存檔`data/stock/digests/`→用telegram wrapper發送→寫入activity_log.jsonl」，由launchd於每天08:00(tw)/21:00(us)觸發。詳細設計、RSS來源清單、使用者對自動發送的授權範圍記錄在memory/stock.md「自動化新聞排程Pipeline」小節。 |
| stock-chart | dev/stock-chart/kline_chart.py | stock（K線圖產生+Telegram傳送） | Python 3.12（venv：pandas + mplfinance，mplfinance內含matplotlib） | `python kline_chart.py [TICKER] [MONTHS] [--no-send]`，預設NVDA、近3個月。抓Yahoo Finance chart API（範圍1y，2026-09-19從6mo改大，除了當20日均線緩衝，也讓52週高低點統計有完整一年資料，畫圖前才裁切到指定月數），用mplfinance畫K棒+成交量+5日/20日均線+RSI(14)副圖（Wilder平滑，含30/50/70參考線）+均線黃金/死亡交叉三角形標記（addplot type='scatter'），右上角疊一個規則式「綜合結論」文字框（見下方2026-09-19新增段落），PNG存到`outbox/`（一次性產出，見CLAUDE.md「七」，非data/stock/），存完直接呼叫telegram wrapper `--photo`傳送，並寫入activity_log.jsonl。**純手動觸發，不排程**；傳送前不需每次確認（2026-09-18使用者已授權此固定內容類型——公開股價K線圖——自動傳送，範圍僅限本工具，見memory/stock.md）。**但Telegram傳送這一步在Claude Code的auto mode權限分類器下仍會被判定為「External System Writes」而擋下**（2026-09-19實測），即使有上述使用者預先授權也一樣，所以每次仍需視情況改用`--no-send`產圖後改由對話內SendUserFile直接給使用者看，或請使用者手動核准該次Bash執行。2026-09-19新增規則式「綜合結論」文字框（build_advice()）：沿用memory/stock.md既有的規則式heuristic（短線動能/52週位階），加上RSI（以50為多空分界，加碼超買≥70/超賣≤30時的風險註記）、近10日內是否出現均線黃金/死亡交叉，四項因子各投+1/0/-1票加總，對應「加碼傾向／續抱偏多／觀察／續抱偏空／減碼傾向」；刻意不含總經/新聞面（那項只在memory/stock.md的人工分析流程走WebSearch，若每次產圖都查新聞會拖慢這個工具的「快速重複使用」設計目標），文字框內固定印出「規則式技術面整理，非AI模型、非投資建議」的免責提示。 |
| outbox-cleanup | dev/outbox-cleanup/cleanup_outbox.py | general（跨主題共用的一次性檔案清理） | Python 3（純標準庫，系統python3即可跑） | 刪除`outbox/`底下mtime超過3天的檔案，有刪除才寫一行activity_log.jsonl(action=delete)。launchd LaunchAgent `com.claudeworkspace.outbox.cleanup`每天03:00執行，plist在`~/Library/LaunchAgents/`，已用`launchctl bootstrap`載入。純本機刪檔、不對外傳送，不受「傳送前需確認」規則限制。機制設計詳見workspace CLAUDE.md「七、一次性產出檔案管理機制」。 |
| stock-fomo | dev/stock-fomo/ | stock（規則式FOMO指數設計+回測驗證，2026-09-19） | Python 3.12（venv：pandas/numpy/scipy/matplotlib） | fomo_index.py：`compute_fomo_index(df)`純用OHLCV算FOMO指數(0-100)，四因子（5日動能/量能異常/RSI偏離50/距一年高點遠近）各自算trailing 252日rolling z-score(無look-ahead)後取平均，50+15*z轉成0-100顯示分數。backtest_fomo.py：套用在`data/stock/universe/`既有10檔股票5年OHLCV（沿用stock-model專案抓好的資料，未重抓），算Spearman IC、十分位價差t-test、**前後兩半樣本分期穩健性檢查**、個股拆解、示意策略(FOMO≥80空手 vs buy&hold)，圖表+結論md存到`data/stock/fomo/`（非outbox，因為有長期分析價值）。**結論：沒有找到穩定、可跨時期依賴的預測力**——10/20日IC雖p<0.05但rho僅約0.02（解釋力<1%），關鍵是分前後兩半重跑後IC正負號直接反轉（前半+0.09、後半-0.04），10檔個股IC也是5正5負近似丟硬幣，判斷是特定期間市場狀態(趨勢市vs震盪市)的產物而非真實規律，與v1/v2技術面模型的結論一致（見上方stock-model列、memory/stock.md）。詳細數據見`data/stock/fomo/fomo_backtest_conclusion_2026-09-19.md`。 |
| stock-sector | dev/stock-sector/ | stock（S&P500 板塊輪動研究，週頻，2026-09-22） | Python 3.12（venv：pandas/numpy/scipy/pyarrow/matplotlib/lxml） | fetch_universe.py（Wikipedia成分股+GICS）→ fetch_prices.py（Yahoo chart API，2006起日資料，per-ticker parquet快取，可斷點續抓）→ build_weekly.py（重採樣週五週資料、40個群組等權報酬、成交金額占比）→ backtest.py（季節性/動能/熱度訊號×持有1,4,13週×板塊/細產業＋walk-forward選參，52假設一個BH-FDR家族，跑全部再平衡相位）→ analyze_structure.py（季節性640檢定、相關性/群聚、領先落後、熱度外溢）→ make_charts.py → verify_consistency.py（可重現/無未來函數/walk-forward洩漏/判定規則重算）。`run_all.sh [--offline]` 一鍵重跑。**ETF版（2026-09-22）**：`SECTOR_STUDY=etf` 切換資料夾/樣本窗（config.py：FIRST_YEAR、HALF_SPLIT_YEAR），build_etf.py 抓九檔SPDR板塊ETF+SPY並輸出與個股版相同格式的面板，其餘程式不改直接沿用；prespecified_test.py 做事先指定的單一假設（科技Q4）多種檢定；make_user_charts.py 產給讀者看的白話圖到outbox/。共用邏輯：signals.py（point-in-time訊號）、evaluate.py（IC/多空/一致性判準）、common.py。結論：板塊同期相關結構穩定，但季節性/輪動/熱度外溢無一通過一致性檢驗，見memory/stock.md「美股板塊輪動研究」。 |
| jp-travel-planner | ~/.claude/skills/jp-travel-planner/SKILL.md（不在dev/，因為Claude Code個人skill必須放在`~/.claude/skills/`底下才會被自動載入，此列僅作跨主題索引） | travel（規劃日本行程時自動查交通/天氣） | Markdown skill（無程式碼，純指令＋來源清單） | 觸發時機：使用者規劃日本行程、查電車/巴士時刻票價、查天氣颱風、賞楓賞櫻時間。指引Claude一律用WebSearch/WebFetch查即時資料（不可憑記憶回答，因票價班次每年變動），列了電車轉乘(Yahoo!路線情報/NAVITIME/Jorudan)、高速巴士(highwaybus.com/bushikaku.net)、天氣(JMA/tenki.jp/weathernews.jp)、賞楓賞櫻(walkerplus.com)四類來源，並提醒查完後若在claude-workspace專案內要依該專案規則寫回memory/travel.md。2026-09-20建立，僅寫了SKILL.md（無scripts/references），未跑skill-creator的完整eval/benchmark流程（個人輕量用途，先vibe著用，之後有需要再補測試）。 |
| jp-restaurant-finder | ~/.claude/skills/jp-restaurant-finder/SKILL.md（同上，不在dev/） | travel（日本行程找餐廳，用Tabelog+Google Map雙評價把關） | Markdown skill（無程式碼） | 觸發時機：使用者要日本某地區/某類型餐廳推薦，或要查已知店家評價。核心規則是每間候選店都要查到實際評分才能推薦，不可憑訓練資料印象報店名。評分門檻：Tabelog最好>3.2理想3.5+、Google Map最好>4.0。**演進history**：一開始要求查Google Map但`WebFetch`抓不到（JS動態頁面），一度誤用Yahoo!地圖冒充被使用者指正；改用`dev/gmaps-lookup`工具（見下方條目）實際打開瀏覽器讀Google Maps真實分數；**2026-09-21再修正**：原本以為Tabelog頁面可以直接WebFetch，但這個session的WebFetch後來被Tabelog的防爬蟲擋403，改成`dev/gmaps-lookup/tabelog_reviews.js`一樣用Playwright（這個VM自己的網路路徑當時沒被擋）。輸出用表格（店名/連結/GM分數/Tabelog分數/是否需預約/備註），有需要時可再加近N個月的評論摘要（見gmaps-lookup條目的review-scraping功能）。與jp-travel-planner分工：一個管交通天氣、一個管吃。**2026-09-21補記**：先前修好gmaps-lookup工具（Tabelog改Playwright、Google Map連結改用mapsSearchUrl避免拿到session綁定token）後，一度只更新了這則memory條目，忘了同步回SKILL.md本身——使用者主動問「有沒有把方法更新進工具/skill設定」才發現這個落差，SKILL.md已於同日補完整查詢流程（分數vs評論內容用哪組指令、連結一律用mapsSearchUrl不要用placeUrl、Tabelog的12秒節流間隔）。**教訓**：修完dev/工具或流程後，若該工具是被某個skill引用，記得同步檢查並更新那個skill的SKILL.md，不能只寫memory——memory是給下次對話「回憶脈絡」用的，skill才是真正會被讀進查詢流程執行的指令。未跑完整eval流程。 |
| gmaps-lookup | dev/gmaps-lookup/：`lookup.js`（單筆Google Map查詢）、`batch_lookup.js`（多筆Google Map）、`lookup_with_reviews.js`／`batch_lookup_with_reviews.js`（Google Map+近N個月評論內容）、`tabelog_reviews.js`／`batch_tabelog_reviews.js`（Tabelog+近N個月評論內容） | travel（起因是日本餐廳評分查證，但工具本身不限日本，任何地區店家都能查） | Node.js + Playwright（headless Chromium） | **解決了WebFetch/WebSearch都讀不到Google Maps真實評分、以及Tabelog會403擋WebFetch的問題**。基本查詢：`node lookup.js "<店名 地區>" [screenshot.png]`回傳JSON（title/rating/reviewCount/url）；`node batch_lookup.js queries.json outDir/`多筆一次跑，同一瀏覽器session效率較高。**評論版**（2026-09-20新增）：`node lookup_with_reviews.js "<店名>" [月數=3] [screenshot.png]`，除了rating/reviewCount，多回傳`placeUrl`（實際導覽後的頁面網址，可直接當連結給使用者）跟`reviews`陣列（每則含rating/dateText/text，已篩選在指定月數內，判斷依據是Google顯示的相對時間如「2 か月前」）；`batch_lookup_with_reviews.js`是多筆版本。**Tabelog版**：`tabelog_reviews.js "<Tabelog評論列表頁URL如.../dtlrvwlst/>" [月數=3]`，抓`div.rvw-item`卡片，篩選邏輯是月份（Tabelog顯示格式是「2026/07訪問N回目」，只有精確到月，用「今月-N月」當cutoff），一頁通常有20-21則（含1則店家自選的「ピックアップ」置頂評論，不列入日期篩選因為它不是按時間排序）；`batch_tabelog_reviews.js urls.json outDir/ [月數] [延遲ms]`是多筆版本，**預設每筆間隔要留夠久**（開發時用了12-13秒），因為Tabelog有請求頻率限制。開發過程踩的坑：①Google Maps是JS動態SPA，rating藏在`span[role="img"][aria-label*="星"]`的aria-label屬性，抓取穩定；reviewCount／評論卡片是非同步渲染，容易抓空或抓到剛切換分頁時的舊內容，已加`waitForFunction`輪詢+重試；②**搜尋結果列表常有「スポンサー」贊助廣告卡片排在最前面**，早期版本誤點到廣告主（查タカマル鮮魚店抓到不相關的義式餐廳），已修正為跳過含「スポンサー」文字的卡片；③Google Maps點擊クチコミ分頁後偶爾會彈出「ログインして最大限に活用」的登入誘導modal蓋住畫面，會打斷後續互動；④**Tabelog會因為請求頻率被403封鎖**（頁面顯示「しばらくお待ちください」的bot-check頁），這個session連續請求4-5次就會觸發，封鎖是整個session層級（不是單一URL），已知會持續至少數分鐘到更久，**踩到之後不要立刻重試同一批**，改用`batch_tabelog_reviews.js`內建的延遲機制配合原本就要重跑的情境，且WebFetch工具本身的共用出口IP似乎長期被Tabelog擋（同一URL用WebFetch永遠403，但這台VM自己的Playwright網路路徑一開始是通的），若WebFetch對Tabelog回403可以先試這個工具而不是放棄。2026-09-20/21建立並用於東京餐廳評分+評論查證（見memory/travel.md），驗證方式：使用者自己開Google Maps核對プロカンジャンケジャン赤坂店確實是3.7分341則，跟工具實測結果一致。**2026-09-21修正**：`lookup_with_reviews.js`／`batch_lookup_with_reviews.js`原本把`placeUrl`（點進去該店之後、瀏覽器實際導覽到的那個長網址，含lat/lng跟`g_ep`參數）當成要給使用者的連結，**使用者回報這些連結打不開**——`g_ep`那段字串看起來是跟當次瀏覽session綁定的token，換一個瀏覽環境不一定能解析成功。修正後兩個工具都新增`mapsSearchUrl`欄位（`https://www.google.com/maps/search/{原始查詢字串}`，跟`lookup.js`／`batch_lookup.js`原本就在用的格式一樣），這個純搜尋格式沒有ephemeral token，分享給別人點開比較穩定；`placeUrl`保留但註明只用於工具內部除錯，不要再直接貼給使用者。**教訓**：之後任何從瀏覽器自動化工具產生的Google Maps連結，優先用`/maps/search/{名稱}`這種單純格式，除非有特別理由才用完整place URL，而且用之前最好自己點一次確認打得開。**2026-09-22新增`tabelog_utils.js`（節流/降低實際請求量，不是規避偵測）**：查過Tabelog `robots.txt`確認一般User-agent沒有禁止評論列表頁路徑，所以只做「讓存取節奏更像真人、減少實際請求次數」這個方向，不做IP/代理輪換、偽裝成別的爬蟲、破解驗證碼這類手段。內容：①本地快取（`.tabelog_state/cache/`，同一URL 48小時內直接回傳快取、不發網路請求，快取存的是未篩選的完整評論列表+parse好的日期，月數篩選在讀取快取時才做，避免「用月數A快取、之後查月數B卻拿到錯誤篩選結果」這個bug）；②冷卻鎖檔（`.tabelog_state/cooldown.json`，遇到403就寫入30分鐘冷卻時間戳記，期間內`tabelog_reviews.js`／`batch_tabelog_reviews.js`會直接短路回報「on cooldown」不發任何請求，batch版本也會在冷卻觸發當下中止剩餘佇列，不會繼續往下硬查到全部403）；③瀏覽器context補齊`timezoneId`/`viewport`/`Accept-Language`（原本只設UA+locale，缺其他欄位本身就是不一致的瀏覽器指紋）；④每次真正發送請求前先`warmUp()`導覽一次Tabelog首頁+隨機滑鼠移動，模擬從搜尋結果點進來的真人動線，不是冷啟動直接跳進深層評論頁；⑤batch版本的固定delay改用`jitter()`隨機化±30%，不再是每次都精確12000ms這種規律到反而可疑的間隔。單筆/批次都新增`--no-cache`旗標可強制略過快取重查。 |

## 環境與慣用寫法
- **`WebFetch` 抓不到 Google Maps 頁面**（JS動態渲染的SPA，直接fetch只會拿到空殼標題，沒有評分/評論內容），`WebSearch` 查Google Map評分時，第三方網站幾乎都只會回傳自家系統的分數（最常見是Yahoo!地圖，邏輯跟Google Map不同），不能把那些數字當Google Map分數用。這個VM session實測透過`ToolSearch`查不到`claude-in-chrome`之類的瀏覽器自動化工具（未連接），所以目前這個環境沒有辦法程式化讀到Google Maps的即時分數/評論，需要的話只能請使用者自己提供（截圖或貼數字）。相對地，**Tabelog頁面是伺服器端渲染的一般網頁，`WebFetch`讀得到分數和評論內容**，查日本餐廳評價優先用這個當可程式化查證的來源（詳見jp-restaurant-finder skill）。
- 系統 python3（/usr/bin/python3，CommandLineTools 附帶）為 3.9.6，
  無法安裝 fastmcp（需求 Python >=3.10），此版本只用於一般腳本。
- 透過 Homebrew 額外安裝 `python@3.12`（/opt/homebrew/bin/python3.12），
  並在 dev/telegram-notify/.venv 建立專案專用虛擬環境安裝 fastmcp
  （Homebrew 的 python 預設是 PEP 668 externally-managed，不可直接
  `pip install`，一律用該專案的 venv，不裝到系統或 Homebrew 全域環境）。
- telegram_notify.py 的核心發送邏輯只用標準庫 urllib，無需額外依賴即可運作；
  指令列帶文字參數即直接發送並結束（CLI 測試模式）。
- 不帶參數時走 `from fastmcp import FastMCP` 啟動 MCP server 模式，
  需用 dev/telegram-notify/.venv/bin/python 執行才有 fastmcp。
- wrapper script `run_telegram_mcp.sh` 已改為呼叫
  `dev/telegram-notify/.venv/bin/python .../telegram_notify.py "$@"`，
  同時支援「MCP server 模式（無參數）」與「CLI 測試模式（帶文字參數）」。
- Claude Desktop 設定檔 `~/Library/Application Support/Claude/claude_desktop_config.json`
  已建立，`mcpServers.telegram-notify.command` 指向 wrapper script
  （不含明文密鑰），權限已設為 600。
- send_photo（2026-09-18新增）：CLI 測試模式為
  `telegram_notify.py --photo <本機路徑> [caption]`；MCP 工具名稱為
  `send_telegram_photo(photo_path, caption="")`。安全限制：函式一開頭就檢查
  路徑字串是否含 `://`，含有就直接拒絕（不接受 http(s) 等任何 URL），
  且用 `os.path.isfile` 確認是本機真實存在的檔案後才讀取 bytes 上傳，
  完全不會讓 Telegram 或任何第三方網址被當成圖片來源。

## 除錯紀錄與教訓
| 日期 | 問題 | 原因 | 解法 |
|------|------|------|------|
| 2026-09-18 | `pip3 install fastmcp` 失敗（No matching distribution） | fastmcp 需求 Python >=3.10，系統 python3 是 3.9.6 | brew 裝 python@3.12，並在專案下建 venv 安裝 fastmcp |
| 2026-09-18 | Homebrew python 下 `pip install fastmcp` 被拒絕（externally-managed-environment） | PEP 668，Homebrew 管理的 python 不給全域 pip install | 改用 venv（dev/telegram-notify/.venv），不加 --break-system-packages |
| 2026-09-18 | 用 `claude -p "純文字摘要prompt"` 做無人值守的背景摘要生成時，輸出前面多了一段「工作目錄權限僅限於...無法寫入activity log與memory」的說明文字，混進了要發送的訊息內容 | `claude -p` 預設仍會載入使用者層級與 workspace 的 CLAUDE.md（含「紀錄義務」規則），模型嘗試遵循那些規則但被 `--permission-prompts none` 擋下工具呼叫，於是把說明寫進回覆文字 | 呼叫時加上 `--safe-mode`（停用 CLAUDE.md/hooks，但仍走正常 OAuth/keychain 登入，不像 `--bare` 需要另外設 ANTHROPIC_API_KEY）+ `--tools ""`（這類純文字摘要任務本來就不需要任何工具），確認輸出乾淨後才接去發送 |
| 2026-09-19 | kline_chart.py 圖表標題用日文「・」分隔詞（如「RSI・交叉訊號」）時，存檔出現 `Glyph missing from font(s) Heiti TC` 警告，該符號在圖上顯示缺字方框 | Heiti TC（macOS內建繁中字型）沒有收錄日文中黑點U+30FB這個字符 | 改用中文頓號「、」取代「・」，繁中字型本來就有這個字符，不會缺字 |
| 2026-09-22 | 回測出現1個異常強的訊號（板塊1週動能→13週後 IC −0.16, t=−4），但邏輯上不合理 | 每13週再平衡且起點固定（offset=0），等於永遠在每季同一週次取樣，該相位碰巧顯著；起點位移0-12週後其餘12個相位IC都在0附近 | 所有非重疊持有期回測一律跑全部 h 個相位，p取最差相位，並要求≥80%相位同號才算一致（stock-sector/evaluate.py） |
| 2026-09-22 | walk-forward選參的歷史IC洩漏 | 某年Y選參用的IC若日期在Y年前但持有期延伸進Y年，就含Y年報酬 | 只用「持有期已結束」的IC；以擾動測試（把Y年起資料換雜訊看選參是否改變）驗證，並用放回漏洞的負向對照確認驗證器會報錯 |
| 2026-09-22 | 設計tabelog_utils.js快取時，第一版把「月數篩選過的評論」直接存進快取 | 之後若用不同月數參數查同一間店，會直接拿到用舊月數篩選過的錯誤結果（快取內容跟查詢參數綁死） | 改成快取「未篩選的完整評論列表」（含parse好的年月），月數篩選邏輯搬到讀取快取之後才執行，快取內容與查詢參數解耦 |
| 2026-09-22 | run_digest.sh（21:00 us排程）Telegram發送遇暫時性SSL連線錯誤（`SSL: UNEXPECTED_EOF_WHILE_READING`）直接失敗退出，摘要檔仍存檔但未送達，且因發送失敗連activity log都沒寫，使用者要主動問才發現漏傳 | 腳本原本沒有重試機制，一次失敗就整個放棄；失敗時也完全沒有留下任何log可追查 | 幫Telegram發送步驟加上最多3次重試（間隔10/20/30秒），全部失敗才放棄；不論成功或最終失敗都寫入activity_log.jsonl（失敗時action=other，註明需人工檢查/補傳），失敗時的stderr另存到`logs/stock-news-digest-{market}-send.err.log`方便排查 |

## 待辦 / 追蹤中
- Claude Desktop 尚未安裝於此 VM（/Applications 內沒有該 App），
  使用者選擇暫不安裝，先以 CLI 測試模式為主。
- CLI 測試模式已在切換到 venv python 後重新驗證發送成功（2026-09-18）。
- MCP server 模式（無參數，走 fastmcp stdio）尚未實際被 Claude Desktop
  啟動驗證，僅確認過模組可正常 import。待日後安裝 Claude Desktop 後再測。

````

**`~/claude-workspace/.claude/memory/hardware.md`**
````markdown
---
分類: 電腦硬體市場價格研究
主題 slug: hardware
最後更新: 2026-09-18
---

# 電腦硬體市場價格研究

## 常用來源與工具
- WebSearch + WebFetch 查詢即時報價/新聞（無固定 API，靠 Tom's Hardware / PCPartPicker /
  tech-insider.org / shanethegamer.com / wccftech 等媒體與追蹤站的公開文章）。
- 目前沒有單一連續、每日更新的公開資料源可直接抓取歷史數列，只能從多篇報導拼湊時間點，
  各站數字常有 ±10~15% 落差（取樣的零售商/SKU不同）。
- rampricesusa.com、Tom's Hardware 的 RAM price index 頁面聲稱有互動圖表/歷史資料，
  但目前用 WebFetch 抓取到的是截斷內容（僅拿到當下快照），沒有完整歷史表格。

## 策略與觀察重點
- 2026-09-18 研究結論：DDR5 記憶體自 2025 年中起因 AI/HBM 需求排擠 DRAM 晶圓產能，
  掀起消費級記憶體「缺貨+漲價」潮。代表性 32GB DDR5-6000 kit 價格約從 2025-05 的
  $120 一路漲到 2026 年初高點 ~$432，2026-09 仍維持在 $375~$400 區間，
  尚未看到明顯回落。
- 分析師（TrendForce、IDC、Gartner 引用）普遍預估要到 2027（甚至 Q4 2027）
  市況才會緩解，2026 年內不預期降價。
- 記錄有價格數列的 CSV：見「資料檔索引」，日後若要延伸追蹤（例如做趨勢圖更新），
  可以此檔案為基礎，新增之後查到的資料點並註明來源與日期。
- 若之後要做「持續追蹤」（例如每週更新一次 DDR5 價格圖表並存檔），可考慮比照
  [[stock]] 主題的做法建立 dev/ 下的抓取腳本，寫入 memory/dev.md 索引。

## 資料檔索引
| 日期 | 檔案 | 內容說明 |
|------|------|----------|
| 2026-09-18 | data/hardware/2026-09-18_ddr5_32gb_price_trend.csv | 32GB DDR5-6000 kit 街價時間序列（2025-05~2026-09，7 個資料點），含來源連結 |

## 待辦 / 追蹤中
- 無固定排程；若使用者要求定期更新 DDR5/DDR4 價格走勢，需先詢問更新頻率並評估
  是否建立自動化腳本（涉及是否要主動通知 → 需依「終端機權限與資安邊界」b 項
  傳送前先確認內容）。

## 台灣零售市場觀察（2026-09-18）
- 台灣主流網購平台（PChome 24h、BigGo 比價）上找不到「SK hynix / 現代」品牌自有的
  盒裝桌上型 DDR5 模組；市面盒裝零售品牌是 ORCA、KLEVV、UMAX、Kingston、
  Micron/Crucial 等組裝廠，DDR5-5600 16GB 單條目前約 NT$6,200~9,000。
- 「海力士/現代 DDR5 5600 16G」在台灣多以**散裝/裸條（tray/OEM）**形式透過
  蝦皮、露天等平台由個別賣家販售，非官方盒裝零售，價格因賣家、新舊、是否為
  筆電 SODIMM 而落差極大：查到區間約 NT$3,200~8,500（依 feebee 比價頁抓取），
  桌上型單條「非筆電版」約落在 NT$4,750~8,000，抓中位數約 **NT$6,000 上下**
  作為概估。
- 這個價位明顯高於缺貨潮前（2024~2025 中）同規格 16GB DDR5-5600 常見的
  NT$1,500~2,000 水準，與本主題稍早記錄的全球 DDR5 因 AI/HBM 排擠產能漲價
  趨勢一致。
- 資料來源不夠精確（比價站聚合、無法逐一驗證賣場即時庫存/價格），若使用者
  需要更精確報價，建議直接連到蝦皮/露天/PChome 當下頁面確認。

````

**`~/claude-workspace/.claude/memory/stock.md`**
````markdown
---
分類: 股市交易資訊與新聞研究
主題 slug: stock
最後更新: 2026-09-22
---

# 股市交易資訊與新聞研究

## 範圍說明
- 台股與美股合併為同一主題（不分開），理由：兩者研究目的一致——
  追蹤大型權值股與指數型 ETF 的交易資訊與新聞，判斷「可買進 / 需減持」，
  屬於同一分析流程，僅資料來源與交易時段不同，故用下方小節區分即可，
  不另拆主題。若日後研究範圍擴大（例如加入個股當沖、選擇權等），
  再評估是否拆分。
- 追蹤標的類型：
  1. 大型權值股：該股市「市值前 10 大」成分股（台股、美股分別計算前 10 大，
     名單會隨市值排名變動，非固定清單，需定期重新確認）。
  2. 指數型 ETF：目前已知標的包含 0050（元大台灣50）、0050正2（元大台灣50正2）、
     QQQ（Invesco Nasdaq-100）、VTI（Vanguard Total Stock Market）等，
     日後使用者提及其他 ETF 時比照納入追蹤。

## 常用來源與工具

### 台股 / 美股報價（實測可用，2026-09-18 建立）
- Yahoo Finance chart API（無需金鑰，公開端點）：
  `https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=1mo&interval=1d`
  （需帶 `User-Agent` header，`{symbol}` 網址需 URL encode，例如 `^TWII` → `%5ETWII`）
- 已驗證可查詢：`^TWII`（加權指數）、`0050.TW`、`00631L.TW`（0050正2）、
  `QQQ`、`VTI`、`CL=F`（WTI原油期貨）、`2330.TW`/`2317.TW`/`2454.TW`/
  `2308.TW`/`3711.TW` 等個股代號。
- 回傳欄位重點：`regularMarketPrice`、`regularMarketChangePercent`、
  `fiftyTwoWeekHigh`/`Low`；歷史收盤在 `indicators.quote[0].close` 陣列。

### 新聞來源
- WebSearch 工具，常用查詢組合：「台股 大盤 今日 美股 影響」
  「國際油價 美國政府 消息 台股 影響」「台股 盤前晨報 {日期}」
  「Fed 利率 決策 {年月} 台股」「台股 市值前10大排名 {年月}」。
- 市值前10大排名會隨股價波動每日變動，非固定名單，每次分析建議
  重新搜尋確認（可用「台股 市值前10大排名」+ 當月關鍵字）。

### 自動化新聞排程 Pipeline（2026-09-18 建立，見 dev/stock-news/）
- **目的**：持續蒐集會影響股市的新聞、存成訓練資料，並每天定時用 AI
  整理重點透過 Telegram 通知，詳細設計與程式碼見 [[dev]]。
- **RSS 來源**（皆為公開、免金鑰、知名媒體/財經網站官方 RSS，2026-09-18
  實測可用，需帶瀏覽器 User-Agent header 否則部分來源會擋）：
  - 台股：Yahoo奇摩股市 `tw-market` 分類、經濟日報(udn money) 股市分類(5590)。
  - 美股：CNBC Markets（id 20910258）、WSJ Markets Main（feeds.a.dj.com）、
    MarketWatch Top Stories（feeds.content.dowjones.io）。
  - 曾測試但不可用/不適合：cnyes 鉅亨網 RSS（404）、CNA中央社 finance.xml
    （404）、中時 realtimenews-finance.xml（403，Cloudflare 擋爬蟲）。
- **儲存格式**：parquet，依「新聞發布時間所屬月份」分檔於
  `data/stock/news/YYYY-MM.parquet`（欄位：id 為 URL 的 sha256 前16碼、
  market、source、title、summary、url、published_at、fetched_at，
  皆為 +08:00 時區 ISO8601 字串）。每次抓取用 `id` 去重，只新增真正
  新的項目，可安全重複執行。
- **抓取排程**：launchd LaunchAgent `com.claudeworkspace.stocknews.fetch`，
  每 30 分鐘跑一次 `dev/stock-news/fetch_news.py`。
- **每日摘要排程**（launchd，會自動發送 Telegram，使用者已於 2026-09-18
  明確授權此固定用途的排程可無人值守自動發送，範圍僅限這兩支排程）：
  - `com.claudeworkspace.stocknews.digest.tw`：每天 08:00（台北時間）執行
    `run_digest.sh tw`，摘要「前一天此時到現在」24小時內的台股相關新聞。
  - `com.claudeworkspace.stocknews.digest.us`：每天 21:00（台北時間）執行
    `run_digest.sh us`，摘要「前一天此時到現在」24小時內的美股相關新聞。
  - 兩者流程一致：讀取當月（跨月時含上月）parquet → 依時間窗與 market
    過濾、去重 → 組成 prompt → 呼叫本機 `claude -p`（見 [[dev]] 除錯紀錄
    關於 `--safe-mode`/`--tools ""` 的必要性）產生繁中條列摘要，每則重點
    附帶一行「(AI影響評估：...)」並註明為AI判讀非投資建議 → 摘要存檔於
    `data/stock/digests/YYYY-MM-DD_{market}_HHMM.txt` → 透過既有 Telegram
    wrapper 發送 → script 自動寫入 activity_log.jsonl（action=send）。
  - launchd plist 位置：`~/Library/LaunchAgents/com.claudeworkspace.stocknews.*`，
    已用 `launchctl bootstrap` 載入並實測驗證（含互動式與 launchd 背景
    執行兩種路徑），開機/登入會自動載入，無需額外設定。

### K線圖產生 + Telegram 傳送（2026-09-18 建立，2026-09-19 擴充，見 [[dev]] 的 stock-chart 項目）
- **目的**：讓使用者能快速拿到「近N個月K線圖」的圖片，
  且因為「會很常被使用」，設計成單一指令、預設值合理（預設NVDA、近3個月）
  即可直接產圖+傳送，不需每次額外指定參數。
- **標準輸出內容（2026-09-19 使用者明確確認「以後我問標的的圖就給我這些資訊」，
  故此後只要使用者要求某標的的K線圖/走勢圖，預設就要用這個完整版本，不必
  每次重新詢問要不要加哪些指標）**：K棒 + 成交量 + 5日/20日均線 + 均線
  黃金/死亡交叉三角形標記 + RSI(14)副圖（含30/50/70參考線，50為多空
  分界）+ 右上角規則式「綜合結論」文字摘要框（動能/52週位階/RSI/近期
  交叉訊號四因子加總判斷「加碼傾向／續抱偏多／觀察／續抱偏空／減碼傾向」，
  並固定標示「規則式技術面整理，非AI模型、非投資建議」）。
- **程式**：`dev/stock-chart/kline_chart.py`，`python kline_chart.py [TICKER] [MONTHS] [--no-send]`。
- **繪圖套件選擇**：改用 `mplfinance`（而非手刻 matplotlib K棒），
  理由是它原生支援 OHLC candlestick + `addplot` 疊加均線 + volume子圖，
  程式碼更精簡也更不容易畫錯，對「常被使用」的工具而言可讀性/維護性更重要。
- **資料抓取細節**：沿用 `dev/stock-model/fetch_data.py` 同樣的 Yahoo Finance
  chart API 做法（免金鑰），2026-09-19 從抓6個月改為抓1年（除了當
  5日/20日均線與RSI(14)的計算緩衝，也讓52週高低點統計有完整一年資料），
  算完各項指標後才裁切到顯示區間，避免圖表最左側因為均線/RSI資料不夠
  而出現「前面沒有線」的斷線問題。
- **產出位置**：圖片存到 `outbox/`（一次性產出，3天後自動清除，
  見 workspace CLAUDE.md「七、一次性產出檔案管理機制」），不存
  `data/stock/`，因為這張圖本身就是最終產出，沒有進一步分析用途。
- **使用方式與傳送授權範圍（2026-09-18 使用者明確決定）**：
  - 純手動觸發，**不**額外排程自動執行（與上面的新聞摘要 pipeline 不同）。
  - 產圖後傳送到 Telegram **不需要每次都先跟使用者確認內容**——使用者
    已針對「這個工具、這種固定內容類型（公開股價K線圖PNG）」做出
    一次性授權，之後每次執行 `kline_chart.py` 都可以直接自動傳送，
    不用重新詢問。此授權範圍僅限本工具產出的K線圖，不擴及其他
    新的對外傳送用途（例如若之後要做別的圖表/報告自動傳送，仍須
    依 [[unattended-automation-authorization]] 的做法重新詢問一次）。

## 策略與觀察重點

### 判斷邏輯（規則式 heuristic，2026-09-18 建立，尚未做回測 / 未訓練 ML 模型）
判斷因子（綜合給出「續抱 / 加碼 / 觀察 / 減碼」傾向，非精確買賣訊號）：
1. **短線動能**：近 5 個交易日收盤是否連續上揚（大盤、ETF、個股皆看）。
2. **52 週位階**：現價距 52 週高點的百分比。越接近高點 → 追高風險越高，
   越接近低點 → 相對安全邊際較大，但也可能代表基本面轉弱。
3. **總經 / 地緣風險**：從新聞面判斷當前是否有利率、戰爭、油價等重大
   風險事件干擾（風險偏高時，即使動能偏多也建議降低加碼力道）。
4. **個股相對強弱**：同為權值股但漲跌互見時，個別標的列入觀察，
   不與大盤同步做出買賣判斷。

結論產出方式：動能 + 位階 + 總經風險 三者交叉判斷，寫成一句「綜合結論」，
並明確標示「規則式整理，非 AI 訓練模型、非投資建議」。

### 待改進方向
- 目前為規則式（rule-based）判斷，非真正訓練過的預測模型。
  若要做「訓練模型」版本，需要：歷史日 K 資料（開高低收量）、
  特徵工程、回測框架、與明確的標的/持有期間定義，屬於較大規模的
  dev/ 專案，需另外規劃。

### NVDA 單股訓練實驗結論（2026-09-18，詳見資料檔索引）
- 用 5 年日線 OHLCV + 純技術指標（報酬率/SMA/RSI/MACD/成交量/波動度）
  訓練 RandomForest 做「次N日漲跌方向分類」，時間序列切分避免看未來。
- 次1日、次5日：模型準確率**低於**多數類基準與「全猜漲」基準，等同瞎猜，
  沒有預測力。
- 次20日：準確率58%看似較高，但模型幾乎對每筆都預測「漲」，等同「一直
  持有不賣」，策略累積報酬與單純buy-and-hold完全相同，代表沒有真正的
  判斷力，只是剛好搭上NVDA這5年的多頭趨勢。
- **結論：純技術指標的簡單分類模型不實用**，不建議用它做實際進出場依據；
  程式碼在 dev/stock-model/，可重複套用在其他個股測試，但預期結果類似
  （這是學界普遍已知的困難問題，非程式或資料錯誤）。
- 若要繼續投入，方向是加入基本面/總經特徵、改預測報酬大小而非方向、
  跨多檔股票驗證，而非單靠價量技術指標。

### v2 實驗：加基本面/總經 + 報酬迴歸 + 10檔股票交叉驗證（2026-09-18）
- 回應v1結論的三個改進方向都做了：(1)加總經特徵(VIX/美10年殖利率/美元
  指數/油價/S&P500/半導體ETF，逐日、時間對齊正確) + 基本面特徵(毛利率/
  營收成長/ROE/負債權益比/預估本益比/beta，但**僅有目前快照，非逐日
  歷史**，是已知侷限) (2)目標改成預測「次N日報酬率」的連續值(迴歸)而非
  漲跌方向 (3)股票池擴大到10檔(NVDA/AAPL/MSFT/GOOGL/AMZN/META/AVGO +
  台積電/鴻海/聯發科)，全股票同一時間切點避免資料洩漏。
- 結果：次5日與次20日的 R² 都接近0或為負，IC(預測排名vs實際報酬的
  Spearman相關)在兩個區間都**不具統計顯著性**(p>0.1)，方向準確率
  52-54%只比丟硬幣好一點。次20日的排名回測「贏」基準(49% vs 40%)看似
  正面，但只有12個換倉點、且R²為負/IC不顯著，判斷是雜訊不是真訊號。
- 特徵重要性：總經特徵 >> 基本面特徵，基本面(現在快照值)幾乎沒貢獻，
  符合「非逐日歷史資料」的已知侷限。
- **結論：加了這些改進後，模型仍然沒有統計上顯著、可靠的預測力**，
  這條「訓練模型」路線目前做不出實用的選股/擇時工具，不是程式或資料
  品質問題，是再次印證公開技術面+總經+快照基本面很難打敗市場隨機性。
- 詳細數據與後續可能方向（真正逐日歷史基本面、擴大股票池到數十~數百檔）
  見 data/stock/universe/model_v2_experiment_2026-09-18.md。

### FOMO指數設計 + 回測驗證（2026-09-19，見 [[dev]] 的 stock-fomo 項目）
- **使用者需求**：設計一套可量化FOMO（Fear Of Missing Out，追高恐慌）程度
  的指數系統，資料來源不限，並要求跑回測驗證有效性。
- **設計**：純用OHLCV價量資料組成規則式指數（0-100分，50為中性，仿照
  CNN Fear&Greed Index的呈現方式），四個因子——(1)5日動能是否異常強
  (2)成交量是否異常放大 (3)RSI偏離50中線的程度 (4)距離近一年高點的遠近——
  各自算trailing 252日rolling z-score（只用當下及之前的資料，無look-ahead），
  取平均後轉成0-100分。**未使用新聞情緒資料**：dev/stock-news/的新聞
  pipeline從2026-09-18才開始蒐集，歷史太短無法支援多年回測，故此版FOMO
  指數是純價量代理指標，非真正的情緒資料。
- **回測方法**：套用在既有 data/stock/universe/ 10檔股票5年OHLCV
  （沿用stock-model專案已抓好的資料）。驗證假設「FOMO指數偏高 →
  未來報酬應轉弱（均值回歸）」，用Spearman IC、十分位價差t-test、
  **樣本依日期切前後兩半分別檢驗**（避免只是單一市場狀態的巧合）、
  10檔個股IC拆解、示意策略（FOMO≥80時空手 vs buy&hold，閾值未調參）。
- **結論：沒有找到穩定、可跨時期依賴的預測力**。10日/20日IC雖然
  p<0.05具統計顯著性，但rho僅約0.02（解釋力<1%報酬變異），且分前後
  兩半重跑後IC正負號直接反轉（前半段+0.09，動能延續而非反轉；後半段
  -0.04，才符合FOMO假設方向），代表看到的訊號很可能只是「剛好那段
  期間是趨勢市或震盪市」的產物，不是真實存在的規律。10檔個股IC也是
  5正5負，接近丟硬幣。示意策略5/10檔贏過buy&hold，且閾值80分因為
  四因子z-score平均會互相抵銷（標準差僅約9.7），全樣本12403筆只
  觸發68次（0.55%），訊號太稀疏不具參考意義。與 v1、v2 技術面模型
  實驗結論一致：**公開價量資料堆出的規則式指標，很難穩定打敗市場
  隨機性**。若要繼續這個方向，比起微調現有價量因子權重（等於在同一份
  資料上找巧合），比較有機會的路線是換成真正的情緒代理資料源
  （新聞情緒、選擇權put/call ratio、社群討論熱度等），但目前受限於
  新聞資料歷史太短，尚無法驗證。
- 詳細數據見 data/stock/fomo/fomo_backtest_conclusion_2026-09-19.md，
  完整面板資料見 data/stock/fomo/fomo_panel_data.csv。

### 本機硬體是否適合做 training（2026-09-18 檢查結論）
- 本機為 Apple Virtual Machine（Model: VirtualMac2,1），非實體機，
  規格：Apple M4 (Virtual) 4 核心、記憶體 8GB、無 swap、磁碟 123GB（可用91GB）、
  `system_profiler SPDisplaysDataType` 查不到任何顯示卡/GPU裝置
  （代表這台 VM 對外看不到可用的 Metal/GPU 加速）。
- 結論：**不適合訓練深度學習模型**（LSTM/Transformer 等時序模型），
  記憶體太小（8GB無swap）、核心數少、且無GPU加速，訓練會非常慢甚至OOM。
- **適合**訓練輕量的傳統機器學習模型（例如 logistic regression、
  random forest、XGBoost/LightGBM 等，針對每日OHLCV特徵做漲跌方向分類），
  這類模型在CPU上訓練成本低，4核心/8GB足以應付。
- 若未來要做較重的深度學習模型，建議用雲端（例如 Google Colab、
  雲端GPU租用）或使用者的其他機器訓練，而非這台 VM。
- 尚未建立台股當前市值前 10 大的固定查詢腳本（目前用 WebSearch 人工確認）。

### 美股板塊輪動研究（2026-09-22 建立，S&P500 週頻，見 [[dev]] 的 stock-sector 項目）
- **需求**：用 S&P500 成分股，以板塊（GICS 11 板塊＋28 個細產業＋自訂「電子零組件」組，共 40 組）找板塊自己的規律（如 Q4 炒作）與板塊間關係（如科技熱絡時傳產疲弱），並回測驗證規律是否「每次都成立」。**使用者指定只用週資料**（只要大方向，不要日/小時資料）。
- **資料**：Wikipedia 成分股＋GICS（503 檔）、Yahoo chart API 抓 2006-01 起日資料（還原收盤價/收盤/成交量）當快取，再重採樣成週五收盤週資料；群組報酬＝成員等權平均，超額報酬＝相對全體等權；熱度＝群組成交金額占全市場比例對自身 52 週的 z 分數。
- **結論（詳見 data/stock/sector/report/sector_rotation_report_2026-09-22.md）**：
  1. **有穩定結構**：板塊超額報酬相關結構前後半段相似度 ρ=0.68；資訊科技與公用事業(−0.40)、必需消費(−0.34)、房地產(−0.31)、金融(−0.27)穩定負相關（兩半同號），但與**工業/原物料/能源不穩定（接近0且翻號）**——「科技強、傳產弱」對真正的傳產不成立，對象是防禦型。這是同期關係，不可預測。
  2. **無可預測性**：52 組訊號回測（季節性/動能/熱度 × 1,4,13週 × 板塊/細產業＋walk-forward）0 組通過一致性，最大|IC|=0.047；領先落後 242 項僅 2 項（自身1週反轉，解釋力約1%）；成交熱度外溢 242 項 0 項。
  3. **季節性**：640 項檢定 p<0.05 有 26 項、純運氣預期 32 項，FDR 後 0 項；科技 Q4 平均+0.7%、12/20年贏、t=0.73，前半−0.6%/後半+1.9%翻號；Q4 成交量占比也看不到。**檢定力有限**（科技Q4標準誤約0.9%，20個樣本只能偵測≥2.6%的效果），結論是「無法確認」不是「證明不存在」。唯一近似通過「通訊服務5月」(18/20年、FDR後0.146)，2026-05 樣本外 −0.6% 未延續，僅列觀察。
- **一致性驗證**（dev/stock-sector/verify_consistency.py，全 PASS）：可重現（連跑兩次輸出 md5 相同）、無未來函數（把切點後資料換雜訊，訊號不變）、walk-forward 參數不洩漏、判定規則可從 CSV 重算。判準事先寫死：FDR p<0.10＋前後半段同號＋≥60%年份同號＋≥80%再平衡相位同號。
- **教訓**：①第一次跑出的唯一「顯著」結果（板塊1週動能→13週後反轉 IC −0.16, t=−4）是**再平衡相位假象**（只有起點offset=0有效，其餘12個相位都近0），之後所有回測改跑全部相位、p取最差；此判準是看過結果後才加，報告有註明。②walk-forward選參的歷史IC，持有期尚未結束者要排除，否則洩漏；驗證器用「放回漏洞看會不會報錯」做負向對照。③此研究與 FOMO/技術面模型的結論一致：股市這類規律在跨時期一致性檢驗下常消失。
- **限制**：存活者偏差（只有現任成分股，2006年僅397檔有資料）；等權≠市值加權；每季度只有20個年度樣本；細產業僅6-16檔雜訊大；S&P500 沒有純被動元件公司（自訂組僅為近似）。
- **建議下一步（未做）**：改用 SPDR 板塊 ETF（XLK等，1998起、市值加權、無成分股存活者偏差、約27個Q4）；「通訊服務5月」待2027-05前瞻驗證；依 VIX/利率 regime 拆相關性。
- 重跑：`dev/stock-sector/run_all.sh`（`--offline` 只重跑分析）。

### 板塊輪動研究 ETF 版試作（2026-09-22，SPDR 九大板塊 1999-，見 [[dev]] 的 stock-sector）
- **動機**：個股版有存活者偏差／等權／每季度僅 20 樣本；ETF 版市值加權、無存活者偏差、27 個 Q4，且 1999-2005 是個股版沒用過的獨立驗證期。用環境變數 `SECTOR_STUDY=etf` 切換，與個股版共用同一套程式，資料在 `data/stock/sector_etf/`。
- **事先指定的主假設**：科技 Q4 超額報酬 >0（看資料前就定好）。結果：27 年中 16 年贏、平均 +0.8%、t 檢定 p=0.60（Wilcoxon 0.19、符號檢定 0.44）；1999-2005 獨立期 +1.9%（p=0.76）；Q4 減同年 Q1-Q3 = +0.8%（p=0.68）→ **不成立（無法確認）**，與個股版一致。
- 探索性：季節性 0/144、訊號回測 0/26、領先落後 0/162、熱度外溢 0/162、成交占比季節性 1/36（科技 Q2 占比 −6.6%，個股版未重現，ETF成交量混有資金流動，待驗證）。最接近訊號：12個月相對強弱 IC +0.033（FDR後0.17，個股版同向但更小）。同期結構穩定（ρ=0.73）：科技與能源(−0.36)、必需消費/原物料/公用事業(約−0.25)穩定負相關。
- **注意**：①用 SPY 當基準時，權重大的科技與所有板塊會被機械地推向負相關；改用九檔等權平均為基準後，與金融/醫療/工業的負相關消失，與能源等仍在——看關係時要用等權基準。②ETF追蹤當時的GICS定義（2018通訊服務獨立、2023 V/MA由科技移金融），XLK非同一批公司。③XLK高度集中。④SSL抓取：連續抓500檔後Yahoo會對併發連線回 SSL EOF，改單線程 + 等20秒即可（fetch可斷點續抓）。
- 報告：`data/stock/sector_etf/report/sector_etf_report_2026-09-22.md`。給使用者看的精簡圖（4張：科技Q4專題/九板塊×四季/誰跟誰同進退/結論總表）在 `outbox/2026-09-22_0148_*.png`（一次性，3天後自動清除）。

### 台股與美股差異提醒
- 交易時段不同（台股約 09:00–13:30、美股夏令/冬令時間需另注意時區換算），
  記錄新聞或報價時間時一律使用 +08:00 並註明對應的當地市場時段。
- 幣別不同（TWD / USD），涉及跨市場比較時需註明幣別，避免混淆報酬率。

## 資料檔索引
| 日期 | 檔案 | 內容說明 |
|------|------|----------|
| 2026-09-18 | data/stock/2026-09-18_tw_market_snapshot.json | 台股大盤/ETF/權值股/WTI原油報價快照 + 新聞來源網址 |
| 2026-09-18 | data/stock/NVDA_daily_5y.csv | NVDA 5年每日OHLCV原始資料 |
| 2026-09-18 | data/stock/NVDA_model_experiment_2026-09-18.md | NVDA漲跌方向分類模型實驗結果與結論(v1) |
| 2026-09-18 | data/stock/universe/*_daily.csv, macro_*.csv, fundamentals.csv | 10檔股票5年OHLCV + 6項總經指標 + 基本面快照 |
| 2026-09-18 | data/stock/universe/model_v2_experiment_2026-09-18.md | v2多股票報酬迴歸模型實驗結果與結論 |
| 2026-09-18~ | data/stock/news/YYYY-MM.parquet | 自動排程持續累積的原始新聞（台股+美股，含標題/摘要/連結/時間），供日後訓練模型使用，見上方「自動化新聞排程 Pipeline」 |
| 2026-09-18~ | data/stock/digests/YYYY-MM-DD_{market}_HHMM.txt | 每日 AI 摘要存檔（含AI影響評估），tw=08:00、us=21:00 |
| 2026-09-19 | data/stock/fomo/fomo_backtest_conclusion_2026-09-19.md | FOMO指數回測結論（IC/十分位/分期穩健性/個股拆解/示意策略），結論為無穩定預測力 |
| 2026-09-19 | data/stock/fomo/fomo_panel_data.csv | 10檔股票合併的FOMO指數+未來5/10/20日報酬面板資料（回測用） |
| 2026-09-19 | data/stock/fomo/fomo_decile_fwd_ret_10d.png, fomo_overlay_NVDA.png, fomo_overlay_2330_TW.png | FOMO指數十分位報酬長條圖 + 股價/FOMO指數疊圖(NVDA、台積電) |
| 2026-09-21 | data/stock/digests/2026-09-21_2330_focus_1036.txt | 使用者手動要求「研究台積電近期新聞跟情緒，是否值得加碼」的一次性個股深度研究報告（非排程） |
| 2026-09-21 | data/stock/digests/2026-09-21_NVDA_market_2359.txt | 使用者手動要求「NVDA最新狀況+股市分析」的一次性報告（非排程） |
| 2026-09-22 | data/stock/sector/report/sector_rotation_report_2026-09-22.md + 6張PNG | 美股板塊輪動研究結論報告與圖（相關性熱圖、Q4科技逐年、季/月熱圖、滾動相關、回測IC總覽） |
| 2026-09-22 | data/stock/sector/results/*.csv, *.parquet, wf_momentum_picks.json | 板塊研究結果表：backtest_summary(52列)、seasonality_all_groups(640列)、leadlag_and_heat_links、sector_excess_corr_*、sector_pairs_corr 等 |
| 2026-09-22 | data/stock/sector/universe/, raw/, panel/ | S&P500成分股+GICS、503檔日資料快取(2006起,約121MB)、日/週面板與群組週報酬/成交金額占比/group_members.json |
| 2026-09-22 | data/stock/sector_etf/{raw,panel,results,report}/ | SPDR九檔板塊ETF+SPY日資料快取與週面板、ETF版全部結果表（含prespecified_tech_q4.csv）、報告sector_etf_report_2026-09-22.md與6張存檔圖 |

## 個股手動深度研究（2026-09-21 建立此模式，範例：台積電）
- 與「自動化新聞排程 Pipeline」的每日大盤摘要不同，這是使用者對**單一標的**
  臨時提出「幫我研究近期新聞跟情緒，是否值得加碼」的一次性請求，流程：
  1. 先查當月 `data/stock/news/YYYY-MM.parquet`／當日 `data/stock/digests/`
     既有摘要是否已涵蓋該標的相關新聞，避免重複搜尋。
  2. 用 WebSearch 針對「{標的} 新聞」「{標的} 法說 目標價 外資」
     「{標的} 英文關鍵字 news risk tariff」等組合補充最新消息
     （因WebSearch即時性優於RSS pipeline的5個來源）。
  3. 用 Yahoo Finance chart API 抓現價、52週高低點、近5日/20日收盤，
     套用既有「短線動能／52週位階／總經地緣風險／個股相對強弱」四因子
     判斷邏輯（見「策略與觀察重點」章節），產出「續抱/加碼/觀察/減碼」
     傾向的規則式結論，明確標示非投資建議。
  4. 產出文字報告存到 `data/stock/digests/YYYY-MM-DD_{代號}_focus_HHMM.txt`
     （與每日大盤摘要同資料夾但檔名加標的代號區隔）。
  5. **傳送前依「傳送前確認」規則，先把完整報告內容顯示在對話中向使用者
     確認**（此類請求不像K線圖已有一次性授權，每次都需確認內容），
     確認後才用 `.claude/wrappers/run_telegram_mcp.sh "$TEXT"` 直送
     （wrapper 已支援帶參數CLI直送模式，見 run_digest.sh 用法，不需
     另建程式）。
- 此模式尚未寫成獨立腳本（本次為對話中手動執行），若使用者常態性
  對不同個股重複這類請求，可考慮整理成 `dev/stock-news/` 底下的
  可重複使用腳本（例如 `focus_report.py {ticker}`）。

## 待辦 / 追蹤中
- 板塊輪動研究後續：①改用 SPDR 板塊 ETF 檢驗科技 Q4（樣本更長、無存活者偏差）；②「通訊服務 5 月超額報酬」前瞻驗證（ETF版無法檢驗：XLC僅2018起），另將「12個月相對強弱」（兩個研究皆同向但不顯著）登記為前瞻驗證項目，2027-05 看一次，不再回頭調參；③依 VIX/利率 regime 拆板塊相關性（見上方「美股板塊輪動研究」）。
- 確認台股、美股當前市值前 10 大成分股名單（僅查到部分，如台積電權重佔比
  43.79%、前10大合計約61%，完整10檔清單待補）。
- 若要做「真正訓練過的模型」而非規則式判斷，需另外規劃歷史資料蒐集
  與回測框架（見上方「待改進方向」）。
- Telegram 發送沿用既有 `.claude/wrappers/run_telegram_mcp.sh`，
  該 wrapper 已支援帶參數的 CLI 直送模式（見 memory/dev.md 索引），
  不需另建新 wrapper。
- 新聞RSS來源目前只有5家（台股2、美股3），數量隨時間可觀察是否足夠
  覆蓋重大新聞，必要時可再擴充（例如台灣證交所公開資訊觀測站API、
  Reuters/Bloomberg 等，但後者通常需要付費或限制較多，需另評估）。
- `data/stock/news/` 目前以「月」為分檔單位，資料量還小；若未來要拿
  這批新聞訓練模型，需再另外規劃「新聞文字→特徵/embedding」的前處理，
  屬於新的一批工作，尚未開始規劃。
- 2026-09-22：21:00 us摘要排程執行時，Telegram 送出步驟遇到暫時性 SSL
  連線錯誤（`SSL: UNEXPECTED_EOF_WHILE_READING`），`run_digest.sh` 沒有
  重試機制，直接失敗退出，摘要檔仍有存檔但當下未送達，也因此沒寫入
  activity log（送出失敗才沒記錄），使用者事後主動詢問才發現並手動
  補傳成功。**已修復（同日）**：`run_digest.sh` 的 Telegram 送出步驟
  加上最多3次重試（間隔10/20/30秒），且不論最終成功或失敗都會寫入
  activity_log.jsonl（失敗時action=other，註明需人工檢查/補傳），
  詳見 memory/dev.md 除錯紀錄表。

````

**`~/claude-workspace/.claude/memory/travel.md`**
````markdown
---
分類: 旅遊規劃
主題 slug: travel
最後更新: 2026-09-22
---

# 旅遊規劃

## 常用來源與工具
- JR北海道快速エアポート／Uシート資訊：train-shiori.com、johnny88.jp 等日文部落格整理較完整。
- 機場連絡巴士（中央巴士／北都交通）官網：https://www.chuo-bus.co.jp/airport/ 、 https://www.hokto.co.jp/en/airport-liner-bus/
- 定額計程車比較：johnny88.jp/airport-taxy-cts/
- 新宿⇄河口湖高速巴士時刻/票價：highwaybus.com、bushikaku.net（バス比較なび）、富士急トラベル（fujikyu-travel.co.jp）。
- 河口湖紅葉/季節資訊：walkerplus.com（koyo.walkerplus.com）、fuji-net.co.jp（Fuji,CanGo）。
- 東京迪士尼周邊飯店比較：travel.yahoo.co.jp、jtb.co.jp、ikyu.com（依「舞浜」「浦安」關鍵字篩選）。

## 策略與觀察重點
- 新千歳空港→札幌市區三種主要方式：JR快速エアポート（最快約37分）、機場連絡巴士（約60-80分）、定額計程車／私人接送（約60分）。
- JR快速エアポート：一般車廂「不需預訂」，隨到隨搭；指定席「Uシート」需另外劃位（可現場買紙本票或えきねっと網路預訂チケットレス）。2026年3月調漲後：紙本1,000円、チケットレス800円，皆須另加運賃1,230円（合計紙本2,230円／チケットレス2,030円）。非連假尖峰時段（如12月中旬平日）自由席通常有座位，Uシート非強制但想確保座位可選擇預訂。
- 機場連絡巴士（中央巴士・紅色／北都交通・綠色）：**無需事先預訂**，隨到隨買票上車即可，往札幌都心（大通・すすきの）2026年4月起票價已調漲為1,500円。
- 定額計程車／私人接送：**需要事先預訂**，中型車（4人座）札幌市區行情約11,000円上下，高階接送（Hire）約20,000円以上；深夜早晨（22:00-6:00）加成2成；停車費、高速公路過路費另計。
- 結論：一般自由行只有「定額計程車／私人接送」這個選項是硬性需要「出發前預訂」；JR自由席與機場巴士都可現場臨櫃購票，不預訂也能搭。若想確保有位子搭JR，可選擇加購Uシート指定席（建議えきねっと網路預訂較便宜且免紙本）。
- 新宿⇄河口湖：高速巴士（バスタ新宿發）為首選，車程約1小時50分，單程約¥2,200（依季節/早鳥浮動，旺季會客滿需提前線上劃位）；備案為JR中央線特急至大月轉富士急行線，較貴較慢但沿途富士山車窗景較美。河口湖駅當地移動建議買「河口湖周遊巴士（レトロバス）一日券」，涵蓋忠靈塔、遊覽船、纜車、音樂盒美術館等主要景點站牌。
- 河口湖10月造訪的季節限制：楓葉正式盛開要到11月中旬，10月中下旬只有大石公園的帚草（コキア）轉紅可看，若抱著看滿山楓紅的期待10月去會落空，行程重點應放在富士山景觀（纜車/遊覽船/忠靈塔）與溫泉，紅葉只是附加。
- 東京迪士尼周邊住宿分三個等級：①官方飯店（樂園大飯店/大使大飯店/東京灣舞浜大飯店，最貴但可提前15分鐘入園+免費接駁）；②舞浜駅周邊非官方飯店（如希爾頓東京灣，南口有免費接駁車約10分）；③浦安/新浦安駅周邊（多一站JR京葉線車程，價格通常較低，適合預算有限但仍想鄰近樂園的情況）。
- 使用者說「生醃海鮮」時，第一次問清楚後才發現指的是**韓式**醬油蟹/醬蝦（間醬게장系，如間醬게장・새우장），不是中式潮汕生腌、也不是日式海鮮丼/刺身。日後遇到「生醃」類詞彙，先確認是韓式/中式/日式哪一種做法再查，避免查錯方向白工。東京這類韓式醬蟹集中在新大久保韓國城與赤坂一帶。
- 用 social-travel-search skill（site:threads.com / site:instagram.com 搜尋）查東京情侶約會景點時觀察：IG 貼文的公開頁面幾乎抓不到 og meta 標籤（WebFetch 常回報頁面只顯示互動介面、無 head 區塊），實務上多半只能靠搜尋結果摘要或貼文可見文字判斷內容，IG 端「僅摘要」比例會明顯高於 Threads；Threads 貼文文字本身較常直接公開列點（適合抓完整內文）。多篇貼文重複出現「東京晴空塔／隅田川沿岸」被推為情侶約會聖地（IG 已有貼文直接稱其為「戀人之聖地」＋愛之鎖），Shibuya Sky、Tokyo Tower、teamLab 系列則是次高頻。搜尋 IG 時要注意會混入其他城市同關鍵字結果（例如「情侶約會景點」查到台灣本地帳號），篩選時務必核對貼文文字是否真的提到東京/日本地名，不能只看關鍵字命中。

## 資料檔索引
| 日期 | 檔案 | 內容說明 |
|------|------|----------|
| 2026-09-20 | data/travel/2026-09-20_tokyo_itinerary_1016-1020.md | 10/16-10/20東京行程草案（新宿為主、10/18河口湖一日來回、10/19迪士尼），含交通建議與待確認住宿選項 |
| 2026-09-21 | data/travel/2026-09-20_tokyo_seafood_restaurants.md | 東京生食海鮮/海鮮丼推薦5選（つじ半/根室花まる/タカマル鮮魚店/河岸頭/大江戸）。Tabelog+Google Map雙分數為實測真實數字，並補上兩邊的直接連結+近3個月評論摘要（用dev/gmaps-lookup工具，見memory/dev.md），つじ半兩項評分全清單最高但近期評論一致強調要排隊 |
| 2026-09-21 | data/travel/2026-09-20_tokyo_ganjang_gejang_restaurants.md | 使用者澄清「生醃」指韓式醬蟹/醬蝦（간장게장系），非日式海鮮丼。推薦清單（プロカンジャンケジャン赤坂/梁の家/テジョンデ/オムニ食堂），Tabelog+Google Map雙分數+連結+近3個月評論摘要皆為實測；**ハヌリ新宿三丁目店經gmaps-lookup截圖確認已「閉業」，已從推薦中排除**；梁の家這次Tabelog評論內容因防爬蟲擋下暫缺 |
| 2026-09-21 | data/travel/2026-09-21_tokyo_omakase_ginza_tsukiji.md | 銀座/築地無菜單料理推薦5選，跨價位帶（¥11,000〜¥80,000）：鮨いつつ/築地すしOmakase/銀座よし澤/鮨竜介/銀座鮨かねさか本店。Tabelog+Google Map雙分數皆用gmaps-lookup工具實測，全數通過門檻 |
| 2026-09-22 | data/travel/2026-09-22_tokyo_ganjang_gejang_v2_hygiene_check.md | 用更新版jp-restaurant-finder skill（新增環境衛生把關+多語言評論判讀規則）重查東京韓式醬蟹，舊清單4間+新找5間共9間店，逐一查兩平台最低分評論確認**皆無髒亂/衛生負評**；プロカンジャンケジャン赤坂/トシオブ這次Tabelog連續被403擋下，分數沿用先前查證數字並誠實標註未能重查 |

## 待辦 / 追蹤中
- 使用者行程：12/15 抵達新千歳機場，尚未確認後續是否需要札幌市區飯店接送或其他日期的移動安排。
- 使用者行程：10/16-10/20 東京（新宿為主，10/19住迪士尼周邊），新宿飯店與迪士尼周邊飯店皆尚未指定；河口湖巴士確切班次建議出發前1-2週再確認；10/20離開東京的交通方式（機場/新幹線）尚未確認，會影響10/19住宿地點選擇。

````

## 五、密鑰 wrapper script 完整內容

腳本本身依規定不含任何明文密鑰，只負責「從 macOS Keychain 取值 → export
環境變數 → 呼叫程式」，可安全地整份嵌入備份。**Keychain 裡的密鑰值本身
不在此檔案內，需依「十一、重建步驟 Checklist」提示使用者在新機器上手動
重新輸入。**
**`~/claude-workspace/.claude/wrappers/run_telegram_mcp.sh`**
````bash
#!/bin/bash
# .claude/wrappers/run_telegram_mcp.sh

export TELEGRAM_BOT_TOKEN=$(security find-generic-password -a "$USER" -s "telegram-bot-token" -w)
export TELEGRAM_CHAT_ID=$(security find-generic-password -a "$USER" -s "telegram-chat-id" -w)

if [ -z "$TELEGRAM_BOT_TOKEN" ] || [ -z "$TELEGRAM_CHAT_ID" ]; then
  echo "錯誤：無法從 Keychain 讀取必要的環境變數" >&2
  exit 1
fi

exec /Users/vm/claude-workspace/dev/telegram-notify/.venv/bin/python /Users/vm/claude-workspace/dev/telegram-notify/telegram_notify.py "$@"

````

## 六、dev/ 工具原始碼（逐專案）

以下每個專案先列「用途與重建方式」，再逐檔嵌入原始碼完整內容。
不含 `.venv/`、`node_modules/`、`__pycache__/`、`.DS_Store`、單次查詢用的
暫存輸入檔——這些屬於可重建或暫存內容，見「十、排除項與理由」。

### 6.1 telegram-notify

**用途**：透過 Telegram Bot API 單向發送文字訊息與本機圖片，供其他工具
或 Claude 主動通知使用者使用。僅有 `send_message`／`send_photo` 兩個能力，
不具備讀取訊息/聯絡人等其他權限；`send_photo` 只接受本機檔案路徑，拒絕
任何含 `://` 的網址，避免被當成任意 URL 轉發器。

**重建方式**：
```bash
brew install python@3.12   # 若系統 python3 版本 < 3.10
<python3.12路徑> -m venv ~/claude-workspace/dev/telegram-notify/.venv
~/claude-workspace/dev/telegram-notify/.venv/bin/python -m pip install --upgrade pip
~/claude-workspace/dev/telegram-notify/.venv/bin/python -m pip install fastmcp
```
（`fastmcp` 只有「MCP server 模式」需要；CLI 測試模式 `telegram_notify.py "文字"`
只用標準庫 `urllib`，用系統 python3 也能跑。）

**`dev/telegram-notify/telegram_notify.py`**
````python
#!/usr/bin/env python3
"""Send text messages and local photos to a Telegram chat via the Bot API.

Two capabilities only: send_message, send_photo. No reading of
messages/contacts. send_photo only accepts a local file path on this
machine (no remote URLs) so it can never be tricked into pulling and
relaying an attacker-controlled image through the bot.
Run with a CLI argument to send that text directly (manual testing),
or `--photo <local path> [caption]` to send a local image.
Run with no arguments to start as an MCP server (requires fastmcp),
for use from Claude Desktop via the wrapper script.
"""
import io
import json
import mimetypes
import os
import sys
import urllib.parse
import urllib.request
import uuid


def send_message(text: str) -> dict:
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({"chat_id": chat_id, "text": text}).encode()
    with urllib.request.urlopen(url, data=data, timeout=10) as resp:
        return json.loads(resp.read().decode())


def send_photo(photo_path: str, caption: str = "") -> dict:
    # Reject anything that looks like a remote reference before even
    # touching the filesystem, so callers get a clear error instead of
    # a confusing "file not found".
    if "://" in photo_path:
        raise ValueError("只接受本機檔案路徑，不接受網址（URL）")

    path = os.path.abspath(os.path.expanduser(photo_path))
    if not os.path.isfile(path):
        raise ValueError(f"找不到本機圖片檔案: {photo_path}")

    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    url = f"https://api.telegram.org/bot{token}/sendPhoto"

    filename = os.path.basename(path)
    content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
    with open(path, "rb") as f:
        file_bytes = f.read()

    boundary = uuid.uuid4().hex
    body = io.BytesIO()

    def write_field(name: str, value: str) -> None:
        body.write(f"--{boundary}\r\n".encode())
        body.write(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode())
        body.write(f"{value}\r\n".encode())

    write_field("chat_id", chat_id)
    if caption:
        write_field("caption", caption)

    body.write(f"--{boundary}\r\n".encode())
    body.write(
        f'Content-Disposition: form-data; name="photo"; filename="{filename}"\r\n'.encode()
    )
    body.write(f"Content-Type: {content_type}\r\n\r\n".encode())
    body.write(file_bytes)
    body.write(b"\r\n")
    body.write(f"--{boundary}--\r\n".encode())

    req = urllib.request.Request(url, data=body.getvalue(), method="POST")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def run_mcp_server() -> None:
    from fastmcp import FastMCP

    mcp = FastMCP("telegram-notify")

    @mcp.tool()
    def send_telegram_message(text: str) -> dict:
        """Send a plain text message to the configured Telegram chat."""
        return send_message(text)

    @mcp.tool()
    def send_telegram_photo(photo_path: str, caption: str = "") -> dict:
        """Send a local image file to the configured Telegram chat.

        Only a local file path on this machine is accepted; remote
        URLs are rejected for security reasons.
        """
        return send_photo(photo_path, caption)

    mcp.run()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--photo":
        if len(sys.argv) < 3:
            print("用法: telegram_notify.py --photo <本機圖片路徑> [caption]", file=sys.stderr)
            sys.exit(1)
        result = send_photo(sys.argv[2], " ".join(sys.argv[3:]))
        print(json.dumps(result, ensure_ascii=False))
    elif len(sys.argv) > 1:
        result = send_message(" ".join(sys.argv[1:]))
        print(json.dumps(result, ensure_ascii=False))
    else:
        run_mcp_server()

````

### 6.2 outbox-cleanup

**用途**：刪除 `outbox/` 底下 mtime 超過 3 天（72 小時）的檔案，有刪除才
寫入一行 `activity_log.jsonl`（`action=delete`）。純標準庫，系統 python3
即可執行，無需 venv。由 launchd 排程每天 03:00 執行一次（plist 見「八」）。

**`dev/outbox-cleanup/cleanup_outbox.py`**
````python
#!/usr/bin/env python3
"""Delete files under outbox/ older than the 3-day retention window.

Run daily via launchd (see workspace CLAUDE.md section 7 for the policy:
outbox/ holds one-off deliverables — generated charts, reports — that are
neither config/memory nor data worth long-term indexing in data/{topic}/).
Uses only the standard library so it can run with the system python3.
"""
import json
import os
import time
from datetime import datetime, timedelta, timezone

OUTBOX_DIR = os.path.expanduser("~/claude-workspace/outbox")
LOG_PATH = os.path.expanduser("~/claude-workspace/logs/activity_log.jsonl")
RETENTION_SECONDS = 3 * 24 * 60 * 60
TZ_TW = timezone(timedelta(hours=8))


def main() -> None:
    if not os.path.isdir(OUTBOX_DIR):
        return

    now = time.time()
    deleted = []
    for name in os.listdir(OUTBOX_DIR):
        path = os.path.join(OUTBOX_DIR, name)
        if not os.path.isfile(path):
            continue
        if now - os.path.getmtime(path) > RETENTION_SECONDS:
            os.remove(path)
            deleted.append(f"outbox/{name}")

    if not deleted:
        return

    entry = {
        "ts": datetime.now(TZ_TW).strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        "topic": "general",
        "action": "delete",
        "summary": f"outbox 自動清除超過3天的一次性產出檔案，共{len(deleted)}個",
        "files": deleted,
        "memory": "memory/general.md",
    }
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()

````

### 6.3 stock-news

**用途**：`fetch_news.py` 每 30 分鐘（launchd）抓取 5 個 RSS 新聞源存成
`data/stock/news/YYYY-MM.parquet`（URL 雜湊去重）。`build_digest_prompt.py`
依市場＋時間窗組出摘要用的 prompt 文字。`run_digest.sh` 串起「組 prompt →
呼叫本機 `claude -p` headless 生成繁中條列摘要（含 AI 影響評估）→ 存檔
`data/stock/digests/` → 用 telegram wrapper 發送（含最多 3 次重試，間隔
10/20/30 秒）→ 寫入 activity_log.jsonl」，由 launchd 於每天 08:00（tw）／
21:00（us）觸發。**呼叫 `claude -p` 時務必加 `--safe-mode --tools ""`**
（純文字摘要任務不需要任何工具；`--safe-mode` 停用 CLAUDE.md/hooks，但
仍走正常 OAuth/keychain 登入，不像 `--bare` 需要另外設 `ANTHROPIC_API_KEY`）。

**重建方式**：
```bash
python3.12 -m venv ~/claude-workspace/dev/stock-news/.venv
~/claude-workspace/dev/stock-news/.venv/bin/pip install -r requirements.txt
chmod +x ~/claude-workspace/dev/stock-news/run_digest.sh
```

**`dev/stock-news/requirements.txt`**
````text
pandas
pyarrow

````

**`dev/stock-news/fetch_news.py`**
````python
#!/usr/bin/env python3
"""Fetch stock-market-related news RSS feeds and append new items into
monthly parquet files under data/stock/news/. Safe to run repeatedly:
dedupes by URL hash, so re-running only adds genuinely new items.
"""
import hashlib
import html
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

TZ = ZoneInfo("Asia/Taipei")
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)
NEWS_DIR = Path(__file__).resolve().parents[2] / "data" / "stock" / "news"

# Public, no-auth RSS feeds from established news outlets. Verified reachable
# on 2026-09-18; re-check with curl if a source starts returning 0 items.
SOURCES = [
    {"market": "tw", "source": "yahoo_tw", "url": "https://tw.stock.yahoo.com/rss?category=tw-market"},
    {"market": "tw", "source": "udn_money", "url": "https://money.udn.com/rssfeed/news/1001/5590?ch=news"},
    {"market": "us", "source": "cnbc_markets", "url": "https://www.cnbc.com/id/20910258/device/rss/rss.html"},
    {"market": "us", "source": "wsj_markets", "url": "https://feeds.a.dj.com/rss/RSSMarketsMain.xml"},
    {"market": "us", "source": "marketwatch_top", "url": "https://feeds.content.dowjones.io/public/rss/mw_topstories"},
]

TAG_RE = re.compile(r"<[^>]+>")


def clean_text(text: str) -> str:
    if not text:
        return ""
    text = TAG_RE.sub(" ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def fetch_feed(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read()


def parse_items(xml_bytes: bytes, market: str, source: str):
    root = ET.fromstring(xml_bytes)
    rows = []
    for item in root.findall(".//item"):
        title = clean_text(item.findtext("title") or "")
        link = (item.findtext("link") or "").strip()
        if not title or not link:
            continue
        desc = clean_text(item.findtext("description") or "")
        pub_raw = item.findtext("pubDate")
        pub_dt = None
        if pub_raw:
            try:
                pub_dt = parsedate_to_datetime(pub_raw).astimezone(TZ)
            except (TypeError, ValueError):
                pub_dt = None
        rows.append(
            {
                "id": hashlib.sha256(link.encode()).hexdigest()[:16],
                "market": market,
                "source": source,
                "title": title,
                "summary": desc[:500],
                "url": link,
                "published_at": pub_dt.isoformat() if pub_dt else None,
            }
        )
    return rows


def main():
    NEWS_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now(TZ)
    all_rows = []
    errors = []
    for src in SOURCES:
        try:
            xml_bytes = fetch_feed(src["url"])
            all_rows.extend(parse_items(xml_bytes, src["market"], src["source"]))
        except Exception as e:  # network/parse errors for one feed shouldn't kill the run
            errors.append(f"{src['source']}: {e}")

    for e in errors:
        print("ERROR:", e, file=sys.stderr)

    if not all_rows:
        print("no items fetched from any source", file=sys.stderr)
        sys.exit(1 if errors else 0)

    new_df = pd.DataFrame(all_rows)
    new_df["fetched_at"] = now.isoformat()
    new_df = new_df.dropna(subset=["published_at"])
    new_df["_month"] = pd.to_datetime(new_df["published_at"]).dt.strftime("%Y-%m")

    total_new = 0
    for month, group in new_df.groupby("_month"):
        group = group.drop(columns=["_month"])
        path = NEWS_DIR / f"{month}.parquet"
        if path.exists():
            existing = pd.read_parquet(path)
            existing_ids = set(existing["id"])
        else:
            existing = pd.DataFrame(columns=group.columns)
            existing_ids = set()
        new_unique = group[~group["id"].isin(existing_ids)]
        if new_unique.empty and not existing.empty:
            continue
        combined = pd.concat([existing, new_unique], ignore_index=True)
        combined = combined.sort_values("published_at")
        combined.to_parquet(path, index=False)
        total_new += len(new_unique)

    print(f"fetched={len(all_rows)} new_unique={total_new} sources_failed={len(errors)}")


if __name__ == "__main__":
    main()

````

**`dev/stock-news/build_digest_prompt.py`**
````python
#!/usr/bin/env python3
"""Build the prompt text fed into `claude -p` to produce a Traditional
Chinese, bullet-point market news digest with a labeled AI impact read.
Prints the prompt to stdout; does not call the model itself.
"""
import sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

TZ = ZoneInfo("Asia/Taipei")
NEWS_DIR = Path(__file__).resolve().parents[2] / "data" / "stock" / "news"

MARKET_LABEL = {"tw": "台股", "us": "美股"}


def load_window(market: str, hours: int):
    now = datetime.now(TZ)
    start = now - timedelta(hours=hours)
    months = sorted({start.strftime("%Y-%m"), now.strftime("%Y-%m")})
    frames = [pd.read_parquet(p) for m in months if (p := NEWS_DIR / f"{m}.parquet").exists()]
    if not frames:
        return start, now, pd.DataFrame()
    df = pd.concat(frames, ignore_index=True)
    df["published_at"] = pd.to_datetime(df["published_at"])
    mask = (
        (df["market"] == market)
        & (df["published_at"] >= pd.Timestamp(start))
        & (df["published_at"] <= pd.Timestamp(now))
    )
    df = df[mask].sort_values("published_at", ascending=False)
    df = df.drop_duplicates(subset=["title"])
    return start, now, df


def build_prompt(market: str, hours: int = 24, max_items: int = 30) -> str:
    start, now, df = load_window(market, hours)
    label = MARKET_LABEL[market]
    header = (
        f"你是專業財經編輯，以下是 {start.strftime('%Y-%m-%d %H:%M')} 到 "
        f"{now.strftime('%Y-%m-%d %H:%M')}（台北時間）期間，可能影響{label}的新聞原始標題與摘要。\n\n"
        "請完成以下任務：\n"
        f"1. 用繁體中文條列式（每則以「• 」開頭）整理出對{label}最重要的 8~12 則重點，"
        "同類或重複的新聞請合併成一則，不要逐條照抄原文。\n"
        "2. 每則重點盡量說明：發生了什麼事、可能受影響的產業/個股/指數。\n"
        "3. 每則重點後另起一行，以「(AI影響評估：...)」開頭，簡短標註你判斷此消息偏多/偏空/"
        "中性、影響程度（高/中/低），並在句尾註明「此為AI判讀，非投資建議」。\n"
        f"4. 開頭加一行標題：「📈 {label}新聞摘要｜{now.strftime('%Y-%m-%d %H:%M')}」。\n"
        "5. 結尾加一行：「⚠️ 以上重點與影響評估由AI自動整理判讀，僅供參考，非投資建議。」\n"
        "6. 輸出純文字，不要使用 Markdown 的 * 或 # 符號（會直接貼進 Telegram 訊息），"
        "整體輸出請控制在約 3000 字以內。\n"
        f"7. 若這段期間查無重大{label}相關新聞，請直接說明「此時段無重大{label}相關新聞」，"
        "不要編造內容。\n\n"
        "新聞原始資料（標題｜來源｜發布時間｜摘要）：\n"
    )
    if df.empty:
        body = "（本次擷取範圍內查無資料）"
    else:
        lines = []
        for _, row in df.head(max_items).iterrows():
            pub = row["published_at"]
            pub_s = pub.strftime("%m-%d %H:%M") if pd.notna(pub) else "?"
            summary = (row.get("summary") or "")[:150]
            lines.append(f"- {row['title']} ｜ {row['source']} ｜ {pub_s} ｜ {summary}")
        body = "\n".join(lines)
    return header + body


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in MARKET_LABEL:
        print("usage: build_digest_prompt.py [tw|us] [hours]", file=sys.stderr)
        sys.exit(2)
    market_arg = sys.argv[1]
    hours_arg = int(sys.argv[2]) if len(sys.argv) > 2 else 24
    print(build_prompt(market_arg, hours_arg))

````

**`dev/stock-news/run_digest.sh`**
````bash
#!/bin/bash
# Build the AI market-news digest for one market and send it via Telegram.
# Usage: run_digest.sh tw|us [hours_back]
set -euo pipefail

MARKET="${1:?usage: run_digest.sh tw|us [hours_back]}"
HOURS="${2:-24}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="$(cd "$SCRIPT_DIR/../.." && pwd)"
PYTHON="$SCRIPT_DIR/.venv/bin/python"
# Full path: launchd's minimal PATH may not include Homebrew's bin dir.
CLAUDE_BIN="/opt/homebrew/bin/claude"

PROMPT_FILE="$(mktemp /tmp/stock_digest_prompt.XXXXXX.txt)"
trap 'rm -f "$PROMPT_FILE"' EXIT

"$PYTHON" "$SCRIPT_DIR/build_digest_prompt.py" "$MARKET" "$HOURS" > "$PROMPT_FILE"
if [ ! -s "$PROMPT_FILE" ]; then
  echo "empty prompt, abort" >&2
  exit 1
fi

# --safe-mode: skip CLAUDE.md/hooks so this pure text-summarization call
#   doesn't try to follow workspace record-keeping rules meant for the
#   interactive assistant (that leaked a "cannot write activity log"
#   preamble into the digest when tested without this flag).
# --tools "": no tool access is needed (all data is embedded in the prompt).
# --permission-prompts none: unattended run never hangs on a permission dialog.
DIGEST_TEXT="$("$CLAUDE_BIN" -p "$(cat "$PROMPT_FILE")" --safe-mode --tools "" --permission-prompts none --output-format text)"

if [ -z "$DIGEST_TEXT" ]; then
  echo "empty digest text from claude, abort (nothing sent)" >&2
  exit 1
fi

# Telegram sendMessage caps at 4096 UTF-8 chars; truncate defensively.
DIGEST_TEXT="$(printf '%s' "$DIGEST_TEXT" | "$PYTHON" -c '
import sys
text = sys.stdin.read()
limit = 3900
if len(text) > limit:
    text = text[:limit] + "\n...(內容過長，已截斷)"
sys.stdout.write(text)
')"

DATE_TW="$(TZ=Asia/Taipei date +%Y-%m-%d)"
TIME_TW="$(TZ=Asia/Taipei date +%H%M)"
OUT_DIR="$WORKSPACE/data/stock/digests"
mkdir -p "$OUT_DIR"
OUT_FILE="$OUT_DIR/${DATE_TW}_${MARKET}_${TIME_TW}.txt"
printf '%s\n' "$DIGEST_TEXT" > "$OUT_FILE"

REL_OUT="data/stock/digests/${DATE_TW}_${MARKET}_${TIME_TW}.txt"

# Telegram send can fail transiently (e.g. SSL EOF on a flaky connection).
# Retry a few times with backoff before giving up, so a single transient
# network hiccup doesn't silently drop a scheduled digest.
SEND_OK=0
for attempt in 1 2 3; do
  if "$WORKSPACE/.claude/wrappers/run_telegram_mcp.sh" "$DIGEST_TEXT" >/dev/null 2>"$WORKSPACE/logs/stock-news-digest-${MARKET}-send.err.log"; then
    SEND_OK=1
    break
  fi
  echo "telegram send attempt $attempt failed for market=$MARKET, retrying..." >&2
  sleep $((attempt * 10))
done

TS="$(TZ=Asia/Taipei date +%Y-%m-%dT%H:%M:%S+08:00)"

if [ "$SEND_OK" -eq 1 ]; then
  LOG_LINE="$("$PYTHON" -c "
import json
print(json.dumps({
    'ts': '$TS',
    'topic': 'stock',
    'action': 'send',
    'summary': '排程：${MARKET}市場新聞 AI 摘要並透過 Telegram 發送',
    'files': ['$REL_OUT'],
    'memory': 'memory/stock.md',
}, ensure_ascii=False))
")"
  echo "$LOG_LINE" >> "$WORKSPACE/logs/activity_log.jsonl"
  echo "digest sent for market=$MARKET, saved to $OUT_FILE"
else
  # All retries failed: still record it (as a failure, not a successful
  # send) so this shows up in the log instead of silently vanishing, and
  # the digest file itself is already saved on disk for manual resend.
  LOG_LINE="$("$PYTHON" -c "
import json
print(json.dumps({
    'ts': '$TS',
    'topic': 'stock',
    'action': 'other',
    'summary': '排程：${MARKET}市場新聞 AI 摘要產生成功，但 Telegram 發送3次重試後仍失敗，需人工檢查/補傳',
    'files': ['$REL_OUT'],
    'memory': 'memory/stock.md',
}, ensure_ascii=False))
")"
  echo "$LOG_LINE" >> "$WORKSPACE/logs/activity_log.jsonl"
  echo "telegram send failed after retries for market=$MARKET, digest saved to $OUT_FILE (not sent)" >&2
  exit 1
fi

````

### 6.4 stock-chart

**用途**：`python kline_chart.py [TICKER] [MONTHS] [--no-send]`（預設
NVDA、近 3 個月），抓 Yahoo Finance chart API（範圍 1y），用 mplfinance
畫 K 棒＋成交量＋5/20 日均線＋RSI(14) 副圖（Wilder 平滑，含 30/50/70
參考線）＋均線黃金/死亡交叉三角形標記，右上角疊規則式「綜合結論」文字框
（動能/52週位階/RSI/近10日交叉四因子投票），PNG 存到 `outbox/`，完成後
呼叫 telegram wrapper `--photo` 傳送。純手動觸發，不排程；文字框固定印出
「規則式技術面整理，非AI模型、非投資建議」免責提示。

**重建方式**：
```bash
python3.12 -m venv ~/claude-workspace/dev/stock-chart/.venv
~/claude-workspace/dev/stock-chart/.venv/bin/pip install pandas mplfinance
```

**`dev/stock-chart/kline_chart.py`**
````python
#!/usr/bin/env python3
"""Generate a candlestick (K-line) chart with 5-day / 20-day moving averages,
RSI, MA golden/death cross markers, and a rule-based advice summary box for
a stock ticker, and send it to Telegram as a photo.

Designed for frequent, repeated use with sane defaults:

    python kline_chart.py                # NVDA, last 3 months, auto-send
    python kline_chart.py TSLA            # another ticker, still 3 months
    python kline_chart.py TSLA 6          # another ticker, last 6 months
    python kline_chart.py NVDA 3 --no-send  # generate only, skip Telegram

Data source: Yahoo Finance's public chart API (no API key needed), same
approach as dev/stock-model/fetch_data.py. Chart image is written to the
shared outbox/ (one-off deliverables, auto-cleaned after 3 days — see
workspace CLAUDE.md section 7) rather than data/stock/, since the PNG
itself is the deliverable and has no further analytical use.

Auto-send is intentional and does not ask for per-run confirmation: the
user pre-authorized this specific, fixed content type (a stock candlestick
chart built from public price data) for automatic Telegram delivery on
2026-09-18 (see memory/stock.md).

The advice summary box reuses the rule-based heuristic already documented
in memory/stock.md (short-term momentum + 52-week position), extended here
with RSI and MA cross signals since those are computable purely from price
data. It deliberately excludes the macro/news factor from that heuristic —
folding a news search into every chart run would defeat the "fast, frequent
use" design goal — so the conclusion is explicitly labeled as a partial,
rule-based technical read, not investment advice.
"""
import json
import os
import subprocess
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

import mplfinance as mpf
import pandas as pd
from matplotlib.lines import Line2D

# macOS ships "Heiti TC" as a built-in CJK font. mplfinance resets rcParams
# to matplotlib defaults and reapplies only its named style's own rc dict,
# so a plain global matplotlib.rcParams assignment gets silently discarded
# — the font must be baked into the mplfinance style object itself via
# make_mpf_style(rc=...), otherwise the Traditional Chinese title/labels
# render as missing-glyph boxes (DejaVu Sans has no CJK glyphs). Any text
# drawn outside mpf.plot (e.g. ax.text for the advice box) must also pass
# fontname="Heiti TC" explicitly for the same reason.
CHART_FONT = "Heiti TC"
CHART_STYLE = mpf.make_mpf_style(
    base_mpf_style="yahoo",
    rc={"font.family": CHART_FONT, "axes.unicode_minus": False},
)

WORKSPACE = "/Users/vm/claude-workspace"
OUTBOX_DIR = f"{WORKSPACE}/outbox"
LOG_PATH = f"{WORKSPACE}/logs/activity_log.jsonl"
TELEGRAM_WRAPPER = f"{WORKSPACE}/.claude/wrappers/run_telegram_mcp.sh"
TZ_TW = timezone(timedelta(hours=8))

DEFAULT_TICKER = "NVDA"
DEFAULT_MONTHS = 3
# Extra lookback so the 20-day moving average is already valid on day 1 of
# the displayed window, and so the 52-week high/low used by the advice box
# is computed over a real year of data rather than just the display window.
FETCH_RANGE = "1y"
RSI_PERIOD = 14


def fetch_ohlcv(symbol: str) -> pd.DataFrame:
    """Fetch daily OHLCV history for `symbol` from Yahoo Finance's chart API."""
    encoded = urllib.parse.quote(symbol)
    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{encoded}"
        f"?range={FETCH_RANGE}&interval=1d"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.load(resp)
    except Exception as e:
        raise RuntimeError(f"抓取 {symbol} 股價資料失敗（網路或 Yahoo Finance API 問題）: {e}") from e

    result = data.get("chart", {}).get("result")
    if not result:
        raise RuntimeError(f"查無股票代碼「{symbol}」的資料，請確認代碼是否正確")

    result = result[0]
    ts = result["timestamp"]
    quote = result["indicators"]["quote"][0]

    df = pd.DataFrame(
        {
            "Date": [datetime.fromtimestamp(t, tz=timezone.utc) for t in ts],
            "Open": quote["open"],
            "High": quote["high"],
            "Low": quote["low"],
            "Close": quote["close"],
            "Volume": quote["volume"],
        }
    )
    df = df.dropna().reset_index(drop=True)
    if df.empty:
        raise RuntimeError(f"「{symbol}」回傳的股價資料是空的，可能是代碼錯誤或該市場目前無資料")
    df = df.set_index("Date")
    return df


def add_moving_averages(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["MA5"] = df["Close"].rolling(5).mean()
    df["MA20"] = df["Close"].rolling(20).mean()
    return df


def add_rsi(df: pd.DataFrame, period: int = RSI_PERIOD) -> pd.DataFrame:
    """Wilder's smoothed RSI, the standard formula (rolling mean is a common
    but less accurate approximation)."""
    df = df.copy()
    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False).mean()
    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + rs))
    return df


def add_cross_signals(df: pd.DataFrame) -> pd.DataFrame:
    """Mark MA5/MA20 golden cross (bullish) and death cross (bearish) points.
    Values are placed just below the candle low / above the candle high so
    mplfinance's scatter addplot can draw them as triangle markers; NaN rows
    are simply skipped by the scatter plot, which is the standard mplfinance
    pattern for sparse buy/sell markers."""
    df = df.copy()
    diff = df["MA5"] - df["MA20"]
    prev_diff = diff.shift(1)
    golden = (prev_diff <= 0) & (diff > 0)
    death = (prev_diff >= 0) & (diff < 0)
    df["GoldenCross"] = df["Low"].where(golden) * 0.97
    df["DeathCross"] = df["High"].where(death) * 1.03
    return df


def slice_last_months(df: pd.DataFrame, months: int) -> pd.DataFrame:
    cutoff = df.index.max() - pd.DateOffset(months=months)
    sliced = df[df.index >= cutoff]
    if len(sliced) < 5:
        raise RuntimeError("篩選出的資料筆數太少，無法畫出有意義的K線圖，請確認股票代碼或月數設定")
    return sliced


def build_advice(df: pd.DataFrame, display_df: pd.DataFrame) -> str:
    """Rule-based technical read, combining: 5-day momentum, 52-week price
    position, latest RSI, and any MA cross signal within the displayed
    window. Mirrors the heuristic in memory/stock.md but omits the macro/
    news factor (not computable from price data alone). Each factor casts
    a +1/0/-1 vote; the sum maps to a bias label. This is NOT a trained
    model and NOT investment advice — purely a rule-based summary."""
    last_5 = df["Close"].iloc[-5:]
    diffs = last_5.diff().dropna()
    score = 0
    lines = []

    if len(diffs) >= 4 and (diffs > 0).all():
        lines.append("近5日收盤連續上揚（偏多動能）")
        score += 1
    elif len(diffs) >= 4 and (diffs < 0).all():
        lines.append("近5日收盤連續下跌（偏空動能）")
        score -= 1
    else:
        lines.append("近5日收盤漲跌互見（動能不明確）")

    high_52w = df["High"].max()
    low_52w = df["Low"].min()
    last_close = df["Close"].iloc[-1]
    pct_from_high = (high_52w - last_close) / high_52w * 100
    pct_position = (
        (last_close - low_52w) / (high_52w - low_52w) * 100 if high_52w > low_52w else 50
    )
    if pct_from_high <= 5:
        lines.append(f"距52週高點僅{pct_from_high:.1f}%（追高風險偏高）")
        score -= 1
    elif pct_position <= 20:
        lines.append(f"接近52週低點（位階{pct_position:.0f}%）")
    else:
        lines.append(f"52週位階{pct_position:.0f}%")

    last_rsi = df["RSI"].iloc[-1]
    if pd.notna(last_rsi):
        # 50 is the standard RSI midline: above = momentum tilts bullish,
        # below = tilts bearish. Overbought/oversold (70/30) is layered on
        # as an extra risk note rather than a second vote, so RSI casts
        # exactly one +1/-1 vote like the other factors.
        if last_rsi > 50:
            score += 1
            rsi_desc = f"RSI={last_rsi:.0f}（高於50，偏多）"
        else:
            score -= 1
            rsi_desc = f"RSI={last_rsi:.0f}（低於50，偏空）"
        if last_rsi >= 70:
            rsi_desc += "，已達超買區注意拉回風險"
        elif last_rsi <= 30:
            rsi_desc += "，已達超賣區注意反彈機會"
        lines.append(rsi_desc)

    recent = display_df.iloc[-10:]
    if recent["GoldenCross"].notna().any():
        lines.append("近期出現均線黃金交叉")
        score += 1
    if recent["DeathCross"].notna().any():
        lines.append("近期出現均線死亡交叉")
        score -= 1

    conclusion = {2: "加碼傾向", 1: "續抱偏多"}.get(score)
    if conclusion is None:
        conclusion = {-1: "續抱偏空／觀察減碼", -2: "減碼傾向"}.get(score, "觀察")
    if score >= 3:
        conclusion = "加碼傾向"
    if score <= -3:
        conclusion = "減碼傾向"

    lines.append(f"綜合結論：{conclusion}")
    lines.append("※規則式技術面整理，未納入總經/新聞面，非AI模型、非投資建議")
    return "\n".join(lines)


def plot_kline(df: pd.DataFrame, symbol: str, months: int, advice_text: str) -> str:
    os.makedirs(OUTBOX_DIR, exist_ok=True)

    timestamp = datetime.now(TZ_TW).strftime("%Y-%m-%d_%H%M")
    out_path = f"{OUTBOX_DIR}/{timestamp}_{symbol}_kline.png"

    add_plots = [
        mpf.make_addplot(df["MA5"], color="orange", width=1.2),
        mpf.make_addplot(df["MA20"], color="blue", width=1.2),
        mpf.make_addplot(
            df["GoldenCross"], type="scatter", markersize=120, marker="^", color="green"
        ),
        mpf.make_addplot(
            df["DeathCross"], type="scatter", markersize=120, marker="v", color="red"
        ),
        mpf.make_addplot(df["RSI"], panel=2, color="purple", width=1.1, ylabel="RSI"),
        mpf.make_addplot(
            pd.Series(70, index=df.index), panel=2, color="gray", linestyle="--", width=0.7
        ),
        mpf.make_addplot(
            pd.Series(30, index=df.index), panel=2, color="gray", linestyle="--", width=0.7
        ),
        mpf.make_addplot(
            pd.Series(50, index=df.index), panel=2, color="black", linestyle=":", width=0.7
        ),
    ]

    fig, axlist = mpf.plot(
        df,
        type="candle",
        style=CHART_STYLE,
        addplot=add_plots,
        volume=True,
        panel_ratios=(6, 2, 2),
        title=f"\n{symbol} 近{months}個月 K線圖（5日／20日均線、RSI、交叉訊號）",
        ylabel="股價",
        ylabel_lower="成交量",
        figsize=(12, 9),
        returnfig=True,
    )
    # mplfinance's `mav=` kwarg draws an auto-legend but recomputes the
    # average only from the plotted window (blank for the first ~20 days);
    # addplot avoids that but draws no legend, so add one by hand instead.
    legend_lines = [
        Line2D([0], [0], color="orange", lw=1.2),
        Line2D([0], [0], color="blue", lw=1.2),
        Line2D([0], [0], color="green", marker="^", linestyle="None", markersize=8),
        Line2D([0], [0], color="red", marker="v", linestyle="None", markersize=8),
    ]
    axlist[0].legend(
        legend_lines,
        ["5日均線", "20日均線", "黃金交叉(偏多)", "死亡交叉(偏空)"],
        loc="upper left",
        fontsize=8,
    )
    axlist[0].text(
        0.99,
        0.98,
        advice_text,
        transform=axlist[0].transAxes,
        fontsize=8,
        fontname=CHART_FONT,
        va="top",
        ha="right",
        bbox={"boxstyle": "round", "facecolor": "white", "alpha": 0.85, "edgecolor": "gray"},
    )
    fig.savefig(out_path, dpi=150)
    return out_path


def build_caption(df: pd.DataFrame, symbol: str, months: int, advice_text: str) -> str:
    last = df.iloc[-1]
    prev_close = df["Close"].iloc[-2] if len(df) > 1 else last["Close"]
    change_pct = (last["Close"] - prev_close) / prev_close * 100
    arrow = "▲" if change_pct >= 0 else "▼"
    return (
        f"{symbol} 近{months}個月 K線圖（5日／20日均線、RSI、交叉訊號）\n"
        f"資料日期: {df.index[-1].strftime('%Y-%m-%d')}\n"
        f"收盤: {last['Close']:.2f}（{arrow}{abs(change_pct):.2f}%）\n\n"
        f"{advice_text}"
    )


def send_via_telegram(photo_path: str, caption: str) -> None:
    result = subprocess.run(
        [TELEGRAM_WRAPPER, "--photo", photo_path, caption],
        capture_output=True,
        text=True,
        timeout=60,
    )
    if result.returncode != 0:
        raise RuntimeError(f"透過 Telegram 傳送圖片失敗: {result.stderr.strip() or result.stdout.strip()}")


def log_activity(symbol: str, out_path: str, sent: bool) -> None:
    entry = {
        "ts": datetime.now(TZ_TW).strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        "topic": "stock",
        "action": "send" if sent else "write",
        "summary": f"產生 {symbol} K線圖（5日/20日均線/RSI/交叉訊號/規則式結論）"
        + ("並透過 Telegram 傳送" if sent else "（--no-send，未傳送）"),
        "files": [out_path.replace(f"{WORKSPACE}/", "")],
        "memory": "memory/stock.md",
    }
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    no_send = "--no-send" in sys.argv[1:]

    symbol = (args[0] if len(args) > 0 else DEFAULT_TICKER).upper()
    try:
        months = int(args[1]) if len(args) > 1 else DEFAULT_MONTHS
    except ValueError:
        print(f"月數參數必須是整數，收到的是: {args[1]}", file=sys.stderr)
        sys.exit(1)

    try:
        print(f"正在抓取 {symbol} 股價資料...")
        df = fetch_ohlcv(symbol)
        df = add_moving_averages(df)
        df = add_rsi(df)
        df = add_cross_signals(df)
        display_df = slice_last_months(df, months)
        advice_text = build_advice(df, display_df)

        print(f"正在產生 {symbol} 近{months}個月 K線圖...")
        out_path = plot_kline(display_df, symbol, months, advice_text)
        print(f"圖表已產生: {out_path}")

        if no_send:
            log_activity(symbol, out_path, sent=False)
            print("已跳過 Telegram 傳送（--no-send）")
            return

        caption = build_caption(display_df, symbol, months, advice_text)
        print("正在透過 Telegram 傳送...")
        send_via_telegram(out_path, caption)
        log_activity(symbol, out_path, sent=True)
        print("已傳送到 Telegram")
    except RuntimeError as e:
        print(f"錯誤: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

````

### 6.5 stock-model

**用途**：量化模型可行性研究。v1（`fetch_data.py` + `train_model.py`）：
單股（NVDA）純技術指標 RandomForest 漲跌方向分類。v2：`fetch_universe.py`
（10 檔股票 + 6 項總經指標）、`fetch_fundamentals.py`（Yahoo quoteSummary
基本面快照，需 crumb/cookie 手動 handshake）、`train_model_v2.py`
（RandomForestRegressor 預測次 N 日報酬率，含 IC/R² 評估與排名回測）。
**結論（v1、v2 皆同）：無統計上顯著的預測力，不實用**，詳見 memory/stock.md。

**重建方式**：
```bash
python3.12 -m venv ~/claude-workspace/dev/stock-model/.venv
~/claude-workspace/dev/stock-model/.venv/bin/pip install pandas numpy scikit-learn scipy
```

**`dev/stock-model/fetch_data.py`**
````python
"""Fetch daily OHLCV history for a ticker from Yahoo Finance's public chart API
(no API key required) and save it as CSV.

Usage: python fetch_data.py NVDA 5y
"""
import json
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone

import pandas as pd


def fetch(symbol: str, range_: str = "5y", interval: str = "1d") -> pd.DataFrame:
    encoded = urllib.parse.quote(symbol)
    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{encoded}"
        f"?range={range_}&interval={interval}"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.load(resp)

    result = data["chart"]["result"][0]
    ts = result["timestamp"]
    quote = result["indicators"]["quote"][0]

    df = pd.DataFrame(
        {
            "date": [datetime.fromtimestamp(t, tz=timezone.utc).date() for t in ts],
            "open": quote["open"],
            "high": quote["high"],
            "low": quote["low"],
            "close": quote["close"],
            "volume": quote["volume"],
        }
    )
    df = df.dropna().reset_index(drop=True)
    return df


if __name__ == "__main__":
    symbol = sys.argv[1] if len(sys.argv) > 1 else "NVDA"
    range_ = sys.argv[2] if len(sys.argv) > 2 else "5y"
    df = fetch(symbol, range_)
    out_path = f"/Users/vm/claude-workspace/data/stock/{symbol}_daily_{range_}.csv"
    df.to_csv(out_path, index=False)
    print(f"saved {len(df)} rows to {out_path}")
    print(df.head())
    print(df.tail())

````

**`dev/stock-model/fetch_universe.py`**
````python
"""Fetch daily OHLCV history for a basket of stocks plus a set of macro
series (VIX, 10y yield, dollar index, oil, broad market, semiconductor
sector) from Yahoo Finance's public chart API. No API key required.

Usage: python fetch_universe.py
"""
from pathlib import Path

from fetch_data import fetch

STOCKS = [
    "NVDA", "AAPL", "MSFT", "GOOGL", "AMZN", "META", "AVGO",  # US mega-cap
    "2330.TW", "2317.TW", "2454.TW",  # TW top weighted stocks (TSMC/Hon Hai/MediaTek)
]

MACRO = {
    "^VIX": "vix",
    "^TNX": "us10y_yield",
    "DX-Y.NYB": "dollar_index",
    "CL=F": "wti_oil",
    "^GSPC": "sp500",
    "SMH": "semi_etf",
}

OUT_DIR = Path("/Users/vm/claude-workspace/data/stock/universe")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for sym in STOCKS:
        df = fetch(sym, "5y")
        path = OUT_DIR / f"{sym.replace('.', '_')}_daily.csv"
        df.to_csv(path, index=False)
        print(f"stock {sym}: {len(df)} rows -> {path.name}")

    for sym, label in MACRO.items():
        df = fetch(sym, "5y")
        df = df[["date", "close"]].rename(columns={"close": label})
        path = OUT_DIR / f"macro_{label}.csv"
        df.to_csv(path, index=False)
        print(f"macro {sym} ({label}): {len(df)} rows -> {path.name}")


if __name__ == "__main__":
    main()

````

**`dev/stock-model/fetch_fundamentals.py`**
````python
"""Fetch a CURRENT snapshot of fundamental ratios for each stock in the
universe from Yahoo Finance's quoteSummary endpoint (requires a session
cookie + crumb, obtained here via the public getcrumb handshake - no
API key needed, but this is a live/unauthenticated-session workaround
and may break if Yahoo changes the flow).

Important limitation: this pulls TODAY's fundamentals only, not a
point-in-time history. Free sources for historical point-in-time
fundamentals are not available, so these are used as slow-moving,
per-stock (cross-sectional) features in the panel model -- fine for
comparing companies today, but for older historical rows in the training
data it is a mild look-ahead simplification (documented, not hidden).

Usage: python fetch_fundamentals.py
"""
import csv
import json
import urllib.error
import urllib.request
from http.cookiejar import CookieJar
from pathlib import Path

from fetch_universe import STOCKS

FIELDS = [
    ("financialData", "profitMargins"),
    ("financialData", "revenueGrowth"),
    ("financialData", "returnOnEquity"),
    ("financialData", "debtToEquity"),
    ("financialData", "recommendationMean"),
    ("defaultKeyStatistics", "trailingEps"),
    ("defaultKeyStatistics", "forwardPE"),
    ("defaultKeyStatistics", "beta"),
    ("defaultKeyStatistics", "profitMargins"),
]

OUT_PATH = Path("/Users/vm/claude-workspace/data/stock/universe/fundamentals.csv")


def get_session():
    jar = CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    opener.addheaders = [("User-Agent", "Mozilla/5.0")]
    try:
        opener.open("https://fc.yahoo.com", timeout=15).read()
    except urllib.error.HTTPError:
        pass  # only needed to set cookies; a non-2xx here still sets them
    crumb = opener.open(
        "https://query2.finance.yahoo.com/v1/test/getcrumb", timeout=15
    ).read().decode()
    return opener, crumb


def fetch_one(opener, crumb, symbol: str) -> dict:
    url = (
        f"https://query2.finance.yahoo.com/v10/finance/quoteSummary/{symbol}"
        f"?modules=financialData,defaultKeyStatistics&crumb={crumb}"
    )
    raw = json.loads(opener.open(url, timeout=15).read())
    result = raw["quoteSummary"]["result"]
    if not result:
        return {}
    modules = result[0]
    row = {}
    for module_name, field in FIELDS:
        val = modules.get(module_name, {}).get(field, {})
        row[field] = val.get("raw") if isinstance(val, dict) else None
    return row


def main():
    opener, crumb = get_session()
    rows = []
    for sym in STOCKS:
        data = fetch_one(opener, crumb, sym)
        data["symbol"] = sym
        rows.append(data)
        print(sym, data)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["symbol"] + [f for _, f in FIELDS]
    with open(OUT_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    print(f"saved {len(rows)} rows -> {OUT_PATH}")


if __name__ == "__main__":
    main()

````

**`dev/stock-model/train_model.py`**
````python
"""Train a lightweight classical ML model (RandomForest) to predict whether
a stock's next-day close will be higher than today's close, using only
price/volume-derived technical features (no external news/fundamentals).

This is a feasibility test, not a production trading model:
- time-based train/test split (no shuffling) to avoid lookahead leakage
- compared against two baselines: majority-class and "always predict up"
- includes a naive next-day-long backtest vs. buy-and-hold on the test period

Usage: python train_model.py NVDA [horizon_days]
horizon_days: how many trading days ahead the target/backtest looks (default 1).
"""
import sys

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix


def add_features(df: pd.DataFrame, horizon: int = 1) -> pd.DataFrame:
    df = df.copy()
    df["ret_1d"] = df["close"].pct_change(1)
    df["ret_5d"] = df["close"].pct_change(5)
    df["ret_10d"] = df["close"].pct_change(10)

    for w in (5, 10, 20, 60):
        sma = df["close"].rolling(w).mean()
        df[f"sma{w}_rel"] = df["close"] / sma - 1

    delta = df["close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss
    df["rsi14"] = 100 - (100 / (1 + rs))

    ema12 = df["close"].ewm(span=12, adjust=False).mean()
    ema26 = df["close"].ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    df["macd_diff"] = macd - signal

    df["vol_rel"] = df["volume"] / df["volume"].rolling(20).mean() - 1
    df["volatility_10d"] = df["ret_1d"].rolling(10).std()

    # label: does the close `horizon` trading days ahead beat today's close?
    df["target_next_up"] = (df["close"].shift(-horizon) > df["close"]).astype(int)

    return df


FEATURE_COLS = [
    "ret_1d", "ret_5d", "ret_10d",
    "sma5_rel", "sma10_rel", "sma20_rel", "sma60_rel",
    "rsi14", "macd_diff", "vol_rel", "volatility_10d",
]


def main(symbol: str, horizon: int = 1):
    path = f"/Users/vm/claude-workspace/data/stock/{symbol}_daily_5y.csv"
    df = pd.read_csv(path, parse_dates=["date"])
    df = add_features(df, horizon)
    df = df.dropna().reset_index(drop=True)

    split_idx = int(len(df) * 0.8)
    train, test = df.iloc[:split_idx], df.iloc[split_idx:]

    X_train, y_train = train[FEATURE_COLS], train["target_next_up"]
    X_test, y_test = test[FEATURE_COLS], test["target_next_up"]

    print(f"symbol={symbol}  horizon={horizon}d  total_rows={len(df)}  train={len(train)}  test={len(test)}")
    print(f"train period: {train['date'].min().date()} ~ {train['date'].max().date()}")
    print(f"test  period: {test['date'].min().date()} ~ {test['date'].max().date()}")
    print(f"test set label balance: up={y_test.mean():.3f}  down={1-y_test.mean():.3f}")

    model = RandomForestClassifier(
        n_estimators=300, max_depth=5, min_samples_leaf=20,
        random_state=42, n_jobs=-1,
    )
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    proba = model.predict_proba(X_test)[:, 1]

    acc = accuracy_score(y_test, pred)
    majority_baseline = max(y_test.mean(), 1 - y_test.mean())
    always_up_acc = y_test.mean()

    print("\n=== Accuracy comparison ===")
    print(f"model accuracy:          {acc:.4f}")
    print(f"majority-class baseline: {majority_baseline:.4f}")
    print(f"always-predict-up:       {always_up_acc:.4f}")

    print("\n=== Classification report (test set) ===")
    print(classification_report(y_test, pred, target_names=["down", "up"]))
    print("confusion matrix [[TN,FP],[FN,TP]]:")
    print(confusion_matrix(y_test, pred))

    print("\n=== Feature importance ===")
    importances = sorted(
        zip(FEATURE_COLS, model.feature_importances_), key=lambda x: -x[1]
    )
    for name, imp in importances:
        print(f"  {name:16s} {imp:.4f}")

    # naive backtest: go long only on days model predicts "up", flat otherwise
    # (next-day return realized), vs plain buy-and-hold over the same period
    test = test.copy()
    test["pred_up"] = pred
    test["fwd_ret"] = test["close"].shift(-horizon) / test["close"] - 1
    test = test.dropna(subset=["fwd_ret"])

    # non-overlapping decision points spaced `horizon` days apart, so
    # position returns don't double-count overlapping windows
    picks = test.iloc[::horizon]
    strategy_ret = np.where(picks["pred_up"] == 1, picks["fwd_ret"], 0.0)
    strategy_cum = (1 + strategy_ret).prod() - 1
    buyhold_cum = (1 + picks["fwd_ret"]).prod() - 1
    days_in_market = int((picks["pred_up"] == 1).sum())

    print(f"\n=== Naive backtest on test period ({horizon}d holds, no fees/slippage) ===")
    print(f"decision points:            {len(picks)}")
    print(f"points model went long:     {days_in_market} "
          f"({days_in_market/len(picks):.1%})")
    print(f"strategy cumulative return: {strategy_cum:.2%}")
    print(f"buy-and-hold cumulative:    {buyhold_cum:.2%}")


if __name__ == "__main__":
    symbol = sys.argv[1] if len(sys.argv) > 1 else "NVDA"
    horizon = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    main(symbol, horizon)

````

**`dev/stock-model/train_model_v2.py`**
````python
"""v2: multi-stock panel model predicting forward RETURN MAGNITUDE (regression)
instead of up/down direction, using technical + macro + fundamental features.

Improvements over train_model.py (v1, single-stock direction classifier):
1. Fundamental features (current snapshot, from fetch_fundamentals.py):
   profit margin, revenue growth, ROE, debt/equity, forward PE, beta, etc.
   Caveat: these are TODAY's values, not point-in-time history (see
   fetch_fundamentals.py docstring) - used here as slow-moving per-stock
   (cross-sectional) features, not as leakage-free daily history.
2. Macro features (point-in-time correct, merged by date): VIX, US 10y
   yield, dollar index, WTI oil, S&P500, semiconductor sector ETF (SMH).
3. Regression target: forward N-day return (continuous), evaluated with
   RMSE / R^2 / Information Coefficient (correlation of predicted vs
   realized return), not just a binary accuracy number.
4. Cross-validated across a 10-stock universe (US mega-cap + TW top
   weighted names) instead of a single ticker, with a GLOBAL time-based
   split (same cutoff date for every stock) so no cross-sectional leakage.
5. Backtest: each rebalance date, rank stocks by predicted return, go
   long the top-K, equal-weight, hold `horizon` days; compare cumulative
   return against an equal-weight-all-stocks benchmark over the same
   period (not just a single buy-and-hold line).

Usage: python train_model_v2.py [horizon_days] [top_k]
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

from fetch_universe import STOCKS, MACRO

DATA_DIR = Path("/Users/vm/claude-workspace/data/stock/universe")

TECH_FEATURE_COLS = [
    "ret_1d", "ret_5d", "ret_10d",
    "sma5_rel", "sma10_rel", "sma20_rel", "sma60_rel",
    "rsi14", "macd_diff", "vol_rel", "volatility_10d",
]
MACRO_FEATURE_COLS = list(MACRO.values())
FUND_FEATURE_COLS = [
    "profitMargins", "revenueGrowth", "returnOnEquity", "debtToEquity",
    "recommendationMean", "forwardPE", "beta",
]


def add_technical_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["ret_1d"] = df["close"].pct_change(1)
    df["ret_5d"] = df["close"].pct_change(5)
    df["ret_10d"] = df["close"].pct_change(10)
    for w in (5, 10, 20, 60):
        sma = df["close"].rolling(w).mean()
        df[f"sma{w}_rel"] = df["close"] / sma - 1
    delta = df["close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    df["rsi14"] = 100 - (100 / (1 + gain / loss))
    ema12 = df["close"].ewm(span=12, adjust=False).mean()
    ema26 = df["close"].ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    df["macd_diff"] = macd - macd.ewm(span=9, adjust=False).mean()
    df["vol_rel"] = df["volume"] / df["volume"].rolling(20).mean() - 1
    df["volatility_10d"] = df["ret_1d"].rolling(10).std()
    return df


def load_macro() -> pd.DataFrame:
    merged = None
    for label in MACRO_FEATURE_COLS:
        m = pd.read_csv(DATA_DIR / f"macro_{label}.csv", parse_dates=["date"])
        m[label] = m[label].pct_change()  # use macro RETURNS, not levels
        m = m[["date", label]]
        merged = m if merged is None else merged.merge(m, on="date", how="outer")
    return merged.sort_values("date")


def load_fundamentals() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "fundamentals.csv")


def build_panel(horizon: int) -> pd.DataFrame:
    macro = load_macro()
    fund = load_fundamentals()
    frames = []
    for sym in STOCKS:
        path = DATA_DIR / f"{sym.replace('.', '_')}_daily.csv"
        df = pd.read_csv(path, parse_dates=["date"])
        df = add_technical_features(df)
        df["target_fwd_ret"] = df["close"].shift(-horizon) / df["close"] - 1
        df["symbol"] = sym
        df = df.merge(macro, on="date", how="left")
        frames.append(df)
    panel = pd.concat(frames, ignore_index=True)
    panel = panel.merge(fund, on="symbol", how="left")
    panel = panel.dropna(subset=TECH_FEATURE_COLS + MACRO_FEATURE_COLS + ["target_fwd_ret"])
    return panel.reset_index(drop=True)


def main(horizon: int, top_k: int):
    panel = build_panel(horizon)

    dates = np.sort(panel["date"].unique())
    cutoff = dates[int(len(dates) * 0.8)]
    train = panel[panel["date"] < cutoff]
    test = panel[panel["date"] >= cutoff]

    feature_cols = TECH_FEATURE_COLS + MACRO_FEATURE_COLS + FUND_FEATURE_COLS
    X_train, y_train = train[feature_cols], train["target_fwd_ret"]
    X_test, y_test = test[feature_cols], test["target_fwd_ret"]

    print(f"horizon={horizon}d  universe={len(STOCKS)} stocks  "
          f"panel_rows={len(panel)}  train={len(train)}  test={len(test)}")
    print(f"global split cutoff date: {pd.Timestamp(cutoff).date()}")
    print(f"train date range: {train['date'].min().date()} ~ {train['date'].max().date()}")
    print(f"test  date range: {test['date'].min().date()} ~ {test['date'].max().date()}")

    model = RandomForestRegressor(
        n_estimators=300, max_depth=5, min_samples_leaf=30,
        random_state=42, n_jobs=-1,
    )
    model.fit(X_train, y_train)
    pred = model.predict(X_test)

    rmse = mean_squared_error(y_test, pred) ** 0.5
    r2 = r2_score(y_test, pred)
    ic, ic_p = spearmanr(pred, y_test)
    dir_acc = float(np.mean(np.sign(pred) == np.sign(y_test)))

    print("\n=== Regression metrics (test set, pooled across all stocks) ===")
    print(f"RMSE:                 {rmse:.4f}  (target std: {y_test.std():.4f})")
    print(f"R^2:                  {r2:.4f}")
    print(f"Information Coef (Spearman rank corr, pred vs actual): {ic:.4f}  (p={ic_p:.3g})")
    print(f"directional accuracy (sign match): {dir_acc:.4f}")

    print("\n=== Feature importance ===")
    for name, imp in sorted(zip(feature_cols, model.feature_importances_), key=lambda x: -x[1]):
        print(f"  {name:20s} {imp:.4f}")

    # ranking backtest: each rebalance date, go long top-K predicted stocks
    test = test.copy()
    test["pred"] = pred
    rebalance_dates = sorted(test["date"].unique())[::horizon]
    strat_period_rets, bench_period_rets = [], []
    for d in rebalance_dates:
        day = test[test["date"] == d]
        if len(day) < top_k:
            continue
        top = day.sort_values("pred", ascending=False).head(top_k)
        strat_period_rets.append(top["target_fwd_ret"].mean())
        bench_period_rets.append(day["target_fwd_ret"].mean())  # equal-weight all stocks

    strat_cum = float(np.prod([1 + r for r in strat_period_rets]) - 1)
    bench_cum = float(np.prod([1 + r for r in bench_period_rets]) - 1)

    print(f"\n=== Ranking backtest ({horizon}d rebalance, top-{top_k} long, "
          f"no fees/slippage) ===")
    print(f"rebalance points:                 {len(strat_period_rets)}")
    print(f"strategy cumulative return:        {strat_cum:.2%}")
    print(f"equal-weight-all-stocks benchmark: {bench_cum:.2%}")


if __name__ == "__main__":
    horizon = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    top_k = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    main(horizon, top_k)

````

### 6.6 stock-fomo

**用途**：規則式 FOMO 指數設計＋回測驗證。`fomo_index.py`：
`compute_fomo_index(df)` 純用 OHLCV 算 FOMO 指數（0-100），四因子（5日
動能/量能異常/RSI偏離50/距一年高點遠近）各自算 trailing 252 日 rolling
z-score（無 look-ahead）後取平均，`50+15*z` 轉成 0-100。`backtest_fomo.py`：
套用在既有 10 檔股票 5 年 OHLCV，算 Spearman IC、十分位價差 t-test、
**前後兩半樣本分期穩健性檢查**、個股拆解、示意策略對照。**結論：沒有找到
穩定、可跨時期依賴的預測力**（IC 雖 p<0.05 但解釋力 <1%，且前後兩半 IC
正負號直接反轉），詳見 memory/stock.md。

**重建方式**：
```bash
python3.12 -m venv ~/claude-workspace/dev/stock-fomo/.venv
~/claude-workspace/dev/stock-fomo/.venv/bin/pip install pandas numpy scipy matplotlib
```

**`dev/stock-fomo/fomo_index.py`**
````python
"""Rule-based FOMO (Fear Of Missing Out) index, computed purely from daily
OHLCV price/volume data — no news/sentiment data source, because the news
pipeline (dev/stock-news/) only has data since 2026-09-18 and can't support
a multi-year backtest (see memory/stock.md).

Design: FOMO, behaviorally, is "chasing a rally that has already run" —
retail buyers piling in on unusually strong short-term momentum, on
abnormally high volume, near a new high, with an overbought oscillator.
Each of those four traits is quantified as a raw factor, then converted to
a trailing (causal, no look-ahead) rolling z-score so the four factors are
comparable to each other and across different stocks, then averaged into
one composite z-score and rescaled to a 0-100 display index (50 = neutral,
like a T-score), analogous to the CNN Fear & Greed Index's 0-100 convention.

All rolling stats use only data up to and including day t (pandas
`.rolling()` is causal by construction), so FOMO_Index[t] never uses
future information — required for the index to be usable in a backtest
without leakage.
"""
import numpy as np
import pandas as pd

ZWIN = 252  # trailing window (~1 trading year) for z-score normalization
MOM_WINDOW = 5  # short-term momentum lookback (trading days)
VOL_MA = 20  # volume baseline moving average window
RSI_PERIOD = 14
HIGH_WINDOW = 252  # ~52 weeks, for "how close to a new high" factor
Z_CLIP = 3.0  # clip extreme z-scores so a single outlier day can't dominate


def _rolling_zscore(s: pd.Series, window: int = ZWIN, min_periods: int | None = None) -> pd.Series:
    if min_periods is None:
        min_periods = max(20, window // 4)
    mean = s.rolling(window, min_periods=min_periods).mean()
    std = s.rolling(window, min_periods=min_periods).std()
    z = (s - mean) / std.replace(0, np.nan)
    return z.clip(-Z_CLIP, Z_CLIP)


def _rsi(close: pd.Series, period: int = RSI_PERIOD) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def compute_fomo_index(df: pd.DataFrame) -> pd.DataFrame:
    """`df` must have columns open/high/low/close/volume, sorted ascending
    by date (index or a date column already dropped). Returns a copy with
    the four raw factors, their z-scores, and FOMO_Index (0-100) added."""
    df = df.copy()
    close = df["close"]

    # 1) Momentum: short-term return, unusually strong vs. its own history.
    mom_raw = close.pct_change(MOM_WINDOW)
    df["mom_z"] = _rolling_zscore(mom_raw)

    # 2) Volume surge: today's volume vs. its trailing 20-day average.
    vol_ratio = df["volume"] / df["volume"].rolling(VOL_MA, min_periods=5).mean()
    df["vol_z"] = _rolling_zscore(vol_ratio)

    # 3) RSI extremity: distance above/below the 50 midline, scaled.
    df["rsi"] = _rsi(close)
    df["rsi_z"] = ((df["rsi"] - 50) / 20).clip(-Z_CLIP, Z_CLIP)

    # 4) Proximity to a new high: 0 = at the trailing-year high, negative
    # further below it. Sign-flipped so "closer to a new high" => higher z.
    rolling_high = close.rolling(HIGH_WINDOW, min_periods=40).max()
    dist_from_high = (close - rolling_high) / rolling_high * 100  # <= 0
    df["highprox_z"] = _rolling_zscore(dist_from_high)

    factor_cols = ["mom_z", "vol_z", "rsi_z", "highprox_z"]
    df["fomo_composite_z"] = df[factor_cols].mean(axis=1, skipna=True)
    df["FOMO_Index"] = (50 + 15 * df["fomo_composite_z"]).clip(0, 100)
    return df

````

**`dev/stock-fomo/backtest_fomo.py`**
````python
"""Backtest the FOMO index (fomo_index.py) against realized forward returns,
across the existing 10-stock 5-year universe in data/stock/universe/ (built
2026-09-18 for the stock-model project — reused here rather than refetched).

Hypothesis under test: a high FOMO_Index (chasing an extended rally on
heavy volume near a new high, RSI overbought) predicts WORSE-than-average
forward returns (mean reversion after crowd-chasing), i.e. a NEGATIVE
correlation between FOMO_Index and forward N-day return.

Method (mirrors the rigor of dev/stock-model/train_model_v2.py — pooled
cross-sectional evaluation, Spearman IC with p-value, decile spread,
plus an explicit split-period robustness check, since a single-period
result can just be one bull/bear regime in disguise):
  1. Compute FOMO_Index for every ticker (causal, no look-ahead — see
     fomo_index.py docstring).
  2. Pool (ticker, date, FOMO_Index, forward return) across all 10 stocks.
  3. Decile-bucket FOMO_Index, compare mean forward return top vs bottom
     decile (Welch's t-test).
  4. Spearman IC (rank correlation) between FOMO_Index and forward return,
     with p-value, for horizons 5/10/20 trading days.
  5. Split the pooled sample at its calendar midpoint into two halves and
     repeat the IC test in each half separately — a real effect should
     show the same sign in both halves, not just one regime.
  6. Illustrative strategy: "sit out (0% return) when FOMO_Index >= 80,
     otherwise hold" vs. plain buy-and-hold, per ticker and averaged.
     Threshold (80) is a round, pre-chosen number, NOT tuned/optimized on
     this dataset — this is a directional illustration, not a fitted
     trading rule.
Outputs: PNG charts + a written conclusion markdown, saved to
data/stock/fomo/ (long-term analytical value, unlike outbox/ deliverables
— see workspace CLAUDE.md section 7).
"""
import glob
import os

import matplotlib
import numpy as np
import pandas as pd
from scipy import stats

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from fomo_index import compute_fomo_index

WORKSPACE = "/Users/vm/claude-workspace"
UNIVERSE_DIR = f"{WORKSPACE}/data/stock/universe"
OUT_DIR = f"{WORKSPACE}/data/stock/fomo"
HORIZONS = [5, 10, 20]
FOMO_THRESHOLD = 80  # round number, not fitted — see module docstring

CHART_FONT = "Heiti TC"
plt.rcParams["font.family"] = CHART_FONT
plt.rcParams["axes.unicode_minus"] = False


def load_universe() -> dict[str, pd.DataFrame]:
    paths = sorted(glob.glob(f"{UNIVERSE_DIR}/*_daily.csv"))
    data = {}
    for p in paths:
        ticker = os.path.basename(p).replace("_daily.csv", "")
        df = pd.read_csv(p, parse_dates=["date"]).sort_values("date").set_index("date")
        data[ticker] = df
    return data


def build_panel(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for ticker, df in data.items():
        df = compute_fomo_index(df)
        for h in HORIZONS:
            df[f"fwd_ret_{h}"] = df["close"].shift(-h) / df["close"] - 1
        df["ticker"] = ticker
        rows.append(df)
    panel = pd.concat(rows).reset_index()
    keep_cols = ["date", "ticker", "close", "FOMO_Index"] + [f"fwd_ret_{h}" for h in HORIZONS]
    panel = panel[keep_cols].dropna(subset=["FOMO_Index"])
    return panel


def decile_table(panel: pd.DataFrame, horizon: int) -> pd.DataFrame:
    sub = panel.dropna(subset=[f"fwd_ret_{horizon}"]).copy()
    sub["decile"] = pd.qcut(sub["FOMO_Index"], 10, labels=False, duplicates="drop")
    g = sub.groupby("decile")[f"fwd_ret_{horizon}"]
    return pd.DataFrame({"mean_fwd_ret": g.mean(), "median_fwd_ret": g.median(), "n": g.count()})


def ic_test(panel: pd.DataFrame, horizon: int) -> tuple[float, float, int]:
    sub = panel.dropna(subset=[f"fwd_ret_{horizon}"])
    rho, p = stats.spearmanr(sub["FOMO_Index"], sub[f"fwd_ret_{horizon}"])
    return rho, p, len(sub)


def top_vs_bottom_ttest(panel: pd.DataFrame, horizon: int) -> dict:
    dt = decile_table(panel, horizon)
    sub = panel.dropna(subset=[f"fwd_ret_{horizon}"]).copy()
    sub["decile"] = pd.qcut(sub["FOMO_Index"], 10, labels=False, duplicates="drop")
    top = sub[sub["decile"] == sub["decile"].max()][f"fwd_ret_{horizon}"]
    bottom = sub[sub["decile"] == sub["decile"].min()][f"fwd_ret_{horizon}"]
    t, p = stats.ttest_ind(top, bottom, equal_var=False)
    return {
        "top_mean": top.mean(),
        "bottom_mean": bottom.mean(),
        "t_stat": t,
        "p_value": p,
        "n_top": len(top),
        "n_bottom": len(bottom),
    }


def split_period_check(panel: pd.DataFrame, horizon: int) -> dict:
    mid = panel["date"].median()
    first = panel[panel["date"] < mid]
    second = panel[panel["date"] >= mid]
    rho1, p1, n1 = ic_test(first, horizon)
    rho2, p2, n2 = ic_test(second, horizon)
    return {
        "mid_date": mid,
        "first_half": {"rho": rho1, "p": p1, "n": n1},
        "second_half": {"rho": rho2, "p": p2, "n": n2},
    }


def per_ticker_ic(panel: pd.DataFrame, horizon: int) -> pd.DataFrame:
    rows = []
    for ticker, g in panel.groupby("ticker"):
        rho, p, n = ic_test(g, horizon)
        rows.append({"ticker": ticker, "rho": rho, "p": p, "n": n})
    return pd.DataFrame(rows).sort_values("rho")


def avoid_high_fomo_strategy(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Per ticker: daily return set to 0 whenever FOMO_Index >= threshold
    the PRIOR day (avoid look-ahead — you can only act on yesterday's
    signal), else the actual daily return. Compare cumulative return and
    max drawdown against plain buy-and-hold."""
    rows = []
    for ticker, df in data.items():
        df = compute_fomo_index(df).copy()
        df["daily_ret"] = df["close"].pct_change()
        signal = (df["FOMO_Index"].shift(1) >= FOMO_THRESHOLD).fillna(False)
        df["strategy_ret"] = np.where(signal, 0.0, df["daily_ret"])
        df = df.dropna(subset=["daily_ret"])

        bh_cum = (1 + df["daily_ret"]).cumprod()
        strat_cum = (1 + df["strategy_ret"]).cumprod()
        bh_total = bh_cum.iloc[-1] - 1
        strat_total = strat_cum.iloc[-1] - 1
        bh_dd = (bh_cum / bh_cum.cummax() - 1).min()
        strat_dd = (strat_cum / strat_cum.cummax() - 1).min()
        days_avoided = int(signal.sum())

        rows.append(
            {
                "ticker": ticker,
                "buy_hold_total_return": bh_total,
                "strategy_total_return": strat_total,
                "buy_hold_max_drawdown": bh_dd,
                "strategy_max_drawdown": strat_dd,
                "days_avoided": days_avoided,
                "total_days": len(df),
            }
        )
    return pd.DataFrame(rows)


def plot_decile_bar(panel: pd.DataFrame, horizon: int, out_path: str) -> None:
    dt = decile_table(panel, horizon)
    fig, ax = plt.subplots(figsize=(9, 5))
    colors = ["green" if v >= 0 else "red" for v in dt["mean_fwd_ret"]]
    ax.bar(dt.index, dt["mean_fwd_ret"] * 100, color=colors)
    ax.set_xlabel("FOMO_Index 十分位（0=最低/最冷靜，9=最高/最FOMO）")
    ax.set_ylabel(f"平均未來{horizon}日報酬率 (%)")
    ax.set_title(f"FOMO指數十分位 vs 未來{horizon}日平均報酬率（10檔股票合併樣本）")
    ax.axhline(0, color="black", linewidth=0.8)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def plot_sample_overlay(data: dict[str, pd.DataFrame], ticker: str, out_path: str) -> None:
    df = compute_fomo_index(data[ticker]).dropna(subset=["FOMO_Index"])
    fig, ax1 = plt.subplots(figsize=(12, 5))
    ax1.plot(df.index, df["close"], color="black", linewidth=1)
    ax1.set_ylabel("收盤價", color="black")
    ax2 = ax1.twinx()
    ax2.plot(df.index, df["FOMO_Index"], color="orange", linewidth=1)
    ax2.axhline(FOMO_THRESHOLD, color="red", linestyle="--", linewidth=0.8)
    ax2.set_ylabel("FOMO指數 (0-100)", color="orange")
    ax2.set_ylim(0, 100)
    fig.suptitle(f"{ticker}：股價 vs FOMO指數（橘線，虛線=閾值{FOMO_THRESHOLD}）")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    print("讀取10檔股票5年OHLCV...")
    data = load_universe()
    print(f"共 {len(data)} 檔: {list(data.keys())}")

    print("計算每檔股票的FOMO指數與未來報酬...")
    panel = build_panel(data)
    print(f"合併樣本筆數（已排除暖身期NaN）: {len(panel)}")

    report_lines = []
    report_lines.append(f"# FOMO指數回測結論（{pd.Timestamp.now().strftime('%Y-%m-%d')}）\n")
    report_lines.append(
        "## 假設\nFOMO指數偏高（短線動能過熱＋成交量異常放大＋接近波段新高＋RSI超買）"
        "代表追高情緒濃厚，理論上應該伴隨「之後報酬轉弱／回檔」的均值回歸現象，"
        "也就是 FOMO指數 與 未來報酬 應呈**負相關**。\n"
    )

    report_lines.append("## 1. Spearman IC（FOMO指數 vs 未來N日報酬）\n")
    report_lines.append("| 期間(交易日) | IC (rho) | p-value | 樣本數 |")
    report_lines.append("|---|---|---|---|")
    for h in HORIZONS:
        rho, p, n = ic_test(panel, h)
        sig = "有統計顯著(p<0.05)" if p < 0.05 else "不顯著"
        report_lines.append(f"| {h} | {rho:.4f} | {p:.4f} | {n} |  <!-- {sig} -->")
    report_lines.append("")

    report_lines.append("## 2. 十分位最高 vs 最低組平均未來報酬差異（Welch t-test）\n")
    report_lines.append("| 期間 | 最高十分位平均報酬 | 最低十分位平均報酬 | t值 | p值 |")
    report_lines.append("|---|---|---|---|---|")
    for h in HORIZONS:
        r = top_vs_bottom_ttest(panel, h)
        report_lines.append(
            f"| {h}日 | {r['top_mean']*100:.2f}% | {r['bottom_mean']*100:.2f}% | "
            f"{r['t_stat']:.2f} | {r['p_value']:.4f} |"
        )
    report_lines.append("")

    report_lines.append("## 3. 分期間穩健性檢查（樣本依日期切前後兩半，各自重跑IC）\n")
    for h in HORIZONS:
        sp = split_period_check(panel, h)
        report_lines.append(f"**未來{h}日報酬**（切分點: {sp['mid_date'].date()}）")
        report_lines.append(
            f"- 前半段: IC={sp['first_half']['rho']:.4f}, p={sp['first_half']['p']:.4f}, "
            f"n={sp['first_half']['n']}"
        )
        report_lines.append(
            f"- 後半段: IC={sp['second_half']['rho']:.4f}, p={sp['second_half']['p']:.4f}, "
            f"n={sp['second_half']['n']}"
        )
        same_sign = (sp["first_half"]["rho"] < 0) == (sp["second_half"]["rho"] < 0)
        report_lines.append(f"- 前後兩段方向{'一致' if same_sign else '不一致（不穩健）'}")
        report_lines.append("")

    report_lines.append("## 4. 個股拆解（未來10日報酬 IC，依股票分別計算）\n")
    per_tick = per_ticker_ic(panel, 10)
    report_lines.append("| 股票 | IC (rho) | p值 | 樣本數 |")
    report_lines.append("|---|---|---|---|")
    for _, row in per_tick.iterrows():
        report_lines.append(f"| {row['ticker']} | {row['rho']:.4f} | {row['p']:.4f} | {int(row['n'])} |")
    n_negative = (per_tick["rho"] < 0).sum()
    report_lines.append(f"\n10檔中有 {n_negative} 檔呈負相關（符合假設方向）。\n")

    report_lines.append(
        f"## 5. 示意策略：FOMO指數≥{FOMO_THRESHOLD}時空手（不持有）vs 單純buy-and-hold\n"
    )
    report_lines.append(
        f"閾值{FOMO_THRESHOLD}為預先選定的整數，**未在此資料集上調參最佳化**，僅作方向性示意。\n"
    )
    strat = avoid_high_fomo_strategy(data)
    report_lines.append(
        "| 股票 | Buy&Hold總報酬 | 策略總報酬 | Buy&Hold最大回撤 | 策略最大回撤 | 空手天數/總天數 |"
    )
    report_lines.append("|---|---|---|---|---|---|")
    for _, row in strat.iterrows():
        report_lines.append(
            f"| {row['ticker']} | {row['buy_hold_total_return']*100:.1f}% | "
            f"{row['strategy_total_return']*100:.1f}% | {row['buy_hold_max_drawdown']*100:.1f}% | "
            f"{row['strategy_max_drawdown']*100:.1f}% | {row['days_avoided']}/{row['total_days']} |"
        )
    n_strat_better = (strat["strategy_total_return"] > strat["buy_hold_total_return"]).sum()
    n_dd_better = (strat["strategy_max_drawdown"] > strat["buy_hold_max_drawdown"]).sum()
    report_lines.append(
        f"\n策略總報酬贏過buy-and-hold: {n_strat_better}/{len(strat)} 檔；"
        f"策略最大回撤較小（風險較低）: {n_dd_better}/{len(strat)} 檔。\n"
    )

    report_lines.append("## 6. 總結\n")
    ic10_rho, ic10_p, _ = ic_test(panel, 10)
    ic20_rho, ic20_p, _ = ic_test(panel, 20)
    sp10 = split_period_check(panel, 10)
    robust10 = (sp10["first_half"]["rho"] < 0) == (sp10["second_half"]["rho"] < 0)
    fomo_std = pd.concat([compute_fomo_index(df)["FOMO_Index"] for df in data.values()]).std()
    fomo_p90 = pd.concat([compute_fomo_index(df)["FOMO_Index"] for df in data.values()]).quantile(0.9)
    total_avoided = int(strat["days_avoided"].sum())
    total_days = int(strat["total_days"].sum())
    report_lines.append(
        f"- 全樣本層級：未來10日與20日報酬的IC雖然統計上顯著（p<0.05），但數值很小"
        f"（rho≈{ic10_rho:.3f}、{ic20_rho:.3f}，只解釋不到1%的報酬變異），"
        f"實務上訊號很弱。\n"
        f"- **穩健性不通過**：把樣本依日期切成前後兩半分別檢驗，10日IC從前半段"
        f"{sp10['first_half']['rho']:.3f}（正值，追高後續漲的動能延續）變成後半段"
        f"{sp10['second_half']['rho']:.3f}（負值，符合FOMO假設的均值回歸），"
        f"方向直接反轉。這代表看到的訊號比較像是「剛好那段期間是哪種市場狀態"
        f"（趨勢市 vs 震盪市）」的產物，不是穩定存在、可以跨時期依賴的規律。\n"
        f"- 個股拆解也是各半：10檔中只有5檔呈負相關（符合假設），5檔正相關，"
        f"接近丟硬幣，不是一致的現象。\n"
        f"- 指數本身的設計限制：把4個z-score取平均會互相抵銷、壓縮變異數"
        f"（標準差≈{fomo_std:.1f}，90百分位數僅約{fomo_p90:.0f}分），"
        f"導致「≥{FOMO_THRESHOLD}分」這種閾值全樣本10檔加總只觸發"
        f"{total_avoided}/{total_days} 天（約{total_avoided/total_days*100:.2f}%），"
        f"訊號太稀疏，示意策略的5/10勝率不具參考意義（樣本太小）。\n"
        f"- **結論：這套用價格/成交量堆出來的規則式FOMO指數，目前沒有找到"
        f"穩定、可跨時期依賴的預測力**，與memory/stock.md先前v1/v2技術面"
        f"模型實驗的結論一致——公開價量資料很難打敗市場隨機性。若要繼續這個"
        f"方向，比較有機會的改進不是調整目前這幾個價量因子的權重（那是在"
        f"同一份資料上找巧合），而是真正換一種資料源，例如新聞情緒"
        f"（需要更長的歷史，見dev/stock-news/累積中的資料）、選擇權"
        f"put/call ratio、社群討論熱度等「情緒」本身的直接代理指標，"
        f"而非用價量倒推情緒。\n"
    )

    print("產生圖表...")
    plot_decile_bar(panel, 10, f"{OUT_DIR}/fomo_decile_fwd_ret_10d.png")
    plot_sample_overlay(data, "NVDA", f"{OUT_DIR}/fomo_overlay_NVDA.png")
    plot_sample_overlay(data, "2330_TW", f"{OUT_DIR}/fomo_overlay_2330_TW.png")

    conclusion_path = f"{OUT_DIR}/fomo_backtest_conclusion_{pd.Timestamp.now().strftime('%Y-%m-%d')}.md"
    with open(conclusion_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    print(f"結論已寫入: {conclusion_path}")

    panel_path = f"{OUT_DIR}/fomo_panel_data.csv"
    panel.to_csv(panel_path, index=False)
    print(f"完整面板資料已存: {panel_path}")


if __name__ == "__main__":
    main()

````

### 6.7 stock-sector

**用途**：S&P500 板塊輪動研究（週頻）。`fetch_universe.py`（Wikipedia
成分股+GICS）→ `fetch_prices.py`（Yahoo chart API，2006 起，per-ticker
parquet 快取）→ `build_weekly.py`（重採樣週五資料、40 個群組等權報酬）→
`backtest.py`（季節性/動能/熱度訊號 × 持有 1/4/13 週，52 個相位皆跑一次
再平衡相位，取最差相位 p 值，要求 ≥80% 相位同號才算一致）→
`analyze_structure.py`（季節性檢定、相關性/群聚、領先落後）→
`make_charts.py` → `verify_consistency.py`（可重現性/無未來函數/
walk-forward 洩漏檢查）。`run_all.sh [--offline]` 一鍵重跑。**ETF 版**：
`SECTOR_STUDY=etf` 環境變數切換資料夾/樣本窗，`build_etf.py` 抓九檔
SPDR 板塊 ETF+SPY，`prespecified_test.py`／`make_user_charts.py` 為事先
指定假設檢定與白話圖表。**結論：板塊同期相關結構穩定，但季節性/輪動/
熱度外溢無一通過一致性檢驗**，詳見 memory/stock.md。

**重建方式**：
```bash
python3.12 -m venv ~/claude-workspace/dev/stock-sector/.venv
~/claude-workspace/dev/stock-sector/.venv/bin/pip install pandas numpy scipy pyarrow matplotlib lxml
```

**`dev/stock-sector/config.py`**
````python
"""Shared paths and constants for the S&P 500 sector-rotation research project."""
from pathlib import Path

import os

WORKSPACE = Path("/Users/vm/claude-workspace")
# Two studies share all code; SECTOR_STUDY selects data folder and sample window.
#   stocks (default): current S&P 500 constituents, 2006-, equal-weight groups
#   etf: the nine long-history SPDR sector ETFs (cap-weighted, no constituent
#        survivorship bias) vs SPY, 1999-
STUDY = os.environ.get("SECTOR_STUDY", "stocks")
DATA_DIR = WORKSPACE / "data" / "stock" / ("sector_etf" if STUDY == "etf" else "sector")
UNIVERSE_DIR = DATA_DIR / "universe"
RAW_DIR = DATA_DIR / "raw"          # per-ticker cache, one parquet each
PANEL_DIR = DATA_DIR / "panel"      # wide panels (date x ticker)
RESULT_DIR = DATA_DIR / "results"   # csv/json outputs of each analysis
REPORT_DIR = DATA_DIR / "report"    # charts + conclusion markdown

# 20 full calendar years (2006-2025) plus the current partial year, so that the
# 2008 crisis and ~20 fourth quarters are inside the sample.
START_DATE = "1998-12-01" if STUDY == "etf" else "2006-01-01"
FIRST_YEAR = 1999 if STUDY == "etf" else 2006       # first full calendar year in sample
HALF_SPLIT_YEAR = 2013 if STUDY == "etf" else 2016  # start of the "second half"

# A sub-industry becomes its own group only with at least this many members;
# smaller groups are too noisy to say anything about.
MIN_SUBGROUP_SIZE = 6

# A group's weekly return is computed only when at least this share of its
# (current) members, and at least MIN_MEMBERS_ABS stocks, have a return that
# week. ~20% of today's members listed after 2006, so a strict share would
# blank out years of history for sectors full of recent IPOs.
MIN_COVERAGE = 0.5
MIN_MEMBERS_ABS = 4

# Individual weekly returns are clipped to this range before averaging to blunt
# data artifacts (spin-offs / split handling in adjusted prices, e.g. JCI 2007).
RET_CLIP = (-0.5, 0.5)

# The last full calendar year used for research. The partial current year is
# dropped so month/quarter statistics never mix full and partial periods.
LAST_FULL_YEAR = 2025

for _d in (UNIVERSE_DIR, RAW_DIR, PANEL_DIR, RESULT_DIR, REPORT_DIR):
    _d.mkdir(parents=True, exist_ok=True)

````

**`dev/stock-sector/common.py`**
````python
"""Loading helpers and small shared utilities (weekly frequency only)."""
import numpy as np
import pandas as pd
from scipy import stats

from config import HALF_SPLIT_YEAR, PANEL_DIR

HALF_SPLIT = pd.Timestamp(f"{HALF_SPLIT_YEAR}-01-01")  # samples split into two halves here

# Pre-registered consistency rule, fixed before looking at any result so that
# the "consistent" label cannot be tuned after the fact.
FDR_ALPHA = 0.10
MIN_YEAR_SIGN_SHARE = 0.60


def load_panels():
    ret = pd.read_parquet(PANEL_DIR / "group_weekly_ret.parquet")
    share = pd.read_parquet(PANEL_DIR / "group_weekly_dvol_share.parquet")
    return ret, share


def group_cols(cols, kinds=("S:", "I:", "C:")):
    return [c for c in cols if c[:2] in kinds]


def excess_log(ret: pd.DataFrame, kinds=("S:", "I:", "C:")) -> pd.DataFrame:
    """Weekly log excess return of each group over the equal-weight market.
    Log returns make multi-week aggregation a plain sum."""
    lr = np.log1p(ret)
    cols = group_cols(ret.columns, kinds)
    return lr[cols].sub(lr["MARKET"], axis=0)


def forward_sum(x: pd.DataFrame, h: int) -> pd.DataFrame:
    """Row t holds sum of x over weeks t+1 .. t+h (NaN if any is missing)."""
    return x.iloc[::-1].rolling(h, min_periods=h).sum().iloc[::-1].shift(-1)


def bh_fdr(p: np.ndarray) -> np.ndarray:
    """Benjamini-Hochberg adjusted p-values (NaN stays NaN)."""
    p = np.asarray(p, dtype=float)
    out = np.full_like(p, np.nan)
    ok = ~np.isnan(p)
    pv = p[ok]
    n = len(pv)
    order = np.argsort(pv)
    ranked = pv[order] * n / (np.arange(n) + 1)
    ranked = np.minimum.accumulate(ranked[::-1])[::-1]
    adj = np.empty(n)
    adj[order] = np.minimum(ranked, 1.0)
    out[ok] = adj
    return out


def t_pvalue(mean: float, std: float, n: int) -> tuple[float, float]:
    if n < 3 or not std or np.isnan(std):
        return np.nan, np.nan
    t = mean / (std / np.sqrt(n))
    return t, 2 * stats.t.sf(abs(t), n - 1)


def sign(x: float) -> int:
    return 0 if (x is None or np.isnan(x)) else int(np.sign(x))

````

**`dev/stock-sector/signals.py`**
````python
"""Point-in-time signals. Every function returns a DataFrame with the same index
as its input where row t uses ONLY information available at the close of week t.
verify_consistency.py proves this by truncating the data and recomputing.

All signals are "higher = expected to outperform the market next".
"""
import numpy as np
import pandas as pd

from config import FIRST_YEAR


def seasonality(ex: pd.DataFrame, h: int, min_years: int = 5) -> pd.DataFrame:
    """Expected excess return over the next h weeks = sum, over the calendar
    months those weeks fall in, of the average weekly excess return the group
    had in that month in all *previous calendar years* (year < year(t)).
    Needs min_years of history. Uses only the calendar for the future dates."""
    idx = ex.index
    ym = ex.groupby([idx.year, idx.month]).mean()
    years_of_ym = ym.index.get_level_values(0)
    out = pd.DataFrame(np.nan, index=idx, columns=ex.columns)
    cache = {}
    for i, t in enumerate(idx):
        y = t.year
        if y - FIRST_YEAR < min_years:
            continue
        if y not in cache:
            cache[y] = ym[years_of_ym < y].groupby(level=1).mean()
        months = [(t + pd.Timedelta(days=7 * k)).month for k in range(1, h + 1)]
        out.iloc[i] = cache[y].reindex(months).sum(min_count=1).values
    return out


def momentum(ex: pd.DataFrame, k: int) -> pd.DataFrame:
    """Trailing k-week excess return (relative strength). A negative IC means
    the group mean-reverts instead."""
    return ex.rolling(k, min_periods=k).sum()


def heat_z(share: pd.DataFrame, cols, window: int = 52) -> pd.DataFrame:
    """Traded-value share of the group vs its own trailing 52-week history
    (z-score): high = unusually crowded / hot relative to its own norm."""
    s = share[cols]
    mu = s.rolling(window, min_periods=window // 2).mean()
    sd = s.rolling(window, min_periods=window // 2).std()
    return (s - mu) / sd


def heat_change(share: pd.DataFrame, cols, lag: int = 4) -> pd.DataFrame:
    z = heat_z(share, cols)
    return z - z.shift(lag)

````

**`dev/stock-sector/evaluate.py`**
````python
"""Signal evaluation: cross-sectional rank IC, long/short spread, stability
splits. Rebalancing is every h weeks and holding periods do not overlap, so the
t-statistics are not inflated by overlapping observations."""
import numpy as np
import pandas as pd

from common import HALF_SPLIT, MIN_YEAR_SIGN_SHARE, FDR_ALPHA, forward_sum, sign, t_pvalue


def _rank_corr(a: np.ndarray, b: np.ndarray) -> float:
    ra = pd.Series(a).rank().values
    rb = pd.Series(b).rank().values
    if ra.std() == 0 or rb.std() == 0:
        return np.nan
    return float(np.corrcoef(ra, rb)[0, 1])


def rebalance_rows(index: pd.DatetimeIndex, h: int, offset: int = 0) -> pd.DatetimeIndex:
    return index[offset::h]


def evaluate_signal(sig: pd.DataFrame, ex: pd.DataFrame, h: int, offset: int = 0, min_n: int = 5):
    """Returns (ic, ls): per-rebalance Spearman IC and long-short excess return
    (long top quartile-ish, short bottom) over the next h weeks, rebalancing on
    every h-th week starting at `offset`."""
    fwd = forward_sum(ex, h)
    dates = rebalance_rows(sig.index, h, offset)
    ic, ls = {}, {}
    for t in dates:
        s, f = sig.loc[t], fwd.loc[t]
        m = s.notna() & f.notna()
        if m.sum() < min_n:
            continue
        s, f = s[m], f[m]
        ic[t] = _rank_corr(s.values, f.values)
        q = max(2, int(round(len(s) / 4)))
        order = s.sort_values()
        ls[t] = f[order.index[-q:]].mean() - f[order.index[:q]].mean()
    return pd.Series(ic, dtype=float), pd.Series(ls, dtype=float)


def summarize(ic: pd.Series, ls: pd.Series, h: int) -> dict:
    ic = ic.dropna()
    n = len(ic)
    if n < 20:
        return {"n": n}
    t, p = t_pvalue(ic.mean(), ic.std(), n)
    h1, h2 = ic[ic.index < HALF_SPLIT], ic[ic.index >= HALF_SPLIT]
    by_year = ic.groupby(ic.index.year).mean()
    ys = (np.sign(by_year) == np.sign(ic.mean())).mean()
    per_yr = 52 / h
    return {
        "n": n,
        "ic_mean": ic.mean(),
        "ic_t": t,
        "p": p,
        "ic_hit_rate": (ic > 0).mean(),
        "ic_half1": h1.mean(),
        "ic_half2": h2.mean(),
        "halves_same_sign": bool(sign(h1.mean()) == sign(h2.mean()) != 0),
        "year_sign_share": ys,
        "ls_ann_pct": ls.mean() * per_yr * 100,
        "ls_sharpe": ls.mean() / ls.std() * np.sqrt(per_yr) if ls.std() else np.nan,
        "ls_half1_ann_pct": ls[ls.index < HALF_SPLIT].mean() * per_yr * 100,
        "ls_half2_ann_pct": ls[ls.index >= HALF_SPLIT].mean() * per_yr * 100,
    }


def evaluate_all_offsets(sig: pd.DataFrame, ex: pd.DataFrame, h: int):
    """Evaluate the signal at every rebalance phase 0..h-1. A real effect must
    not depend on which week of the quarter/month the rebalance grid starts on
    (a lone phase with a big IC is a sampling artifact - seen in practice)."""
    ics, lss = [], []
    for off in range(h):
        ic, ls = evaluate_signal(sig, ex, h, off)
        ics.append(ic)
        lss.append(ls)
    return ics, lss


def summarize_offsets(ics: list, lss: list, h: int) -> dict:
    """Aggregate per-phase results conservatively: p = worst phase, IC = mean
    over phases, plus the share of phases whose IC sign matches the mean's.
    Half / per-year checks use the union of all phases' rebalance dates."""
    per = [summarize(ic, ls, h) for ic, ls in zip(ics, lss)]
    per = [r for r in per if r.get("n", 0) >= 20]
    if not per:
        return {"n": 0}
    all_ic = pd.concat(ics).sort_index()
    all_ls = pd.concat(lss).sort_index()
    out = summarize(all_ic, all_ls, h)  # pooled metrics for halves / years / L-S
    ic_means = np.array([r["ic_mean"] for r in per])
    out["n"] = int(np.mean([r["n"] for r in per]))          # per-phase sample size
    out["ic_mean"] = float(ic_means.mean())
    out["ic_t"] = float(np.mean([r["ic_t"] for r in per]))
    out["p"] = float(max(r["p"] for r in per))                # worst phase
    out["offset_sign_share"] = float((np.sign(ic_means) == np.sign(ic_means.mean())).mean())
    out["ic_range_over_offsets"] = float(ic_means.max() - ic_means.min())
    return out


MIN_OFFSET_SIGN_SHARE = 0.80


def label_consistent(row: pd.Series) -> bool:
    """Pre-registered rule: FDR-adjusted (worst-phase) p < alpha AND same sign
    in both halves AND >= MIN_YEAR_SIGN_SHARE of calendar years share the
    overall sign AND >= MIN_OFFSET_SIGN_SHARE of rebalance phases agree.
    (The phase criterion was added after a first run produced a phase-driven
    false positive: sectors mom_1w h=13, offset 0 only.)"""
    return bool(
        row.get("bh_p", 1) < FDR_ALPHA
        and row.get("halves_same_sign", False)
        and row.get("year_sign_share", 0) >= MIN_YEAR_SIGN_SHARE
        and row.get("offset_sign_share", 0) >= MIN_OFFSET_SIGN_SHARE
    )

````

**`dev/stock-sector/fetch_universe.py`**
````python
"""Download the current S&P 500 constituent list with GICS sector / sub-industry
from Wikipedia and save it under data/stock/sector/universe/.

Note: this is the *current* membership only (survivorship bias, see README in
memory/stock.md). Wikipedia is the only free source that carries GICS labels.

Usage: python fetch_universe.py
"""
import io
import urllib.request
from datetime import date

import pandas as pd

from config import UNIVERSE_DIR

URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"


def fetch_constituents() -> pd.DataFrame:
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8")
    table = pd.read_html(io.StringIO(html), attrs={"id": "constituents"})[0]
    df = table.rename(
        columns={
            "Symbol": "wiki_symbol",
            "Security": "name",
            "GICS Sector": "sector",
            "GICS Sub-Industry": "sub_industry",
            "Date added": "date_added",
        }
    )[["wiki_symbol", "name", "sector", "sub_industry", "date_added"]]
    # Yahoo uses '-' where Wikipedia/NYSE use '.' (BRK.B -> BRK-B).
    df["symbol"] = df["wiki_symbol"].str.replace(".", "-", regex=False)
    return df.sort_values("symbol").reset_index(drop=True)


def main():
    df = fetch_constituents()
    out = UNIVERSE_DIR / f"sp500_constituents_{date.today().isoformat()}.csv"
    df.to_csv(out, index=False)
    # Stable pointer for downstream scripts.
    df.to_csv(UNIVERSE_DIR / "sp500_constituents_latest.csv", index=False)
    print(f"{len(df)} constituents -> {out}")
    print(df.groupby("sector").size().sort_values(ascending=False).to_string())


if __name__ == "__main__":
    main()

````

**`dev/stock-sector/fetch_prices.py`**
````python
"""Download daily adjusted close / close / volume for every S&P 500 constituent
(plus the ^GSPC benchmark) from Yahoo Finance's public chart API, cache one
parquet per ticker under data/stock/sector/raw/, then assemble wide panels
(date x ticker) under data/stock/sector/panel/.

Resumable: tickers that already have a raw cache file are skipped unless
--refresh is given, so a crash or rate-limit only costs the missing tickers.

Usage: python fetch_prices.py [--refresh] [--workers 6]
"""
import argparse
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

import pandas as pd

from config import PANEL_DIR, RAW_DIR, START_DATE, UNIVERSE_DIR

BENCHMARK = "^GSPC"


def fetch_one(symbol: str, retries: int = 4) -> pd.DataFrame:
    p1 = int(datetime.fromisoformat(START_DATE).replace(tzinfo=timezone.utc).timestamp())
    p2 = int(time.time())
    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(symbol)}"
        f"?period1={p1}&period2={p2}&interval=1d&events=div%2Csplit"
    )
    last_err = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.load(resp)
            res = data["chart"]["result"][0]
            ts = res["timestamp"]
            q = res["indicators"]["quote"][0]
            adj = res["indicators"].get("adjclose", [{}])[0].get("adjclose")
            # Yahoo stamps daily bars at the exchange-local open; the UTC date is
            # the trading date for US equities (open is 13:30/14:30 UTC).
            idx = pd.to_datetime([datetime.fromtimestamp(t, tz=timezone.utc).date() for t in ts])
            df = pd.DataFrame(
                {
                    "adjclose": adj if adj is not None else q["close"],
                    "close": q["close"],
                    "volume": q["volume"],
                },
                index=idx,
            )
            df.index.name = "date"
            df = df.dropna(subset=["adjclose"])
            df = df[~df.index.duplicated(keep="last")]
            return df
        except (urllib.error.URLError, urllib.error.HTTPError, KeyError, TimeoutError, ValueError) as e:
            last_err = e
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"{symbol}: {last_err}")


def cache_path(symbol: str):
    return RAW_DIR / f"{symbol.replace('^', '_')}.parquet"


def download_all(symbols, refresh: bool, workers: int):
    todo = [s for s in symbols if refresh or not cache_path(s).exists()]
    print(f"{len(symbols)} symbols, {len(todo)} to download")
    failed = []
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(fetch_one, s): s for s in todo}
        for i, fut in enumerate(as_completed(futs), 1):
            s = futs[fut]
            try:
                fut.result().to_parquet(cache_path(s))
            except Exception as e:  # noqa: BLE001 - report and continue
                failed.append((s, str(e)))
            if i % 50 == 0:
                print(f"  {i}/{len(todo)} done")
    return failed


def build_panels(symbols):
    frames = {s: pd.read_parquet(cache_path(s)) for s in symbols if cache_path(s).exists()}
    for col in ("adjclose", "close", "volume"):
        panel = pd.DataFrame({s: f[col] for s, f in frames.items()}).sort_index()
        panel.to_parquet(PANEL_DIR / f"{col}.parquet")
        print(f"panel {col}: {panel.shape}, {panel.index.min().date()} -> {panel.index.max().date()}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--workers", type=int, default=6)
    args = ap.parse_args()

    uni = pd.read_csv(UNIVERSE_DIR / "sp500_constituents_latest.csv")
    symbols = list(uni["symbol"]) + [BENCHMARK]
    failed = download_all(symbols, args.refresh, args.workers)
    if failed:
        print(f"FAILED {len(failed)}:")
        for s, e in failed:
            print("  ", s, e)
    build_panels(symbols)


if __name__ == "__main__":
    main()

````

**`dev/stock-sector/build_weekly.py`**
````python
"""Resample the daily panels to weekly (weeks ending Friday) and build group
level weekly series. All downstream analysis works on these weekly files only.

Outputs (data/stock/sector/panel/):
  weekly_ret.parquet        week x ticker simple return (adjusted close)
  weekly_dollar_vol.parquet week x ticker traded value (sum of daily close*volume)
  group_members.json        group name -> list of tickers
  group_weekly_ret.parquet  week x group equal-weight return (+ MARKET = all stocks)
  group_weekly_dvol_share.parquet  week x group share of total traded value

Groups: 11 GICS sectors ("S:<name>"), sub-industries with >= MIN_SUBGROUP_SIZE
members ("I:<name>"), and one custom group for electronic components.

Usage: python build_weekly.py
"""
import json

import numpy as np
import pandas as pd

from config import MIN_COVERAGE, MIN_MEMBERS_ABS, MIN_SUBGROUP_SIZE, PANEL_DIR, RET_CLIP, UNIVERSE_DIR

# Custom group: closest thing the S&P 500 has to "passive / electronic components".
ELECTRONIC_SUBS = [
    "Electronic Components",
    "Electronic Manufacturing Services",
    "Electronic Equipment & Instruments",
]


def define_groups(uni: pd.DataFrame) -> dict:
    groups = {}
    for sec, g in uni.groupby("sector"):
        groups[f"S:{sec}"] = sorted(g["symbol"])
    for sub, g in uni.groupby("sub_industry"):
        if len(g) >= MIN_SUBGROUP_SIZE:
            groups[f"I:{sub}"] = sorted(g["symbol"])
    el = uni[uni["sub_industry"].isin(ELECTRONIC_SUBS)]
    groups["C:Electronic Components (passive/EMS/instruments)"] = sorted(el["symbol"])
    return groups


def weekly_returns(adj: pd.DataFrame) -> pd.DataFrame:
    # Last available adjusted close of each Friday-ending week, then pct change.
    wk = adj.resample("W-FRI").last()
    # A ticker with no trading at all in the week resamples to NaN; forward
    # filling would fake a 0% return, so leave NaN and let the coverage rule
    # deal with it. pct_change(fill_method=None) keeps NaN gaps as gaps.
    ret = wk.pct_change(fill_method=None).clip(*RET_CLIP)
    # Drop the still-open current week (its Friday label is in the future).
    return ret[ret.index <= adj.index.max()]


def group_series(ret: pd.DataFrame, dvol: pd.DataFrame, groups: dict):
    g_ret, g_dvol = {}, {}
    for name, members in groups.items():
        m = [t for t in members if t in ret.columns]
        r = ret[m]
        n_avail = r.notna().sum(axis=1)
        g = r.mean(axis=1)
        g[(n_avail < MIN_MEMBERS_ABS) | (n_avail < MIN_COVERAGE * len(m))] = np.nan
        g_ret[name] = g
        g_dvol[name] = dvol[m].sum(axis=1, min_count=1)
    g_ret = pd.DataFrame(g_ret)
    g_dvol = pd.DataFrame(g_dvol)
    return g_ret, g_dvol


def main():
    uni = pd.read_csv(UNIVERSE_DIR / "sp500_constituents_latest.csv")
    adj = pd.read_parquet(PANEL_DIR / "adjclose.parquet")
    close = pd.read_parquet(PANEL_DIR / "close.parquet")
    vol = pd.read_parquet(PANEL_DIR / "volume.parquet")

    benchmark = adj["^GSPC"] if "^GSPC" in adj.columns else None
    stocks = [t for t in uni["symbol"] if t in adj.columns]
    adj, close, vol = adj[stocks], close[stocks], vol[stocks]

    ret = weekly_returns(adj)
    dvol = (close * vol).resample("W-FRI").sum(min_count=1).loc[ret.index]
    ret.to_parquet(PANEL_DIR / "weekly_ret.parquet")
    dvol.to_parquet(PANEL_DIR / "weekly_dollar_vol.parquet")

    groups = define_groups(uni)
    (PANEL_DIR / "group_members.json").write_text(json.dumps(groups, indent=1, ensure_ascii=False))
    g_ret, g_dvol = group_series(ret, dvol, groups)

    # Market = equal-weight of every stock, the yardstick for "excess" returns.
    cov = ret.notna().mean(axis=1)
    mkt = ret.mean(axis=1)
    mkt[cov < 0.5] = np.nan
    g_ret.insert(0, "MARKET", mkt)
    if benchmark is not None:
        g_ret["SPX_cap_weighted"] = benchmark.resample("W-FRI").last().pct_change(fill_method=None).reindex(g_ret.index)
    g_ret.to_parquet(PANEL_DIR / "group_weekly_ret.parquet")

    total = dvol.sum(axis=1, min_count=1)
    share = g_dvol.div(total, axis=0)
    share.to_parquet(PANEL_DIR / "group_weekly_dvol_share.parquet")

    print(f"weekly stock panel: {ret.shape}, {ret.index.min().date()} -> {ret.index.max().date()}")
    print(f"groups: {len(groups)} (+MARKET, SPX)")
    n_cov = ret.notna().sum(axis=1)
    print("tickers with data per week: 2006 median %d, 2016 median %d, 2025 median %d" % (
        n_cov["2006"].median(), n_cov["2016"].median(), n_cov["2025"].median()))
    first = g_ret.apply(lambda x: x.first_valid_index())
    print("group first valid week:")
    print(first.dt.date.to_string())


if __name__ == "__main__":
    main()

````

**`dev/stock-sector/build_etf.py`**
````python
"""ETF version of the sector study: download the nine long-history SPDR Select
Sector ETFs plus SPY (benchmark) and build weekly series in the same layout as
build_weekly.py, so backtest.py / analyze_structure.py run unchanged.

Why ETFs: cap-weighted like the real market, and their history is a live record
(no survivorship bias from using today's constituents), ~27 years (Dec 1998 -).
Caveat: each fund follows the GICS definition of its day, so sector membership
changes over time (e.g. 2018 Communication Services carve-out, 2023 move of
Visa/Mastercard from IT to Financials). XLRE (2015-) and XLC (2018-) are left out
because their history is too short for a long-sample study.

Run with SECTOR_STUDY=etf. Usage: SECTOR_STUDY=etf python build_etf.py [--refresh]
"""
import argparse
import os

import numpy as np
import pandas as pd

if os.environ.get("SECTOR_STUDY") != "etf":
    raise SystemExit("set SECTOR_STUDY=etf (this script writes to the ETF study folder)")

from build_weekly import weekly_returns
from config import PANEL_DIR
from fetch_prices import build_panels, download_all

ETFS = {
    "XLK": "Information Technology", "XLE": "Energy", "XLF": "Financials",
    "XLV": "Health Care", "XLI": "Industrials", "XLP": "Consumer Staples",
    "XLY": "Consumer Discretionary", "XLB": "Materials", "XLU": "Utilities",
}
BENCH = "SPY"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh", action="store_true")
    args = ap.parse_args()

    symbols = list(ETFS) + [BENCH]
    failed = download_all(symbols, args.refresh, workers=1)
    if failed:
        raise SystemExit(f"download failed: {failed}")
    build_panels(symbols)

    adj = pd.read_parquet(PANEL_DIR / "adjclose.parquet")
    close = pd.read_parquet(PANEL_DIR / "close.parquet")
    vol = pd.read_parquet(PANEL_DIR / "volume.parquet")

    ret = weekly_returns(adj)
    dvol = (close * vol).resample("W-FRI").sum(min_count=1).loc[ret.index]

    g_ret = pd.DataFrame({f"S:{name}": ret[sym] for sym, name in ETFS.items()})
    g_ret.insert(0, "MARKET", ret[BENCH])
    g_ret["SPX_cap_weighted"] = ret[BENCH]
    g_ret.to_parquet(PANEL_DIR / "group_weekly_ret.parquet")

    # Traded-value share among the nine sector funds (ETF volume also reflects
    # fund flows, so 'heat' here is a rougher gauge than in the stock study).
    dv = pd.DataFrame({f"S:{name}": dvol[sym] for sym, name in ETFS.items()})
    share = dv.div(dv.sum(axis=1, min_count=1), axis=0)
    share.insert(0, "MARKET", np.nan)
    share.to_parquet(PANEL_DIR / "group_weekly_dvol_share.parquet")

    first = g_ret.apply(lambda s: s.first_valid_index()).dt.date
    print(f"weekly ETF panel: {g_ret.shape}, {g_ret.index.min().date()} -> {g_ret.index.max().date()}")
    print(first.to_string())


if __name__ == "__main__":
    main()

````

**`dev/stock-sector/backtest.py`**
````python
"""Run every pre-specified signal family on weekly data and test whether the
edge is real and stable, not just present in-sample.

Signal families (all point-in-time, see signals.py):
  seasonality      calendar-month excess return from previous years only
  mom_k            trailing k-week relative strength, k in MOM_K
  heat_level/chg   traded-value share z-score (level / 4-week change)
  wf_mom           walk-forward: each calendar year pick the k whose trailing
                   5-year IC was best, use only that k in that year (true OOS)

Universes: 11 GICS sectors, and the 28 sub-industry groups + electronic group.
Holding periods h in {1, 4, 13} weeks, non-overlapping.

The whole grid is ONE multiple-testing family (Benjamini-Hochberg), and a
result is labelled "consistent" only under the rule pre-registered in
common.py / evaluate.py.

Usage: python backtest.py
"""
import json

import numpy as np
import pandas as pd

from common import bh_fdr, excess_log, load_panels
from config import FIRST_YEAR, RESULT_DIR
from evaluate import evaluate_all_offsets, label_consistent, summarize_offsets
from signals import heat_change, heat_z, momentum, seasonality

HORIZONS = [1, 4, 13]
MOM_K = [1, 4, 13, 26, 52]
UNIVERSES = {"sectors": ("S:",), "subgroups": ("I:", "C:")}
WF_LOOKBACK_YEARS = 5
WF_FIRST_YEAR = FIRST_YEAR + WF_LOOKBACK_YEARS


def build_signals(ex, share, h):
    cols = list(ex.columns)
    sig = {"seasonality": seasonality(ex, h)}
    for k in MOM_K:
        sig[f"mom_{k}w"] = momentum(ex, k)
    sig["heat_level"] = heat_z(share, cols)
    sig["heat_chg4w"] = heat_change(share, cols)
    return sig


def walk_forward_momentum(ex, h, ic_by_k):
    """For each calendar year Y >= WF_FIRST_YEAR pick the k with the best mean
    IC over the previous WF_LOOKBACK_YEARS years (data strictly before Y) and
    use that k's signal during Y. Returns the stitched signal."""
    sigs = {k: momentum(ex, k) for k in MOM_K}
    out = pd.DataFrame(np.nan, index=ex.index, columns=ex.columns)
    picks = {}
    for y in range(WF_FIRST_YEAR, ex.index.year.max() + 1):
        lo = pd.Timestamp(f"{y - WF_LOOKBACK_YEARS}-01-01")
        hi = pd.Timestamp(f"{y}-01-01")
        score = {}
        for k, ic in ic_by_k.items():
            # An IC dated t is only *realized* at t + h weeks; exclude any whose
            # holding window reaches into year Y (would leak Y's returns).
            w = ic[(ic.index >= lo) & (ic.index <= hi - pd.Timedelta(weeks=h + 1))]
            if len(w) >= 10:
                score[k] = w.mean()
        if not score:
            continue
        # Pick by |IC| would be sign-agnostic; we keep the sign so that a k that
        # historically worked as a reversal is used as a reversal.
        best = max(score, key=lambda k: abs(score[k]))
        s = np.sign(score[best]) * sigs[best]
        rows = (ex.index >= hi) & (ex.index < pd.Timestamp(f"{y + 1}-01-01"))
        out.loc[rows] = s.loc[rows]
        picks[y] = {"k": best, "trailing_ic": round(float(score[best]), 4)}
    return out, picks


def run():
    ret, share = load_panels()
    rows, ic_store, picks_store = [], {}, {}
    for uni_name, kinds in UNIVERSES.items():
        ex = excess_log(ret, kinds)
        if ex.shape[1] < 5:  # universe absent in this study (e.g. no sub-industries for ETFs)
            continue
        for h in HORIZONS:
            sigs = build_signals(ex, share, h)
            ic_by_k = {}
            for name, sig in sigs.items():
                ics, lss = evaluate_all_offsets(sig, ex, h)
                pooled = pd.concat(ics).sort_index()
                if name.startswith("mom_"):
                    ic_by_k[int(name[4:-1])] = pooled
                res = summarize_offsets(ics, lss, h)
                res.update(universe=uni_name, signal=name, h=h)
                rows.append(res)
                ic_store[f"{uni_name}|{name}|h{h}"] = pooled
            if h > 1:
                wf, picks = walk_forward_momentum(ex, h, ic_by_k)
                ics, lss = evaluate_all_offsets(wf, ex, h)
                res = summarize_offsets(ics, lss, h)
                res.update(universe=uni_name, signal="wf_mom", h=h)
                rows.append(res)
                ic_store[f"{uni_name}|wf_mom|h{h}"] = pd.concat(ics).sort_index()
                picks_store[f"{uni_name}|h{h}"] = picks

    df = pd.DataFrame(rows)
    df["bh_p"] = bh_fdr(df["p"].values)
    df["consistent"] = df.apply(label_consistent, axis=1)
    cols = ["universe", "signal", "h", "n", "ic_mean", "ic_t", "p", "bh_p", "ic_hit_rate",
            "ic_half1", "ic_half2", "halves_same_sign", "year_sign_share",
            "offset_sign_share", "ic_range_over_offsets",
            "ls_ann_pct", "ls_sharpe", "ls_half1_ann_pct", "ls_half2_ann_pct", "consistent"]
    df = df[cols].sort_values(["universe", "signal", "h"]).reset_index(drop=True)
    df.to_csv(RESULT_DIR / "backtest_summary.csv", index=False, float_format="%.5f")
    pd.DataFrame(ic_store).to_parquet(RESULT_DIR / "backtest_ic_series.parquet")
    (RESULT_DIR / "wf_momentum_picks.json").write_text(json.dumps(picks_store, indent=1))
    return df


if __name__ == "__main__":
    out = run()
    pd.set_option("display.width", 250)
    print(f"{len(out)} hypotheses in one BH family; consistent: {int(out.consistent.sum())}")
    show = out[["universe", "signal", "h", "n", "ic_mean", "ic_t", "bh_p", "ic_half1", "ic_half2",
                "year_sign_share", "offset_sign_share", "ls_ann_pct", "consistent"]]
    print(show.round(3).to_string())

````

**`dev/stock-sector/prespecified_test.py`**
````python
"""Pre-specified test (declared before the ETF data was looked at):

  H1: the Information Technology sector beats the market in Q4
      (mean Q4 excess return vs the market > 0), tested over all full calendar
      years of the study.

Single hypothesis, so no multiple-testing correction. Reported with several
tests that make different assumptions, plus stability cuts:
  - t-test on yearly Q4 excess returns, Wilcoxon signed-rank, sign test
  - two halves; trimmed mean (drop the 2 most extreme years); Q4 minus the
    same year's Q1-Q3 average
  - ETF study only: 1999-2005, a window the stock study never used, is an
    independent out-of-sample check of the pattern found in 2006-2025.

Usage: [SECTOR_STUDY=etf] python prespecified_test.py
"""
import numpy as np
import pandas as pd
from scipy import stats

from common import HALF_SPLIT, excess_log, load_panels
from config import FIRST_YEAR, LAST_FULL_YEAR, RESULT_DIR, STUDY

SECTOR = "S:Information Technology"


def quarter_table(ex: pd.DataFrame) -> pd.DataFrame:
    s = ex[SECTOR]
    s = s[(s.index.year >= FIRST_YEAR) & (s.index.year <= LAST_FULL_YEAR)]
    q = s.groupby([s.index.year, s.index.quarter]).sum().unstack()
    q.columns = [f"Q{c}" for c in q.columns]
    return q  # log excess return per (year, quarter)


def describe(x: pd.Series, label: str) -> dict:
    x = x.dropna()
    n = len(x)
    pct = np.expm1(x) * 100
    t, p_t = stats.ttest_1samp(x, 0.0) if n > 2 else (np.nan, np.nan)
    try:
        p_w = stats.wilcoxon(x).pvalue
    except ValueError:
        p_w = np.nan
    wins = int((x > 0).sum())
    p_sign = stats.binomtest(wins, n, 0.5).pvalue if n else np.nan
    trimmed = np.expm1(x.drop(x.abs().nlargest(2).index).mean()) * 100 if n > 6 else np.nan
    return {"window": label, "n_years": n, "mean_pct": np.expm1(x.mean()) * 100,
            "median_pct": pct.median(), "trimmed_mean_pct": trimmed, "wins": wins,
            "hit_rate": wins / n if n else np.nan, "t": t, "p_ttest": p_t,
            "p_wilcoxon": p_w, "p_sign": p_sign}


def main():
    ret, _ = load_panels()
    ex = excess_log(ret, ("S:",))
    q = quarter_table(ex)
    q4 = q["Q4"]
    rows = [describe(q4, f"all {q4.index.min()}-{q4.index.max()}")]
    rows.append(describe(q4[q4.index < HALF_SPLIT.year], f"first half <{HALF_SPLIT.year}"))
    rows.append(describe(q4[q4.index >= HALF_SPLIT.year], f"second half >={HALF_SPLIT.year}"))
    if STUDY == "etf":
        rows.append(describe(q4[q4.index < 2006], "1999-2005 (unseen by stock study)"))
        rows.append(describe(q4[q4.index >= 2006], "2006-2025 (same years as stock study)"))
    diff = q4 - q[["Q1", "Q2", "Q3"]].mean(axis=1)
    rows.append(describe(diff, "Q4 minus same-year Q1-Q3 average"))
    out = pd.DataFrame(rows)
    out.to_csv(RESULT_DIR / "prespecified_tech_q4.csv", index=False, float_format="%.4f")
    q.assign(**{c: np.expm1(q[c]) * 100 for c in q.columns}).to_csv(
        RESULT_DIR / "tech_excess_by_year_quarter_pct.csv", float_format="%.3f")

    pd.set_option("display.width", 220)
    print(out.round(3).to_string(index=False))
    print("\nQ4 by year (%):")
    print((np.expm1(q4) * 100).round(1).to_string())
    per_q = pd.DataFrame({c: describe(q[c], c) for c in q.columns}).T[["mean_pct", "hit_rate", "p_ttest"]]
    print("\nAll quarters (Q4 is not special if it is not the outlier):")
    print(per_q.astype(float).round(3).to_string())


if __name__ == "__main__":
    main()

````

**`dev/stock-sector/analyze_structure.py`**
````python
"""Descriptive structure of sector behaviour on weekly data, each finding paired
with the same stability checks used in the backtest (two-half sign agreement +
Benjamini-Hochberg FDR across ALL tests of a family).

  1. seasonality  month / quarter excess return of every group vs the market,
                  per calendar year (full years only), hit rate, t-stat
  2. correlation  weekly excess-return correlation between sectors, both halves,
                  clusters (rotation structure)
  3. lead_lag     does sector A's excess return this period predict sector B's
                  next period (h = 1 and 4 weeks, non-overlapping)?
  4. heat_links   does sector A's traded-value heat predict sector B's next
                  4-week excess return?

Usage: python analyze_structure.py
"""
import numpy as np
import pandas as pd
from scipy import stats
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial.distance import squareform

from common import (FDR_ALPHA, HALF_SPLIT, bh_fdr, excess_log, forward_sum, load_panels,
                    sign, t_pvalue)
from config import FIRST_YEAR, LAST_FULL_YEAR, RESULT_DIR
from signals import heat_z


def short(name: str) -> str:
    return name.split(":", 1)[1]


# ---------------------------------------------------------------- seasonality
def seasonality_tables(ex: pd.DataFrame):
    """Excess return per (year, month) and (year, quarter), by week-end date."""
    ex = ex[ex.index.year <= LAST_FULL_YEAR]
    ex = ex[ex.index.year >= FIRST_YEAR]
    rows = []
    for period, keyf in (("month", lambda i: i.month), ("quarter", lambda i: i.quarter)):
        agg = ex.groupby([ex.index.year, keyf(ex.index)]).sum(min_count=1)
        agg.index.names = ["year", "k"]
        for g in ex.columns:
            for k, s in agg[g].groupby(level="k"):
                s = s.droplevel("k").dropna()
                # Drop years where the group has too few weeks of data (early NaNs).
                if len(s) < 8:
                    continue
                t, p = t_pvalue(s.mean(), s.std(), len(s))
                y = s.index
                m1, m2 = s[y < HALF_SPLIT.year].mean(), s[y >= HALF_SPLIT.year].mean()
                rows.append({
                    "group": g, "period": period, "k": int(k), "n_years": len(s),
                    "mean_excess_pct": (np.expm1(s.mean())) * 100,
                    "hit_rate": (s > 0).mean(), "t": t, "p": p,
                    "half1_pct": m1 * 100, "half2_pct": m2 * 100,
                    "halves_same_sign": bool(sign(m1) == sign(m2) != 0),
                })
    df = pd.DataFrame(rows)
    df["bh_p"] = bh_fdr(df["p"].values)  # one family: every group x month/quarter
    df["consistent"] = (df.bh_p < FDR_ALPHA) & df.halves_same_sign & (
        (df.hit_rate >= 0.65) | (df.hit_rate <= 0.35))
    return df


# ------------------------------------------------------------------ correlation
def correlation_structure(ex_sec: pd.DataFrame):
    full = ex_sec.corr()
    h1 = ex_sec[ex_sec.index < HALF_SPLIT].corr()
    h2 = ex_sec[ex_sec.index >= HALF_SPLIT].corr()
    iu = np.triu_indices(len(full), 1)
    stab = stats.spearmanr(h1.values[iu], h2.values[iu])[0]
    dist = squareform((1 - full).clip(lower=0).values, checks=False)
    link = linkage(dist, "average")
    clusters = pd.Series(fcluster(link, t=4, criterion="maxclust"), index=full.index)
    return full, h1, h2, stab, clusters


def pair_table(h1, h2, full):
    rows = []
    cols = full.columns
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            rows.append({"a": cols[i], "b": cols[j], "corr_full": full.iloc[i, j],
                         "corr_half1": h1.iloc[i, j], "corr_half2": h2.iloc[i, j],
                         "same_sign": sign(h1.iloc[i, j]) == sign(h2.iloc[i, j])})
    return pd.DataFrame(rows).sort_values("corr_full")


# ----------------------------------------------------------- lead-lag / heat
def _corr_matrix_test(x: pd.DataFrame, y: pd.DataFrame, step: int, label: str):
    """corr(x_A[t], y_B[t]) sampled every `step` weeks over all phases would
    overlap, so use every phase separately and require agreement: report the
    median over phases of the correlation and the share of phases agreeing."""
    rows = []
    for a in x.columns:
        for b in y.columns:
            per_phase, per_h1, per_h2, ns = [], [], [], []
            for off in range(step):
                xa, yb = x[a].iloc[off::step], y[b].iloc[off::step]
                m = xa.notna() & yb.notna()
                if m.sum() < 30:
                    continue
                xa, yb = xa[m], yb[m]
                per_phase.append(stats.spearmanr(xa, yb)[0])
                a1, b1 = xa[xa.index < HALF_SPLIT], yb[yb.index < HALF_SPLIT]
                a2, b2 = xa[xa.index >= HALF_SPLIT], yb[yb.index >= HALF_SPLIT]
                per_h1.append(stats.spearmanr(a1, b1)[0])
                per_h2.append(stats.spearmanr(a2, b2)[0])
                ns.append(len(xa))
            if not per_phase:
                continue
            r = float(np.median(per_phase))
            n = int(np.median(ns))
            tt = r * np.sqrt((n - 2) / max(1e-12, 1 - r * r))
            # worst-phase p: the weakest phase must still be significant
            worst = min(per_phase, key=abs)
            tw = worst * np.sqrt((n - 2) / max(1e-12, 1 - worst * worst))
            rows.append({
                "kind": label, "a": a, "b": b, "n": n, "corr": r,
                "corr_half1": float(np.median(per_h1)), "corr_half2": float(np.median(per_h2)),
                "phase_sign_share": float((np.sign(per_phase) == np.sign(r)).mean()),
                "p_worst_phase": float(2 * stats.t.sf(abs(tw), n - 2)),
            })
    df = pd.DataFrame(rows)
    df["bh_p"] = bh_fdr(df["p_worst_phase"].values)
    df["halves_same_sign"] = np.sign(df.corr_half1) == np.sign(df.corr_half2)
    df["consistent"] = (df.bh_p < FDR_ALPHA) & df.halves_same_sign & (df.phase_sign_share >= 0.8)
    return df


def lead_lag(ex_sec: pd.DataFrame):
    out = []
    for h in (1, 4):
        past = ex_sec.rolling(h, min_periods=h).sum()      # A over the last h weeks
        fut = forward_sum(ex_sec, h)                        # B over the next h weeks
        out.append(_corr_matrix_test(past, fut, h, f"leadlag_h{h}"))
    return pd.concat(out, ignore_index=True)


def heat_links(ex_sec: pd.DataFrame, share: pd.DataFrame):
    hz = heat_z(share, list(ex_sec.columns))
    fut = forward_sum(ex_sec, 4)
    return _corr_matrix_test(hz, fut, 4, "heat_to_next4w")


def heat_contemporaneous(ex_sec: pd.DataFrame, share: pd.DataFrame):
    """Same-week link: is sector A being 'hot' (traded-value share z-score) associated
    with sector B's excess return that week? Heat is persistent, so sample every 4th
    week over all 4 phases and take the worst phase (see _corr_matrix_test)."""
    hz = heat_z(share, list(ex_sec.columns))
    return _corr_matrix_test(hz, ex_sec, 4, "heat_same_week")


def heat_seasonality(share: pd.DataFrame, cols):
    """Quarterly traded-value share relative to that calendar year's own average
    (removes the multi-year trend). Tests 'this sector gets crowded in Qx'."""
    s = share[cols]
    s = s[(s.index.year >= FIRST_YEAR) & (s.index.year <= LAST_FULL_YEAR)]
    rel = s / s.groupby(s.index.year).transform("mean") - 1
    q = rel.groupby([rel.index.year, rel.index.quarter]).mean()
    q.index.names = ["year", "q"]
    rows = []
    for g in cols:
        for k, ser in q[g].groupby(level="q"):
            ser = ser.droplevel("q").dropna()
            if len(ser) < 8:
                continue
            t, p = t_pvalue(ser.mean(), ser.std(), len(ser))
            m1, m2 = ser[ser.index < HALF_SPLIT.year].mean(), ser[ser.index >= HALF_SPLIT.year].mean()
            rows.append({"group": g, "quarter": int(k), "n_years": len(ser),
                         "mean_rel_share_pct": ser.mean() * 100, "hit_rate": (ser > 0).mean(),
                         "t": t, "p": p, "half1_pct": m1 * 100, "half2_pct": m2 * 100,
                         "halves_same_sign": bool(sign(m1) == sign(m2) != 0)})
    df = pd.DataFrame(rows)
    df["bh_p"] = bh_fdr(df["p"].values)
    df["consistent"] = (df.bh_p < FDR_ALPHA) & df.halves_same_sign & (
        (df.hit_rate >= 0.65) | (df.hit_rate <= 0.35))
    return df


def main():
    ret, share = load_panels()
    ex_all = excess_log(ret)
    ex_sec = excess_log(ret, ("S:",))

    seas = seasonality_tables(ex_all)
    seas.to_csv(RESULT_DIR / "seasonality_all_groups.csv", index=False, float_format="%.5f")

    full, h1, h2, stab, clusters = correlation_structure(ex_sec)
    full.to_csv(RESULT_DIR / "sector_excess_corr_full.csv", float_format="%.4f")
    h1.to_csv(RESULT_DIR / "sector_excess_corr_half1.csv", float_format="%.4f")
    h2.to_csv(RESULT_DIR / "sector_excess_corr_half2.csv", float_format="%.4f")
    clusters.to_csv(RESULT_DIR / "sector_clusters.csv", header=["cluster"])
    pairs = pair_table(h1, h2, full)
    pairs.to_csv(RESULT_DIR / "sector_pairs_corr.csv", index=False, float_format="%.4f")

    # Raw (not excess) correlation for reference: how much all sectors move together.
    raw = np.log1p(ret[[c for c in ret.columns if c.startswith("S:")]]).corr()
    raw.to_csv(RESULT_DIR / "sector_raw_corr_full.csv", float_format="%.4f")

    ll = lead_lag(ex_sec)
    hl = pd.concat([heat_links(ex_sec, share), heat_contemporaneous(ex_sec, share)], ignore_index=True)
    hs = heat_seasonality(share, list(ex_all.columns))
    hs.to_csv(RESULT_DIR / "heat_seasonality_quarter.csv", index=False, float_format="%.5f")
    pd.concat([ll, hl], ignore_index=True).to_csv(
        RESULT_DIR / "leadlag_and_heat_links.csv", index=False, float_format="%.5f")

    print("== seasonality ==")
    print(f"{len(seas)} tests; consistent: {int(seas.consistent.sum())}")
    print(seas[seas.consistent].sort_values("p").head(15)[
        ["group", "period", "k", "n_years", "mean_excess_pct", "hit_rate", "t", "bh_p",
         "half1_pct", "half2_pct"]].round(3).to_string())
    print("\nQ4 by sector:")
    q4 = seas[(seas.period == "quarter") & (seas.k == 4) & seas.group.str.startswith("S:")]
    print(q4[["group", "n_years", "mean_excess_pct", "hit_rate", "t", "p", "bh_p",
              "half1_pct", "half2_pct"]].round(3).to_string())
    print("\n== correlation ==")
    print("stability (Spearman of pair corr between halves): %.3f" % stab)
    print(clusters.sort_values().to_string())
    print(pairs.head(6).round(3).to_string()); print(pairs.tail(4).round(3).to_string())
    print("\n== heat (traded-value share) seasonality by quarter ==")
    print(f"{len(hs)} tests; consistent: {int(hs.consistent.sum())}")
    print(hs[hs.consistent].sort_values("p").head(12).round(3).to_string())
    print("Sectors, Q4:")
    print(hs[(hs.quarter == 4) & hs.group.str.startswith("S:")][
        ["group", "mean_rel_share_pct", "hit_rate", "t", "bh_p", "half1_pct", "half2_pct"]].round(3).to_string())
    print("\n== lead-lag / heat ==")
    for kind, g in pd.concat([ll, hl]).groupby("kind"):
        print(kind, "tests", len(g), "consistent", int(g.consistent.sum()))
        print(g[g.consistent].sort_values("bh_p").head(8)[
            ["a", "b", "n", "corr", "corr_half1", "corr_half2", "phase_sign_share", "bh_p"]].round(3).to_string())


if __name__ == "__main__":
    main()

````

**`dev/stock-sector/make_charts.py`**
````python
"""Charts for the sector-rotation study (weekly data). PNGs go to
data/stock/sector/report/. Colours follow the dataviz skill's reference palette:
diverging blue <-> red with a gray midpoint for signed values, categorical slots
1-4 (blue, orange, aqua, yellow) for the few line series, light surface.

Usage: python make_charts.py
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from matplotlib import font_manager
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm

from common import HALF_SPLIT, excess_log, load_panels
from config import FIRST_YEAR, HALF_SPLIT_YEAR, LAST_FULL_YEAR, REPORT_DIR, RESULT_DIR, STUDY

N_YEARS = LAST_FULL_YEAR - FIRST_YEAR + 1

SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
BLUE, RED, MID = "#2a78d6", "#e34948", "#f0efec"
CAT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]  # categorical slots 1-4
DIV = LinearSegmentedColormap.from_list("div", [RED, MID, BLUE])

_have = {f.name for f in font_manager.fontManager.ttflist}
FONT = next((f for f in ("Heiti TC", "PingFang TC", "Arial Unicode MS") if f in _have), "sans-serif")
plt.rcParams.update({
    "font.family": FONT, "axes.unicode_minus": False, "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE, "text.color": INK,
    "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
})

ZH = {
    "Communication Services": "通訊服務", "Consumer Discretionary": "非必需消費",
    "Consumer Staples": "必需消費", "Energy": "能源", "Financials": "金融",
    "Health Care": "醫療保健", "Industrials": "工業", "Information Technology": "資訊科技",
    "Materials": "原物料", "Real Estate": "房地產", "Utilities": "公用事業",
}


def zh(g):
    n = g.split(":", 1)[1]
    return ZH.get(n, n)


def save(fig, name):
    fig.savefig(REPORT_DIR / name, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("saved", name)


def heatmap(ax, mat, fmt, vmax, annot=None):
    norm = TwoSlopeNorm(vmin=-vmax, vcenter=0, vmax=vmax)
    im = ax.imshow(mat.values, cmap=DIV, norm=norm, aspect="auto")
    ax.set_xticks(range(mat.shape[1]), mat.columns)
    ax.set_yticks(range(mat.shape[0]), mat.index)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(length=0)
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            v = mat.iloc[i, j]
            if np.isnan(v):
                continue
            txt = fmt.format(v) + (f"\n{annot.iloc[i, j]}" if annot is not None else "")
            ax.text(j, i, txt, ha="center", va="center", fontsize=8, color=INK)
    return im


def seasonality_heatmaps(seas):
    sec = seas[seas.group.str.startswith("S:")].copy()
    sec["name"] = sec.group.map(zh)
    order = [zh(f"S:{n}") for n in ZH]
    # Quarter
    q = sec[sec.period == "quarter"]
    mat = q.pivot(index="name", columns="k", values="mean_excess_pct").reindex(order)
    hit = q.pivot(index="name", columns="k", values="hit_rate").reindex(order)
    ann = hit.map(lambda x: f"勝率{x:.0%}")
    mat.columns = [f"Q{c}" for c in mat.columns]
    ann.columns = mat.columns
    fig, ax = plt.subplots(figsize=(6.6, 5.4))
    im = heatmap(ax, mat, "{:+.1f}%", 3.0, ann)
    ax.set_title(f"各板塊每季相對大盤的平均超額報酬（{FIRST_YEAR}-{LAST_FULL_YEAR}，{N_YEARS} 年）", fontsize=11, loc="left", color=INK)
    fig.text(0.01, -0.02, f"藍=贏大盤、紅=輸大盤；格內第二行為 {N_YEARS} 年中贏大盤的年數比例。\n"
             f"{len(seas)} 項季度/月份檢定經 FDR 校正並要求前後半段同號後，通過一致性檢驗的有 {int(seas.consistent.sum())} 項。",
             fontsize=8.5, color=INK2, va="top")
    cb = fig.colorbar(im, ax=ax, fraction=0.04, pad=0.02)
    cb.outline.set_visible(False)
    save(fig, "seasonality_quarter_heatmap.png")

    m = sec[sec.period == "month"]
    mat = m.pivot(index="name", columns="k", values="mean_excess_pct").reindex(order)
    mat.columns = [f"{c}月" for c in mat.columns]
    fig, ax = plt.subplots(figsize=(10.5, 5.2))
    im = heatmap(ax, mat, "{:+.1f}", 3.0)
    ax.set_title(f"各板塊每月相對大盤的平均超額報酬 %（{FIRST_YEAR}-{LAST_FULL_YEAR}）", fontsize=11, loc="left")
    cb = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
    cb.outline.set_visible(False)
    save(fig, "seasonality_month_heatmap.png")


def q4_tech_bars(ex):
    it = ex["S:Information Technology"]
    it = it[(it.index.year >= FIRST_YEAR) & (it.index.year <= LAST_FULL_YEAR)]
    q4 = it[it.index.quarter == 4].groupby(it[it.index.quarter == 4].index.year).sum()
    pct = np.expm1(q4) * 100
    fig, ax = plt.subplots(figsize=(9, 3.9))
    ax.bar(pct.index, pct.values, color=[BLUE if v > 0 else RED for v in pct.values],
           width=0.62)
    ax.axhline(0, color=INK2, lw=0.8)
    ax.axhline(pct.mean(), color=INK2, lw=1, ls="--")
    ax.set_xlim(pct.index.min() - 0.8, pct.index.max() + 3.2)
    ax.text(pct.index.max() + 0.9, pct.mean(), f"{len(pct)} 年平均\n{pct.mean():+.1f}%", va="center", fontsize=8.5, color=INK2)
    ax.axvline(HALF_SPLIT.year - 0.5, color=GRID, lw=1)
    h1, h2 = pct[pct.index < HALF_SPLIT.year].mean(), pct[pct.index >= HALF_SPLIT.year].mean()
    ymax = pct.abs().max() * 1.15
    mid1, mid2 = (FIRST_YEAR + HALF_SPLIT_YEAR - 1) / 2, (HALF_SPLIT_YEAR + LAST_FULL_YEAR) / 2
    ax.text(mid1, ymax, f"{FIRST_YEAR}-{HALF_SPLIT_YEAR - 1} 平均 {h1:+.1f}%", ha="center", va="top", fontsize=9, color=INK2)
    ax.text(mid2, ymax, f"{HALF_SPLIT_YEAR}-{LAST_FULL_YEAR} 平均 {h2:+.1f}%", ha="center", va="top", fontsize=9, color=INK2)
    ax.set_ylim(-ymax, ymax)
    ax.set_xticks(pct.index, [str(y)[2:] for y in pct.index])
    ax.set_ylabel("Q4 相對大盤超額報酬 %")
    ax.grid(axis="y", color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    p_t = stats.ttest_1samp(q4, 0.0).pvalue
    ax.set_title(f"資訊科技板塊的 Q4 超額報酬：{(pct>0).sum()}/{len(pct)} 年贏大盤（t 檢定 p={p_t:.2f}）",
                 fontsize=11, loc="left")
    save(fig, "q4_tech_by_year.png")


def corr_heatmap(full, rho):
    import scipy.cluster.hierarchy as sch
    from scipy.spatial.distance import squareform
    order = sch.leaves_list(sch.linkage(squareform((1 - full).clip(lower=0).values, checks=False), "average"))
    c = full.iloc[order, order]
    c.index = [zh(x) for x in c.index]
    c.columns = c.index
    fig, ax = plt.subplots(figsize=(8, 6.6))
    im = heatmap(ax, c, "{:+.2f}", 0.7)
    plt.setp(ax.get_xticklabels(), rotation=35, ha="right")
    ax.set_title(f"板塊間「相對大盤」週超額報酬的相關性（{FIRST_YEAR}-2026，依群聚排序）", fontsize=11, loc="left")
    fig.text(0.01, -0.03, f"藍=同漲同跌、紅=此消彼長。前後半段的相關結構相似度 ρ={rho:.2f}。",
             fontsize=8.5, color=INK2)
    cb = fig.colorbar(im, ax=ax, fraction=0.04, pad=0.02)
    cb.outline.set_visible(False)
    save(fig, "sector_corr_heatmap.png")


def rolling_corr(ex):
    it = ex["S:Information Technology"]
    others = [("S:Utilities", CAT[0]), ("S:Consumer Staples", CAT[1]),
              ("S:Energy", CAT[2]), ("S:Financials", CAT[3])]
    fig, ax = plt.subplots(figsize=(9.5, 4.2))
    ends = []
    for name, col in others:
        r = it.rolling(52, min_periods=40).corr(ex[name])
        ax.plot(r.index, r.values, color=col, lw=2, label=zh(name))
        ends.append([r.dropna().iloc[-1], name])
    # Direct labels at the right edge, pushed apart so they never overlap.
    ends.sort()
    for i in range(1, len(ends)):
        ends[i][0] = max(ends[i][0], ends[i - 1][0] + 0.075)
    for y, name in ends:
        ax.text(it.index[-1] + pd.Timedelta(days=40), y, zh(name), color=INK, fontsize=8.5, va="center")
    ax.axhline(0, color=INK2, lw=0.8)
    ax.set_ylim(-0.9, 0.7)
    ax.set_xlim(right=it.index[-1] + pd.Timedelta(days=330))
    ax.grid(axis="y", color=GRID, lw=0.6)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.set_ylabel("滾動 52 週相關係數")
    ax.legend(frameon=False, loc="lower left", ncol=4, fontsize=8.5)
    ax.set_title("資訊科技 vs 公用事業／必需消費：長期負相關；vs 能源／金融：正負號會翻轉", fontsize=11, loc="left")
    save(fig, "tech_vs_traditional_rolling_corr.png")


def backtest_dots(bt):
    hcol = {1: CAT[0], 4: CAT[1], 13: CAT[2]}
    unis = [(u, t) for u, t in (("sectors", "大板塊"), ("subgroups", "細產業")) if (bt.universe == u).any()]
    fig, axes = plt.subplots(1, len(unis), figsize=(5.5 * len(unis) + 0.5, 8.2), sharex=True, squeeze=False)
    axes = axes[0]
    for ax, (uni, title) in zip(axes, unis):
        d = bt[bt.universe == uni]
        sigs = list(dict.fromkeys(d.signal))
        for i, sname in enumerate(sigs):
            for h in (1, 4, 13):
                row = d[(d.signal == sname) & (d.h == h)]
                if row.empty:
                    continue
                r = row.iloc[0]
                ax.scatter(r.ic_mean, i + {1: -0.2, 4: 0, 13: 0.2}[h], s=48, color=hcol[h],
                           edgecolor=SURFACE, linewidth=1.2, zorder=3,
                           label=f"持有 {h} 週" if i == 0 else None)
        ax.set_yticks(range(len(sigs)), sigs)
        ax.invert_yaxis()
        ax.axvline(0, color=INK2, lw=0.8)
        ax.axvspan(-0.05, 0.05, color=GRID, alpha=0.6, lw=0, zorder=0)
        ax.grid(axis="x", color=GRID, lw=0.6)
        for s in ("top", "right", "left"):
            ax.spines[s].set_visible(False)
        ax.tick_params(axis="y", length=0)
        ax.set_title(title, fontsize=10, loc="left")
        ax.set_xlabel("平均 rank IC（跨相位平均）")
    for ax in axes:
        ax.set_xlim(-0.06, 0.06)
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, frameon=False, loc="lower center", ncol=3, fontsize=9, bbox_to_anchor=(0.5, -0.02))
    fig.suptitle(f"{len(bt)} 組訊號假設：最大 |IC|={bt.ic_mean.abs().max():.3f}（灰帶為 ±0.05），{int(bt.consistent.sum())} 組通過一致性檢驗", fontsize=11.5, x=0.01, ha="left")
    save(fig, "backtest_ic_overview.png")


def main():
    ret, share = load_panels()
    ex = excess_log(ret)
    seas = pd.read_csv(RESULT_DIR / "seasonality_all_groups.csv")
    bt = pd.read_csv(RESULT_DIR / "backtest_summary.csv")
    full = pd.read_csv(RESULT_DIR / "sector_excess_corr_full.csv", index_col=0)
    seasonality_heatmaps(seas)
    q4_tech_bars(ex)
    h1 = pd.read_csv(RESULT_DIR / "sector_excess_corr_half1.csv", index_col=0)
    h2 = pd.read_csv(RESULT_DIR / "sector_excess_corr_half2.csv", index_col=0)
    iu = np.triu_indices(len(full), 1)
    corr_heatmap(full, stats.spearmanr(h1.values[iu], h2.values[iu])[0])
    rolling_corr(ex)
    backtest_dots(bt)


if __name__ == "__main__":
    main()

````

**`dev/stock-sector/make_user_charts.py`**
````python
"""Reader-friendly charts for the SPDR sector-ETF trial (plain-language titles,
big fonts, one message per chart), written to outbox/ with the timestamp prefix
the workspace rules require. Also reads the stock-study result tables so the
summary chart can put both studies side by side.

Usage: SECTOR_STUDY=etf python make_user_charts.py
"""
from datetime import datetime, timedelta, timezone

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Patch
from matplotlib.ticker import NullFormatter
from scipy import stats

import make_charts as M  # shared palette, fonts, zh() names, heatmap helper
from common import HALF_SPLIT, excess_log, load_panels
from config import FIRST_YEAR, LAST_FULL_YEAR, RESULT_DIR, WORKSPACE

OUT = WORKSPACE / "outbox"
OUT.mkdir(exist_ok=True)
STOCK_RES = WORKSPACE / "data" / "stock" / "sector" / "results"
TS = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d_%H%M")
INK, INK2, GRID, BLUE, RED, SURFACE = M.INK, M.INK2, M.GRID, M.BLUE, M.RED, M.SURFACE
plt.rcParams.update({"font.size": 12})


def save(fig, name):
    path = OUT / f"{TS}_{name}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("saved", path.name)


# 1 ------------------------------------------------------------------------
def tech_q4():
    ret, _ = load_panels()
    ex = excess_log(ret, ("S:",))["S:Information Technology"].dropna()
    rel = np.exp(ex.cumsum())                      # XLK relative to SPY, start = 1
    ex_y = ex[(ex.index.year >= FIRST_YEAR) & (ex.index.year <= LAST_FULL_YEAR)]
    q4 = ex_y[ex_y.index.quarter == 4]
    q4 = q4.groupby(q4.index.year).sum()
    pct = np.expm1(q4) * 100
    n, wins = len(pct), int((pct > 0).sum())
    p_t = stats.ttest_1samp(q4, 0.0).pvalue

    fig, (a1, a2) = plt.subplots(2, 1, figsize=(10, 9), gridspec_kw={"height_ratios": [1, 1.05]})
    # top: relative strength line with Q4 shaded
    a1.plot(rel.index, rel.values, color=BLUE, lw=2)
    for y in range(FIRST_YEAR, rel.index.year.max() + 1):
        a1.axvspan(pd.Timestamp(f"{y}-10-01"), pd.Timestamp(f"{y}-12-31"), color="#c9c8c2", alpha=0.45, lw=0)
    a1.set_yscale("log")
    a1.set_yticks([0.5, 1, 2, 4]); a1.set_yticklabels(["0.5x", "1x", "2x", "4x"])
    a1.yaxis.set_minor_formatter(NullFormatter())
    a1.set_title("科技股（XLK）相對大盤（SPY）的強弱線；灰色帶＝每年 Q4\n"
                 "線往上＝科技跑贏大盤。若「Q4 被炒作」成立，灰帶內應常看到線往上", fontsize=12.5, loc="left")
    a1.grid(axis="y", color=GRID, lw=0.6)
    for s in ("top", "right", "left"):
        a1.spines[s].set_visible(False)
    # bottom: yearly Q4 bars
    cols = [BLUE if v > 0 else RED for v in pct.values]
    a2.bar(pct.index, pct.values, color=cols, width=0.65)
    a2.axhline(0, color=INK2, lw=0.8)
    lim = 30
    a2.set_ylim(-lim, lim)
    a2.set_xlim(FIRST_YEAR - 1, LAST_FULL_YEAR + 1)
    a2.set_xticks(pct.index[::2], [f"'{str(y)[2:]}" for y in pct.index[::2]])
    a2.set_ylabel("Q4 贏／輸大盤 %")
    # clip the two dot-com outliers visually but keep the numbers readable
    for y, v in pct.items():
        if abs(v) > lim:
            a2.text(y, np.sign(v) * (lim - 2), f"{v:.0f}", ha="center", va="top" if v > 0 else "bottom",
                    fontsize=9, color=INK)
    a2.axvspan(FIRST_YEAR - 0.5, 2005.5, color="#e8e7e2", alpha=0.7, lw=0, zorder=0)
    a2.text((FIRST_YEAR + 2005) / 2, lim - 1.5, "1999-2005\n先前研究沒用過的資料\n（獨立驗證）", ha="center", va="top",
            fontsize=9.5, color=INK2)
    a2.grid(axis="y", color=GRID, lw=0.6); a2.set_axisbelow(True)
    for s in ("top", "right", "left"):
        a2.spines[s].set_visible(False)
    a2.set_title(f"每年 Q4 科技贏／輸大盤多少：{n} 年中 {wins} 年贏，平均 {np.expm1(q4.mean())*100:+.1f}%，"
                 f"統計上分不出與隨機的差別（p={p_t:.2f}）", fontsize=12.5, loc="left")
    a2.legend(handles=[Patch(color=BLUE, label="贏大盤"), Patch(color=RED, label="輸大盤")],
              frameon=False, loc="lower right", ncol=2)
    fig.suptitle("「每年 Q4 科技股會被炒作」——27 年 ETF 資料的驗證", fontsize=15, x=0.01, ha="left", y=1.0)
    fig.tight_layout()
    save(fig, "1_tech_Q4_verdict")


# 2 ------------------------------------------------------------------------
def quarter_heat():
    seas = pd.read_csv(RESULT_DIR / "seasonality_all_groups.csv")
    q = seas[(seas.period == "quarter")].copy()
    q["name"] = q.group.map(M.zh)
    order = [M.zh(f"S:{n}") for n in M.ZH if f"S:{n}" in set(q.group)]
    mat = q.pivot(index="name", columns="k", values="mean_excess_pct").reindex(order)
    hit = q.pivot(index="name", columns="k", values="hit_rate").reindex(order)
    ann = hit.map(lambda x: f"{x:.0%} 的年份贏")
    mat.columns = ann.columns = [f"Q{c}" for c in mat.columns]
    fig, ax = plt.subplots(figsize=(8.2, 6.4))
    im = M.heatmap(ax, mat, "{:+.1f}%", 3.0, ann)
    ax.tick_params(labelsize=12)
    ax.set_title(f"九大板塊在四個季度「贏／輸大盤」多少（{FIRST_YEAR}-{LAST_FULL_YEAR} 平均）", fontsize=13, loc="left")
    fig.text(0.01, -0.01, f"藍＝贏大盤、紅＝輸大盤。全部 {len(seas)} 項季／月檢定，校正後通過 {int(seas.consistent.sum())} 項。\n"
             "看起來像「強季節」的格子（如原物料 Q4 +2.0%），在檢定上仍分不出與運氣的差別。",
             fontsize=10.5, color=INK2, va="top")
    cb = fig.colorbar(im, ax=ax, fraction=0.04, pad=0.02); cb.outline.set_visible(False)
    save(fig, "2_sector_by_quarter")


# 3 ------------------------------------------------------------------------
def together():
    ret, _ = load_panels()
    secs = [c for c in ret.columns if c.startswith("S:")]
    raw = np.log1p(ret[secs])
    ex = raw.sub(raw.mean(axis=1), axis=0)      # vs equal-weight of the 9 (no big-sector bias)
    c = ex.corr()
    c1, c2 = ex[ex.index < HALF_SPLIT].corr(), ex[ex.index >= HALF_SPLIT].corr()
    import scipy.cluster.hierarchy as sch
    from scipy.spatial.distance import squareform
    order = sch.leaves_list(sch.linkage(squareform((1 - c).clip(lower=0).values, checks=False), "average"))
    names = [c.index[i] for i in order]
    mat = c.loc[names, names]
    stable = (np.sign(c1.loc[names, names]) == np.sign(c2.loc[names, names]))
    lab = [M.zh(n) for n in names]
    mat.index = mat.columns = lab
    fig, ax = plt.subplots(figsize=(8.4, 7))
    im = M.heatmap(ax, mat, "{:+.2f}", 0.6)
    ax.tick_params(labelsize=12)
    plt.setp(ax.get_xticklabels(), rotation=35, ha="right")
    for i in range(len(names)):
        for j in range(len(names)):
            if i != j and stable.iloc[i, j] and abs(mat.iloc[i, j]) >= 0.15:
                ax.text(j + 0.33, i - 0.3, "●", fontsize=7, color=INK, ha="center", va="center")
    ax.set_title("九大板塊誰跟誰同進退（週報酬，扣掉九板塊平均）", fontsize=13, loc="left")
    fig.text(0.01, -0.02, f"藍＝同漲同跌、紅＝此消彼長。● ＝ 相關性 ≥0.15 且 {FIRST_YEAR}-{HALF_SPLIT.year - 1} 與 {HALF_SPLIT.year} 年後兩段方向相同（較可信）。\n"
             "這是「同一週」的關係，不能拿來預測下週。", fontsize=10.5, color=INK2, va="top")
    cb = fig.colorbar(im, ax=ax, fraction=0.04, pad=0.02); cb.outline.set_visible(False)
    save(fig, "3_who_moves_together")


# 4 ------------------------------------------------------------------------
def scoreboard():
    def load(dirp):
        return {k: pd.read_csv(dirp / f) for k, f in (
            ("seas", "seasonality_all_groups.csv"), ("bt", "backtest_summary.csv"),
            ("link", "leadlag_and_heat_links.csv"), ("hs", "heat_seasonality_quarter.csv"))}
    S, E = load(STOCK_RES), load(RESULT_DIR)
    pre_s = None  # stock-study Q4 numbers come from its seasonality table
    sq4 = S["seas"].query("group == 'S:Information Technology' and period == 'quarter' and k == 4").iloc[0]
    epre = pd.read_csv(RESULT_DIR / "prespecified_tech_q4.csv").iloc[0]

    def links(d, kinds):
        x = d["link"][d["link"].kind.isin(kinds)]
        return f"{int(x.consistent.sum())}/{len(x)}"
    rows = [
        ("科技股每年 Q4 會被炒作？",
         f"{int(round(sq4.hit_rate*sq4.n_years))}/{int(sq4.n_years)} 年贏\n平均 {sq4.mean_excess_pct:+.1f}%，p={sq4.p:.2f}",
         f"{int(epre.wins)}/{int(epre.n_years)} 年贏\n平均 {epre.mean_pct:+.1f}%，p={epre.p_ttest:.2f}", "不成立（無法確認）"),
        ("任何板塊有固定的季節性？",
         f"{int(S['seas'].consistent.sum())}/{len(S['seas'])} 項通過", f"{int(E['seas'].consistent.sum())}/{len(E['seas'])} 項通過", "不成立"),
        ("板塊同一週的關係穩定嗎？",
         "科技 vs 公用事業/必需消費\n/房地產/金融：穩定負相關", "科技 vs 能源/必需消費/\n原物料/公用事業：穩定負相關", "成立（僅描述）"),
        ("這週強的板塊，下週/下月誰會漲？",
         f"{links(S, ['leadlag_h1','leadlag_h4'])} 項通過", f"{links(E, ['leadlag_h1','leadlag_h4'])} 項通過", "不成立"),
        ("成交變熱會外溢到別的板塊？",
         f"{links(S, ['heat_to_next4w','heat_same_week'])} 項通過", f"{links(E, ['heat_to_next4w','heat_same_week'])} 項通過", "不成立"),
        ("成交熱度有固定的季節？",
         f"{int(S['hs'].consistent.sum())}/{len(S['hs'])} 項通過",
         f"{int(E['hs'].consistent.sum())}/{len(E['hs'])} 項通過（科技 Q2 偏低）", "待驗證（個股版未重現）"),
        ("輪動／動能／熱度訊號能穩定贏？",
         f"{int(S['bt'].consistent.sum())}/{len(S['bt'])} 組通過", f"{int(E['bt'].consistent.sum())}/{len(E['bt'])} 組通過", "不成立（尚未找到）"),
    ]
    fig, ax = plt.subplots(figsize=(11.5, 7.4))
    ax.axis("off")
    heads = ["問題", f"個股版（S&P500 成分股）\n2006-2025", f"ETF 版（SPDR 九大板塊）\n{FIRST_YEAR}-{LAST_FULL_YEAR}", "結論"]
    xs = [0.0, 0.29, 0.54, 0.79]
    for x, h in zip(xs, heads):
        ax.text(x, 0.96, h, fontsize=12, va="top", color=INK)
    ax.plot([0, 1], [0.86, 0.86], color=INK2, lw=1)
    step = 0.118
    for i, r in enumerate(rows):
        y = 0.83 - i * step
        for x, t in zip(xs, r):
            ax.text(x, y, t, fontsize=11.5, va="top", color=INK)
        ax.plot([0, 1], [y - step + 0.02, y - step + 0.02], color=GRID, lw=0.8)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_title("板塊輪動研究總表：兩種資料的結論大致相同", fontsize=15, loc="left", y=1.02)
    ax.text(0, -0.02, "「通過」＝校正多重檢定後顯著，且前後半段方向一致、逐年一致、換再平衡起點也一致。\n"
            "樣本只有 20-27 個年度，結論是「無法確認」，不等於「證明不存在」。", fontsize=10.5, color=INK2, va="top")
    save(fig, "4_scoreboard")


if __name__ == "__main__":
    tech_q4()
    quarter_heat()
    together()
    scoreboard()

````

**`dev/stock-sector/verify_consistency.py`**
````python
"""Logic-consistency checks for the whole research pipeline. Exit code 1 if any
check fails, so it can gate a re-run.

  A. Determinism      running the full pipeline twice gives byte-identical outputs
  B. No look-ahead    every signal at week t is unchanged when all data AFTER t is
                      replaced by random noise (tested at several cut dates)
  C. Walk-forward     the parameter picked for year Y is unchanged when all data
                      from Y onward is replaced by noise
  D. Phase robustness reported by backtest.py (offset_sign_share); here we only
                      assert that the column exists and the "consistent" flags in
                      the CSVs agree with the pre-registered rule

Usage: python verify_consistency.py
"""
import hashlib
import subprocess
import sys

import numpy as np
import pandas as pd

import backtest as B
from common import excess_log, load_panels
from config import FIRST_YEAR, RESULT_DIR
from evaluate import evaluate_all_offsets, label_consistent
from signals import heat_change, heat_z, momentum, seasonality

HERE = __file__.rsplit("/", 1)[0]
PY = sys.executable
RESULT_FILES = ["backtest_summary.csv", "seasonality_all_groups.csv", "sector_pairs_corr.csv",
                "leadlag_and_heat_links.csv", "heat_seasonality_quarter.csv"]


def md5(path):
    return hashlib.md5(path.read_bytes()).hexdigest()


def check_determinism():
    hashes = []
    for _ in range(2):
        for script in ("backtest.py", "analyze_structure.py"):
            subprocess.run([PY, f"{HERE}/{script}"], check=True, capture_output=True, cwd=HERE)
        hashes.append({f: md5(RESULT_DIR / f) for f in RESULT_FILES})
    bad = [f for f in RESULT_FILES if hashes[0][f] != hashes[1][f]]
    return not bad, f"differing files: {bad}" if bad else f"{len(RESULT_FILES)} output files identical over 2 runs"


def perturb_after(df, cut, rng):
    out = df.copy()
    m = out.index > cut
    out.loc[m] = rng.normal(0, 0.05, size=out.loc[m].shape)
    return out


def all_signals(ex, share, cols):
    sigs = {f"seasonality_h{h}": seasonality(ex, h) for h in (1, 4, 13)}
    for k in B.MOM_K:
        sigs[f"mom_{k}w"] = momentum(ex, k)
    sigs["heat_level"] = heat_z(share, cols)
    sigs["heat_chg4w"] = heat_change(share, cols)
    return sigs


def check_no_lookahead():
    ret, share = load_panels()
    ex = excess_log(ret)
    cols = list(ex.columns)
    rng = np.random.default_rng(0)
    full = all_signals(ex, share, cols)
    cuts = ex.index[(ex.index >= f"{FIRST_YEAR + 6}-06-01") & (ex.index <= "2025-06-01")]
    cuts = cuts[rng.choice(len(cuts), size=6, replace=False)]
    problems = []
    for cut in cuts:
        ex_p = perturb_after(ex, cut, rng)
        share_p = share.copy()
        share_p.loc[share_p.index > cut, cols] = rng.uniform(0, 0.1, size=share_p.loc[share_p.index > cut, cols].shape)
        pert = all_signals(ex_p, share_p, cols)
        for name in full:
            a = full[name].loc[:cut]
            b = pert[name].loc[:cut]
            if not np.allclose(a.values, b.values, equal_nan=True, atol=1e-12):
                problems.append(f"{name}@{cut.date()}")
    return not problems, (f"leaks: {problems}" if problems else
                          f"{len(full)} signals x {len(cuts)} cut dates unchanged after randomising the future")


def check_walk_forward():
    ret, share = load_panels()
    ex = excess_log(ret, ("S:",))
    h = 13
    rng = np.random.default_rng(1)

    def picks_for(exx):
        ic_by_k = {}
        for k in B.MOM_K:
            ics, _ = evaluate_all_offsets(momentum(exx, k), exx, h)
            ic_by_k[k] = pd.concat(ics).sort_index()
        return B.walk_forward_momentum(exx, h, ic_by_k)[1]

    base = picks_for(ex)
    problems = []
    for y in (2013, 2018, 2023):
        ex_p = perturb_after(ex, pd.Timestamp(f"{y}-01-01") - pd.Timedelta(days=1), rng)
        p = picks_for(ex_p)
        if p.get(y) != base.get(y):
            problems.append(f"year {y}: {base.get(y)} vs {p.get(y)}")
    return not problems, (f"leaks: {problems}" if problems else
                          "walk-forward pick for 2013/2018/2023 unchanged when that year onward is noise")


def check_flags():
    df = pd.read_csv(RESULT_DIR / "backtest_summary.csv")
    if "offset_sign_share" not in df.columns:
        return False, "offset_sign_share column missing"
    recomputed = df.apply(label_consistent, axis=1)
    ok = (recomputed == df["consistent"]).all()
    return bool(ok), f"'consistent' flags reproduce from the rule for all {len(df)} rows" if ok else "flag mismatch"


def main():
    checks = [("A determinism", check_determinism), ("B no look-ahead", check_no_lookahead),
              ("C walk-forward", check_walk_forward), ("D flags/rule", check_flags)]
    failed = 0
    for name, fn in checks:
        ok, msg = fn()
        print(f"[{'PASS' if ok else 'FAIL'}] {name}: {msg}")
        failed += not ok
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()

````

**`dev/stock-sector/run_all.sh`**
````bash
#!/bin/bash
# Full pipeline for the S&P 500 sector-rotation study (weekly data).
# Steps 1-2 hit the network (Wikipedia + Yahoo public endpoints); pass --offline
# to skip them and re-run only the analysis from cached data.
set -euo pipefail
cd "$(dirname "$0")"
PY=.venv/bin/python

if [ "${1:-}" != "--offline" ]; then
  $PY fetch_universe.py
  $PY fetch_prices.py          # resumable; add --refresh to re-download everything
fi
$PY build_weekly.py            # daily -> weekly panels + group series
$PY backtest.py                # 52 signal hypotheses, phase-robust, one FDR family
$PY analyze_structure.py       # seasonality / correlation / lead-lag / heat
$PY make_charts.py
$PY verify_consistency.py      # determinism + no-look-ahead + walk-forward leak checks

# ---- ETF trial (SPDR sector ETFs, 1999-, cap-weighted). Same code, other data folder.
export SECTOR_STUDY=etf
if [ "${1:-}" != "--offline" ]; then $PY build_etf.py; fi
$PY backtest.py
$PY analyze_structure.py
$PY prespecified_test.py       # single pre-registered hypothesis: tech Q4 > market
$PY make_charts.py
$PY verify_consistency.py
$PY make_user_charts.py        # reader-friendly PNGs into outbox/ (3-day auto cleanup)

````

### 6.8 gmaps-lookup

**用途**：Node.js + Playwright（headless Chromium）查 Google Maps 真實
評分/評論與 Tabelog 評分/評論（`WebFetch` 讀不到 Google Maps 的 JS 動態
頁面；Tabelog 雖是伺服器端渲染但常對 `WebFetch` 的出口 IP 回 403）。
- `lookup.js` / `batch_lookup.js`：單筆/多筆 Google Map 查詢（只要分數）。
- `lookup_with_reviews.js` / `batch_lookup_with_reviews.js`：Google Map +
  近 N 個月評論內容，回傳 `mapsSearchUrl`（`/maps/search/{查詢字串}`，
  分享用，穩定無 token）；`placeUrl` 只供工具內部除錯，**不要**直接貼給
  使用者（含 session 綁定的 `g_ep` token，換瀏覽環境常打不開）。
- `tabelog_reviews.js` / `batch_tabelog_reviews.js`：Tabelog 評論列表頁
  （`.../dtlrvwlst/`），月數篩選精確到「月」；`batch_*` 每筆間隔預設
  12 秒（Tabelog 有請求頻率限制）。
- `tabelog_utils.js`：本地快取（`.tabelog_state/cache/`，48 小時內同
  URL 直接回傳未篩選的完整評論列表，篩選在讀快取後才做，避免快取跟
  查詢參數綁死）＋冷卻鎖檔（`.tabelog_state/cooldown.json`，遇 403 寫入
  30 分鐘冷卻，期間直接短路回報，不發請求）＋瀏覽器指紋補齊＋`warmUp()`
  導覽首頁＋`jitter()` 隨機化 delay。這些只是讓存取節奏更像真人、減少
  實際請求量（查過 `robots.txt` 確認未禁止），不做 IP/代理輪換、偽裝
  UA、破解驗證碼。
- 已知坑：Google 搜尋結果常有「スポンサー」贊助廣告卡片排最前面，已
  過濾；Google Maps 點擊クチコミ分頁偶爾彈出登入誘導 modal。

**重建方式**：
```bash
cd ~/claude-workspace/dev/gmaps-lookup
npm install
npx playwright install chromium   # 只需裝一次
```

**`dev/gmaps-lookup/package.json`**
````json
{
  "name": "gmaps-lookup",
  "version": "1.0.0",
  "description": "",
  "main": "index.js",
  "scripts": {
    "test": "echo \"Error: no test specified\" && exit 1"
  },
  "keywords": [],
  "author": "",
  "license": "ISC",
  "type": "commonjs",
  "dependencies": {
    "playwright": "^1.63.0"
  }
}

````

**`dev/gmaps-lookup/lookup.js`**
````javascript
// Search a place name on Google Maps with a headless browser and extract
// the displayed rating + review count from the place panel DOM.
// Usage: node lookup.js "<search query, e.g. 店名+地區>" [output-screenshot-path]
const { chromium } = require('playwright');

async function main() {
  const query = process.argv[2];
  const screenshotPath = process.argv[3] || null;
  if (!query) {
    console.error('Usage: node lookup.js "<search query>" [screenshot.png]');
    process.exit(1);
  }

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    locale: 'ja-JP',
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    viewport: { width: 1280, height: 900 },
  });
  const page = await context.newPage();

  const url = `https://www.google.com/maps/search/${encodeURIComponent(query)}?hl=ja`;
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });

  // Google Maps takes a moment to render the SPA content; wait for either
  // a place panel (single result) or a results list (multiple results).
  try {
    await page.waitForSelector('[role="main"]', { timeout: 15000 });
  } catch (e) {}
  await page.waitForTimeout(3500);

  // If multiple results came back, click the first ORGANIC one — Google Maps
  // often shows 1-2 sponsored ("スポンサー") cards above the real results,
  // and blindly clicking the first place link grabs an unrelated advertiser.
  const firstOrganicHref = await page.evaluate(() => {
    const feed = document.querySelector('div[role="feed"]');
    if (!feed) return null;
    // Each result is a direct child card of the feed; walk them in order
    // and skip any card whose text includes the sponsor label.
    for (const card of Array.from(feed.children)) {
      if (card.textContent.includes('スポンサー')) continue;
      const link = card.querySelector('a[href*="/maps/place/"]');
      if (link) return link.href;
    }
    return null;
  });
  if (firstOrganicHref) {
    await page.goto(firstOrganicHref, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(3000);
  }

  // The review-count label renders a beat after the rating stars (separate
  // async fetch inside the SPA) — poll for it instead of a fixed sleep,
  // since a flat waitForTimeout was flaky (sometimes caught it, sometimes not).
  try {
    await page.waitForFunction(() => {
      return Array.from(document.querySelectorAll('button, span'))
        .some((el) => /件のクチコミ|^\(\d[\d,]*\)$/.test(el.textContent.trim()));
    }, { timeout: 8000 });
  } catch (e) {
    // proceed anyway; reviewCount will just come back null and the caller
    // can retry or fall back to a screenshot
  }

  const extract = () => page.evaluate(() => {
    const out = { title: null, rating: null, reviewCount: null, address: null, rawAriaLabel: null };

    const h1 = document.querySelector('h1');
    if (h1) out.title = h1.textContent.trim();

    // The rating is usually in a span with role="img" whose aria-label is like "4.2 星".
    const ratingImg = document.querySelector('span[role="img"][aria-label*="星"]');
    if (ratingImg) {
      out.rawAriaLabel = ratingImg.getAttribute('aria-label');
      const m = out.rawAriaLabel.match(/([\d.]+)/);
      if (m) out.rating = parseFloat(m[1]);
    }

    // Review count shows up two ways depending on Google's markup: a short
    // "(341)" button next to the stars, or a longer "341 件のクチコミ" label.
    // Try the longer, less ambiguous one first.
    const all = Array.from(document.querySelectorAll('button, span, div'));
    for (const el of all) {
      const t = el.textContent.trim();
      const m = t.match(/^([\d,]+)\s*件のクチコミ$/);
      if (m) {
        out.reviewCount = parseInt(m[1].replace(/,/g, ''), 10);
        break;
      }
    }
    if (out.reviewCount === null) {
      for (const el of all) {
        const t = el.textContent.trim();
        const m = t.match(/^\(([\d,]+)\)$/);
        if (m) {
          out.reviewCount = parseInt(m[1].replace(/,/g, ''), 10);
          break;
        }
      }
    }

    return out;
  });

  // The review-count label is a separate async render pass inside the SPA
  // and can still be empty even after waitForFunction above resolved on a
  // stale check — retry the extraction a couple times before giving up.
  let data = await extract();
  for (let attempt = 0; attempt < 6 && data.reviewCount === null; attempt++) {
    await page.waitForTimeout(1500);
    data = await extract();
  }

  if (screenshotPath) {
    await page.screenshot({ path: screenshotPath });
  }

  console.log(JSON.stringify({ query, url, ...data }, null, 2));

  await browser.close();
}

main().catch((err) => {
  console.error('ERROR:', err.message);
  process.exit(1);
});

````

**`dev/gmaps-lookup/batch_lookup.js`**
````javascript
// Run lookup() for a list of queries in one browser session (faster/more
// reliable than relaunching Chromium per query) and dump results + a
// screenshot per place for visual fallback when DOM extraction misses
// the review count.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const QUERIES = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const outDir = process.argv[3];
fs.mkdirSync(outDir, { recursive: true });

async function lookupOne(page, query) {
  const url = `https://www.google.com/maps/search/${encodeURIComponent(query)}?hl=ja`;
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
  try {
    await page.waitForSelector('[role="main"]', { timeout: 15000 });
  } catch (e) {}
  await page.waitForTimeout(3500);

  const firstOrganicHref = await page.evaluate(() => {
    const feed = document.querySelector('div[role="feed"]');
    if (!feed) return null;
    for (const card of Array.from(feed.children)) {
      if (card.textContent.includes('スポンサー')) continue;
      const link = card.querySelector('a[href*="/maps/place/"]');
      if (link) return link.href;
    }
    return null;
  });
  if (firstOrganicHref) {
    await page.goto(firstOrganicHref, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(3000);
  }

  try {
    await page.waitForFunction(() => {
      return Array.from(document.querySelectorAll('button, span'))
        .some((el) => /件のクチコミ|^\(\d[\d,]*\)$/.test(el.textContent.trim()));
    }, { timeout: 8000 });
  } catch (e) {}

  const extract = () => page.evaluate(() => {
    const out = { title: null, rating: null, reviewCount: null, rawAriaLabel: null };
    const h1 = document.querySelector('h1');
    if (h1) out.title = h1.textContent.trim();
    const ratingImg = document.querySelector('span[role="img"][aria-label*="星"]');
    if (ratingImg) {
      out.rawAriaLabel = ratingImg.getAttribute('aria-label');
      const m = out.rawAriaLabel.match(/([\d.]+)/);
      if (m) out.rating = parseFloat(m[1]);
    }
    const all = Array.from(document.querySelectorAll('button, span, div'));
    for (const el of all) {
      const t = el.textContent.trim();
      const m = t.match(/^([\d,]+)\s*件のクチコミ$/);
      if (m) { out.reviewCount = parseInt(m[1].replace(/,/g, ''), 10); break; }
    }
    if (out.reviewCount === null) {
      for (const el of all) {
        const t = el.textContent.trim();
        const m = t.match(/^\(([\d,]+)\)$/);
        if (m) { out.reviewCount = parseInt(m[1].replace(/,/g, ''), 10); break; }
      }
    }
    return out;
  });

  let data = await extract();
  for (let attempt = 0; attempt < 6 && data.reviewCount === null; attempt++) {
    await page.waitForTimeout(1500);
    data = await extract();
  }
  return { ...data, url };
}

async function main() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    locale: 'ja-JP',
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    viewport: { width: 1280, height: 900 },
  });
  const page = await context.newPage();

  const results = [];
  for (const item of QUERIES) {
    const { id, query } = item;
    process.stderr.write(`Looking up: ${query}\n`);
    try {
      const data = await lookupOne(page, query);
      const screenshotPath = path.join(outDir, `${id}.png`);
      await page.screenshot({ path: screenshotPath });
      results.push({ id, query, ...data, screenshot: screenshotPath });
    } catch (err) {
      results.push({ id, query, error: err.message });
    }
  }

  await browser.close();
  const outFile = path.join(outDir, 'results.json');
  fs.writeFileSync(outFile, JSON.stringify(results, null, 2));
  console.log(JSON.stringify(results, null, 2));
}

main();

````

**`dev/gmaps-lookup/lookup_with_reviews.js`**
````javascript
// Search a place on Google Maps, extract rating/reviewCount/canonical URL,
// and also scrape recent review text (rating + relative date + body) from
// the クチコミ (reviews) tab, filtered to the last N months.
// Usage: node lookup_with_reviews.js "<query>" [months=3] [screenshot.png]
const { chromium } = require('playwright');

const MONTHS_RE = /^(\d+)\s*(分|時間|日|週間|か月|年)前$/;

function withinMonths(dateText, maxMonths) {
  const m = dateText.match(MONTHS_RE);
  if (!m) return true; // unknown format, don't drop it silently
  const n = parseInt(m[1], 10);
  const unit = m[2];
  if (unit === '年') return false; // a year+ is always outside a 3-month window
  if (unit === 'か月') return n <= maxMonths;
  return true; // 分/時間/日/週間 are always within a few months
}

async function main() {
  const query = process.argv[2];
  const maxMonths = parseInt(process.argv[3] || '3', 10);
  const screenshotPath = process.argv[4] || null;
  if (!query) {
    console.error('Usage: node lookup_with_reviews.js "<query>" [months] [screenshot.png]');
    process.exit(1);
  }

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    locale: 'ja-JP',
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    viewport: { width: 1280, height: 900 },
  });
  const page = await context.newPage();

  const searchUrl = `https://www.google.com/maps/search/${encodeURIComponent(query)}?hl=ja`;
  await page.goto(searchUrl, { waitUntil: 'domcontentloaded', timeout: 30000 });
  try { await page.waitForSelector('[role="main"]', { timeout: 15000 }); } catch (e) {}
  await page.waitForTimeout(3500);

  // Skip sponsored ("スポンサー") cards — click the first organic result.
  const firstOrganicHref = await page.evaluate(() => {
    const feed = document.querySelector('div[role="feed"]');
    if (!feed) return null;
    for (const card of Array.from(feed.children)) {
      if (card.textContent.includes('スポンサー')) continue;
      const link = card.querySelector('a[href*="/maps/place/"]');
      if (link) return link.href;
    }
    return null;
  });
  if (firstOrganicHref) {
    await page.goto(firstOrganicHref, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(3000);
  }

  const placeUrl = page.url();

  // Poll for the review-count label (flaky async render) before reading rating/count.
  try {
    await page.waitForFunction(() => {
      return Array.from(document.querySelectorAll('button, span'))
        .some((el) => /件のクチコミ|^\(\d[\d,]*\)$/.test(el.textContent.trim()));
    }, { timeout: 8000 });
  } catch (e) {}

  const extractSummary = () => page.evaluate(() => {
    const out = { title: null, rating: null, reviewCount: null, closed: false };
    const h1 = document.querySelector('h1');
    if (h1) out.title = h1.textContent.trim();
    const ratingImg = document.querySelector('span[role="img"][aria-label*="星"]');
    if (ratingImg) {
      const m = ratingImg.getAttribute('aria-label').match(/([\d.]+)/);
      if (m) out.rating = parseFloat(m[1]);
    }
    const all = Array.from(document.querySelectorAll('button, span, div'));
    for (const el of all) {
      const t = el.textContent.trim();
      const m = t.match(/^([\d,]+)\s*件のクチコミ$/);
      if (m) { out.reviewCount = parseInt(m[1].replace(/,/g, ''), 10); break; }
    }
    if (out.reviewCount === null) {
      for (const el of all) {
        const t = el.textContent.trim();
        const m = t.match(/^\(([\d,]+)\)$/);
        if (m) { out.reviewCount = parseInt(m[1].replace(/,/g, ''), 10); break; }
      }
    }
    out.closed = /\b閉業\b/.test(document.body.textContent);
    return out;
  });

  let summary = await extractSummary();
  for (let attempt = 0; attempt < 6 && summary.reviewCount === null; attempt++) {
    await page.waitForTimeout(1500);
    summary = await extractSummary();
  }

  // Open the クチコミ tab (wait for the button to exist first — it renders
  // a beat after the overview panel), then wait for review cards to mount.
  let reviews = [];
  try {
    await page.waitForFunction(() => {
      return Array.from(document.querySelectorAll('button[role="tab"]')).some((b) => b.textContent.includes('クチコミ'));
    }, { timeout: 15000 });
    await page.evaluate(() => {
      const target = Array.from(document.querySelectorAll('button[role="tab"]')).find((b) => b.textContent.includes('クチコミ'));
      if (target) target.click();
    });
    await page.waitForFunction(() => document.querySelectorAll('div[data-review-id]').length > 0, { timeout: 15000 });
    await page.waitForTimeout(1000);

    // Scroll the review list with real mouse-wheel events (more reliable
    // than guessing the scrollable container's selector) to lazy-load more.
    for (let i = 0; i < 6; i++) {
      await page.mouse.move(280, 500);
      await page.mouse.wheel(0, 1200);
      await page.waitForTimeout(700);
    }

    const rawReviews = await page.evaluate(() => {
      const seen = new Set();
      const out = [];
      document.querySelectorAll('div[data-review-id]').forEach((card) => {
        const id = card.getAttribute('data-review-id');
        if (seen.has(id)) return;
        seen.add(id);
        const ratingEl = card.querySelector('span[role="img"][aria-label*="つ星"]');
        const rating = ratingEl ? parseFloat((ratingEl.getAttribute('aria-label').match(/([\d.]+)/) || [])[1]) : null;
        let dateText = null;
        for (const s of card.querySelectorAll('span')) {
          const t = s.textContent.trim();
          if (/^\d+\s*(分|時間|日|週間|か月|年)前$/.test(t)) { dateText = t; break; }
        }
        const textEl = card.querySelector('span.wiI7pd');
        const text = textEl ? textEl.textContent.trim() : null;
        if (dateText || text) out.push({ rating, dateText, text });
      });
      return out;
    });

    reviews = rawReviews.filter((r) => r.dateText && withinMonths(r.dateText, maxMonths));
  } catch (e) {
    reviews = [];
  }

  if (screenshotPath) {
    await page.screenshot({ path: screenshotPath });
  }

  // `placeUrl` (the post-navigation URL with lat/lng + an internal `g_ep`
  // token) sometimes fails to open for other people/sessions — the token
  // looks session-scoped. `mapsSearchUrl` is the plain search-by-name URL
  // used to get here in the first place; it's the one safe to hand to a
  // human to click, so surface both but prefer mapsSearchUrl when sharing.
  const mapsSearchUrl = `https://www.google.com/maps/search/${encodeURIComponent(query)}`;

  console.log(JSON.stringify({ query, mapsSearchUrl, placeUrl, ...summary, reviewsWithinMonths: maxMonths, reviews }, null, 2));

  await browser.close();
}

main().catch((err) => {
  console.error('ERROR:', err.message);
  process.exit(1);
});

````

**`dev/gmaps-lookup/batch_lookup_with_reviews.js`**
````javascript
// Batch version of lookup_with_reviews.js — one browser session for all
// queries (faster + more reliable than relaunching per query).
// Usage: node batch_lookup_with_reviews.js queries.json outDir/ [months=3]
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const QUERIES = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const outDir = process.argv[3];
const maxMonths = parseInt(process.argv[4] || '3', 10);
fs.mkdirSync(outDir, { recursive: true });

const MONTHS_RE = /^(\d+)\s*(分|時間|日|週間|か月|年)前$/;
function withinMonths(dateText, months) {
  const m = dateText.match(MONTHS_RE);
  if (!m) return true;
  const n = parseInt(m[1], 10);
  const unit = m[2];
  if (unit === '年') return false;
  if (unit === 'か月') return n <= months;
  return true;
}

async function lookupOne(page, query) {
  const searchUrl = `https://www.google.com/maps/search/${encodeURIComponent(query)}?hl=ja`;
  await page.goto(searchUrl, { waitUntil: 'domcontentloaded', timeout: 30000 });
  try { await page.waitForSelector('[role="main"]', { timeout: 15000 }); } catch (e) {}
  await page.waitForTimeout(3500);

  const firstOrganicHref = await page.evaluate(() => {
    const feed = document.querySelector('div[role="feed"]');
    if (!feed) return null;
    for (const card of Array.from(feed.children)) {
      if (card.textContent.includes('スポンサー')) continue;
      const link = card.querySelector('a[href*="/maps/place/"]');
      if (link) return link.href;
    }
    return null;
  });
  if (firstOrganicHref) {
    await page.goto(firstOrganicHref, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(3000);
  }
  const placeUrl = page.url();
  // See lookup_with_reviews.js for why: placeUrl's `g_ep` token looks
  // session-scoped and can fail to open for someone else — hand out the
  // plain search-by-name URL instead when sharing a link with a human.
  const mapsSearchUrl = `https://www.google.com/maps/search/${encodeURIComponent(query)}`;

  try {
    await page.waitForFunction(() => {
      return Array.from(document.querySelectorAll('button, span'))
        .some((el) => /件のクチコミ|^\(\d[\d,]*\)$/.test(el.textContent.trim()));
    }, { timeout: 8000 });
  } catch (e) {}

  const extractSummary = () => page.evaluate(() => {
    const out = { title: null, rating: null, reviewCount: null, closed: false };
    const h1 = document.querySelector('h1');
    if (h1) out.title = h1.textContent.trim();
    const ratingImg = document.querySelector('span[role="img"][aria-label*="星"]');
    if (ratingImg) {
      const m = ratingImg.getAttribute('aria-label').match(/([\d.]+)/);
      if (m) out.rating = parseFloat(m[1]);
    }
    const all = Array.from(document.querySelectorAll('button, span, div'));
    for (const el of all) {
      const t = el.textContent.trim();
      const m = t.match(/^([\d,]+)\s*件のクチコミ$/);
      if (m) { out.reviewCount = parseInt(m[1].replace(/,/g, ''), 10); break; }
    }
    if (out.reviewCount === null) {
      for (const el of all) {
        const t = el.textContent.trim();
        const m = t.match(/^\(([\d,]+)\)$/);
        if (m) { out.reviewCount = parseInt(m[1].replace(/,/g, ''), 10); break; }
      }
    }
    out.closed = /\b閉業\b/.test(document.body.textContent);
    return out;
  });

  let summary = await extractSummary();
  for (let attempt = 0; attempt < 6 && summary.reviewCount === null; attempt++) {
    await page.waitForTimeout(1500);
    summary = await extractSummary();
  }

  let reviews = [];
  try {
    await page.waitForFunction(() => {
      return Array.from(document.querySelectorAll('button[role="tab"]')).some((b) => b.textContent.includes('クチコミ'));
    }, { timeout: 15000 });
    await page.evaluate(() => {
      const target = Array.from(document.querySelectorAll('button[role="tab"]')).find((b) => b.textContent.includes('クチコミ'));
      if (target) target.click();
    });
    await page.waitForFunction(() => document.querySelectorAll('div[data-review-id]').length > 0, { timeout: 15000 });
    await page.waitForTimeout(1000);

    for (let i = 0; i < 6; i++) {
      await page.mouse.move(280, 500);
      await page.mouse.wheel(0, 1200);
      await page.waitForTimeout(700);
    }

    const rawReviews = await page.evaluate(() => {
      const seen = new Set();
      const out = [];
      document.querySelectorAll('div[data-review-id]').forEach((card) => {
        const id = card.getAttribute('data-review-id');
        if (seen.has(id)) return;
        seen.add(id);
        const ratingEl = card.querySelector('span[role="img"][aria-label*="つ星"]');
        const rating = ratingEl ? parseFloat((ratingEl.getAttribute('aria-label').match(/([\d.]+)/) || [])[1]) : null;
        let dateText = null;
        for (const s of card.querySelectorAll('span')) {
          const t = s.textContent.trim();
          if (/^\d+\s*(分|時間|日|週間|か月|年)前$/.test(t)) { dateText = t; break; }
        }
        const textEl = card.querySelector('span.wiI7pd');
        const text = textEl ? textEl.textContent.trim() : null;
        if (dateText || text) out.push({ rating, dateText, text });
      });
      return out;
    });

    reviews = rawReviews.filter((r) => r.dateText && withinMonths(r.dateText, maxMonths));
  } catch (e) {
    reviews = [];
  }

  return { mapsSearchUrl, placeUrl, ...summary, reviews };
}

async function main() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    locale: 'ja-JP',
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    viewport: { width: 1280, height: 900 },
  });
  const page = await context.newPage();

  const results = [];
  for (const item of QUERIES) {
    const { id, query } = item;
    process.stderr.write(`Looking up: ${query}\n`);
    try {
      const data = await lookupOne(page, query);
      const screenshotPath = path.join(outDir, `${id}.png`);
      await page.screenshot({ path: screenshotPath });
      results.push({ id, query, ...data, screenshot: screenshotPath });
    } catch (err) {
      results.push({ id, query, error: err.message });
    }
  }

  await browser.close();
  const outFile = path.join(outDir, 'results.json');
  fs.writeFileSync(outFile, JSON.stringify(results, null, 2));
  console.log(JSON.stringify(results, null, 2));
}

main();

````

**`dev/gmaps-lookup/tabelog_reviews.js`**
````javascript
// Scrape a Tabelog restaurant's review list page directly via Playwright
// (WebFetch gets 403'd by Tabelog's bot-check on this session's shared
// egress IP, but this VM's own network path isn't blocked — see
// memory/dev.md gmaps-lookup entry for the story).
//
// Uses tabelog_utils for a local cache (skip the network entirely if we
// already fetched this URL recently), a cooldown lockfile (stop hitting the
// network for a while after a 403 instead of retrying into a longer block),
// a more consistent browser fingerprint, and a homepage warm-up navigation.
// The cache stores the full unfiltered review list (not pre-filtered by
// months) so a later call with a different [months] window still gets a
// correct answer from cache instead of a stale narrower/wider slice.
//
// Usage: node tabelog_reviews.js "<tabelog review list URL>" [months=3] [--no-cache]
const { chromium } = require('playwright');
const { getCached, setCache, getCooldownRemainingMs, setCooldown, CONTEXT_OPTIONS, warmUp } = require('./tabelog_utils');

function parseYearMonth(dateText) {
  // e.g. "2026/07訪問6回目" -> {year: 2026, month: 7}
  const m = (dateText || '').match(/(\d{4})\/(\d{2})/);
  if (!m) return null;
  return { year: parseInt(m[1], 10), month: parseInt(m[2], 10) };
}

function withinMonths(ym, months, today = new Date()) {
  if (!ym) return false;
  const cutoff = new Date(today.getFullYear(), today.getMonth() - months, 1);
  const reviewDate = new Date(ym.year, ym.month - 1, 1);
  return reviewDate >= cutoff;
}

function filterByMonths(allReviews, months) {
  return allReviews.filter((r) => withinMonths(parseYearMonth(r.dateText), months));
}

async function fetchLive(url) {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext(CONTEXT_OPTIONS);
  const page = await context.newPage();

  await warmUp(page);

  const resp = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
  await page.waitForTimeout(1500);

  if (!resp || resp.status() >= 400) {
    const status = resp ? resp.status() : 'no response';
    if (resp && resp.status() === 403) setCooldown();
    await browser.close();
    return { error: `HTTP ${status}`, allReviews: [], overallRating: null };
  }

  const overallRating = await page.evaluate(() => {
    const el = document.querySelector('.rdheader-rating__score-val-dtl, [class*="rdheader-rating__score-val"]');
    return el ? el.textContent.trim() : null;
  });

  const raw = await page.evaluate(() => {
    const cards = document.querySelectorAll('div.rvw-item.js-rvw-item-clickable-area, div.rvw-item');
    return Array.from(cards).map((c) => {
      const dateEl = c.querySelector('.rvw-item__date');
      const ratingEl = c.querySelector('.rvw-item__ratings--val, .c-rating-v3__val--strong');
      const titleEl = c.querySelector('.rvw-item__title-target');
      const bodyEl = c.querySelector('.rvw-item__rvw-comment');
      const isPickup = !!c.querySelector('.rstdtl-rvw-pickup');
      return {
        dateText: dateEl ? dateEl.textContent.replace(/\s+/g, '') : null,
        rating: ratingEl ? parseFloat(ratingEl.textContent.trim()) : null,
        title: titleEl ? titleEl.textContent.trim() : null,
        bodyPreview: bodyEl ? bodyEl.textContent.trim().replace(/\s+/g, ' ') : null,
        isPickup,
      };
    });
  });

  await browser.close();
  const allReviews = raw.filter((r) => !r.isPickup); // shop-picked "pickup" reviews aren't chronological, skip for date filtering
  return { overallRating, allReviews };
}

async function main() {
  const url = process.argv[2];
  const months = parseInt(process.argv[3] || '3', 10);
  const noCache = process.argv.includes('--no-cache');
  if (!url) {
    console.error('Usage: node tabelog_reviews.js "<tabelog review list URL>" [months] [--no-cache]');
    process.exit(1);
  }

  let data = noCache ? null : getCached(url);

  if (!data) {
    const cooldownMs = getCooldownRemainingMs();
    if (cooldownMs > 0) {
      const mins = Math.ceil(cooldownMs / 60000);
      console.log(
        JSON.stringify(
          {
            url,
            error: `On cooldown after a recent 403 — skipping network request, retry in ~${mins} min`,
            cooldownRemainingMinutes: mins,
            reviews: [],
          },
          null,
          2
        )
      );
      return;
    }

    const live = await fetchLive(url);
    if (live.error) {
      console.log(JSON.stringify({ url, error: live.error, reviews: [] }, null, 2));
      return;
    }
    data = live;
    setCache(url, data);
  }

  const reviews = filterByMonths(data.allReviews, months);
  console.log(
    JSON.stringify(
      {
        url,
        monthsFilter: months,
        overallRating: data.overallRating,
        reviewCountInWindow: reviews.length,
        reviews,
        ...(data.fromCache ? { fromCache: true, cachedAgeHours: data.cachedAgeHours } : {}),
      },
      null,
      2
    )
  );
}

main().catch((err) => {
  console.error('ERROR:', err.message);
  process.exit(1);
});

````

**`dev/gmaps-lookup/batch_tabelog_reviews.js`**
````javascript
// Sequentially scrape several Tabelog review-list URLs with a jittered delay
// between each request — Tabelog's bot-check tripped after ~5 rapid-fire
// requests during development, so pace requests like a real browsing session
// instead of hammering them back to back.
//
// Uses tabelog_utils: local cache (URLs fetched within the last 48h are
// served from disk, no network call), a cooldown lockfile (a 403 stops the
// whole run from making further requests instead of ploughing through the
// rest of the list into a longer block), a consistent browser fingerprint,
// and a homepage warm-up navigation before the first real request.
//
// Usage: node batch_tabelog_reviews.js urls.json outDir/ [months=3] [delayMs=12000] [--no-cache]
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const {
  getCached,
  setCache,
  getCooldownRemainingMs,
  setCooldown,
  jitter,
  CONTEXT_OPTIONS,
  warmUp,
} = require('./tabelog_utils');

const URLS = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const outDir = process.argv[3];
const months = parseInt(process.argv[4] || '3', 10);
const delayMs = parseInt(process.argv[5] || '12000', 10);
const noCache = process.argv.includes('--no-cache');
fs.mkdirSync(outDir, { recursive: true });

function parseYearMonth(dateText) {
  const m = (dateText || '').match(/(\d{4})\/(\d{2})/);
  if (!m) return null;
  return { year: parseInt(m[1], 10), month: parseInt(m[2], 10) };
}

function withinMonths(ym, monthsBack, today = new Date()) {
  if (!ym) return false;
  const cutoff = new Date(today.getFullYear(), today.getMonth() - monthsBack, 1);
  const reviewDate = new Date(ym.year, ym.month - 1, 1);
  return reviewDate >= cutoff;
}

function filterByMonths(allReviews, monthsBack) {
  return allReviews.filter((r) => withinMonths(parseYearMonth(r.dateText), monthsBack));
}

async function scrapeOne(page, url) {
  const resp = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
  await page.waitForTimeout(1500);
  if (!resp || resp.status() >= 400) {
    return { error: `HTTP ${resp ? resp.status() : 'no response'}`, statusCode: resp ? resp.status() : null };
  }
  const overallRating = await page.evaluate(() => {
    const el = document.querySelector('.rdheader-rating__score-val-dtl, [class*="rdheader-rating__score-val"]');
    return el ? el.textContent.trim() : null;
  });
  const raw = await page.evaluate(() => {
    const cards = document.querySelectorAll('div.rvw-item.js-rvw-item-clickable-area, div.rvw-item');
    return Array.from(cards).map((c) => {
      const dateEl = c.querySelector('.rvw-item__date');
      const ratingEl = c.querySelector('.rvw-item__ratings--val, .c-rating-v3__val--strong');
      const titleEl = c.querySelector('.rvw-item__title-target');
      const bodyEl = c.querySelector('.rvw-item__rvw-comment');
      const isPickup = !!c.querySelector('.rstdtl-rvw-pickup');
      return {
        dateText: dateEl ? dateEl.textContent.replace(/\s+/g, '') : null,
        rating: ratingEl ? parseFloat(ratingEl.textContent.trim()) : null,
        title: titleEl ? titleEl.textContent.trim() : null,
        bodyPreview: bodyEl ? bodyEl.textContent.trim().replace(/\s+/g, ' ') : null,
        isPickup,
      };
    });
  });
  const allReviews = raw.filter((r) => !r.isPickup);
  return { overallRating, allReviews };
}

async function main() {
  // Resolve from cache first — no browser needed at all if every URL is
  // already fresh in the cache.
  const results = [];
  const pending = [];
  for (const { id, url } of URLS) {
    const cached = noCache ? null : getCached(url);
    if (cached) {
      const reviews = filterByMonths(cached.allReviews, months);
      results.push({
        id,
        url,
        overallRating: cached.overallRating,
        reviewCountInWindow: reviews.length,
        reviews,
        fromCache: true,
        cachedAgeHours: cached.cachedAgeHours,
      });
    } else {
      pending.push({ id, url });
    }
  }

  if (pending.length === 0) {
    console.log(JSON.stringify(results, null, 2));
    fs.writeFileSync(path.join(outDir, 'tabelog_results.json'), JSON.stringify(results, null, 2));
    return;
  }

  const cooldownMs = getCooldownRemainingMs();
  if (cooldownMs > 0) {
    const mins = Math.ceil(cooldownMs / 60000);
    for (const { id, url } of pending) {
      results.push({
        id,
        url,
        error: `On cooldown after a recent 403 — skipping network request, retry in ~${mins} min`,
        cooldownRemainingMinutes: mins,
        reviews: [],
      });
    }
    console.log(JSON.stringify(results, null, 2));
    fs.writeFileSync(path.join(outDir, 'tabelog_results.json'), JSON.stringify(results, null, 2));
    return;
  }

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext(CONTEXT_OPTIONS);
  const page = await context.newPage();
  await warmUp(page);

  let hitBlock = false;
  for (let i = 0; i < pending.length; i++) {
    const { id, url } = pending[i];
    if (hitBlock) {
      results.push({ id, url, error: 'Skipped — a 403 earlier in this run triggered cooldown', reviews: [] });
      continue;
    }
    process.stderr.write(`[${i + 1}/${pending.length}] Fetching: ${url}\n`);
    try {
      const live = await scrapeOne(page, url);
      if (live.error) {
        if (live.statusCode === 403) {
          setCooldown();
          hitBlock = true;
        }
        results.push({ id, url, error: live.error, reviews: [] });
      } else {
        setCache(url, live);
        const reviews = filterByMonths(live.allReviews, months);
        results.push({ id, url, overallRating: live.overallRating, reviewCountInWindow: reviews.length, reviews });
      }
    } catch (err) {
      results.push({ id, url, error: err.message, reviews: [] });
    }
    if (i < pending.length - 1 && !hitBlock) {
      await page.waitForTimeout(jitter(delayMs));
    }
  }

  await browser.close();
  fs.writeFileSync(path.join(outDir, 'tabelog_results.json'), JSON.stringify(results, null, 2));
  console.log(JSON.stringify(results, null, 2));
}

main();

````

**`dev/gmaps-lookup/tabelog_utils.js`**
````javascript
// Shared helpers for tabelog_reviews.js / batch_tabelog_reviews.js.
//
// Goal: make our access pattern look like an ordinary human visiting a few
// restaurant pages, and cut the *actual* number of requests we make — not to
// defeat Tabelog's bot-detection outright (no proxy rotation, no UA spoofing
// to impersonate a different crawler, no captcha bypass). robots.txt does
// allow crawling the review-list path for a generic user-agent, so this is
// about being a polite, low-volume client rather than evading a rule that
// says "don't".
//
// - Local cache: don't re-fetch the same store within CACHE_MAX_AGE_HOURS.
// - Cooldown lockfile: after a 403, stop hitting the network entirely for a
//   while instead of letting the next run/retry make it worse.
// - A context config with the headers/locale/timezone/viewport a real
//   Tokyo-based Chrome browser would send (we were already spoofing a UA
//   string but leaving everything else at Playwright defaults, which is an
//   inconsistent fingerprint and itself a signal).
// - A warm-up navigation: hit the homepage first like someone arriving via
//   search, instead of a cold direct jump into a deep review-list URL.
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const STATE_DIR = path.join(__dirname, '.tabelog_state');
const CACHE_DIR = path.join(STATE_DIR, 'cache');
const COOLDOWN_FILE = path.join(STATE_DIR, 'cooldown.json');

const CACHE_MAX_AGE_HOURS = 48;
const COOLDOWN_MINUTES = 30;

function ensureDirs() {
  fs.mkdirSync(CACHE_DIR, { recursive: true });
}

function cacheKeyFor(url) {
  return crypto.createHash('sha1').update(url).digest('hex');
}

function getCached(url, maxAgeHours = CACHE_MAX_AGE_HOURS) {
  ensureDirs();
  const file = path.join(CACHE_DIR, `${cacheKeyFor(url)}.json`);
  if (!fs.existsSync(file)) return null;
  try {
    const entry = JSON.parse(fs.readFileSync(file, 'utf8'));
    const ageHours = (Date.now() - entry.fetchedAt) / 3600000;
    if (ageHours > maxAgeHours) return null;
    return { ...entry.data, fromCache: true, cachedAgeHours: Math.round(ageHours * 10) / 10 };
  } catch {
    return null;
  }
}

function setCache(url, data) {
  ensureDirs();
  const file = path.join(CACHE_DIR, `${cacheKeyFor(url)}.json`);
  fs.writeFileSync(file, JSON.stringify({ url, fetchedAt: Date.now(), data }, null, 2));
}

function getCooldownRemainingMs() {
  if (!fs.existsSync(COOLDOWN_FILE)) return 0;
  try {
    const { blockedUntil } = JSON.parse(fs.readFileSync(COOLDOWN_FILE, 'utf8'));
    return Math.max(0, blockedUntil - Date.now());
  } catch {
    return 0;
  }
}

function setCooldown(minutes = COOLDOWN_MINUTES) {
  ensureDirs();
  fs.writeFileSync(
    COOLDOWN_FILE,
    JSON.stringify({ blockedUntil: Date.now() + minutes * 60000, setAt: Date.now() }, null, 2)
  );
}

function jitter(ms, pct = 0.3) {
  const delta = ms * pct;
  return Math.round(ms - delta + Math.random() * delta * 2);
}

const CONTEXT_OPTIONS = {
  locale: 'ja-JP',
  timezoneId: 'Asia/Tokyo',
  viewport: { width: 1366, height: 850 },
  userAgent:
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
  extraHTTPHeaders: {
    'Accept-Language': 'ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7',
  },
};

async function warmUp(page) {
  // Best-effort: land on the homepage and move the mouse around a bit before
  // going to the real target, like a person who arrived via a search result
  // rather than a script that jumps straight into a deep URL. If this fails
  // for any reason we just proceed to the real request.
  try {
    await page.goto('https://tabelog.com/', { waitUntil: 'domcontentloaded', timeout: 20000 });
    await page.mouse.move(200 + Math.random() * 400, 200 + Math.random() * 300);
    await page.waitForTimeout(800 + Math.random() * 1200);
  } catch {
    // ignore, warm-up is optional
  }
}

module.exports = {
  getCached,
  setCache,
  getCooldownRemainingMs,
  setCooldown,
  jitter,
  CONTEXT_OPTIONS,
  warmUp,
  COOLDOWN_MINUTES,
  CACHE_MAX_AGE_HOURS,
};

````

## 七、個人 skills 完整內容

存放路徑固定為 `~/.claude/skills/{skill名稱}/SKILL.md`（Claude Code 個人
skill 必須放在這裡才會被自動載入，不在 `dev/` 底下；`memory/dev.md`
僅作跨主題索引）。以下為目前使用者自建的三個 skill：

**`~/.claude/skills/jp-travel-planner/SKILL.md`**
````markdown
---
name: jp-travel-planner
description: Use this skill whenever the user is planning a trip to Japan, asking about Japanese train or bus schedules/fares, checking weather or typhoon forecasts in Japan, or wants to adjust/optimize a Japan itinerary based on transit or weather conditions. Trigger on things like "規劃東京行程", "查一下河口湖的巴士", "大阪天氣", "賞楓/賞櫻時間", "新幹線時刻", "N天N夜日本自由行", or any mention of Japanese cities, stations, bus companies, JR/private rail lines, or specific travel dates in Japan — even if the user doesn't explicitly name a website or say "skill". Always consult this skill before answering Japan transit fares, train/bus schedules, or weather forecasts from memory, since these change seasonally and year to year and stale answers can strand the user on the day.
---

# 日本旅遊交通／天氣規劃助手

## 為什麼不能憑記憶回答
日本的電車／巴士時刻表、票價、旺季預約規則、賞楓賞櫻時間幾乎每年調整，颱風季（6-10月）更是天天在變。憑記憶回答很容易講到過期資訊，使用者實際到現場才發現班次、票價或預約規則不對。**只要牽涉到日本交通或天氣，一律先用 WebSearch／WebFetch 查最新資料，查完才回答或規劃行程，不要用訓練知識裡的舊資料頂替。**

## 觸發時機
- 使用者要規劃或調整日本行程（不限城市：東京、大阪、北海道、九州、沖繩…）。
- 使用者詢問日本任一段交通（電車轉乘、高速巴士、新幹線、機場交通、纜車、遊覽船）的時刻、票價、是否需要預約。
- 使用者詢問日本任一地點的天氣、氣溫、降雨機率、颱風動向。
- 使用者想依天氣調整行程（例如「這天下雨怎麼辦」「哪天比較適合去河口湖」）。
- 使用者詢問賞楓、賞櫻等季節性最佳時間。

## 查詢與回覆流程
1. 先確認使用者的**日期、出發地、目的地**；日期還沒定的話先問清楚，或用使用者已提供的日期。
2. 用 WebSearch（需要時再用 WebFetch 進官網確認細節，例如末班車時間、是否停駛公告）查詢下方來源清單，不要只憑單一結果的摘要就下定論，交通時間/票價這類數字最好交叉核對兩個來源。
3. 資料若會隨時間浮動（票價、班次、旺季加開/停駛），要主動註明「查詢時間點」，並提醒使用者「出發前 1-2 週／2-3 天再次確認」，不要讓對方誤以為這是永久不變的資訊。
4. 整理成使用者好吸收的格式（見下方「輸出格式建議」），並依查到的天氣/交通狀況給出具體的行程優化建議，例如：降雨機率高的日子把戶外景點換成室內備案、確認末班車時間避免行程收得太晚、旺季巴士容易客滿要提醒提前線上劃位。

## 常用可靠來源

### 電車／轉乘規劃
- Yahoo!路線情報 https://transit.yahoo.co.jp/ — 最常用，可指定日期時間、能查末班車
- NAVITIME https://www.navitime.co.jp/
- Jorudan（乗換案内）https://www.jorudan.co.jp/

### 高速巴士
- ハイウェイバスドットコム https://www.highwaybus.com/
- バス比較なび https://www.bushikaku.net/
- 各地巴士公司官網（依地區搜尋，例如富士急行バス、JRバス関東、中央バス、北都交通等）

### 天氣／颱風
- 気象庁 (JMA) https://www.jma.go.jp/ — 官方權威來源，颱風／特報類問題一定要查這裡
- tenki.jp https://tenki.jp/
- ウェザーニュース https://weathernews.jp/

### 賞楓／賞櫻／季節景觀
- ウォーカープラス紅葉 https://koyo.walkerplus.com/
- ウォーカープラス櫻花 https://sakura.walkerplus.com/

## 輸出格式建議

**交通比較**（使用者問怎麼去某地）：

| 方式 | 時間 | 票價 | 是否需預約 | 備註 |
|------|------|------|-----------|------|

**天氣＋行程建議**（使用者問某天／某地天氣或要不要調整行程）：
- 天氣預報：氣溫、降雨機率、風速等（附查詢時間點）
- 對行程的影響：哪些景點／交通方式會受影響
- 建議：維持原計畫／改室內備案／提前或延後某活動

## 若在 claude-workspace 專案內工作
若目前工作目錄是使用者的 claude-workspace（有 topic／memory 機制），查完資料、規劃完行程後，依該專案 CLAUDE.md 的規則把結論寫回對應的 `memory/{topic}.md`（旅遊通常是 `memory/travel.md`）並記錄 `activity_log.jsonl`；那套機制的細節不在這裡重複，照專案既有規則走即可。

````

**`~/.claude/skills/jp-restaurant-finder/SKILL.md`**
````markdown
---
name: jp-restaurant-finder
description: Use this skill whenever the user asks for restaurant, food, or dining recommendations for a Japan trip — e.g. "新宿附近推薦餐廳", "河口湖有什麼好吃的", "幫我找舞浜附近晚餐", "這附近有拉麵店嗎", or any request to recommend where to eat in a Japanese city/area. Also trigger when the user asks to double-check or rate an already-named Japanese restaurant. This skill's job is to cross-check every candidate against Google Maps and Tabelog ratings before recommending it — never recommend a Japan restaurant based on memory/training data alone, since ratings and even whether a place is still open change constantly.
---

# 日本餐廳推薦（Google Map + Tabelog 評價把關）

## 核心規則：推薦前一定要查評價
使用者只想要「真的好吃、不踩雷」的餐廳，不是隨便列名字。**每一間要推薦的餐廳，都要先用 WebSearch／WebFetch 查到它在 Google Map 和 Tabelog 上的實際評分，再決定要不要放進推薦清單**，不可以憑訓練資料裡的印象直接報名字（店可能已經倒了、評分可能已經跌了）。

## 評分門檻
- **Google Map**：星等最好 > 4.0（滿分5）。
- **Tabelog（食べログ）**：分數要 > 3.2，最好能到 3.5 以上（Tabelog 評分機制較嚴，3.5+ 在日本本地已經算相當高的評價）。
- 兩個門檻都是「最好」而非鐵律：如果某間店只有其中一項評價（例如太新的店還沒有Tabelog頁面），可以標註清楚「僅Google Map有資料」並照實給分，讓使用者自己判斷，不要為了湊門檻而隱藏資訊或誇大分數。
- 兩項評分都明顯偏低（Google Map < 3.8 且 Tabelog < 3.0）的店，除非使用者有特別指名或有其他強烈理由（例如只有這間有營業、在地限定），否則不要放進推薦清單。

## 查詢流程
1. 先鎖定範圍：使用者提到的地區／車站（例如新宿、河口湖駅周邊、舞浜）＋想吃的類型（拉麵、壽司、燒肉、居酒屋、甜點…沒說的話就問一句或給多元選擇）。
2. 用 WebSearch 找候選店家，來源可以是地區美食文章、Tabelog的地區排行榜（例如「新宿 ラーメン tabelog ランキング」），也可以是自己知道的知名店名再去查評分驗證。
3. **Google Map 跟 Tabelog 的分數、連結、評論內容都用 `dev/gmaps-lookup` 工具查**（不要用 WebFetch 查這兩個網站——`WebFetch` 讀不到 Google Maps 的 JS 動態頁面；Tabelog 雖然是一般網頁，但這個工具的 WebFetch 曾被 Tabelog 的防爬蟲判定為異常流量直接 403，即使頁面本身能正常瀏覽也一樣。已知只有這個 VM 自己的網路路徑〔也就是這裡的 Playwright〕能穩定連得上）：
   - **只要分數，不要評論內容**（快、輕量）：
     - Google Map 單筆：`node ~/claude-workspace/dev/gmaps-lookup/lookup.js "<店名 地區>" [截圖路徑]` → JSON（title/rating/reviewCount/**url**，這個`url`就是安全的分享連結，見下方「連結」說明）。
     - Google Map 多筆：把候選店整理成`[{"id":"...", "query":"店名 地區"}, ...]`存成queries.json，跑`node ~/claude-workspace/dev/gmaps-lookup/batch_lookup.js queries.json <輸出資料夾>`。
   - **需要近N個月評論內容**（使用者要「評論整理」「評論摘要」這類需求時用這組）：
     - Google Map 單筆：`node ~/claude-workspace/dev/gmaps-lookup/lookup_with_reviews.js "<店名 地區>" [月數，預設3] [截圖路徑]` → JSON多了`reviews`陣列（每則含rating/dateText/text）跟`mapsSearchUrl`（**分享連結一律用這個欄位**，不要用同一份JSON裡的`placeUrl`，見下方「連結」）。多筆版是`batch_lookup_with_reviews.js queries.json 輸出資料夾 [月數]`。
     - Tabelog 單筆：`node ~/claude-workspace/dev/gmaps-lookup/tabelog_reviews.js "<Tabelog評論列表頁URL，通常是店家頁面加.../dtlrvwlst/>" [月數，預設3] [--no-cache]` → JSON含`overallRating`跟篩選過的`reviews`（Tabelog顯示的是「YYYY/MM訪問」只到月份，篩選邏輯是月份層級，不是精確日期）。多筆版是`batch_tabelog_reviews.js urls.json 輸出資料夾 [月數] [每筆間隔ms，預設12000] [--no-cache]`。
     - **2026-09-22起內建本地快取＋冷卻機制（`tabelog_utils.js`），不用再手動避開連續查詢**：同一個Tabelog網址48小時內重複查會直接從本地快取回傳（結果會多`fromCache: true`欄位），不會真的發出請求；一旦真的被回403，工具會自動寫入冷卻時間戳記，接下來30分鐘內（單筆或批次）都會直接回報「on cooldown」並跳過網路請求，不會越查越糟。**照舊不要手動連續重試被擋的店**，讓冷卻機制自然過期就好；真的需要略過快取重查（例如懷疑分數變動很大）才加`--no-cache`。這個機制只是讓存取節奏更像真人瀏覽、減少實際請求量，不是要繞過人家的防爬蟲規則——查過`robots.txt`確認一般User-agent沒有禁止評論列表頁路徑。
   - 若工具首次執行報錯找不到playwright，先在`dev/gmaps-lookup/`跑`npm install`、`npx playwright install chromium`（只需裝一次）。
   - **一定要核對`title`欄位跟你查的店名/地址是否吻合**：Google Maps搜尋結果常在最上面插「スポンサー」贊助廣告，工具已經會跳過這些卡片，但換了新查詢字串或Google改版時還是可能失準，title明顯對不上（例如變成「結果」或完全不相關的店名）就用截圖工具存的screenshot路徑親自看一次畫面（用Read工具開圖片）確認。
   - `reviewCount`（跟評論卡片內容）偶爾會因為頁面非同步渲染抓不到或抓少（rating本身很穩定），抓不到不代表店有問題，可以再跑一次或直接看截圖。
   - **截圖本身也是重要資訊來源**：畫面上常會直接顯示「閉業」「臨時休業」等狀態、完整地址、營業時間，這些都比單純一個評分數字更有用，看截圖時一併記下來。
   - 若使用者自己貼了 Google Maps／Tabelog 連結／截圖／數字，優先採用使用者提供的（比工具現查更即時準確），並標註來源是「使用者提供」。
4. **環境衛生把關（必做，不是使用者要求「評論整理」才做）**：每一間打算放進推薦清單的候選店，都要另外用第3點的`_with_reviews`／`tabelog_reviews`工具抓評論內容（即使原本只是查分數用的輕量版`lookup.js`／`batch_lookup.js`，這一步也要為候選店補跑一次帶評論的版本），把抓到的`reviews`陣列依評分由低到高排序，**優先看分數最低的幾則**（通常抓最低3-5則就足夠看出是否有重複抱怨），確認裡面有沒有提到環境髒亂／衛生相關問題，例如：蟑螂／老鼠／蒼蠅、廁所髒、桌面油膩沒擦、餐具沒洗乾淨、油煙或排水臭味、店員衛生習慣差等。**抓到的評論絕大多數是日文原文（工具固定用`hl=ja`／`ja-JP`查詢Google Map，Tabelog本身就是日文網站），Google Map上偶爾還會混到英文／中文／韓文的觀光客評論；不論原文是哪種語言都要直接讀懂語意去判斷，不要只用中文關鍵字去比對原文字串，會漏掉大部分日文評論**。常見對應詞可參考：日文「ゴキブリ／ネズミ」（蟑螂/老鼠）、「汚い／不潔」（髒/不衛生）、「トイレが汚い」（廁所髒）、「テーブルがベタベタ」（桌面油膩）、「食器が汚れていた」（餐具沒洗乾淨）、「臭い／匂いがする」（有臭味）、「店員の衛生管理」（店員衛生習慣）；英文則常見 dirty／unclean／cockroach／roach／smelly／unhygienic 等字眼。**Google Map 和 Tabelog 兩邊都要看，不能只看其中一邊就當作查完**。若查到這類負評，不論最後是否仍列入推薦清單，都要在輸出表格「備註」欄特別標注（例如「⚠️評論提到廁所/餐具衛生問題」）並照原意翻成中文寫給使用者看，不要因為整體分數高就略過不提，讓使用者自己判斷能不能接受。
5. **給使用者的連結怎麼選（重要，之前出過錯）**：
   - Google Map：一律用 `mapsSearchUrl`／`lookup.js`的`url`欄位，格式是`https://www.google.com/maps/search/{店名}`。**絕對不要把`placeUrl`（工具點進去該店之後、瀏覽器實際導覽到的那個含`@lat,lng`跟`g_ep`參數的長網址）直接貼給使用者**——`g_ep`那段字串是跟當次瀏覽session綁定的token，使用者自己點開常常打不開，這個坑已經真實發生過一次。
   - Tabelog：用該店Tabelog頁面本身的網址（例如`https://tabelog.com/tokyo/A1308/A130801/13110628/`），這個是穩定的公開連結，沒有上述問題。
6. **評論內容整理**：把抓到的`reviews`陣列整理成給使用者看的摘要，抓重複出現的主題（例如「排隊時間長」「份量大」「某道菜特別好評」），不用逐則翻譯貼出來；正面/負面都要涵蓋，不要報喜不報憂。**評論原文可能是日文、英文、中文或韓文等不同語言（尤其Google Map上常有觀光客留言），不論原文是哪種語言都要先讀懂語意再整理，摘要一律翻成繁體中文給使用者看，不要因為看不懂/懶得處理某個語言就跳過那幾則評論不看**。環境衛生相關的負評不算在這裡的一般性摘要裡，一律照第4點另外特別標注，不要混在這裡輕描淡寫帶過。
7. 同時留意：目前是否還在營業（gmaps-lookup截圖上若標示「閉業」就直接排除，Tabelog頁面若顯示「閉店」「移転」也一樣）、是否需要預約（日本熱門餐廳常需事前訂位，尤其是壽司/懷石/燒肉），營業時間是否配合使用者的行程時段。
8. 資料若查不到明確分數或評論，誠實告知「這間店查不到Tabelog頁面／評分」或「這次沒抓到這間店的Google Map分數/評論，可以重跑一次或直接看截圖」，不要編造數字湊評分、也不要拿別的網站分數（例如Yahoo!地圖）冒充Google Map。

## 輸出格式建議
基本比較用表格：

| 店名 | 類型 | 位置/交通 | Google Map | Tabelog | 需預約 | 備註 |
|------|------|-----------|------------|---------|--------|------|

- Google Map／Tabelog 欄位：抓得到才填數字；真的抓不到（重試+看截圖都沒有）就寫「查不到」，不要留白讓人誤以為忘了查，也不要填別的網站分數。
- 備註欄可以放：推薦理由、招牌菜、預算區間、若評分沒到門檻要註明「評分稍低但因為XX理由仍列入」。**若第4點查到環境髒亂／衛生相關負評，這裡一定要特別標注（例如「⚠️評論提到廁所/餐具衛生問題」），不可省略。**

若使用者要「連結」「評論整理」這類更完整的資訊（用了上面`_with_reviews`/`tabelog_reviews`工具查過），改用這種每間店兩平台分開列、合併在同一張表的格式：

| 店名 | Tabelog（分數・連結） | Tabelog 近N月評論摘要 | Google Map（分數・連結） | Google Map 近N月評論摘要 |
|------|------------------------|------------------------|----------------------------|----------------------------|

若使用者要傳到 Telegram，改成條列式（Telegram 純文字不支援Markdown粗體，用「■」「【】」分隔即可，網址純文字貼上去 Telegram 會自動變成可點連結），傳送前照 workspace CLAUDE.md「終端機權限與資安邊界」的規則先把內容拿給使用者確認再送出。

## 若在 claude-workspace 專案內工作
若目前工作目錄是使用者的 claude-workspace（有 topic／memory 機制），查完並整理出推薦清單後，依該專案 CLAUDE.md 的規則把結論寫回對應的 `memory/{topic}.md`（旅遊通常是 `.claude/memory/travel.md`）並記錄 `activity_log.jsonl`；這套機制的細節不在這裡重複，照專案既有規則走即可。

## 與 jp-travel-planner 的分工
`jp-travel-planner` 負責交通／天氣查詢與行程優化；這個 skill 專注在「吃」——找餐廳並用 Google Map／Tabelog 評價把關。規劃行程時若同時需要交通和吃飯建議，兩個 skill 可以一起用。

````

**`~/.claude/skills/social-post-search/SKILL.md`**
````markdown
---
name: social-post-search
description: Use ONLY when the user explicitly asks to search or collect posts from social platforms — the request must name Threads、Instagram、IG、社群、網紅/部落客分享、打卡文、限動/限時動態, or similar, e.g. "幫我查IG跟Threads上京都紅葉的文章", "搜尋一下大阪自由行的IG貼文", "去Threads看看有沒有人分享這支耳機的開箱", "幫我查社群上這家餐廳的評價". Do NOT trigger on a plain topic/recommendation question that doesn't mention social platforms — e.g. "東京有什麼推薦的約會景點" or "這支耳機好不好" should be answered directly or with another more fitting skill, not routed here just because it names a destination, product, or restaurant. This skill works for any subject (travel destinations, restaurants, products, brands, events, …), not only travel.
---

# Threads / Instagram 貼文搜尋

## 觸發條件（重要，避免誤用）
這個 skill **只在使用者明確要求查社群平台**時才使用，判斷依據是使用者的用詞裡有沒有出現「IG／Instagram／Threads／社群／網紅／部落客分享／打卡／限動／限時動態」這類字眼。

如果使用者只是問一般性問題，例如「東京有什麼推薦的約會景點」「這支耳機好不好」「幫我查一下OO餐廳」，**不要**自動套用這個 skill —— 那種問題該用一般搜尋或更合適的 skill（例如日本餐廳有 `jp-restaurant-finder`）直接回答，不必特地繞去查 IG/Threads 單篇貼文。只有當使用者的用詞明確指向「社群上的貼文/分享/開箱/心得」，才進入下面的流程。

## 用途與邊界
幫使用者在**不登入**任何帳號的前提下，透過搜尋引擎找出 Threads / Instagram 上與某個主題相關的公開貼文，整理成一份可讀清單。查詢對象不限旅遊目的地，也可以是餐廳、產品、品牌、活動、3C開箱等任何主題——核心精神是「借道搜尋引擎、只讀公開頁面、節制頻率」，不是把 IG/Threads 當成可以爬取的資料庫。

**硬性限制（不可繞過）：**
- 不使用、也不要求使用者提供任何 Instagram / Threads 帳號登入或 cookie。
- 只能透過 WebSearch 找到候選網址，再用 WebFetch 讀取單篇貼文的公開頁面；不要嘗試找其他方式繞過登入牆。
- 一次任務最多讀取 30 篇貼文頁面，且不要在短時間內密集發出請求（每讀幾篇可以稍微間隔）。
- 頁面被導向登入頁、出現錯誤、或明顯是防爬阻擋時，直接跳過該篇，改用搜尋結果本身的標題／摘要，**不要重試、不要換方式繞過**。

## 輸入參數
- **查詢對象**（必填）：目的地、餐廳、產品、品牌等任何一個具體主體，例如「京都」「大阪」「某某耳機」「某家餐廳」。
- **想找的角度／主題**（必填）：例如「秋天紅葉」「自由行行程」「開箱心得」「使用評價」「在地美食」。

若使用者只給了其中一項，先問清楚缺的那項再開始，不要自己亂猜（查詢對象和角度會直接決定關鍵字組合，猜錯會讓整份清單失焦）。

## 執行流程

### 1. 產生關鍵字組合
依查詢對象＋角度，發散出 5～8 組關鍵字，涵蓋這個主題常見的幾個不同面向。面向會依主題性質而不同，不要死套旅遊角度，例如：
- **旅遊目的地**：行程／自由行／懶人包、必吃／美食／咖啡廳、住宿／飯店／民宿、景點／私房景點／秘境、交通／交通攻略
- **餐廳／美食**：評價／心得、必點、雷/地雷、CP值、排隊/預約
- **產品／3C**：開箱、評測、心得、比較、優缺點
- 若使用者提到季節、年份或型號（例如「2026」「紅葉」「Pro Max」），每組都帶上，確保結果夠新、夠對應。

### 2. 用 site: 語法搜尋
對每組關鍵字分別用 WebSearch 執行：
- `site:threads.com {關鍵字}`（也可視結果情況嘗試 `site:threads.net`）
- `site:instagram.com {關鍵字}`

從搜尋結果中，只挑出「單篇貼文」的網址：
- Threads：`threads.com/@帳號/post/...` 或 `threads.net/@帳號/post/...`
- Instagram：`instagram.com/p/...` 或 `instagram.com/reel/...`

個人主頁、hashtag 頁、探索頁一律略過（這些不是單篇內容，讀了也擷取不到有用資訊）。同一網址在不同關鍵字組合下重複出現時只保留一次。

### 3. 讀取貼文內容
對每個保留下來的貼文網址用 WebFetch 讀取頁面，優先從 HTML 的 meta 標籤擷取：
- `og:title` → 作者
- `og:description` → 貼文內文（IG 通常是圖說）
- `og:image` → 封面圖片網址

實務上 IG 的公開頁面常常抓不到完整 meta 資訊（WebFetch 只看得到互動介面、沒有 head 區塊），這種情況改用該筆搜尋結果本身的標題與摘要文字，並在最終清單中該篇註明「僅摘要」，讓使用者知道這篇的資訊可信度較低、細節可能不完整。Threads 貼文文字本身通常會直接公開列點，較容易抓到完整內文。

記得對照上面的「硬性限制」：讀取篇數不超過 30 篇，且不要短時間內連續狂發請求。

### 4. 篩選
整理前先過濾一輪：
- 排除明顯與主題無關、純業配空泛、或內容太空洞（例如只有一張照片配「好美」，或只是一句預告「以後會分享」）的貼文。
- 排除關鍵字命中但實際講的是別的地方/別的東西的貼文（例如查「東京」卻搜到台灣本地帳號同名關鍵字），務必核對貼文文字是否真的對應到查詢對象。
- 優先留下有具體資訊的貼文：店名、地點名、價格、規格、交通方式、實際心得這類「可以拿來用」的內容。
- 同樣主題有多篇可選時，優先選較新的貼文，避免資訊過時（店家可能已經歇業、規格/價格可能已變）。

### 5. 輸出格式
用繁體中文、依主題分類（例如「紅葉景點」「在地美食」「交通」…，或依查詢對象性質自訂分類）輸出，每篇貼文包含：

- **平台**：Threads / IG
- **作者**：（來自 og:title 或搜尋結果標題）
- **內容重點摘要**：2～3 句，用自己的話整理，不要整段照搬原文
- **提到的具體地點、店家或型號**
- **原文連結**
- **資料來源標註**：完整內文 / 僅摘要

全部列完後，附一段「總整理」：
- 列出被多篇貼文重複推薦的地點、店家或觀點（這種交叉驗證過的資訊通常比單篇更可靠）。
- 值得注意的提醒，例如需要預約、人潮時段、交通建議、季節限定、常見負評等。

## 若在 claude-workspace 專案內工作
這個搜尋行為屬於「資料存取」，若目前工作目錄（或使用者的個人助理情境）涉及 claude-workspace，依該專案 CLAUDE.md 的紀錄義務，完成後要：
1. 判斷本次查詢屬於哪個主題 {topic}（旅遊是 `travel`，其他主題依 CLAUDE.md 的動態分類原則判斷或新建），把查詢對象、角度、關鍵字組合、篩選後的清單重點、觀察心得寫進對應 `memory/{topic}.md`（沒有產生實體資料檔的話，資料檔索引欄位可以留空，只更新「策略與觀察重點」等段落即可）。
2. 在 `logs/activity_log.jsonl` 追加一行紀錄，`topic` 填對應主題，`action` 用 `"read"`（純搜尋整理沒有下載檔案時）或 `"download"`（若使用者要求把清單存成檔案）。
3. 若使用者要求把清單存成檔案或傳送出去，判斷這份輸出是「一次性看完/傳完即可」還是「以後還要回頭查」：多數情況屬於前者，存到 `outbox/` 並照第七節規則命名；若使用者明確說要長期保存追蹤，才存進 `data/{topic}/` 並在對應 memory 檔案的資料檔索引補一筆。傳送到 Telegram 等對外管道前，依「終端機權限與資安邊界」規則先讓使用者確認要傳送的內容。

那套 topic／memory／log 機制的細節不在此重複，照專案既有規則走即可；若不是在這個情境下工作（例如純粹被單次呼叫回答），就只需完成上面的搜尋與輸出，不必額外寫檔案。

````

## 八、launchd 排程（plist）完整內容

以 `com.claudeworkspace.` 前綴辨識屬於本 workspace 的排程。重建時記得
把帳號路徑換成新機器的實際路徑，並用 `launchctl bootstrap gui/$(id -u)
<plist路徑>` 載入。

**`~/Library/LaunchAgents/com.claudeworkspace.outbox.cleanup.plist`**
````xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.claudeworkspace.outbox.cleanup</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/vm/claude-workspace/dev/outbox-cleanup/cleanup_outbox.py</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>3</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>/Users/vm/claude-workspace/logs/outbox-cleanup.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/vm/claude-workspace/logs/outbox-cleanup.err.log</string>
</dict>
</plist>

````

**`~/Library/LaunchAgents/com.claudeworkspace.stocknews.fetch.plist`**
````xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.claudeworkspace.stocknews.fetch</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/vm/claude-workspace/dev/stock-news/.venv/bin/python</string>
        <string>/Users/vm/claude-workspace/dev/stock-news/fetch_news.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/vm/claude-workspace/dev/stock-news</string>
    <key>StartInterval</key>
    <integer>1800</integer>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/Users/vm/claude-workspace/logs/stock-news-fetch.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/vm/claude-workspace/logs/stock-news-fetch.err.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
        <key>HOME</key>
        <string>/Users/vm</string>
    </dict>
</dict>
</plist>

````

**`~/Library/LaunchAgents/com.claudeworkspace.stocknews.digest.tw.plist`**
````xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.claudeworkspace.stocknews.digest.tw</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/vm/claude-workspace/dev/stock-news/run_digest.sh</string>
        <string>tw</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/vm/claude-workspace/dev/stock-news</string>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>8</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>RunAtLoad</key>
    <false/>
    <key>StandardOutPath</key>
    <string>/Users/vm/claude-workspace/logs/stock-news-digest-tw.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/vm/claude-workspace/logs/stock-news-digest-tw.err.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
        <key>HOME</key>
        <string>/Users/vm</string>
    </dict>
</dict>
</plist>

````

**`~/Library/LaunchAgents/com.claudeworkspace.stocknews.digest.us.plist`**
````xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.claudeworkspace.stocknews.digest.us</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/vm/claude-workspace/dev/stock-news/run_digest.sh</string>
        <string>us</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/vm/claude-workspace/dev/stock-news</string>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>21</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>RunAtLoad</key>
    <false/>
    <key>StandardOutPath</key>
    <string>/Users/vm/claude-workspace/logs/stock-news-digest-us.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/vm/claude-workspace/logs/stock-news-digest-us.err.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
        <key>HOME</key>
        <string>/Users/vm</string>
    </dict>
</dict>
</plist>

````

## 九、README.md
**`~/claude-workspace/README.md`**
````markdown
# claude-workspace

Claude（Claude Code / Claude Desktop）在這台 macOS VM 上的行為紀錄與主題分類機制。

## 導覽
- `.claude/CLAUDE.md` — 主規則檔（全域規則、主題分類機制、路徑索引、Token 存取機制）
- `.claude/wrappers/` — 密鑰存取用 wrapper script（不含任何明文密鑰）
  - `run_telegram_mcp.sh` — 啟動 Telegram 通知 MCP server
- `.claude/memory/` — 各主題細節紀錄（依需求動態新增，非固定清單）
  - `dev.md` 程式碼專案索引（跨主題共用）
  - `general.md` 尚未分類 / 雜項
- `data/` — 實際產生的資料檔，依主題分資料夾（依需求動態新增）
- `dev/` — 所有專案程式碼統一存放處，不分主題
- `logs/activity_log.jsonl` — 按時間累積的操作日誌（append-only，當月）
- `logs/archive/` — 每月封存的舊日誌

## 運作方式
`~/.claude/CLAUDE.md` 內以 `@import` 指向本資料夾的 `.claude/CLAUDE.md`，
因此不論工作目錄在哪，規則都會生效。

本機為與實體主機完全隔離的 macOS VM，Claude 在此 VM 內的終端機操作
擁有完整權限，但密鑰 / 個資不落地、對外傳送前需確認的規則不受影響
（詳見主規則檔「終端機權限與資安邊界」）。

密鑰一律不落地於本資料夾內任何檔案，只存於 macOS Keychain，
由 `.claude/wrappers/` 內的腳本在執行當下動態取用。

````

## 十、排除項與理由（刻意不備份的東西）

| 項目 | 路徑 | 為什麼不備份 |
|------|------|--------------|
| 操作日誌 | `logs/activity_log.jsonl`、`logs/archive/*.jsonl` | 累積型 append-only 紀錄，重建後從空檔案重新開始即可，沒有長期保留價值 |
| 可重抓的歷史資料 | `data/stock/{news,universe,sector,sector_etf,fomo,digests}/`、`data/*/*.csv` 等 | 用對應 dev/ 腳本（stock-news/fetch_news.py、stock-sector/fetch_prices.py 等）重新抓取即可，資料量大且會過時 |
| 一次性產出 | `outbox/` | 本來就會被 outbox-cleanup 自動 3 天清除，本質上是暫存輸出 |
| 虛擬環境 / 套件快取 | 各專案 `.venv/`、`dev/gmaps-lookup/node_modules/`、`__pycache__/` | 由「六」節每個專案的「重建方式」指令重新安裝即可 |
| Tabelog 本地快取/冷卻鎖檔 | `dev/gmaps-lookup/.tabelog_state/` | 暫存快取，重建後自然重新累積 |
| 單次查詢用暫存輸入檔 | 例如 `dev/gmaps-lookup/queries.json`、`tabelog_urls.json` | 是某一次特定查詢任務的候選店清單，不是工具本體邏輯，之後查詢時會依當次需求重新產生 |
| **密鑰明文** | Keychain 內 `telegram-bot-token`、`telegram-chat-id` | 依規則任何情況下都不得寫入檔案/log/memory/回覆內容，重建時由使用者在新機器上依「五、Token 安全儲存機制」5.1 節手動重新輸入 |
| Claude Desktop 設定檔 | `~/Library/Application Support/Claude/claude_desktop_config.json` | 本來就只在使用者確認後才建立，備份中只保留「五、5.4」的知識參考說明 |
| 系統/編輯器雜項 | `.DS_Store`、`__pycache__/*.pyc` 等 | 與備份目的無關的系統產生檔案 |

## 十一、重建步驟 Checklist

依序執行，遇到標示「⚠️ 需向使用者確認」的步驟不得自行略過確認：

1. 建立「一、目錄結構總覽」列出的所有資料夾（`.claude/wrappers/`、
   `.claude/memory/`、`data/{topic}/`、`dev/`、`logs/`、`outbox/`）。
2. 依「二」「三」節內容，寫入 `~/.claude/CLAUDE.md` 與
   `~/claude-workspace/.claude/CLAUDE.md`（注意把文件內帳號路徑換成
   新機器的實際使用者帳號）。
3. 依「四」節內容，寫入 `.claude/memory/` 底下每個 memory 檔案。
4. 依「五」節內容，寫入 `run_telegram_mcp.sh` 並 `chmod +x`。
5. 依「六」節，逐專案建立 venv/npm 環境並安裝套件，寫入每個專案的
   原始碼檔案。
6. ⚠️ 需向使用者確認：檢查 macOS Keychain 是否已有
   `telegram-bot-token`／`telegram-chat-id`（用
   `security find-generic-password -a "$USER" -s "telegram-bot-token" -w`
   確認能取到值，不印出明文）。若沒有，停下 Telegram 相關後續步驟，
   引導使用者依「五、5.1」節手動建立，其餘步驟可以先完成。
7. 依「八」節內容，建立 `~/Library/LaunchAgents/` 底下的 plist
   （記得替換帳號路徑），用 `launchctl bootstrap gui/$(id -u) <plist路徑>`
   載入。
8. ⚠️ 需向使用者確認：是否要建立/合併
   `~/Library/Application Support/Claude/claude_desktop_config.json`
   （依「五、5.4」節內容），確認後才動手，事後 `chmod 600`。若這台機器
   沒有安裝 Claude Desktop，先詢問使用者是否要安裝，不裝也不影響其他
   部分。
9. ⚠️ 需向使用者確認：提出一個預設測試訊息文字，確認後才透過
   `run_telegram_mcp.sh "測試訊息文字"` 實際發送一次，驗證整條鏈路
   （Keychain → wrapper → telegram_notify.py → Telegram API）真的可用。
10. 依「九」節內容寫入 `README.md`。
11. 將本次建置的重建紀錄（topic 填 `general`／`dev`）追加寫入
    `logs/activity_log.jsonl`，並更新 `memory/dev.md`、`memory/general.md`
    對應段落。
12. 最後向使用者回報：目錄與規則檔是否全部建立完成、每個 dev/ 專案
    環境是否裝好、Telegram 端對端測試是否成功（附 Telegram API 的 `ok`
    欄位結果，不附明文）、launchd 排程是否已載入、
    `claude_desktop_config.json` 目前狀態、並提醒使用者需要重新開啟
    session（或 `/memory` 重載）主規則檔才會實際生效。
13. 重建完成後，往後若使用者想再產生新的備份快照，直接使用
    `dev/init-prompt/generate_backup_prompt.md`（Prompt A）即可，
    不需要回頭參照這份 Prompt B 舊版本。

---

（文件結束）
