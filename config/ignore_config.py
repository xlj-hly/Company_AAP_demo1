#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import json
import os
from utils.logger import get_logger

class IgnoreConfig:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.initialized = False
        return cls._instance
    
    def __init__(self):
        if self.initialized:
            return
            
        self.config_file = "config/ignore_rules.json"
        self.ignore_rules = self._load_rules()
        self.logger = get_logger(__name__)
        self.initialized = True
    
    def _load_rules(self):
        """加载忽略规则"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {
                "warnings": {},    # 警告级别忽略规则
                "errors": {},      # 错误级别忽略规则
                "info": {}         # 信息级别忽略规则
            }
        except Exception as e:
            # 这里不使用logger，因为可能还未初始化
            print(f"加载忽略规则失败: {str(e)}")
            return {}
    
    def save_rules(self):
        """保存忽略规则"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.ignore_rules, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"保存忽略规则失败: {str(e)}")
    
    def add_ignore_rule(self, level, message_pattern, module=None):
        """添加忽略规则"""
        if level not in self.ignore_rules:
            self.ignore_rules[level] = {}
        
        if module:
            if module not in self.ignore_rules[level]:
                self.ignore_rules[level][module] = []
            self.ignore_rules[level][module].append(message_pattern)
        else:
            if "global" not in self.ignore_rules[level]:
                self.ignore_rules[level]["global"] = []
            self.ignore_rules[level]["global"].append(message_pattern)
        
        self.save_rules()
    
    def should_ignore(self, level, message, module=None):
        """检查是否应该忽略消息"""
        if level not in self.ignore_rules:
            return False
        
        # 检查模块特定规则
        if module and module in self.ignore_rules[level]:
            for pattern in self.ignore_rules[level][module]:
                if pattern in message:
                    return True
        
        # 检查全局规则
        if "global" in self.ignore_rules[level]:
            for pattern in self.ignore_rules[level]["global"]:
                if pattern in message:
                    return True
        
        return False

# 创建全局实例
ignore_config = IgnoreConfig() 