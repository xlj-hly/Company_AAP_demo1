#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Author  ：何
@Project ：project_1 
@File    ：logger.py.py
@IDE     ：PyCharm 
@Date    ：2025/3/17 01:35 
"""

"""
日志配置模块功能：
1. 统一日志格式
2. 文件与控制台双输出
3. 按模块分日志文件
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
import os
from config.settings import LOG_CONFIG, LOG_DIR

class FilteredHandler(logging.StreamHandler):
    def __init__(self, ignore_rules=None):
        super().__init__(sys.stdout)
        self.ignore_rules = ignore_rules or {}

    def emit(self, record):
        """实现emit方法"""
        try:
            if self.should_ignore(record):
                return
            super().emit(record)
        except Exception:
            self.handleError(record)
    
    def should_ignore(self, record):
        level = record.levelname.lower()
        message = record.getMessage()
        module = record.name
        
        rules = self.ignore_rules
        if not rules:
            return False
            
        # 检查模块特定规则
        if module in rules.get(level, {}):
            for pattern in rules[level][module]:
                if pattern in message:
                    return True
        
        # 检查全局规则
        if "global" in rules.get(level, {}):
            for pattern in rules[level]["global"]:
                if pattern in message:
                    return True
        
        return False

def get_logger(name):
    """获取模块专用日志记录器"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # 如果已经有处理器，则不重复添加
    if logger.handlers:
        return logger
    
    # 创建日志目录
    os.makedirs(LOG_DIR, exist_ok=True)
    
    try:
        # 尝试导入ignore_config
        from config.ignore_config import ignore_config
        console_handler = FilteredHandler(ignore_config.ignore_rules)
    except ImportError:
        # 如果无法导入，使用基本的StreamHandler
        console_handler = logging.StreamHandler(sys.stdout)
    
    console_handler.setLevel(LOG_CONFIG['CONSOLE_LEVEL'])
    console_formatter = logging.Formatter(LOG_CONFIG['FORMAT'])
    console_handler.setFormatter(console_formatter)
    
    # 文件处理器
    file_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, f"{name}.log"),
        maxBytes=LOG_CONFIG['MAX_BYTES'],
        backupCount=LOG_CONFIG['BACKUP_COUNT'],
        encoding='utf-8'
    )
    file_handler.setLevel(LOG_CONFIG['FILE_LEVEL'])
    file_formatter = logging.Formatter(LOG_CONFIG['FORMAT'])
    file_handler.setFormatter(file_formatter)
    
    # 添加处理器
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger
