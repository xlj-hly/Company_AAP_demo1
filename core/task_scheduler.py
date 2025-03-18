#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Author  ：何
@Project ：project_1 
@File    ：task_scheduler.py.py
@IDE     ：PyCharm 
@Date    ：2025/3/17 01:26 
"""

"""
任务调度模块功能：
1. 管理定时任务队列
2. 添加未来执行任务
3. 提供安卓自动化接口
"""

from datetime import datetime
import time
from utils.logger import get_logger
import os
from core.android_automation import AndroidAutomation
from utils.content_reader import ContentReader
from config.settings import ROOT_DIR, DEVICE_MAPPING

logger = get_logger(__name__)

class TaskScheduler:
    def __init__(self):
        self.tasks = []  # 任务队列
    
    def add_task(self, row):
        """添加新任务到队列"""
        try:
            # 确保时间是字符串格式
            time_str = str(row['time'])
            task_time = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
            
            if task_time > datetime.now():
                self.tasks.append({
                    'time': task_time,
                    'data': row
                })
                logger.info(f"添加新任务: {row['postName']} - {time_str}")
        except Exception as e:
            logger.error(f"添加任务失败: {str(e)}")
    
    def run_android_automation(self, task_data):
        """执行安卓自动化任务"""
        try:
            device_id = DEVICE_MAPPING.get(task_data['postName'])
            if not device_id:
                logger.error(f"设备未找到: {task_data['postName']}")
                return False
            
            automation = AndroidAutomation(device_id)
            if not automation.connect_device():
                return False
            
            # 构建目录路径
            time_str = self._convert_time_format(task_data['time'])
            base_dir = os.path.join(ROOT_DIR, task_data['postName'], time_str)
            
            # 获取图片路径
            image_dir = os.path.join(base_dir, 'img')
            image_paths = [os.path.join(image_dir, f) for f in os.listdir(image_dir)
                          if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
            
            # 读取内容文件
            content_file = os.path.join(base_dir, 'content.txt')
            if not os.path.exists(content_file):
                logger.error(f"内容文件不存在: {content_file}")
                return False
            
            # 读取标题和正文
            title, content = ContentReader.read_content_file(content_file)
            if not title or not content:
                logger.error("读取标题或正文失败")
                return False
            
            logger.info(f"准备发布内容 - 标题: {title}")
            success, status = automation.post_content(title, content, image_paths)
            return success
        
        except Exception as e:
            logger.error(f"自动化执行失败: {str(e)}")
            return False
