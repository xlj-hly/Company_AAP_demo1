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
        logger.info("任务调度器初始化")
    
    def add_task(self, row):
        """添加新任务到队列"""
        try:
            # 确保时间是字符串格式
            time_str = str(row['time'])
            task_time = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
            
            # 添加调试信息：检查任务时间
            now = datetime.now()
            time_diff = task_time - now
            logger.debug(f"任务时间检查 - 当前时间: {now}, 任务时间: {task_time}, 相差: {time_diff}")
            
            # 检查是否已存在相同的任务
            task_id = f"{row['postName']}_{time_str}"
            existing_tasks = [f"{t['data']['postName']}_{t['time'].strftime('%Y-%m-%d %H:%M:%S')}" 
                             for t in self.tasks]
            
            if task_id not in existing_tasks and task_time > now:
                self.tasks.append({
                    'time': task_time,
                    'data': row
                })
                logger.info(f"成功添加新任务: {row['postName']} - {time_str}")
                logger.debug(f"当前任务队列长度: {len(self.tasks)}")
                logger.debug(f"任务队列内容: {[{t['data']['postName']: t['time']} for t in self.tasks]}")
            else:
                if task_id in existing_tasks:
                    logger.warning(f"跳过重复任务: {row['postName']} - {time_str}")
                else:
                    logger.warning(f"跳过过期任务: {row['postName']} - {time_str}")
        except Exception as e:
            logger.error(f"添加任务失败: {str(e)}")
    
    def check_pending_tasks(self):
        """检查待执行的任务"""
        try:
            current_time = datetime.now()
            logger.debug(f"检查待执行任务 - 当前时间: {current_time}")
            logger.debug(f"待执行任务数量: {len(self.tasks)}")
            
            # 找出需要执行的任务
            tasks_to_execute = []
            remaining_tasks = []
            
            # 使用集合来跟踪已处理的任务
            processed_tasks = set()
            
            for task in self.tasks:
                time_diff = task['time'] - current_time
                task_id = f"{task['data']['postName']}_{task['time']}"
                
                logger.debug(f"任务 {task['data']['postName']} 距离执行还有: {time_diff}")
                
                if task['time'] <= current_time:
                    # 检查任务是否已经处理过
                    if task_id not in processed_tasks:
                        tasks_to_execute.append(task)
                        processed_tasks.add(task_id)
                else:
                    remaining_tasks.append(task)
            
            # 更新任务队列
            self.tasks = remaining_tasks
            
            # 执行到期的任务
            for task in tasks_to_execute:
                logger.info(f"开始执行任务: {task['data']['postName']} - 计划时间: {task['time']}")
                self.run_android_automation(task['data'])
                
        except Exception as e:
            logger.error(f"检查待执行任务时出错: {str(e)}")
    
    def _convert_time_format(self, time_str):
        """转换时间格式为目录格式"""
        try:
            if isinstance(time_str, str):
                dt = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
            else:
                dt = time_str
            return dt.strftime('%Y-%m-%d_%H-%M')
        except Exception as e:
            logger.error(f"时间格式转换失败: {str(e)}")
            return None

    def run_android_automation(self, task_data):
        """执行安卓自动化任务"""
        try:
            device_id = DEVICE_MAPPING.get(task_data['postName'])
            if not device_id:
                logger.error(f"设备未找到: {task_data['postName']}")
                return False
            
            automation = AndroidAutomation(device_id)
            if not automation.connect_device():
                logger.error(f"设备连接失败: {device_id}")
                return False
            
            # 构建目录路径
            time_str = self._convert_time_format(task_data['time'])
            if not time_str:
                return False
                
            logger.debug(f"开始执行自动化任务 - 设备: {task_data['postName']}, 时间: {time_str}")
            
            base_dir = os.path.join(ROOT_DIR, task_data['postName'], time_str)
            image_dir = os.path.join(base_dir, 'img')
            
            # 获取图片路径（这是必需的）
            if not os.path.exists(image_dir):
                logger.error(f"图片目录不存在: {image_dir}")
                return False
                
            image_paths = [os.path.join(image_dir, f) for f in os.listdir(image_dir)
                          if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
            
            if not image_paths:
                logger.error("没有找到图片文件")
                return False
            
            # 读取内容文件（可选）
            content_file = os.path.join(base_dir, 'content.txt')
            title, content = ContentReader.read_content_file(content_file)
            
            # 标题和正文都允许为空
            logger.info(f"准备发布内容 - 标题: {'[无标题]' if not title else title}")
            logger.debug(f"正文长度: {len(content) if content else 0}")
            
            success, status = automation.post_content(title, content, image_paths)
            
            if success:
                logger.info(f"任务执行成功: {task_data['postName']} - {time_str}")
            else:
                logger.error(f"任务执行失败: {task_data['postName']} - {time_str} - {status}")
                
            return success
            
        except Exception as e:
            logger.error(f"自动化执行失败: {str(e)}")
            return False
