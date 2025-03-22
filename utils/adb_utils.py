#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Author  ：何
@Project ：project_1 
@File    ：adb_utils.py.py
@IDE     ：PyCharm 
@Date    ：2025/3/17 01:35 
"""

"""
ADB工具模块功能：
1. 管理ADB设备连接
2. 执行文件传输命令
3. 设备状态实时监控
"""

import subprocess
from utils.logger import get_logger
from config.settings import ADB_COMMAND, DEVICE_PATHS
import re
import os
import time

logger = get_logger(__name__)

class ADBHelper:
    def __init__(self):
        self.connected_devices = set()  # 已连接设备集合
        self.update_connected_devices() # 初始化设备列表
    
    def update_connected_devices(self):
        """更新已连接的设备列表"""
        try:
            result = subprocess.run(
                [ADB_COMMAND, 'devices'], 
                capture_output=True, 
                text=True, 
                check=True
            )
            
            # 解析ADB输出
            lines = result.stdout.strip().split('\n')[1:]  # 跳过标题行
            self.connected_devices = {
                line.split()[0] for line in lines 
                if line.strip() and 'device' in line  # 过滤掉未授权设备
            }
            
            logger.info(f"当前连接的设备: {self.connected_devices}")
            return self.connected_devices
            
        except subprocess.CalledProcessError as e:
            logger.error(f"获取设备列表失败: {str(e)}")
            self.connected_devices = set()
            return set()
    
    def is_device_connected(self, device_id):
        """检查指定设备是否在线"""
        self.update_connected_devices()  # 每次检查前更新状态
        return device_id in self.connected_devices
    
    def push_file(self, device_id, source_path, target_path):
        """使用ADB推送文件并触发媒体扫描"""
        try:
            if not self.is_device_connected(device_id):
                return False, "DEVICE_NOT_FOUND"
            
            # 创建目标目录
            target_dir = os.path.dirname(target_path)
            mkdir_command = [
                ADB_COMMAND,
                '-s', device_id,
                'shell',
                'mkdir',
                '-p',
                target_dir
            ]
            
            try:
                subprocess.run(mkdir_command, capture_output=True, encoding='utf-8')
            except:
                pass
            
            # 执行文件传输
            command = [
                ADB_COMMAND,
                '-s', device_id,
                'push',
                source_path,
                target_path
            ]
            
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                self.trigger_media_scan(device_id, target_path)
                logger.debug(f"文件传输成功: {target_path}")
                return True, "SUCCESS"
            else:
                logger.debug(f"传输失败: {stderr.decode('utf-8', errors='ignore')}")
                return False, "TRANSFER_FAILED"
            
        except Exception as e:
            logger.error(f"传输异常: {str(e)}")
            return False, "FAILED"

    def check_device_permissions(self, device_id, path):
        """检查设备存储权限"""
        try:
            # 检查目录权限
            command = [
                ADB_COMMAND,
                '-s', device_id,
                'shell',
                'ls',
                os.path.dirname(path)
            ]
            result = subprocess.run(command, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"目录访问权限检查失败: {result.stderr}")
                return False
            
            return True
        except Exception as e:
            logger.error(f"权限检查失败: {str(e)}")
            return False

    def ensure_device_connected(self, device_id, max_retries=3, retry_interval=5):
        """确保设备连接可用"""
        for attempt in range(max_retries):
            if self.is_device_connected(device_id):
                return True
                
            logger.warning(f"设备未连接，尝试重新连接 ({attempt + 1}/{max_retries}): {device_id}")
            try:
                # 尝试重新连接设备
                subprocess.run([ADB_COMMAND, 'connect', device_id], 
                             capture_output=True, text=True)
                time.sleep(retry_interval)
            except Exception as e:
                logger.error(f"连接设备失败: {str(e)}")
                
        return False

    def trigger_media_scan(self, device_id, target_path):
        """触发媒体扫描的备用方法"""
        try:
            # 方法1：使用广播
            scan_command1 = [
                ADB_COMMAND,
                '-s', device_id,
                'shell',
                'am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d file://' + target_path
            ]
            
            # 方法2：使用媒体存储命令
            scan_command2 = [
                ADB_COMMAND,
                '-s', device_id,
                'shell',
                'content call --uri content://media/none/all --method SCAN_FILE --arg file://' + target_path
            ]
            
            # 尝试第一种方法
            result = subprocess.run(scan_command1, capture_output=True, encoding='utf-8')
            if result.returncode != 0:
                # 如果失败，尝试第二种方法
                subprocess.run(scan_command2, capture_output=True, encoding='utf-8')
            
            logger.debug(f"媒体扫描请求已发送: {target_path}")
            return True
        
        except Exception as e:
            logger.warning(f"媒体扫描触发失败: {str(e)}")
            return False
