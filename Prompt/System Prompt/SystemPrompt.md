讓 AI agent 讀取的 system prompt

## 🤖 AI Agent 專案行為準則 (AI Agent System Prompts)

本專案配置了嚴格的 AI 行為準則，以保護本地端開發環境並維護 Git 儲存庫的乾淨與完整。當你使用 **Claude Code**、**VS Code AI 插件 (如 Gemini / Continue)** 或其他 AI 程式碼助手時，AI 會自動讀取並遵循以下規範。

### 📁 規則檔案配置
專案根目錄下可依專案類型（Python 或 C# / .NET）配置相應的規則檔案（內容同步）：
- `system.prompt`：專門提供給 Antigravity IDE 內建 AI 引擎，檔案需放置於 `root/.antigravity` 下面。
- `.clauderules`：專門提供給 **Claude Code** 命令列工具。
- `.cursorrules` / `.clinerules`：提供給 **VS Code** 內支援專案規則的 AI 插件。

#### 📂 範本目錄說明與命名規範
在 [_.antigravity](./_.antigravity) 目錄中，提供了針對不同開發語言與環境的 System Prompt 範本。

> [!NOTE]
> **關於底線（`_`）的命名規則：**
> 範本路徑與檔案名稱中包含的底線是為了避免與實際生效的配置衝突，並提示開發者在複製使用時需進行重新命名：
> 1. **目錄重新命名**：將 `_.antigravity` 目錄複製到專案根目錄時，需將首字的底線改為點，命名為 `.antigravity`。
> 2. **檔案重新命名**：複製對應的環境範本（如 `system.prompt_python_` 或 `system.prompt_csharp_`）至該目錄下時，需將其重新命名為 `system.prompt`（即刪除後方底線及語言後綴）。

- **[system.prompt_python_](./_.antigravity/system.prompt_python_)**：適用於 Python 開發環境。
- **[system.prompt_csharp_](./_.antigravity/system.prompt_csharp_)**：適用於 C# / .NET 開發環境。

---

### 🛡️ AI 核心行為約束 (Strict Constraints)

AI 在提供程式碼或執行指令時，必須無條件遵守以下原則：

---

### 🐍 Python 環境行為約束 (Python Directives)
詳細規範見：[system.prompt_python_](./_.antigravity/system.prompt_python_)

#### 1. Python 環境隔離 (Environment Isolation)
- **禁止全域安裝：** 嚴禁在系統全域環境執行 `pip install`。
- **強制使用虛擬環境：** 所有套件安裝與 Python 執行指令必須強制指定在 `.venv` 下進行。
- **防錯機制：** 若專案內不存在 `.venv`，AI 必須先引導使用者建立，不得擅自安裝至外部環境。

#### 2. Git 倉庫安全性 (Git Repository Integrity)
- **唯一允許的 Git 指令：** 僅允許 AI 執行 `git pull`。
- **禁止擅自變更提交：** 嚴禁 AI 執行 `git add`, `git commit`, `git push`, `git reset`, `git clean` 等會改變版本歷史或刪除檔案的指令。若有需要，AI 僅能提供文字指令供開發者手動審查並執行。
- **防止未追蹤垃圾檔案：** AI 在產生任何新檔案前，必須檢查是否符合 `.gitignore` 規範，避免污染本地 Git 狀態。

#### 3. 本地環境防護 (Local Environment Protection)
- **禁止變更系統全域設定：** 嚴禁擅自執行 `apt-get`, `brew`, `choco` 等系統級安裝指令。
- **Docker 優先原則：** 當專案需要資料庫 (如 PostgreSQL) 或第三方服務 (如 Redis) 時，AI 應優先產生 `docker-compose.yml` 進行容器化隔離，而非直接安裝在開發者本機。
- **腳本等冪性 (Idempotence)：** AI 生成的任何 Shell 腳本必須確保可重複執行，且不會毀損現有資料或重複寫入設定檔（例如 `.bashrc`）。

---

### ⚡ C# / .NET 環境行為約束 (.NET Directives)
詳細規範見：[system.prompt_csharp_](./_.antigravity/system.prompt_csharp_)

#### 1. .NET 環境與相依性管理 (.NET Environment & Dependency Management)
- **僅限本地工具：** 嚴禁在全域環境安裝 .NET 全域工具 (global tools) 或 SDK。
- **專案級套件管理：** 所有套件依賴必須透過 NuGet 於專案層級 (`.csproj`) 進行管理。建議依賴時應提供 `dotnet add package <package-name>` 指令。
- **環境隔離：** AI 生成的任何腳本或指令必須限制在當前專案範圍內運作，禁止修改系統級環境變數（如 `PATH`、`DOTNET_ROOT`），除非使用者明確要求並確認。

#### 2. Git 倉庫安全性與專案整潔 (Git Operations & Project Hygiene)
- **唯一允許的 Git 指令：** 僅允許 AI 執行 `git pull`。
- **禁止變更版本歷史：** 嚴禁 AI 執行 `git add`, `git commit`, `git push`, `git checkout`, `git reset`, `git clean` 等指令。若有需要，AI 僅能提供文字指令供開發者手動審查與執行。
- **專案結構衛生：** 在生成新檔案時，應確保符合標準的 .NET 專案結構，且編譯產物（如 `/bin` 和 `/obj` 目錄）絕對不能被納入 Git 追蹤，避免在未通知使用者的情況下破壞或修改 `.gitignore`。

#### 3. 本地環境防護與安全性 (Local Environment Protection & Security)
- **禁止全域系統變更：** 未經使用者明確且高層級的確認，嚴禁執行會修改全域系統配置、登錄檔 (Registry) 或全域套件管理器 (如 `apt-get`, `brew`, `choco`, `winget`) 的指令。
- **容器化優先：** 針對基礎設施相依性（如 SQL Server, Redis, RabbitMQ），應優先產生 `docker-compose.yml` 或本地 `container-manifest`，以確保開發環境乾淨並具備環境一致性。
- **指令等冪性 (Idempotence)：** AI 生成的任何 CLI 指令（如 `dotnet ef migrations add`, `dotnet build`, `dotnet run`）或 Shell 腳本必須可重複執行，且不會損壞專案狀態或配置文件。
- **敏感資訊安全防護：** 嚴禁在程式碼範例中寫入任何金鑰 (Secrets)、API Key 或連線字串。應引導並建議使用者使用 `appsettings.Development.json` 或 `User Secrets` (`dotnet user-secrets`) 進行本地端配置。