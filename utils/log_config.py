#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from config.settings import LOG_CONFIG, LOG_DIR

class FilteredHandler(logging.Handler):
    def __init__(self, ignore_rules=None):
        super().__init__()
        self.ignore_rules = ignore_rules or {}

    def emit(self, record):
        if self.should_ignore(record):
            return
        super().emit(record)
    
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

def setup_logger(name):
    """设置日志记录器"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # 如果已经有处理器，则不重复添加
    if logger.handlers:
        return logger
    
    # 创建日志目录
    os.makedirs(LOG_DIR, exist_ok=True)
    
    # 控制台处理器
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