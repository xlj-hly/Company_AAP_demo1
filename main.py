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
from config.settings import *
import pandas as pd
import time
import signal
import sys
from utils.logger import get_logger
import subprocess

logger = get_logger(__name__)

class Application:
    def __init__(self):
        # 初始化核心组件
        self.excel_monitor = ExcelMonitor(EXCEL_PATH, EXCEL_HEADERS)
        self.task_scheduler = TaskScheduler()
        self.file_handler = FileHandler(ROOT_DIR)
        self.running = True  # 运行状态标志
    
    def signal_handler(self, signum, frame):
        """处理系统终止信号"""
        logger.info("收到终止信号，正在关闭服务...")
        self.running = False
        self.excel_monitor.stop_monitoring()
        sys.exit(0)
    
    def update_excel_status(self, row_index, status):
        """更新Excel中的任务状态"""
        max_retries = 3
        retry_delay = 2  # 增加重试间隔
        
        for attempt in range(max_retries):
            try:
                # 使用 pandas 的 mode='a' 来避免文件锁定问题
                with pd.ExcelWriter(EXCEL_PATH, mode='a', if_sheet_exists='replace') as writer:
                    df = pd.read_excel(EXCEL_PATH)
                    if 'status' not in df.columns:
                        df['status'] = pd.Series(dtype='str')
                    else:
                        df['status'] = df['status'].astype(str)
                    
                    df.at[row_index, 'status'] = str(status)
                    df.to_excel(writer, index=False)
                    
                logger.info(f"更新任务状态: 行 {row_index + 1}, 状态 {status}")
                return True
                
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"更新Excel状态失败: {str(e)}")
                    return False
                logger.warning(f"更新状态重试 ({attempt + 1}/{max_retries})")
                time.sleep(retry_delay)
    
    def check_device_status(self, device_id):
        """检查设备状态"""
        try:
            command = [ADB_COMMAND, 'get-state']
            result = subprocess.run(command, capture_output=True, text=True)
            return result.stdout.strip() == 'device'
        except Exception:
            return False
    
    def run(self):
        """运行应用"""
        # 注册信号处理
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # 启动Excel监控
        self.excel_monitor.start_monitoring()
        
        logger.info("应用程序已启动")
        
        try:
            while self.running:
                valid_rows = self.excel_monitor.get_valid_rows()
                
                if valid_rows.empty:
                    logger.debug("没有找到有效数据，等待下一次检查...")
                    time.sleep(1)
                    continue
                
                logger.info(f"处理 {len(valid_rows)} 条有效数据")
                
                # 处理每一行数据
                for index, row in valid_rows.iterrows():
                    try:
                        current_status = str(row.get('status', '')).strip()
                        
                        # 跳过已处理的任务
                        if current_status and current_status not in ['FAILED', 'DEVICE_NOT_FOUND', 'nan', 'None']:
                            logger.debug(f"跳过已处理的任务: {row['postName']} - {row['time']}")
                            continue
                        
                        # 设备检查
                        device_id = DEVICE_MAPPING.get(row['postName'])
                        if not device_id:
                            logger.error(f"设备映射未找到: {row['postName']}")
                            self.update_excel_status(index, TASK_STATUS['DEVICE_NOT_FOUND'])
                            continue
                        
                        # 处理文件传输
                        logger.info(f"处理任务: {row['postName']} - {row['time']}")
                        success, status = self.file_handler.transfer_images(
                            row['postName'],
                            row['time']
                        )
                        
                        # 更新状态
                        if status == "NO_IMAGES":
                            self.update_excel_status(index, "等待图片")
                        else:
                            self.update_excel_status(index, TASK_STATUS[status])
                        
                        # 添加定时任务
                        if success:
                            self.task_scheduler.add_task(row)
                    
                    except Exception as e:
                        logger.error(f"处理任务出错: {str(e)}")
                        continue
                
                time.sleep(1)
                
        except Exception as e:
            logger.error(f"程序运行异常: {str(e)}")
        finally:
            self.excel_monitor.stop_monitoring()
            logger.info("应用程序已停止")

def main():
    app = Application()
    app.run()

if __name__ == "__main__":
    print(ROOT_DIR)
    main()
