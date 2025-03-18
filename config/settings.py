#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
项目配置文件：
统一管理所有配置参数，包括路径、时间格式、任务设置等
"""

import os

# 项目根目录配置
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 基础路径配置
BASE_PATHS = {
    "EXCEL_ROOT": os.path.join("E:\\", "php", "phpstudy", "phpstudy_pro", "WWW", "company"),
    "RESOURCE_ROOT": os.path.join("E:\\", "php", "phpstudy", "phpstudy_pro", "WWW", "company", "project_1")  # 移除多余的 uploads
}

# 资源目录配置
RESOURCE_DIRS = {
    "UPLOADS": os.path.join(BASE_PATHS["RESOURCE_ROOT"], 'uploads'),
    "LOGS": os.path.join(BASE_PATHS["RESOURCE_ROOT"], 'logs'),
    "TEMP": os.path.join(BASE_PATHS["RESOURCE_ROOT"], 'temp'),
    "BACKUP": os.path.join(BASE_PATHS["RESOURCE_ROOT"], 'backup')
}

# Excel文件配置
EXCEL_CONFIG = {
    "PATH": os.path.join(BASE_PATHS["EXCEL_ROOT"], "content.xlsx"),
    "BACKUP_PATH": os.path.join(BASE_PATHS["EXCEL_ROOT"], "backup"),  # Excel备份目录
    "REQUIRED_HEADERS": ["time", "postName"],
    "LOCK_TIMEOUT": 300,
    "CHECK_INTERVAL": 2,
    "MAX_RETRIES": 3,
    "BACKUP_INTERVAL": 3600,  # Excel备份间隔（秒）
    "KEEP_BACKUP_DAYS": 7     # 保留备份天数
}

# 目录结构配置
DIRECTORY_STRUCTURE = {
    "TASK_DIR": {              # 每个任务的目录结构
        "IMG_DIR": "img",      # 图片目录名
        "CONTENT_FILE": "content.txt"  # 内容文件名
    },
    "CONTENT_TEMPLATE": "标题：\n正文：\n"  # 内容文件模板
}

# 文件路径配置
ROOT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'uploads')  # root目录
LOG_DIR = os.path.join(ROOT_DIR, "logs")  # 日志目录

# ADB配置
ADB_COMMAND = "adb"  # ADB命令路径（假设已加入系统PATH）

# 设备映射配置（逻辑名称 -> 物理设备序列号）
DEVICE_MAPPING = {
    "deviceA": "XPL5T19A28003051",  # 使用 Excel 中的设备名称
    "deviceB": "EFGH5678",
    "deviceC": "IJKL9012"
}

# 各设备的文件存储路径
DEVICE_PATHS = {
    "XPL5T19A28003051": "/storage/emulated/0/Pictures/",  # Android设备图片目录
    "EFGH5678": "/storage/emulated/0/Pictures",
    "IJKL9012": "/storage/emulated/0/Pictures"
}

# 使用新的统一日志配置
LOG_CONFIG = {
    "CONSOLE_LEVEL": "INFO",      # 控制台日志级别
    "FILE_LEVEL": "DEBUG",        # 文件日志级别
    "MAX_BYTES": 10485760,        # 单个日志文件最大大小（10MB）
    "BACKUP_COUNT": 5,            # 保留的日志文件数量
    "FORMAT": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
}

# 任务状态映射表（中英文对照）
TASK_STATUS = {
    "SUCCESS": "传输成功",
    "WAITING_CONTENT": "等待内容文件",
    "WAITING_MEDIA": "等待媒体文件",
    "NO_MEDIA_FILES": "无媒体文件",
    "DEVICE_NOT_FOUND": "设备未配置",
    "TRANSFER_INCOMPLETE": "传输未完成",
    "VERIFICATION_FAILED": "验证失败",
    "FAILED": "传输失败"
}

# 添加自动化相关配置
AUTOMATION_CONFIG = {
    "APP_PACKAGE": "com.xingin.xhs",
    "SCREEN_LOCK_PASSWORD": "000000",
    "DEFAULT_TITLE_PREFIX": "美食探索之",
    "WAIT_TIMEOUT": 5
}

# 更新任务状态
TASK_STATUS.update({
    "DEVICE_NOT_CONNECTED": "设备未连接",
    "PARTIAL_SUCCESS": "部分成功",
    "WAITING_CONTENT": "等待内容",
    "WAITING_MEDIA": "等待媒体"
})

# 任务验证配置
TASK_VALIDATION = {
    "BUFFER_MINUTES": 30,      # 任务过期缓冲时间（分钟）
    "TIME_FORMAT": "%Y-%m-%d %H:%M:%S",  # 标准时间格式
    "ALLOW_PAST_VIEW": False,  # 是否允许查看过期任务
    "MAX_FUTURE_DAYS": 30     # 最大允许提前天数
}
