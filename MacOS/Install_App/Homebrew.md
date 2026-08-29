# Homebrew 安裝跟套件管理

https://brew.sh/

```bash
$ /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

```text
安裝完console會顯示，照著執行。

==> Next steps:
- Run these commands in your terminal to add Homebrew to your PATH:
    echo >> /Users/brian/.zprofile
    echo 'eval "$(/opt/homebrew/bin/brew shellenv zsh)"' >> /Users/brian/.zprofile
    eval "$(/opt/homebrew/bin/brew shellenv zsh)"
- Run brew help to get started
...
```

# Basic command

```bash
# 搜尋套件
$ brew search <name>

# 安裝套件
$ brew install <name>

# 安裝清單
$ brew list -l

# 更新 Homebrew 本身（及獲取最新套件清單）
$ brew update

# 升級所有已安裝套件
$ brew upgrade

# 查看哪些套件有新版本
$ brew outdated

# 清理舊版本的安裝檔（釋放硬碟空間）
$ brew cleanup

# 檢查系統環境（會提示潛在問題與修復建議）
$ brew doctor

# 查看套件詳細資訊（如依賴關係、安裝路徑）
$ brew info <name>

# 常用
$ brew update && brew upgrade && brew cleanup
```

# Install Formulae

```bash
# 好用套件
$ brew install git tree
```

# Remove  Formulae

```bash
# 顯示安裝清單
$ brew list -l

# 卸載軟體
$ brew uninstall <name>

# 清理不再需要的依賴套件 (Dependencies)
$ brew autoremove

# 清理下載的快取檔案 (Cache files)
$ brew cleanup
```


# Install Casks

```bash
# 好用工具
$ brew install --cask raycast rectangle google-chrome warp

# 開發 IDE
$ brew install --cask visual-studio-code
$ brew install --cask postman
$ brew install --cask sourcetree
$ brew install --cask docker-desktop
$ brew install --cask sublime-text
$ brew install --cask antigravity
$ brew install --cask dbeaver-community

# 有訂閱的
$ brew install --cask setapp
$ brew install --cask nordvpn
$ brew install --cask parallels
$ brew install --cask pycharm
$ brew install --cask jetbrains-rider

# 字體
# JetBrains Mono，等同於官網下載解壓縮後用「字體簿 (Font Book)」安裝 .ttf 檔案
$ brew install --cask font-jetbrains-mono

### Other ###
# Logi Options+
$ brew install --cask logi-options-plus

# Google Chrome Remote Desktop（預設不安裝，需要遠端桌面功能時再手動執行）
# $ brew install --cask chrome-remote-desktop-host
 
```

# 一次安裝全部（懶人版）必裝

```bash
brew install --cask raycast rectangle google-chrome warp visual-studio-code postman sourcetree docker-desktop sublime-text dbeaver-community setapp nordvpn font-jetbrains-mono
```

# 一次安裝全部（懶人版）選配

```bash
brew install --cask antigravity parallels logi-options-plus pycharm jetbrains-rider
```

# Remove Casks

```bash
# 如果你想用 Homebrew 卸載 app 並清乾淨所有暫存檔，建議使用
$ brew uninstall --cask --zap <name>

# Force uninstall and zap the application
$ brew uninstall --cask --zap --force <name>
```

# 管理 Brewfile
```bash
# 輸出備份：將目前電腦已安裝的所有軟體紀錄成一個 Brewfile
$ brew bundle dump

# 自動安裝：讀取當前目錄下的 Brewfile 並安裝所有缺失的軟體。
$ brew bundle

# 檢查狀態：檢查目前的環境是否與 Brewfile 一致。
$ brew bundle check

# 強制一致：移除「不在」Brewfile 清單中的所有軟體 (慎用)。
$ brew bundle cleanup

```


