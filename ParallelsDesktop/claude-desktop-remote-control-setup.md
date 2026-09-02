# Claude Code Remote Control 完整設定教學

從「VM 已安裝完成」開始，到可以用手機或另一台電腦遠端操控 VM 裡的 Claude Code 為止。

---

## 一、Windows VM 版本

### 1. 安裝 Node.js

**方法 A：官方安裝檔**
1. 瀏覽器開啟 `https://nodejs.org`
2. 下載 **LTS 版本**的 Windows Installer (.msi)
3. 執行安裝檔，一路下一步完成安裝（會自動加入系統 PATH）
4. **重新開啟 PowerShell**（必須開新視窗）

**方法 B：winget（Windows 11 內建指令安裝）**
```powershell
winget install OpenJS.NodeJS.LTS
```
裝完同樣要重開 PowerShell。

**驗證安裝：**
```powershell
node --version
npm --version
```

> 若不小心打 `node` 直接進入 REPL 模式（提示字元變成 `>`），輸入 `.exit` 離開即可回到 PowerShell。

### 2. 處理 PowerShell 執行原則限制

若執行 npm 指令出現：
```
File ...\npm.ps1 cannot be loaded because running scripts is disabled on this system.
```

**用系統管理員身分開啟 PowerShell**，執行：
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```
出現確認提示時輸入 `Y`。

> 這只允許本機腳本與已簽章的遠端腳本執行，僅套用於目前使用者帳號，不影響整台機器。

### 3. 安裝 Claude Code

```powershell
npm install -g @anthropic-ai/claude-code
```

驗證安裝：
```powershell
claude --version
```

### 4. 登入並啟動 Claude Code

切到你要讓 Claude 操作的資料夾：
```powershell
cd C:\Users\你的使用者名稱\Documents\你的專案資料夾
```

啟動：
```powershell
claude
```

第一次執行會要求透過瀏覽器完成 OAuth 登入，依畫面指示操作即可。

### 5. 啟用 Remote Control

在 Claude Code 對話中輸入：
```
/remote-control
```

或啟動時直接指定：
```powershell
claude remote-control
```

啟動後畫面會顯示一組 **session URL**，按空白鍵可顯示 **QR code** 方便手機掃描連線。

> 想讓之後每次啟動都自動開啟 Remote Control，可在 session 中執行 `/config`，將 **Enable Remote Control for all sessions** 設為 `true`。

### 6. 保持連線的注意事項

- VM 內的 PowerShell / 終端機視窗**必須保持開啟**，關閉就會斷線
- 不需要額外設定連接埠轉發、固定 IP 或 VPN，連線是透過 Anthropic 伺服器中繼

---

## 二、macOS 版本

### 1. 安裝 Node.js

**方法 A：官方安裝檔**
1. 瀏覽器開啟 `https://nodejs.org`
2. 下載 **LTS 版本**的 macOS Installer (.pkg)
3. 執行安裝，完成後開啟新的終端機視窗

**方法 B：Homebrew（推薦，若已安裝 Homebrew）**
```bash
brew install node
```

**驗證安裝：**
```bash
node --version
npm --version
```

### 2. 安裝 Claude Code

macOS 通常不需要額外調整權限，直接安裝：
```bash
npm install -g @anthropic-ai/claude-code
```

若遇到權限錯誤（`EACCES`），**不要用 `sudo npm install`**，改為修正 npm 全域目錄權限，或改用 `nvm` 管理 Node 版本（可避免權限問題）：
```bash
# 使用 nvm 安裝 Node（如果尚未安裝 nvm）
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
# 重開終端機後
nvm install --lts
nvm use --lts
npm install -g @anthropic-ai/claude-code
```

驗證安裝：
```bash
claude --version
```

### 3. 登入並啟動 Claude Code

切到工作目錄：
```bash
cd ~/Documents/你的專案資料夾
```

啟動：
```bash
claude
```

依畫面指示完成瀏覽器 OAuth 登入。

### 4. 啟用 Remote Control

對話中輸入：
```
/remote-control
```

或啟動時直接指定：
```bash
claude remote-control
```

同樣會顯示 session URL 與可掃描的 QR code。

啟用「每次自動開啟 Remote Control」：
```
/config
```
將 **Enable Remote Control for all sessions** 設為 `true`。

### 5. 保持連線的注意事項

- 終端機視窗（Terminal / iTerm2）**必須保持開啟**
- 不需要額外網路設定（連線經 Anthropic 伺服器中繼）

---

## 三、從另一台電腦或手機連線（Windows / macOS 通用）

### 網頁瀏覽器
1. 任一電腦開啟瀏覽器，前往 `https://claude.ai/code`
2. 用**與 VM 端相同的帳號**登入
3. 在 session 列表中找到該台機器的 session，點擊進入即可操作

### 手機 App
1. 開啟 Claude App（iOS / Android）
2. 進入 **Code** 分頁
3. 該機器會顯示為一張裝置卡片（綠色狀態燈 = 在線）
4. 點擊進入，選擇資料夾（新 session）或接續既有 session

---

## 四、限制與注意事項

| 項目 | 說明 |
|---|---|
| 訂閱方案 | 目前為 Research Preview，需 Claude Pro 或 Max（Max 優先開放） |
| 同時連線數 | 每個 Claude Code 實例同時只支援 **一個** 遠端連線 |
| 終端機狀態 | 來源機器的終端機視窗必須保持開啟，關閉即斷線 |
| 帳號要求 | 連線端與執行端必須是同一 Claude 帳號 |
| 網路設定 | 不需對外開 port、不需固定 IP 或 VPN |
| 危險操作確認 | Claude Code 預設會在刪除檔案等破壞性操作前要求確認，建議保留此設定以確保安全 |

---

## 五、快速指令總覽

**Windows：**
```powershell
winget install OpenJS.NodeJS.LTS
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
npm install -g @anthropic-ai/claude-code
claude remote-control
```

**macOS：**
```bash
brew install node
npm install -g @anthropic-ai/claude-code
claude remote-control
```
