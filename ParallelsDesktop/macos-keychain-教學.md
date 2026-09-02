# macOS Keychain 密鑰管理教學

以 LINE Bot 的 `LINE_CHANNEL_ACCESS_TOKEN` 與 `LINE_USER_ID` 為例，說明如何用 macOS 內建的 Keychain 安全地儲存密鑰，並讓程式（例如 MCP server）在執行時動態取用，避免明文 token 長期躺在任何設定檔或程式碼裡。

---

## 一、基本觀念

Keychain 是 macOS 內建的加密憑證儲存系統，本身受你的登入密碼 / Touch ID 保護。用 `security` 指令可以在 Terminal 對它做存取、查詢、刪除等操作。

核心概念只有三個：

| 參數 | 意義 |
|------|------|
| `-a`（account） | 通常填 `$USER`，代表這筆密鑰屬於哪個系統帳號 |
| `-s`（service） | 這筆密鑰的「名字」，之後查找時要用同樣的名字 |
| `-w`（password/data） | 實際要存的內容（token、id 等） |

---

## 二、存入密鑰

```bash
security add-generic-password -a "$USER" -s "LINE_CHANNEL_ACCESS_TOKEN" -w "你的token"
security add-generic-password -a "$USER" -s "LINE_USER_ID" -w "你的id"
```

執行後這兩筆資料就加密存在 Keychain 裡，**不會**出現在任何檔案、shell history 以外的地方（建議存完後清一下 shell history，見第七節）。

> 如果同一個 `-s` 名稱已經存在，這行指令會報錯 `SecKeychainAddGenericPassword: already exists`。要更新請看第五節。

---

## 三、驗證有沒有存成功

```bash
security find-generic-password -a "$USER" -s "LINE_CHANNEL_ACCESS_TOKEN"
```

這樣只會顯示這筆密鑰的「屬性資訊」（帳號、服務名稱、建立時間等），**不會**直接顯示密碼內容，這是正常的、也是安全設計的一部分。

---

## 四、真正取出明文內容

只有加上 `-w` 才會印出密碼本身：

```bash
security find-generic-password -a "$USER" -s "LINE_CHANNEL_ACCESS_TOKEN" -w
```

**第一次**執行時，如果是別的程式（非 `security` 指令本身，例如某個 script）去呼叫底層 API 讀取，macOS 會跳出系統彈窗，詢問是否允許該程式存取。用 Terminal 直接下 `security` 指令通常不會跳窗，因為這是系統內建工具。

---

## 五、更新已存在的密鑰

Keychain 不支援「覆蓋寫入」，要嘛用 `-U` 參數就地更新，要嘛先刪除再新增：

```bash
# 方法一：就地更新（推薦）
security add-generic-password -a "$USER" -s "LINE_CHANNEL_ACCESS_TOKEN" -w "新的token" -U

# 方法二：先刪除再新增
security delete-generic-password -a "$USER" -s "LINE_CHANNEL_ACCESS_TOKEN"
security add-generic-password -a "$USER" -s "LINE_CHANNEL_ACCESS_TOKEN" -w "新的token"
```

---

## 六、刪除密鑰

```bash
security delete-generic-password -a "$USER" -s "LINE_CHANNEL_ACCESS_TOKEN"
security delete-generic-password -a "$USER" -s "LINE_USER_ID"
```

---

## 七、存完密鑰後清一下 shell history（重要）

因為指令本身包含明文 token，會被記錄在 shell 的歷史紀錄檔（`~/.zsh_history` 或 `~/.bash_history`）裡，建議：

```bash
# 找出剛剛那幾行
history | tail -5

# 刪除特定行號（zsh 範例，數字換成實際行號）
history -d 1234

# 或比較簡單粗暴：直接清空當前 session 的 history
history -c
```

如果你用的是 zsh 且想避免以「空白開頭的指令」被記錄，可以在 `~/.zshrc` 加：

```bash
setopt HIST_IGNORE_SPACE
```

