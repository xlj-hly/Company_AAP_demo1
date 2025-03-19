## 🚀 專案概述 📱

一個基於 Python 的自動化內容發布系統，可通過 Excel 配置任務，自動將內容和圖片發布到小紅書平台。系統支援多裝置管理、定時發布、檔案監控等功能。

![Python版本](https://img.shields.io/badge/Python-3.9-blue?logo=python)
![授權許可](https://img.shields.io/github/license/xlj-hly/Company_AAP_demo1)
![依賴管理](https://img.shields.io/badge/dependencies-poetry-blueviolet)
![中文版](https://img.shields.io/badge/語言-繁體中文-brightgreen)

🌐 多語言支援：简体中文 | [English](README.en.md) | [繁體中文](README.zh-TW.md)

## 🛠️ 技術棧

- **🐍 Python 3.x**: 核心開發語言
- **📊 pandas**: 資料處理和 Excel 檔案操作
- **📱 uiautomator2**: Android 裝置自動化控制
- **🔍 watchdog**: 檔案系統監控
- **🧵 threading**: 多執行緒任務處理
- **📦 poetry**: 依賴管理
- **📝 logging**: 日誌管理

## 🌟 核心功能

**📋 Excel 任務管理**

- ✅ 自動監控 Excel 檔案變化
- 🔄 支援多任務併發處理
- 📅 任務狀態即時更新

**📂 檔案系統監控**

- 📁 即時監控資源檔案變化
- 📦 自動建立任務目錄結構
- 🖼️ 支援 JPG/PNG/MP4 等格式

**📱 裝置管理**

- 🔌 裝置狀態即時監控
- 📲 ADB 檔案傳輸
- 🔃 自動重連機制

**🚀 自動化發布**

- 🔓 自動解鎖裝置
- 🤖 智慧識別 UI 元素
- 📸 支援圖文混合發布

**⏰ 任務調度**

- ⏰ 定時任務執行
- 🚦 任務佇列管理
- ❗ 異常任務處理

## 📂 專案結構

```bash
project_root/
├── config/                 # 設定檔目錄
│   ├── settings.py        # 主設定檔
│   └── ignore_config.py   # 日誌過濾設定
├── core/                  # 核心模組目錄
│   ├── excel_monitor.py   # Excel監控模組
│   ├── file_handler.py    # 檔案處理模組
│   ├── task_scheduler.py  # 任務調度模組
│   └── android_automation.py # 安卓自動化模組
├── utils/                 # 工具模組目錄
│   ├── adb_utils.py      # ADB工具
│   ├── excel_utils.py    # Excel工具
│   ├── logger.py         # 日誌工具
│   └── content_reader.py # 內容讀取工具
├── uploads/              # 上傳檔案目錄
├── logs/                 # 日誌目錄
├── temp/                 # 暫存檔案目錄
└── main.py              # 程式入口
```

## ⚙️ 執行流程

**1️⃣ 初始化階段**

- 載入設定檔
- 初始化日誌系統
- 建立必要目錄結構
- 啟動檔案監控服務

**2️⃣ 任務處理流程**

```
Excel檔案變化 -> 資料驗證 -> 建立任務目錄 -> 等待資源就緒 ->
檔案傳輸 -> 更新任務狀態 -> 加入調度佇列 -> 執行自動化發布
```

**3️⃣ 自動化發布流程**

```
連接裝置 -> 解鎖螢幕 -> 啟動應用 -> 選擇相簿 ->
全部圖片 -> 輸入文案 -> 發布內容 -> 更新狀態
```

## 📦 安裝部署

**🖥️ 環境要求**

- Python 3.9.0
- ADB 工具
- Android 裝置（已開啟開發者模式）

**🛠️ 安裝步驟**

```bash
1️⃣ 克隆專案master分支
git clone -b master https://github.com/xlj-hly/Company_AAP_demo1.git

2️⃣ 建立虛擬環境
python -m venv .venv

3️⃣ 啟動虛擬環境
.\.venv\Scripts\activate

4️⃣ 安裝套件管理器
pip3 install poetry

5️⃣ 安裝依賴
poetry install
```

**📲 ADB 配置**

- 解壓 adb 壓縮檔
- 參考以下步驟配置 adb 環境變數：
  ![配置adb環境變數說明](adb/adb.png)
- 測試連接
  ![adb測試連接](adb/adb2.png)

**⚠️ 設定說明**

- 在 `config/settings.py` 中配置裝置資訊
- 在 Excel 檔案中配置發布任務
- 確保裝置已正確連接並授權

**🚀 啟動系統**

```bash
python main.py
```

⚠️ 注意事項

📊 Excel 必須包含 `time` 和 `postName` 欄位
📁 圖片需按 uploads/{任務名}/ 結構存放
📶 確保穩定的網路連接
📝 建議定期檢查日誌檔案了解系統運行狀態

## 🚨 錯誤處理

🚨 檔案操作異常處理
📲 裝置連接重試機制
📊 任務執行狀態追蹤
📝 詳細錯誤日誌記錄

## 📊 日誌管理

📉 支援多層級日誌記錄
📊 按模組分類日誌檔案
📅 可配置的日誌過濾規則
📊 自動日誌檔案輪轉
