# Git Submodule Commands Guide

以下為 Git Submodule 常用更新與狀態查詢指令整理：

## 1. Update and Merge Submodules
此指令會將子模組更新至 `.gitmodules` 中設定的遠端追蹤分支的最新版本，並將變更合併（merge）到子模組當前的本地分支中，避免子模組進入 Detached HEAD 狀態。

```bash
git submodule update --remote --merge

```

## 2. Fetch Submodule Updates Silently

此指令用於從遠端下載主專案與所有子模組的最新的 Commit 與參考紀錄（refs），但不會更改目前的工作目錄或更新檔案內容。

```bash
git fetch --recurse-submodules --quiet

```

## 3. Update All Submodules Recursively

此指令用於將所有子模組（包含巢狀子模組）更新至遠端追蹤分支的最新版本。執行後預設會讓子模組處於 Detached HEAD 狀態。

```bash
git submodule update --remote --recursive

```

## 4. Check Submodule Status and Branches

此腳本用於遞迴查詢所有子模組的狀態。會優先嘗試讀取子模組當前的本地分支名稱；若處於 Detached HEAD 狀態，則顯示當前的短 Commit Hash。

```bash
git submodule foreach --quiet --recursive 'branch=$(git symbolic-ref --short HEAD 2>/dev/null) || branch=$(git rev-parse --short HEAD); echo "/$displaypath ($branch)"'
```
