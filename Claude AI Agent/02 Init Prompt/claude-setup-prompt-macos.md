【給 Claude 的初始設定 prompt】(macOS 版 / 獨立隔離 VM，含 Telegram 通知機制)
請依照以下規格，在這台 macOS 電腦上建立完整的工作目錄與規則檔案，
並完成 Telegram 通知機制的程式碼、執行環境與端對端測試。
帳號路徑請一律使用 /Users/{account}/（或 ~/），{account} 請替換為當前 macOS 使用者帳號名稱。

================================================================
一、基本原則
================================================================
1. 工作目錄位置：~/claude-workspace/
2. 不導入 Git 版本控制。
3. 操作日誌格式採用 JSONL（activity_log.jsonl）。
   理由：append 不會破壞格式、可用 jq 或程式查詢統計；
         人眼閱讀需求由 memory/*.md 的整理表格滿足。
4. 目錄配置原則：
   - data/ 與 logs/ 放在 .claude/ 之外（workspace 根層），
     .claude/ 只放「給 AI 的指示與記憶」。
   - activity_log 放進 logs/，支援每月封存至 logs/archive/。
   - 不預先固定任何主題（如股票、旅遊等）的資料夾或 memory 檔名。
     每當出現一個新的主題領域，才動態建立：
       data/{topic}/         → 該主題產生的資料檔
       .claude/memory/{topic}.md → 該主題的細節紀錄
     {topic} 一律使用簡短英文小寫 slug（例：travel、finance、network）。
   - 開發用「程式碼」不分主題，一律集中存放於 dev/（workspace 根層），
     由 .claude/memory/dev.md 統一索引每個專案的路徑、用途、所屬主題標籤。
     即使某段程式碼是為了某個主題而寫，程式碼本體仍放 dev/，
     只在對應 memory/{topic}.md 裡引用 dev/ 底下的路徑，不重複複製。
   - 另建立 .claude/wrappers/，專門存放「密鑰存取用的 wrapper script」，
     此資料夾內只放腳本本身，不放任何明文密鑰。
5. Python 套件安裝原則（適用於所有需要外部套件的 dev/ 專案，不限 Telegram）：
   - 任何需要安裝 Python 套件的情境，一律在對應 dev/{project}/ 專案目錄下
     建立專屬虛擬環境（dev/{project}/.venv），不得對系統 python 或
     Homebrew 管理的 python 執行全域 pip install（也不得加
     `--break-system-packages` 硬闖 PEP 668 限制）。
   - 若系統內建 python3 版本過舊、不符合套件需求（例如 fastmcp 需要
     Python >=3.10，但系統可能只有 3.9），可用 Homebrew 安裝所需版本
     （例：`brew install python@3.12`），再用該版本建立專屬 venv，
     不覆蓋、不取代系統原有的 python3。
   - wrapper script 若需要呼叫這類套件，直接指向對應 venv 內的
     python 執行檔（例：dev/{project}/.venv/bin/python），
     而不是呼叫系統 python3。

================================================================
二、請建立以下檔案／資料夾架構
================================================================
~/
├── .claude/
│   └── CLAUDE.md                  # 使用者層級：一行 @import 掛載主規則檔
│                                  #（不論工作目錄在哪都會被讀取）
│
└── claude-workspace/
    ├── README.md                  # 給人看的導覽
    ├── .claude/
    │   ├── CLAUDE.md              # 主規則檔（全域規則 + 分類機制 + 路徑索引）
    │   ├── wrappers/               # 密鑰存取 wrapper script 存放處（無明文密鑰）
    │   │   └── run_telegram_mcp.sh
    │   └── memory/
    │       ├── dev.md             # 程式碼專案索引（跨主題共用）
    │       ├── general.md         # 尚未分類 / 雜項
    │       └── （其他 {topic}.md 依實際需求動態新增）
    ├── data/
    │   ├── general/                # 尚未分類的資料檔
    │   └── （其他 {topic}/ 依實際需求動態新增）
    ├── dev/                        # 所有專案程式碼統一存放處（不分主題）
    │   └── telegram-notify/
    │       ├── telegram_notify.py # Telegram 發送邏輯（見四之五之 5.3）
    │       └── .venv/              # 專屬虛擬環境（安裝 fastmcp 後產生，
    │                               #   不手動建立內容，由 pip/venv 產生）
    └── logs/
        ├── activity_log.jsonl     # append-only 操作日誌（當月）
        └── archive/
            └── YYYY-MM.jsonl      # 每月封存

運作方式：
~/.claude/CLAUDE.md 以 @import 指向 ~/claude-workspace/.claude/CLAUDE.md，
因此不論 Claude Code / Claude Desktop 的工作目錄在哪，規則仍自動生效。
※ 修改後需重開 session（或 /memory 重載）才會載入。

================================================================
三、~/.claude/CLAUDE.md 內容
================================================================
# 使用者層級規則

實際規則內容集中在 workspace 主檔，透過下方 import 載入
（不論工作目錄在哪，此檔都會被讀取）：

@/Users/{account}/claude-workspace/.claude/CLAUDE.md

================================================================
四、claude-workspace/.claude/CLAUDE.md 內容（主規則檔）
================================================================
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

### Python 套件安裝原則
- 任何需要安裝 Python 套件的情境，一律在對應 dev/{project}/ 專案目錄下
  建立專屬虛擬環境（dev/{project}/.venv），不得對系統 python 或
  Homebrew 管理的 python 執行全域 pip install，也不得使用
  `--break-system-packages` 繞過 PEP 668 限制。
- 若系統 python3 版本不符套件需求，可用 Homebrew 安裝所需版本
  （例：`brew install python@3.12`），再用該版本建立專屬 venv。
- 需要呼叫該套件的 wrapper script，一律指向對應 venv 內的 python
  執行檔，而不是系統 python3。

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
     內容，避免非預期夾帶個資或內部資料。每次發送都要重新確認內容，
     即使是重複測試也不能省略。
  c. 不得自行變更 VM 對外的網路 / 防火牆設定以「擴大」對外存取範圍，
     除非使用者明確指示。
  d. 修改 `claude_desktop_config.json` 前必須先向使用者確認
     （詳見「五、Token 安全儲存機制」5.4 節），不因它屬於「初始建置」
     範圍而略過這一步 —— 初始建置只代表「產生程式碼 / 建立 venv /
     更新 wrapper」這幾項本機、可逆的操作不需逐一確認，
     不代表寫入 Claude Desktop 設定檔或對外發送測試訊息也可以省略確認。

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
| general | memory/general.md | data/general/ | （建置當天）|
| dev | memory/dev.md | dev/（不分主題，統一路徑）| （建置當天）|

---

## 三、資料路徑索引

| 項目 | 路徑 |
|------|------|
| 各主題資料 | ~/claude-workspace/data/{topic}/ |
| 程式碼（跨主題共用） | ~/claude-workspace/dev/ |
| 操作日誌（當月） | ~/claude-workspace/logs/activity_log.jsonl |
| 日誌封存 | ~/claude-workspace/logs/archive/YYYY-MM.jsonl |
| 密鑰 wrapper script | ~/claude-workspace/.claude/wrappers/ |

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
使用者需於 Terminal 手動執行（Claude 不需、也不應重複執行）：
```bash
security add-generic-password -a "$USER" -s "telegram-bot-token" -w "你的token"
security add-generic-password -a "$USER" -s "telegram-chat-id" -w "你的chat id"
```
若 Claude 檢查 Keychain 發現這兩筆密碼尚未建立，必須停止 Telegram 機制的
建置並告知使用者先完成上述步驟，不得詢問使用者要不要直接貼明文。

### 5.2 wrapper script：run_telegram_mcp.sh
- 存放路徑固定為：`~/claude-workspace/.claude/wrappers/run_telegram_mcp.sh`
- 需要執行權限：`chmod +x ~/claude-workspace/.claude/wrappers/run_telegram_mcp.sh`
- 本身不得包含任何明文密鑰，只負責「從 Keychain 取值 → export 環境變數
  → 呼叫 telegram_notify.py，並把自己收到的參數原樣轉發」。
- 之所以轉發參數（`"$@"`）：telegram_notify.py 同時支援「CLI 測試模式
  （帶文字參數，直接發送並結束，供手動驗證用）」與「MCP server 模式
  （不帶參數，走 fastmcp，供 Claude Desktop 呼叫）」，wrapper 需讓兩種
  呼叫方式都能用同一支腳本進入。
- `command` 指向的是 dev/telegram-notify/.venv 裡的 python（因為
  MCP server 模式需要 fastmcp，而 fastmcp 只安裝在這個專屬 venv，
  不是系統 python3），CLI 測試模式的 stdlib 邏輯在這個 venv 裡一樣能跑。

```bash
#!/bin/bash
# .claude/wrappers/run_telegram_mcp.sh

export TELEGRAM_BOT_TOKEN=$(security find-generic-password -a "$USER" -s "telegram-bot-token" -w)
export TELEGRAM_CHAT_ID=$(security find-generic-password -a "$USER" -s "telegram-chat-id" -w)

if [ -z "$TELEGRAM_BOT_TOKEN" ] || [ -z "$TELEGRAM_CHAT_ID" ]; then
  echo "錯誤：無法從 Keychain 讀取必要的環境變數" >&2
  exit 1
fi

exec /Users/{account}/claude-workspace/dev/telegram-notify/.venv/bin/python /Users/{account}/claude-workspace/dev/telegram-notify/telegram_notify.py "$@"
```

第一次執行 `security find-generic-password` 時，macOS 會跳出系統彈窗
詢問是否允許該程式存取 Keychain 中的這筆密碼，選「一律允許」即可，
之後不會再重複詢問。

### 5.3 telegram_notify.py 程式碼與執行環境

程式碼本體（僅提供單一功能：發送文字訊息，不具備讀取訊息 / 聯絡人等
其他權限）放在：
```
~/claude-workspace/dev/telegram-notify/telegram_notify.py
```
依「開發用程式碼統一集中於 dev/」原則管理，並於 memory/dev.md 索引。
內容如下（已驗證可直接運作，建置時直接寫入這個內容即可，不需重新設計）：

```python
#!/usr/bin/env python3
"""Send text messages to a Telegram chat via the Bot API.

Single capability only: send_message. No reading of messages/contacts.
Run with a CLI argument to send that text directly (manual testing).
Run with no arguments to start as an MCP server (requires fastmcp),
for use from Claude Desktop via the wrapper script.
"""
import json
import os
import sys
import urllib.parse
import urllib.request


def send_message(text: str) -> dict:
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({"chat_id": chat_id, "text": text}).encode()
    with urllib.request.urlopen(url, data=data, timeout=10) as resp:
        return json.loads(resp.read().decode())


def run_mcp_server() -> None:
    from fastmcp import FastMCP

    mcp = FastMCP("telegram-notify")

    @mcp.tool()
    def send_telegram_message(text: str) -> dict:
        """Send a plain text message to the configured Telegram chat."""
        return send_message(text)

    mcp.run()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        result = send_message(" ".join(sys.argv[1:]))
        print(json.dumps(result, ensure_ascii=False))
    else:
        run_mcp_server()
```

**執行環境建置步驟（建置時依序執行）：**
1. 確認系統 python3 版本：`python3 --version`。
2. 若版本 < 3.10（fastmcp 的最低需求），先用 Homebrew 安裝夠新的版本：
   `brew install python@3.12`（若 Homebrew 本身未安裝，先告知使用者
   並詢問是否要安裝 Homebrew，不自行擴大安裝範圍）。
3. 在專案目錄下建立專屬虛擬環境：
   `<python3.12路徑> -m venv ~/claude-workspace/dev/telegram-notify/.venv`
4. 升級 pip 並安裝 fastmcp（只在這個 venv 裡，不裝到系統或 Homebrew
   全域環境，不使用 `--break-system-packages`）：
   ```
   ~/claude-workspace/dev/telegram-notify/.venv/bin/python -m pip install --upgrade pip
   ~/claude-workspace/dev/telegram-notify/.venv/bin/python -m pip install fastmcp
   ```
5. 驗證安裝：確認 `telegram_notify` 模組與 `fastmcp` 都能在這個 venv
   裡正常 import（不需要真的啟動 MCP server 去做這個驗證）。

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
      "command": "/Users/{account}/claude-workspace/.claude/wrappers/run_telegram_mcp.sh"
    }
  }
}
```

若該檔案已存在且已有其他 `mcpServers` 項目，採「合併」方式加入
`telegram-notify` 這個項目，不整檔覆蓋既有設定。

此章節屬於「知識參考」，Claude **不得自動修改** `claude_desktop_config.json`，
即使是在「初始建置」流程中，也必須先向使用者確認要不要建立 / 修改這個檔案，
確認後才動手。修改完成後執行：
```bash
chmod 600 ~/Library/Application\ Support/Claude/claude_desktop_config.json
```
確保只有目前使用者帳號能讀取這個設定檔本身。

若這台機器根本沒有安裝 Claude Desktop（`/Applications` 裡找不到），
不需要幫使用者安裝，先詢問使用者是否要安裝；使用者選擇不裝時，
Telegram 機制仍可透過「CLI 測試模式」（wrapper script 帶文字參數）
獨立驗證可用，不影響其他部分的建置。

### 5.5 使用時機
- 任何需要「主動通知使用者」的情境（任務完成、異常告警等），
  一律透過呼叫 `send_telegram_message` 工具送出，且送出前需依
  「終端機權限與資安邊界」b 項向使用者確認訊息內容。
- 未來若新增其他密鑰（非 Telegram），比照本節模式：
  Keychain 存值 → 新增一支 wrapper script → 於 claude_desktop_config.json
  或對應設定檔中指向該 wrapper；若該密鑰對應的程式需要額外 Python 套件，
  比照「Python 套件安裝原則」建立專屬 venv。

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
| telegram-notify | dev/telegram-notify/telegram_notify.py | （通知類，跨主題共用） | Python 3（stdlib）+ fastmcp（於 .venv） | 單向發送 Telegram 文字訊息，僅有 send_message 一個能力 |

## 環境與慣用寫法
（Python/Node 版本、虛擬環境位置、常用套件、程式風格慣例；
Python 專案若需要外部套件，預設在 dev/{project}/.venv 建立虛擬環境，
不對系統或 Homebrew python 執行全域 pip install）

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

================================================================
五、README.md 內容
================================================================
# claude-workspace

Claude（Claude Code / Claude Desktop）在這台 macOS VM 上的行為紀錄與主題分類機制。

## 導覽
- `.claude/CLAUDE.md` — 主規則檔（全域規則、主題分類機制、路徑索引、Token 存取機制）
- `.claude/wrappers/` — 密鑰存取用 wrapper script（不含任何明文密鑰）
  - `run_telegram_mcp.sh` — 啟動 / 呼叫 Telegram 通知（MCP server 模式或 CLI 測試模式）
- `.claude/memory/` — 各主題細節紀錄（依需求動態新增，非固定清單）
  - `dev.md` 程式碼專案索引（跨主題共用）
  - `general.md` 尚未分類 / 雜項
- `data/` — 實際產生的資料檔，依主題分資料夾（依需求動態新增）
- `dev/` — 所有專案程式碼統一存放處，不分主題
  - `telegram-notify/` — Telegram 發送邏輯 + 專屬 venv（fastmcp）
- `logs/activity_log.jsonl` — 按時間累積的操作日誌（append-only，當月）
- `logs/archive/` — 每月封存的舊日誌

## 運作方式
`~/.claude/CLAUDE.md` 內以 `@import` 指向本資料夾的 `.claude/CLAUDE.md`，
因此不論工作目錄在哪，規則都會生效。

本機為與實體主機完全隔離的 macOS VM，Claude 在此 VM 內的終端機操作
擁有完整權限，但密鑰 / 個資不落地、對外傳送前需確認、修改 Claude Desktop
設定前需確認的規則不受影響（詳見主規則檔「終端機權限與資安邊界」）。

密鑰一律不落地於本資料夾內任何檔案，只存於 macOS Keychain，
由 `.claude/wrappers/` 內的腳本在執行當下動態取用。

================================================================
六、資料檔命名規則
================================================================
一律日期前綴：YYYY-MM-DD_主題_內容.副檔名
例：2026-08-29_tokyo_itinerary.csv
    2026-08-29_gateway_ping.log
    2026-08-29_portscan_192.168.1.0-24.txt

================================================================
七、建置流程與完成後請回報
================================================================
建置請依下列順序執行：

1. 建立「二、目錄結構」內的所有檔案與資料夾（含 .claude/wrappers/、dev/）。
2. 檢查 Keychain 是否已有 `telegram-bot-token` 與 `telegram-chat-id`
   （用 `security find-generic-password` 檢查是否能取到值，不印出明文）。
   若沒有，停止 Telegram 相關的後續步驟，告知使用者依「5.1」節先手動建立，
   其餘目錄骨架仍可先完成。
3. 若 Keychain 已備妥，依「5.3」節內容建立 `telegram_notify.py`，
   並依該節「執行環境建置步驟」建立 venv、安裝 fastmcp。
4. 依「5.2」節內容建立 / 更新 `run_telegram_mcp.sh`，並 `chmod +x`。
5. 在 `activity_log.jsonl` 寫入本次建置的紀錄（topic 填 general 與/或 dev），
   並在 `general.md`、`dev.md` 寫入對應的雜項與專案索引紀錄
   （步驟 1-4 屬於本機、可逆操作，不需向使用者逐一確認）。
6. 詢問使用者是否要建立 / 合併 `claude_desktop_config.json`
   （即使使用者已經在最初的指示中要求「完成 Telegram 機制」，
   這一步仍要單獨詢問，因為它是「五、Token 安全儲存機制」5.4 節
   明訂的硬性確認邊界）。使用者同意才動手，並事後 `chmod 600`。
   若這台機器沒有安裝 Claude Desktop，告知使用者並詢問是否要安裝；
   使用者選擇不裝也不影響其他步驟完成。
7. 詢問使用者要發送的測試訊息內容（提出一個預設文字讓使用者確認即可，
   不得未經確認就發送），確認後才透過
   `run_telegram_mcp.sh "測試訊息文字"` 實際發送一次，驗證整條鏈路
   （Keychain → wrapper → telegram_notify.py → Telegram API）真的可用。
8. 將步驟 3-7 的結果（含測試發送成功與否、Telegram API 回應的
   `ok` 欄位）追加寫入 `activity_log.jsonl` 與 `memory/dev.md`。
9. 最後向使用者回報：
   - 目錄與規則檔是否全部建立完成。
   - `run_telegram_mcp.sh` 是否已建立且具執行權限。
   - Telegram 端對端測試是否成功（附上 Telegram API 的 `ok` 欄位結果，
     不附上 token / chat id 等明文）。
   - `claude_desktop_config.json` 目前狀態（已建立 / 使用者選擇不建立 /
     Claude Desktop 未安裝）。
   - 明確提醒使用者：需重新開啟 session（或執行 `/memory` 重載）
     主規則檔才會實際生效。
================================================================
