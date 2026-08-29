# Application 官網下載安裝和設定

### 基本

Google Chrome <https://www.google.com/intl/zh-TW/chrome/>

Raycast <https://www.raycast.com/>

Rectangle <https://rectangleapp.com/>

Git <https://git-scm.com/>
```bash
# 可以直接使用 xcode 安裝
$ xcode-select --install
```

---

### 訂閱

Setapp <https://setapp.com/> ⚙︎ [App List](Settings/Setapp/apps.md)

NordVPN <https://nordvpn.com/zh-tw/download/mac/>

Parallels <https://www.parallels.com/products/desktop/>

---

### Tool

Sourcetree <https://www.sourcetreeapp.com/>

Postman <https://www.postman.com/downloads/>

Docker Desktop <https://www.docker.com/products/docker-desktop/>

Sublime Text <https://www.sublimetext.com/>

DBeaver <https://dbeaver.io/download/>

Google Chrome Remote Desktop <https://remotedesktop.google.com/access>

Warp <https://www.warp.dev/mac-terminal>

Tree [使用macOS內建find](Settings/Tree/setting.md)

Logi Options+ <https://www.logitech.com/zh-tw/software/logi-options-plus>

---

### IDE

Visual Studio Code <https://code.visualstudio.com/>
```bash
# 加到環境變數
$ echo 'export PATH="$PATH:/Applications/Visual Studio Code.app/Contents/Resources/app/bin"' >> ~/.zshrc
$ source ~/.zshrc

# 開啟範例
$ code
$ code .
```


Antigravity IDE <https://antigravity.google/download>

Pycharm <https://www.jetbrains.com/pycharm/>

Rider <https://www.jetbrains.com/rider/>
```bash
# 如果使用 Rider 安裝 SDK .net 路徑會在這裡，使用方法如下
$ /Users/{UserName}/.dotnet/dotnet new sln -n SolutionName

# 加到環境變數
$ echo 'export DOTNET_ROOT=$HOME/.dotnet' >> ~/.zshrc
$ echo 'export PATH=$PATH:$HOME/.dotnet' >> ~/.zshrc
$ echo 'export PATH=$PATH:$HOME/.dotnet/tools' >> ~/.zshrc
$ source ~/.zshrc
```


---

### Font

JetBrains Mono <https://www.jetbrains.com/lp/mono/>

1.  前往 [JetBrains Mono 官網](https://www.jetbrains.com/lp/mono/)。
2.  點擊 **Download Font** 按鈕下載壓縮檔。
3.  解壓縮後，進入 `fonts/ttf` 資料夾。
4.  選取所有的 `.ttf` 檔案，**連按兩下 (Double Click)**。
5.  macOS 會跳出「字體簿 (Font Book)」視窗，點擊 **安裝字體 (Install Font)** 即可。
