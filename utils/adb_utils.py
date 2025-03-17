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
        """
        使用ADB推送文件到设备
        """
        try:
            if not self.is_device_connected(device_id):
                logger.error(f"设备未连接: {device_id}")
                return False, "DEVICE_NOT_FOUND"
            
            # 检查源文件是否存在
            if not os.path.exists(source_path):
                logger.error(f"源文件不存在: {source_path}")
                return False, "SOURCE_NOT_FOUND"
            
            # 获取目标目录
            target_dir = os.path.dirname(target_path)
            print(target_dir)
            
            # 先尝试创建目录
            mkdir_command = [
                ADB_COMMAND,
                '-s', device_id,
                'shell',
                'mkdir',
                '-p',
                target_dir
            ]
            
            try:
                # 创建目录（忽略错误）
                subprocess.run(mkdir_command, capture_output=True, text=True)
            except:
                pass  # 忽略目录创建错误，因为目录可能已存在
            
            # 执行文件传输
            command = [
                ADB_COMMAND,
                '-s', device_id,
                'push',
                source_path,
                target_path
            ]
            
            logger.info(f"执行传输命令: {' '.join(command)}")
            result = subprocess.run(command, capture_output=True, text=True)
            
            if result.stdout:
                logger.info(f"命令输出: {result.stdout}")
            if result.stderr:
                logger.warning(f"错误输出: {result.stderr}")
            
            # 验证传输是否成功
            if result.returncode == 0:
                logger.info(f"文件传输成功: {target_path}")
                return True, "SUCCESS"
            else:
                logger.error(f"传输失败: {result.stderr}")
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