之後在指令前面加一個空白（` security add-generic-password ...`）就不會被記進 history。

---

## 八、寫 wrapper script 動態取用（實際串接的關鍵一步）

單獨存進 Keychain 還不夠，你的程式（例如 LINE Bot MCP server）並不知道去哪裡拿。做法是寫一個 wrapper script，啟動時先去 Keychain 撈值、export 成環境變數，再啟動真正的程式。

**建議存放路徑：**
```
~/claude-workspace/.claude/wrappers/start-line-bot.sh
```

**內容：**
```bash
#!/bin/bash
# start-line-bot.sh

export LINE_CHANNEL_ACCESS_TOKEN=$(security find-generic-password -a "$USER" -s "LINE_CHANNEL_ACCESS_TOKEN" -w)
export LINE_USER_ID=$(security find-generic-password -a "$USER" -s "LINE_USER_ID" -w)

if [ -z "$LINE_CHANNEL_ACCESS_TOKEN" ] || [ -z "$LINE_USER_ID" ]; then
  echo "錯誤：無法從 Keychain 讀取必要的環境變數" >&2
  exit 1
fi

exec node /path/to/your/line-bot-mcp-server/index.js
```

**給執行權限：**
```bash
chmod +x ~/claude-workspace/.claude/wrappers/start-line-bot.sh
```

之後不論是手動執行、排程執行，還是被 Claude Desktop 的 MCP 設定呼叫，都是呼叫這支 script，而不是直接把 token 寫死在任何地方。

---

## 九、串進 Claude Desktop 的 MCP 設定（如果有用到）

設定檔位置：
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**錯誤示範**（明文外露）：
```json
{
  "mcpServers": {
    "line-bot": {
      "command": "node",
      "args": ["/path/to/line-bot-mcp-server/index.js"],
      "env": {
        "LINE_CHANNEL_ACCESS_TOKEN": "明文token寫在這裡",
        "LINE_USER_ID": "明文id寫在這裡"
      }
    }
  }
}
```

**正確做法**（指向 wrapper）：
```json
{
  "mcpServers": {
    "line-bot": {
      "command": "/Users/你的帳號/claude-workspace/.claude/wrappers/start-line-bot.sh"
    }
  }
}
```

改完後重啟 Claude Desktop，第一次啟動 MCP server 時，如果 macOS 跳出「是否允許存取 Keychain 項目」的彈窗，選「一律允許（Always Allow）」即可，之後不會再跳。

建議順手把設定檔本身權限也收緊：
```bash
chmod 600 ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

---

## 十、常見問題

**Q: 別人偷到我的 Mac 帳號密碼，Keychain 裡的東西會外洩嗎？**
會。Keychain 的保護前提是「你的登入帳號沒有被攻破」。它防的是「明文散落在檔案裡、被程式或雲端同步意外掃到」這類風險，不是萬能保險箱。

**Q: 任何程式都能讀我 Keychain 裡的密鑰嗎？**
不一定。第一次有新程式嘗試存取時，系統會跳授權彈窗讓你確認；用 `security` 指令在 Terminal 下通常不會跳窗，因為是你本人主動操作。若想更嚴謹地限制「只有某支程式能免密碼存取」，可以在 `add-generic-password` 時加 `-T /path/to/允許的程式`。

**Q: token 要不要定期更換？**
建議會。萬一哪天真的外洩，換過的 token 能縮短被濫用的時間窗。更換時走第五節「更新已存在的密鑰」即可，不需要動到 wrapper script。

---

## 十一、指令總覽（速查）

```bash
# 存入
security add-generic-password -a "$USER" -s "SERVICE_NAME" -w "值"

# 查屬性（不顯示明文）
security find-generic-password -a "$USER" -s "SERVICE_NAME"

# 查明文
security find-generic-password -a "$USER" -s "SERVICE_NAME" -w

# 更新
security add-generic-password -a "$USER" -s "SERVICE_NAME" -w "新值" -U

# 刪除
security delete-generic-password -a "$USER" -s "SERVICE_NAME"
```
