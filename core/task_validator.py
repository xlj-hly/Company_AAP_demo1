#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
任务验证模块：
负责处理所有与任务时效性和有效性相关的验证逻辑。

主要功能：
1. 任务时效性检查
2. 任务修改权限验证
3. 统一的时间格式处理
"""

from datetime import datetime, timedelta
from utils.logger import get_logger
from config.settings import TASK_VALIDATION

logger = get_logger(__name__)

class TaskValidator:
    def __init__(self):
        """
        初始化任务验证器
        使用配置文件中的验证参数
        """
        self.time_format = TASK_VALIDATION['TIME_FORMAT']
        self.buffer_minutes = TASK_VALIDATION['BUFFER_MINUTES']
        
    def is_task_valid(self, task_time):
        """
        检查任务是否有效
        
        规则：
        1. 未来任务：可以修改和执行
        2. 当前任务：可以执行，不可修改
        3. 过期任务：保留记录，不执行
        """
        try:
            if isinstance(task_time, str):
                task_time = datetime.strptime(str(task_time).strip(), self.time_format)
            
            now = datetime.now()
            
            # 未来任务
            if task_time > now:
                return True
            
            # 当前任务（考虑缓冲时间）
            buffer_time = now - timedelta(minutes=self.buffer_minutes)
            if task_time > buffer_time:
                return True
                
            # 过期任务
            return False
            
        except Exception as e:
            logger.error(f"任务时间验证失败: {str(e)}")
            return False
    
    def can_modify_task(self, task_time):
        """
        检查任务是否可以修改（仅未来任务可修改）
        
        Args:
            task_time: 任务执行时间
            
        Returns:
            bool: 是否可以修改任务
        """
        return self.is_task_valid(task_time)
    
    def parse_time(self, time_str):
        """
        解析时间字符串为datetime对象
        
        Args:
            time_str: 时间字符串
            
        Returns:
            datetime: 解析后的时间对象，解析失败返回None
        """
        try:
            return datetime.strptime(str(time_str).strip(), self.time_format)
        except ValueError as e:
            logger.error(f"时间格式解析失败: {str(e)}")
            return None 