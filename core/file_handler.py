#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Author  ：何
@Project ：project_1 
@File    ：file_handler.py.py
@IDE     ：PyCharm 
@Date    ：2025/3/17 01:26 
"""

"""
文件处理模块功能：
1. 根据设备映射关系传输文件
2. 支持多图片文件传输
3. 处理设备连接状态检查
4. 返回详细的传输状态
"""

import os
from utils.adb_utils import ADBHelper
from utils.logger import get_logger
from config.settings import DEVICE_MAPPING, TASK_STATUS, LOG_DIR, DEVICE_PATHS
from datetime import datetime

logger = get_logger(__name__)

class FileHandler:
    def __init__(self, root_dir):
        self.root_dir = root_dir       # 项目根目录
        self.adb_helper = ADBHelper()  # ADB工具实例
        self.transfer_log_path = os.path.join(LOG_DIR, 'transfer_history.log')
    
    def _convert_time_format(self, time_str):
        """转换时间格式为目录格式"""
        try:
            # 如果是 Timestamp 类型，直接使用
            if hasattr(time_str, 'strftime'):
                return time_str.strftime('%Y-%m-%d %H-%M-%S')
            
            # 如果是字符串，先解析
            dt = datetime.strptime(str(time_str), '%Y-%m-%d %H:%M:%S')
            return dt.strftime('%Y-%m-%d %H-%M-%S')
        except Exception as e:
            logger.error(f"时间格式转换失败: {str(e)}")
            return None

    def log_transfer_result(self, post_name, time_str, file_name, success, status, error_msg=None):
        """记录传输结果到日志文件"""
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            result = "成功" if success else "失败"
            log_entry = (
                f"时间: {timestamp}\n"
                f"设备: {post_name}\n"
                f"计划时间: {time_str}\n"
                f"文件: {file_name}\n"
                f"结果: {result}\n"
                f"状态: {status}\n"
            )
            if error_msg:
                log_entry += f"错误信息: {error_msg}\n"
            log_entry += "-" * 50 + "\n"
            
            # 确保日志目录存在
            os.makedirs(os.path.dirname(self.transfer_log_path), exist_ok=True)
            
            # 追加写入日志
            with open(self.transfer_log_path, 'a', encoding='utf-8') as f:
                f.write(log_entry)
                
        except Exception as e:
            logger.error(f"写入传输日志失败: {str(e)}")

    def transfer_images(self, post_name, time_str):
        try:
            # 只输出任务开始的关键信息
            logger.info(f"开始处理传输任务 - 设备: {post_name}, 时间: {time_str}")
            
            # 设备映射检查
            device_id = DEVICE_MAPPING.get(post_name)
            if not device_id:
                msg = f"设备映射未找到: {post_name}"
                self.log_transfer_result(post_name, time_str, "N/A", False, "DEVICE_NOT_FOUND", msg)
                return False, "DEVICE_NOT_FOUND"
            
            # 获取设备目标路径
            device_base_path = DEVICE_PATHS.get(device_id)
            if not device_base_path:
                msg = f"设备路径未配置: {device_id}"
                self.log_transfer_result(post_name, time_str, "N/A", False, "INVALID_PATH", msg)
                return False, "INVALID_PATH"
            
            # 构建源目录和目标目录
            dir_time = self._convert_time_format(time_str)
            # date_only = dir_time.split()[0]  # 只取日期部分 "2025-03-17"
            date_only = dir_time.replace(' ', '_').replace('-', '-')  # 日期部分 "2025-03-17"
            
            source_dir = os.path.join(self.root_dir, post_name, dir_time, 'img')
            # 目标目录只使用日期
            target_dir = f"{device_base_path.rstrip('/')}/{date_only}"
            target_dir = target_dir.replace('\\', '/')
            
            logger.info(f"源目录: {source_dir}")
            logger.info(f"目标目录: {target_dir}")
            
            # 检查传输历史
            if self.is_transfer_completed(post_name, time_str):
                logger.info(f"任务已完成: {post_name} - {time_str}")
                return True, "ALREADY_TRANSFERRED"
            
            # 创建源目录
            os.makedirs(source_dir, exist_ok=True)
            
            if not os.path.exists(source_dir):
                logger.error(f"源目录不存在: {source_dir}")
                return False, "INVALID_PATH"
            
            # 获取图片文件列表
            images = [f for f in os.listdir(source_dir) 
                     if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            
            if not images:
                logger.info(f"等待图片文件: {source_dir}")
                return False, "NO_IMAGES"
            
            # 输出传输开始信息
            logger.info(f"开始传输 {len(images)} 个文件")
            
            # 批量传输处理
            transfer_results = []
            success_count = 0
            
            for img in images:
                source_path = os.path.join(source_dir, img)
                # 构建目标文件路径，添加时间作为文件名前缀
                time_prefix = dir_time.replace(' ', '_').replace(':', '-')
                target_filename = f"{time_prefix}_{img}"
                target_path = f"{target_dir}/{target_filename}"
                target_path = target_path.replace('\\', '/')
                
                logger.info(f"传输文件: {img}")
                logger.info(f"源路径: {source_path}")
                logger.info(f"目标路径: {target_path}")
                
                if self.is_file_transferred(post_name, time_str, img):
                    success_count += 1
                    continue
                
                # 输出当前处理的文件
                logger.info(f"传输文件: {img}")
                success, status = self.adb_helper.push_file(device_id, source_path, target_path)
                transfer_results.append((success, status))
                
                self.log_transfer_result(
                    post_name, 
                    time_str, 
                    img, 
                    success, 
                    status,
                    None if success else f"传输失败: {status}"
                )
                
                if success:
                    success_count += 1
            
            # 输出传输结果摘要
            total = len(images)
            logger.info(f"传输完成 - 成功: {success_count}/{total}")
            
            if success_count == total:
                self.mark_transfer_completed(post_name, time_str)
                return True, "SUCCESS"
            elif success_count > 0:
                return False, "PARTIAL_SUCCESS"
            else:
                return False, transfer_results[0][1]
                
        except Exception as e:
            logger.error(f"传输过程出错: {str(e)}")
            return False, "FAILED"

    def is_transfer_completed(self, post_name, time_str):
        """检查任务是否已经完成传输"""
        try:
            with open(self.transfer_log_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # 构建唯一标识
                task_identifier = f"设备: {post_name}\n计划时间: {time_str}\n结果: 成功\n状态: SUCCESS"
                return task_identifier in content
        except FileNotFoundError:
            return False
        except Exception as e:
            logger.error(f"检查传输历史失败: {str(e)}")
            return False

    def is_file_transferred(self, post_name, time_str, file_name):
        """检查单个文件是否已经传输成功"""
        try:
            with open(self.transfer_log_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # 构建文件传输成功的标识
                file_identifier = (
                    f"设备: {post_name}\n"
                    f"计划时间: {time_str}\n"
                    f"文件: {file_name}\n"
                    f"结果: 成功\n"
                )
                return file_identifier in content
        except FileNotFoundError:
            return False
        except Exception as e:
            logger.error(f"检查文件传输历史失败: {str(e)}")
            return False

    def mark_transfer_completed(self, post_name, time_str):
        """标记任务完成"""
        self.log_transfer_result(
            post_name,
            time_str,
            "TASK_COMPLETE",
            True,
            "SUCCESS",
            "所有文件传输完成"
        )
