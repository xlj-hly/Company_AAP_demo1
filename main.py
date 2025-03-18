#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Author  ：何
@Project ：project_1 
@File    ：main.py.py
@IDE     ：PyCharm 
@Date    ：2025/3/17 01:35 
"""

"""
主程序模块功能：
1. 整合各模块功能
2. 信号处理
3. 主循环控制
4. 状态更新管理
"""

from core.excel_monitor import ExcelMonitor
from core.task_scheduler import TaskScheduler
from core.file_handler import FileHandler
from config.settings import (
    RESOURCE_DIRS,
    EXCEL_CONFIG,
    TASK_STATUS,
    ADB_COMMAND
)
import pandas as pd
import time
import signal
import sys
import os
from utils.logger import get_logger
import subprocess
from utils.excel_utils import ExcelUtils
from core.task_validator import TaskValidator

logger = get_logger(__name__)

class Application:
    def __init__(self):
        # 初始化核心组件
        self.excel_monitor = ExcelMonitor(
            EXCEL_CONFIG['PATH'],
            EXCEL_CONFIG['REQUIRED_HEADERS']
        )
        self.task_scheduler = TaskScheduler()
        self.file_handler = FileHandler(RESOURCE_DIRS['UPLOADS'])
        self.running = True  # 运行状态标志
        
        # 注册资源变化处理器
        self.excel_monitor.add_resource_handler(self.handle_resource_change)
    
    def signal_handler(self, signum, frame):
        """处理系统终止信号"""
        logger.info("收到终止信号，正在关闭服务...")
        self.running = False
        self.excel_monitor.stop_monitoring()
        sys.exit(0)
    
    def update_excel_status(self, row_index, status):
        """更新Excel中的任务状态"""
        try:
            # 读取当前Excel内容
            df = pd.read_excel(EXCEL_CONFIG['PATH'])
            
            # 更新状态
            if 'status' not in df.columns:
                df['status'] = pd.Series(dtype='str')
            df.at[row_index, 'status'] = str(status)
            
            # 安全写入Excel
            if ExcelUtils.safe_write_excel(EXCEL_CONFIG['PATH'], df):
                logger.info(f"更新任务状态成功: 行 {row_index + 1}, 状态 {status}")
                return True
            else:
                logger.error("更新Excel状态失败：文件可能被长时间占用")
                return False
                
        except Exception as e:
            logger.error(f"更新Excel状态时发生错误: {str(e)}")
            return False
    
    def check_device_status(self, device_id):
        """检查设备状态"""
        try:
            command = [ADB_COMMAND, 'get-state']
            result = subprocess.run(command, capture_output=True, text=True)
            return result.stdout.strip() == 'device'
        except Exception:
            return False
    
    def process_task(self, index, row, validator):
        """
        处理单个任务
        
        处理流程：
        1. 验证任务时效性
        2. 检查任务状态
        3. 执行文件传输
        4. 更新任务状态
        
        Args:
            index (int): 任务在Excel中的索引
            row (Series): 任务数据
            validator (TaskValidator): 任务验证器实例
        """
        try:
            # 添加任务处理日志
            logger.info(f"处理任务: {row['postName']} - {row['time']}")
            
            if not validator.can_modify_task(row['time']):
                logger.debug(f"跳过已过期任务: {row['postName']} - {row['time']}")
                return
            
            current_status = str(row.get('status', '')).strip()
            if current_status == 'SUCCESS':
                logger.debug(f"跳过已完成任务: {row['postName']} - {row['time']}")
                return
            
            # 执行文件传输
            success, status = self.file_handler.transfer_images(
                row['postName'],
                row['time']
            )
            
            # 输出传输结果
            logger.info(f"传输结果: {success} - {status}")
            
            # 根据传输结果更新状态
            if status == "SUCCESS":
                self.update_excel_status(index, TASK_STATUS[status])
                self.task_scheduler.add_task(row)
            elif status in ["DEVICE_NOT_FOUND", "TRANSFER_INCOMPLETE"]:
                self.update_excel_status(index, TASK_STATUS[status])
            # 其他状态（等待资源就绪）不更新Excel
            
        except Exception as e:
            logger.error(f"处理任务出错: {str(e)}")
    
    def handle_resource_change(self, task_info):
        """处理资源文件变化"""
        try:
            # 获取任务信息
            post_name = task_info['post_name']
            time_str = task_info['time_str']
            
            # 重新执行文件传输
            success, status = self.file_handler.transfer_images(
                post_name,
                time_str
            )
            
            if success:
                logger.info(f"资源更新成功: {post_name} - {time_str}")
            else:
                logger.error(f"资源更新失败: {post_name} - {time_str} - {status}")
                
        except Exception as e:
            logger.error(f"处理资源变化失败: {str(e)}")
    
    def run(self):
        """运行应用"""
        # 注册信号处理
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # 创建任务验证器
        validator = TaskValidator()
        
        # 启动Excel监控
        self.excel_monitor.start_monitoring()
        
        logger.info("应用程序已启动")
        
        try:
            while self.running:
                valid_rows = self.excel_monitor.get_valid_rows()
                
                if valid_rows.empty:
                    time.sleep(1)
                    continue
                
                for index, row in valid_rows.iterrows():
                    self.process_task(index, row, validator)
                
                time.sleep(1)
                
        except Exception as e:
            logger.error(f"程序运行异常: {str(e)}")
        finally:
            self.excel_monitor.stop_monitoring()
            logger.info("应用程序已停止")

def ensure_directories():
    """确保所有必要的目录结构存在"""
    try:
        for dir_path in RESOURCE_DIRS.values():
            os.makedirs(dir_path, exist_ok=True)
            logger.debug(f"确保目录存在: {dir_path}")
    except Exception as e:
        logger.error(f"创建目录结构失败: {str(e)}")
        sys.exit(1)

def main():
    """程序入口"""
    try:
        # 确保目录结构
        ensure_directories()
        
        # 启动应用
        app = Application()
        app.run()
    except Exception as e:
        logger.error(f"程序启动失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
