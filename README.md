## 🚀 项目概述 📱

一个基于 Python 的自动化内容发布系统，可以通过 Excel 配置任务，自动将内容和图片发布到小红书平台。系统支持多设备管理、定时发布、文件监控等功能。

![Python版本](https://img.shields.io/badge/Python-3.9-blue?logo=python)
![许可证](https://img.shields.io/github/license/xlj-hly/Company_AAP_demo1)
![依赖管理](https://img.shields.io/badge/dependencies-poetry-blueviolet)
![中文版](https://img.shields.io/badge/语言-简体中文-brightgreen)

🌐 多语言支持：简体中文 | [English](README.en.md) | [繁體中文](README.zh-TW.md)

## 🛠️ 技术栈

- **🐍 Python 3.9**: 核心开发语言
- **📊 pandas**: 数据处理和 Excel 文件操作
- **📱 uiautomator2**: Android 设备自动化控制
- **🔍 watchdog**: 文件系统监控
- **🧵 threading**: 多线程任务处理
- **📦 poetry**: 依赖管理
- **📝 logging**: 日志管理

## 🌟 核心功能

**📋 Excel 任务管理**

- ✅ 自动监控 Excel 文件变化
- 🔄 支持多任务并发处理
- 📅 任务状态实时更新

**📂 文件系统监控**

- 📁 实时监控资源文件变化
- 📦 自动创建任务目录结构
- 🖼️ 支持 JPG/PNG/MP4 等格式

**📱 设备管理**

- 🔌 设备状态实时监控
- 📲 ADB 文件传输
- 🔃 自动重连机制

**🚀 自动化发布**

- 🔓 自动解锁设备
- 🤖 智能识别 UI 元素
- 📸 支持图文混合发布

**⏰ 任务调度**

- ⏰ 定时任务执行
- 🚦 任务队列管理
- ❗ 异常任务处理

## 📂 项目结构

```bash
project_root/
├── config/                 # 配置文件目录
│   ├── settings.py        # 主配置文件
│   └── ignore_config.py   # 日志过滤配置
├── core/                  # 核心模块目录
│   ├── excel_monitor.py   # Excel监控模块
│   ├── file_handler.py    # 文件处理模块
│   ├── task_scheduler.py  # 任务调度模块
│   └── android_automation.py # 安卓自动化模块
├── utils/                 # 工具模块目录
│   ├── adb_utils.py      # ADB工具
│   ├── excel_utils.py    # Excel工具
│   ├── logger.py         # 日志工具
│   └── content_reader.py # 内容读取工具
├── uploads/              # 上传文件目录
├── logs/                 # 日志目录
├── temp/                 # 临时文件目录
└── main.py              # 程序入口
```

## ⚙️ 运行流程

**1️⃣ 初始化阶段**

- 加载配置文件
- 初始化日志系统
- 创建必要目录结构
- 启动文件监控服务

**2️⃣ 任务处理流程**

```
Excel文件变化 -> 数据验证 -> 创建任务目录 -> 等待资源就绪 ->
文件传输 -> 更新任务状态 -> 加入调度队列 -> 执行自动化发布
```

**3️⃣ 自动化发布流程**

```
连接设备 -> 解锁屏幕 -> 启动应用 -> 选择相册 ->
全部图片 -> 输入文案 -> 发布内容 -> 更新状态
```

## 📦 安装部署

**🖥️ 环境要求**

- Python 3.9.0
- ADB 工具
- Android 设备（已开启开发者模式）

**🛠️ 安装步骤**

```bash
1️⃣ 克隆项目master分支
git clone -b master https://github.com/xlj-hly/Company_AAP_demo1.git

2️⃣ 创建虚拟环境
python -m venv .venv

3️⃣ 启动虚拟环境
.\.venv\Scripts\activate

4️⃣ 安装包管理器
pip3 install poetry

5️⃣ 安装依赖
poetry install
```

**📲 ADB 配置**

- 解压 adb 压缩包
- 参考以下步骤配置 adb 环境变量：
  ![配置adb环境变量说明](adb/adb.png)
- 测试连接
  ![adb测试连接](adb/adb2.png)

**⚠️ 配置说明**

- 在 `config/settings.py` 中配置设备信息
- 在 Excel 文件中配置发布任务
- 确保设备已正确连接并授权

**🚀 启动系统**

```bash
python main.py
```

## ⚠️ 注意事项

📊 Excel 必须包含 `time` 和 `postName` 列
📁 图片需按 uploads/{任务名}/ 结构存放
📶 确保稳定的网络连接
📝 建议定期检查日志文件了解系统运行状态

## 🚨 错误处理

🚨 文件操作异常处理
📲 设备连接重试机制
📊 任务执行状态跟踪
📝 详细错误日志记录

## 📊 日志管理

📉 支持多级别日志记录
📊 按模块分类日志文件
📅 可配置的日志过滤规则
📊 自动日志文件轮转
