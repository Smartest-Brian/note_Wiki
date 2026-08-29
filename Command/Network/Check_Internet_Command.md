針對 macOS 環境，我重新整理了更全面的網路管理指令指南。macOS 的核心基於 BSD，因此部分參數與 Linux (GNU) 略有不同。

---

## 1. 網路配置與介面管理 (Network Configuration)

### **networksetup**
macOS 特有的強大工具，用於修改系統偏好設定中的網路選項。
| 參數 | 說明 |
| :--- | :--- |
| `-listallnetworkservices` | 列出所有網路服務名稱（如 Wi-Fi, Ethernet）。 |
| `-getinfo <service>` | 顯示特定服務的 IP、子網路遮罩、Router 等資訊。 |
| `-setdnsservers <service> <IP>` | 設定特定服務的 DNS 伺服器地址。 |

### **ifconfig**
用於查看與暫時配置網路介面。
| 參數 | 說明 |
| :--- | :--- |
| `en0` / `en1` | macOS 常見的硬體介面名稱（通常 en0 為 Wi-Fi 或乙太網）。 |
| `up` / `down` | 啟用或停用該網路介面。 |
| `alias` | 為介面設定第二個 IP 地址。 |

---

## 2. 連線監控與埠號診斷 (Connection & Port Monitoring)

### **lsof (List Open Files)**
在 macOS 中，這是查看連線與埠號佔用最精準的工具。
> **常用組合：** `lsof -P -i -n | grep ESTABLISHED`

| 參數 | 說明 |
| :--- | :--- |
| `-i` | 僅列出網際網路相關的檔案（IPv4/IPv6 連線）。 |
| `-P` | 強制顯示埠號數字，不轉換為服務名稱（如顯示 80 而非 http）。 |
| `-n` | 不解析主機名稱（顯示 IP 而非網域名稱），大幅提升執行速度。 |
| `grep ESTABLISHED` | 過濾篩選，僅顯示目前已建立連線的狀態。 |

### **netstat**
查看網路路由表與統計數據。
| 參數 | 說明 |
| :--- | :--- |
| `-nr` | 顯示核心路由表（Routing Table），用於排查預設閘道問題。 |
| `-I <interface>` | 顯示特定介面的封包統計（如封包錯誤、流量）。 |
| `-p <protocol>` | 限制顯示特定協定（如 `tcp` 或 `udp`）。 |

---

## 3. 診斷與路徑追蹤 (Diagnostics)

### **ping**
檢查目標主機是否可達。
| 參數 | 說明 |
| :--- | :--- |
| `-c <count>` | 設定發送 Ping 封包的數量（macOS 不會自動停止）。 |
| `-a` | 有感應 Ping，當收到回應時發出系統聲。 |
| `-t <timeout>` | 設定等待回應的超時時間（秒）。 |

### **traceroute**
追蹤前往目的地經過的所有節點。
| 參數 | 說明 |
| :--- | :--- |
| `-n` | 直接顯示節點 IP，不嘗試 DNS 反查（推薦，速度快）。 |
| `-w <time>` | 設定每個節點等待回應的時間。 |
| `-m <hops>` | 設定最大跳轉次數（預設通常為 30）。 |

---

## 4. DNS 與網址查詢

### **dig (Domain Information Groper)**
查詢 DNS 紀錄的最標準工具。
| 參數 | 說明 |
| :--- | :--- |
| `ANY` / `MX` / `A` | 指定查詢類型（如郵件伺服器、IP 紀錄）。 |
| `@<IP>` | 指定向特定的 DNS 伺服器進行查詢（例如 `@8.8.8.8`）。 |
| `+trace` | 追蹤 DNS 查詢路徑，從根域名開始解析。 |

---

## 5. 程式碼範例：進階監控腳本

此腳本整合了 `lsof` 與 `netstat` 的功能，協助您快速掃描 macOS 網路狀態。

```bash
#!/bin/bash

# Define the interface for status check
INTERFACE="en0"

# Log the start of network analysis
echo "Starting network diagnostic for macOS..."

# Show established connections with process names
# -i: internet files, -n: numeric IP, -P: numeric port
echo "--- Active Connections ---"
lsof -i -n -P | grep ESTABLISHED

# Show routing table to verify Gateway
echo "--- Routing Table ---"
netstat -nr | grep default

# Log interface statistics
echo "--- Interface Stats ($INTERFACE) ---"
netstat -I $INTERFACE

# Notify completion
echo "Network check finished."
```
