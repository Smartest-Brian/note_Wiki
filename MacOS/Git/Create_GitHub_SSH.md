## 1. 檢查 Mac 是否已有 SSH Key
首先，我們要確認電腦裡是否已經存在舊的金鑰。

1. 打開 **Terminal** (終端機)。
2. 輸入以下指令查看檔案列表：
   ```bash
   ls -al ~/.ssh
   ```
3. **結果判斷：**
   * 如果看到 `id_rsa.pub`、`id_ecdsa.pub` 或 `id_ed25519.pub`，代表你**已經有**金鑰了。
   * 如果顯示 `No such file or directory` 或沒有上述檔案，請繼續執行步驟 2。

---

## 2. 產生新的 SSH Key
如果你沒有金鑰，請執行以下指令（請將 Email 換成你的 GitHub 帳號）：

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

* 系統會詢問 "Enter file in which to save the key"，直接按 **Enter** 即可（預設路徑）。
* 接著會詢問 "Enter passphrase"，這是額外的密碼保護，可以直接按 **Enter** 跳過（若追求方便）或設定一組密碼。

---

## 3. 將 SSH Key 加入 GitHub 帳號
產生金鑰後，你需要告訴 GitHub 這台電腦是「自己人」。

1. **複製公鑰內容：**
   ```bash
   pbcopy < ~/.ssh/id_ed25519.pub
   ```
2. **前往 GitHub 設定：**
   * 登入 GitHub，點擊右上角頭像 -> **Settings**。
   * 左側選單找到 **SSH and GPG keys**。
   * 點擊 **New SSH key**。
3. **貼上金鑰：**
   * **Title**: 給這台電腦起個名字（例如：My MacBook Pro）。
   * **Key type**: 保持預設。
   * **Key**: 直接貼上（Command + V）。
   * 點擊 **Add SSH key**。

---

## 4. 測試連線
設定完成後，測試是否連線成功：

```bash
ssh -T git@github.com
```
* 如果看到 `Hi username! You've successfully authenticated...`，就代表成功了！

---

## 5. 使用 SSH Clone 專案
之後在 GitHub 專案頁面點擊 **Code** 按鈕時，請切換到 **SSH** 頁籤並複製網址。



**指令範例：**
```bash
# Clone the repository using SSH URL
git clone git@github.com:user-name/repo-name.git
```

---

### 常見問答小撇步
> **Q: 為什麼我設定了還是要輸密碼？**
> A: 如果你當初在 `ssh-keygen` 時有設定 passphrase，每次使用時系統會詢問。若想省去麻煩，可以將金鑰加入 Mac 的 Keychain：
> ```bash
> # Add SSH key to Apple Keychain
> ssh-add --apple-use-keychain ~/.ssh/id_ed25519
> ```
