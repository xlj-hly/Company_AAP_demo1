#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Author  ：何
@Project ：project_1 
@File    ：excel_monitor.py.py
@IDE     ：PyCharm 
@Date    ：2025/3/17 01:25 
"""

"""
Excel文件监控模块功能：
1. 使用watchdog库进行文件系统监控
2. 定时轮询机制双重保障数据同步
3. 数据变化检测（MD5哈希比对）
4. 线程安全的数据读取
5. 数据缓存机制提升性能
"""

import os
import pandas as pd
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from utils.logger import get_logger
import threading
import time
from datetime import datetime, timedelta
import hashlib
from core.task_validator import TaskValidator
from config.settings import (
    RESOURCE_DIRS, 
    EXCEL_CONFIG, 
    DIRECTORY_STRUCTURE,
    TASK_VALIDATION
)
from utils.excel_backup import ExcelBackup

logger = get_logger(__name__)


class ExcelEventHandler(FileSystemEventHandler):
    """文件系统事件处理器（观察者模式）"""
    
    def __init__(self, monitor):
        self.monitor = monitor  # 所属监控器实例
        self.last_modified = 0  # 最后修改时间戳
        self.cooldown = 1  # 事件冷却时间（防止重复触发）
        
    def on_modified(self, event):
        """处理Excel文件修改事件"""
        if not event.is_directory and event.src_path.endswith('.xlsx'):
            current_time = time.time()
            if current_time - self.last_modified > self.cooldown:
                self.last_modified = current_time
                logger.info(f"检测到Excel文件变化: {event.src_path}")
                self.monitor.check_excel_data(force_check=True)
                
    def on_created(self, event):
        """处理新文件创建事件"""
        if not event.is_directory and any(event.src_path.endswith(ext) 
            for ext in ['.jpg', '.jpeg', '.png', '.mp4']):
            logger.info(f"检测到新资源文件: {event.src_path}")
            self.monitor.handle_resource_change(event.src_path)


class ExcelMonitor:
    """Excel文件监控器（主体）"""
    
    def __init__(self, excel_path, headers):
        self.excel_path = excel_path
        self.headers = headers
        self.observer = Observer()   # 文件系统观察者
        self.last_data_hash = None   # 上次数据哈希值
        self.last_check_time = 0     # 上次检查时间
        self.poll_interval = 60      # 轮询间隔（秒）
        self.force_check_interval = 5 # 强制检查间隔
        self._stop_flag = False      # 停止标志
        self._lock = threading.Lock() # 线程锁
        self._data_cache = None      # 数据缓存
        self._cache_time = 0         # 缓存时间
        self.cache_ttl = 2           # 缓存有效期
        self.excel_backup = ExcelBackup()
        self.last_backup_time = 0
        self.resource_handlers = []  # 资源变化处理器列表

    def calculate_data_hash(self, df):
        """计算数据帧的MD5哈希值用于变化检测"""
        data_str = df.to_string()
        return hashlib.md5(data_str.encode('utf-8')).hexdigest()

    def read_excel_safe(self):
        """安全读取Excel文件（带重试机制）"""
        max_retries = 3  # 最大重试次数
        retry_delay = 1  # 重试间隔

        for attempt in range(max_retries):
            try:
                return pd.read_excel(self.excel_path)
            except (PermissionError, IOError) as e:
                if attempt == max_retries - 1:  # 最后一次尝试仍失败
                    logger.error(f"无法读取Excel文件: {str(e)}")
                    raise
                time.sleep(retry_delay)

    def is_row_valid(self, row):
        """
        检查行数据是否有效（未过期）
        添加30分钟缓冲时间，避免因各种延迟导致的任务丢失
        """
        try:
            # 获取当前时间
            now = datetime.now()

            # 获取时间字符串
            time_str = str(row['time']).strip()

            # 尝试解析时间
            try:
                task_time = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                try:
                    task_time = datetime.strptime(time_str, '%Y-%m-%d_%H')
                except ValueError:
                    logger.error(f"不支持的时间格式: {time_str}")
                    return False

            # 添加30分钟的缓冲时间
            buffer_time = now - timedelta(minutes=30)

            # 如果任务时间在（当前时间-30分钟）之后，则认为有效
            return task_time > buffer_time

        except Exception as e:
            logger.error(f"解析时间失败: {str(e)}, 时间字符串: {row.get('time', 'None')}")
            return False

    def filter_valid_rows(self, df):
        """
        过滤有效的数据行
        
        处理流程：
        1. 检查必要字段
        2. 过滤未来任务
        3. 创建任务目录结构
        
        Args:
            df (DataFrame): 原始数据框
            
        Returns:
            DataFrame: 过滤后的有效数据行
        """
        try:
            validator = TaskValidator()
            
            # 基础数据清理
            required_fields = ['time', 'postName']
            valid_rows = df.copy()  # 创建副本，不直接修改原数据
            
            # 添加状态列（如果不存在）
            if 'status' not in valid_rows.columns:
                valid_rows['status'] = ''
            
            # 标记无效行而不是删除它们
            valid_rows['is_valid'] = valid_rows['time'].apply(validator.is_task_valid)
            
            # 创建任务目录
            for _, row in valid_rows.iterrows():
                if validator.can_modify_task(row['time']):
                    self._ensure_task_directories(row)
            
            return valid_rows
            
        except Exception as e:
            logger.error(f"过滤数据行失败: {str(e)}")
            return pd.DataFrame()

    def _ensure_task_directories(self, row):
        """确保任务目录结构存在"""
        try:
            time_str = str(row['time']).strip()
            post_name = str(row['postName']).strip()
            
            # 转换时间格式为目录名
            dt = datetime.strptime(time_str, TASK_VALIDATION['TIME_FORMAT'])
            dir_name = dt.strftime('%Y-%m-%d_%H-%M')  # 使用相同的格式
            
            # 创建目录结构
            base_dir = os.path.join(RESOURCE_DIRS['UPLOADS'], post_name, dir_name)
            img_dir = os.path.join(base_dir, DIRECTORY_STRUCTURE['TASK_DIR']['IMG_DIR'])
            
            # 创建目录结构
            os.makedirs(img_dir, exist_ok=True)
            
            # 创建content.txt文件
            content_file = os.path.join(base_dir, DIRECTORY_STRUCTURE['TASK_DIR']['CONTENT_FILE'])
            if not os.path.exists(content_file):
                with open(content_file, 'w', encoding='utf-8') as f:
                    f.write(DIRECTORY_STRUCTURE['CONTENT_TEMPLATE'])
            
            logger.info(f"成功创建任务目录: {base_dir}")
            return True
            
        except Exception as e:
            logger.error(f"创建任务目录失败: {str(e)}")
            return False

    def check_excel_data(self, force_check=False):
        """检查Excel数据变化"""
        current_time = time.time()
        
        # 定期备份Excel
        if current_time - self.last_backup_time >= EXCEL_CONFIG['BACKUP_INTERVAL']:
            self.excel_backup.create_backup()
            self.last_backup_time = current_time
        
        # 使用缓存数据
        if not force_check and self._data_cache is not None:
            if current_time - self._cache_time < self.cache_ttl:
                return self._data_cache
        
        try:
            with self._lock:
                df = self.read_excel_safe()
                logger.debug(f"读取到的原始数据行数: {len(df)}")
                
                valid_rows = self.filter_valid_rows(df)
                logger.debug(f"过滤后的有效数据行数: {len(valid_rows)}")
                
                # 如果行数减少，输出详细信息
                if len(valid_rows) < len(df):
                    logger.warning(f"被过滤掉的行数: {len(df) - len(valid_rows)}")
                    logger.debug("被过滤的原因可能是：必填字段为空或时间格式不正确")
                
                current_hash = self.calculate_data_hash(valid_rows)
                
                # 只在数据变化时更新缓存和输出日志
                if force_check or self.last_data_hash != current_hash:
                    if self.last_data_hash is not None:  # 不是首次检查
                        logger.info("检测到数据变化")
                    self.last_data_hash = current_hash
                    self._data_cache = valid_rows
                    self._cache_time = current_time
                    
                    # 只在数据变化时输出详细信息
                    if not valid_rows.empty:
                        logger.info(f"找到 {len(valid_rows)} 条未过期的有效数据")
                        logger.info(f"时间范围: {valid_rows.iloc[0]['time']} 至 {valid_rows.iloc[-1]['time']}")
                
                return self._data_cache
                
        except Exception as e:
            logger.error(f"检查Excel数据时发生错误: {str(e)}")
            return pd.DataFrame()

    def poll_excel(self):
        """轮询线程方法（备用检查机制）"""
        while not self._stop_flag:
            try:
                current_time = time.time()
                # 定期强制检查
                if current_time - self.last_check_time >= self.poll_interval:
                    self.check_excel_data(force_check=True)
                    self.last_check_time = current_time
                time.sleep(self.force_check_interval)
            except Exception as e:
                logger.error(f"轮询检查时发生错误: {str(e)}")
                time.sleep(5)  # 错误时延长等待

    def start_monitoring(self):
        """启动监控服务"""
        # 初始化文件系统监控
        event_handler = ExcelEventHandler(self)
        self.observer.schedule(event_handler, path=os.path.dirname(self.excel_path))
        self.observer.start()

        # 启动轮询线程
        self.poll_thread = threading.Thread(target=self.poll_excel, daemon=True)
        self.poll_thread.start()

        logger.info(f"Excel监控服务已启动 - 文件: {self.excel_path}")
        # 初始数据检查
        self.check_excel_data(force_check=True)

    def stop_monitoring(self):
        """停止监控服务"""
        self._stop_flag = True
        self.observer.stop()
        self.observer.join()
        logger.info("Excel监控服务已停止")

    def get_valid_rows(self):
        """获取有效数据行（使用缓存）"""
        return self.check_excel_data(force_check=False)

    def add_resource_handler(self, handler):
        """添加资源变化处理器"""
        self.resource_handlers.append(handler)
        
    def handle_resource_change(self, file_path):
        """处理资源文件变化"""
        try:
            # 从文件路径解析任务信息
            task_info = self._parse_resource_path(file_path)
            if task_info:
                for handler in self.resource_handlers:
                    handler(task_info)
        except Exception as e:
            logger.error(f"处理资源变化失败: {str(e)}")
            
    def _parse_resource_path(self, file_path):
        """从文件路径解析任务信息"""
        try:
            # 路径格式: .../uploads/设备名/时间/img/文件名
            parts = file_path.split(os.sep)
            if 'uploads' in parts:
                idx = parts.index('uploads')
                if len(parts) > idx + 3:
                    return {
                        'post_name': parts[idx + 1],
                        'time_str': parts[idx + 2],
                        'file_name': parts[-1]
                    }
            return None
        except Exception:
            return None 