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
import subprocess
import hashlib

logger = get_logger(__name__)

class FileHandler:
    def __init__(self, root_dir):
        self.root_dir = root_dir       # 项目根目录
        self.adb_helper = ADBHelper()  # ADB工具实例
        self.transfer_log_path = os.path.join(LOG_DIR, 'transfer_history.log')
        self.file_hashes = {}  # 存储文件哈希值
    
    def _convert_time_format(self, time_str):
        """转换时间格式为目录格式"""
        try:
            # 如果是 Timestamp 类型，直接使用
            if hasattr(time_str, 'strftime'):
                return time_str.strftime('%Y-%m-%d_%H-%M')
            
            # 如果是字符串，先解析
            dt = datetime.strptime(str(time_str), '%Y-%m-%d %H:%M:%S')
            return dt.strftime('%Y-%m-%d_%H-%M')
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

    def _get_target_path(self, device_id, source_path, time_str):
        """获取设备上的目标路径"""
        try:
            # 获取设备基础路径
            base_path = DEVICE_PATHS.get(device_id)
            if not base_path:
                raise ValueError(f"设备路径未配置: {device_id}")
            
            # 处理时间格式 (YYYY-MM-DD HH:MM -> YYYY-MM-DD_HH-MM)
            if hasattr(time_str, 'strftime'):
                dir_name = time_str.strftime('%Y-%m-%d_%H-%M')
            else:
                # 转换字符串格式
                dt = datetime.strptime(str(time_str), '%Y-%m-%d %H:%M:%S')
                dir_name = dt.strftime('%Y-%m-%d_%H-%M')
            
            # 获取文件名
            file_name = os.path.basename(source_path)
            
            # 构建目标路径
            target_path = f"{base_path.rstrip('/')}/{dir_name}/{file_name}"
            return target_path.replace('\\', '/')
            
        except Exception as e:
            logger.error(f"构建目标路径失败: {str(e)}")
            raise

    def _calculate_file_hash(self, file_path):
        """计算文件的MD5哈希值"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return None
            
    def _check_file_changed(self, file_path):
        """检查文件是否发生变化"""
        current_hash = self._calculate_file_hash(file_path)
        if not current_hash:
            return True
            
        previous_hash = self.file_hashes.get(file_path)
        self.file_hashes[file_path] = current_hash
        return previous_hash != current_hash
        
    def transfer_images(self, post_name, time_str):
        """传输文件并确保完成"""
        try:
            # 初始化传输状态
            transfer_summary = {
                'total': 0,
                'success': 0,
                'failed': 0,
                'failed_files': []
            }
            
            # 首先检查设备连接
            device_id = DEVICE_MAPPING.get(post_name)
            if not device_id:
                logger.error(f"设备映射未找到: {post_name}")
                return False, "DEVICE_NOT_FOUND"
            
            if not self.adb_helper.is_device_connected(device_id):
                logger.error(f"设备未连接: {device_id}")
                return False, "DEVICE_NOT_CONNECTED"
            
            # 构建源目录路径
            dir_time = self._convert_time_format(time_str)
            base_dir = os.path.join(self.root_dir, post_name, dir_time)
            source_dir = os.path.join(base_dir, 'img')
            
            # 添加路径调试信息
            logger.debug(f"检查目录: {base_dir}")
            logger.debug(f"图片目录: {source_dir}")
            
            # 检查媒体目录
            if not os.path.exists(source_dir):
                logger.info(f"等待媒体文件目录: {source_dir}")
                return False, "WAITING_MEDIA"
            
            # 获取所有媒体文件并输出调试信息
            media_files = [f for f in os.listdir(source_dir) 
                         if f.lower().endswith(('.png', '.jpg', '.jpeg', '.mp4'))]
            
            if not media_files:
                logger.info(f"没有找到媒体文件: {source_dir}")
                return False, "NO_MEDIA_FILES"
            
            logger.info(f"找到 {len(media_files)} 个媒体文件")
            
            # 检查文件变化
            changed_files = []
            for media_file in media_files:
                file_path = os.path.join(source_dir, media_file)
                if self._check_file_changed(file_path):
                    changed_files.append(media_file)
            
            if not changed_files:
                logger.debug("没有检测到文件变化，跳过传输")
                return True, "NO_CHANGES"
            
            # 只传输发生变化的文件
            logger.info(f"开始传输变化的文件 - {post_name} ({len(changed_files)}个文件)")
            
            success_count = 0
            failed_files = []
            
            for media_file in changed_files:
                try:
                    source_path = os.path.join(source_dir, media_file)
                    target_path = self._get_target_path(device_id, source_path, time_str)
                    
                    # 详细日志写入文件
                    logger.debug(f"传输: {media_file} -> {target_path}")
                    
                    success, status = self.adb_helper.push_file(device_id, source_path, target_path)
                    if success:
                        success_count += 1
                    else:
                        failed_files.append((media_file, status))
                        
                except Exception as e:
                    failed_files.append((media_file, str(e)))
                    logger.debug(f"文件传输失败: {media_file} - {str(e)}")
            
            # 简化的结果输出
            if failed_files:
                logger.info(f"传输完成: {success_count}/{len(changed_files)} 成功")
                # 详细失败信息写入debug日志
                for file, error in failed_files:
                    logger.debug(f"失败: {file} - {error}")
                return False, "TRANSFER_INCOMPLETE"
            else:
                logger.info(f"传输成功: {success_count}/{len(changed_files)}")
                return True, "SUCCESS"
            
        except Exception as e:
            logger.error(f"传输过程出错: {str(e)}")
            return False, "FAILED"

    def _log_transfer_summary(self, post_name, summary):
        """输出传输汇总信息"""
        logger.info(f"""
传输任务汇总 - {post_name}
----------------------------
总文件数: {summary['total']}
成功: {summary['success']}
失败: {summary['failed']}
""")
        
        # 只有在有失败的情况下才输出详细失败信息
        if summary['failed'] > 0:
            logger.error("失败文件详情:")
            for fail in summary['failed_files']:
                if 'error' in fail:
                    logger.error(f"- {fail['file']}: {fail['error']}")
                else:
                    logger.error(f"- {fail['file']}: {fail['status']}")

    def _transfer_and_verify(self, device_id, source_path, time_str):
        """传输单个文件并验证"""
        try:
            # 获取目标路径
            target_path = self._get_target_path(device_id, source_path, time_str)
            
            # 执行传输
            success, status = self.adb_helper.push_file(device_id, source_path, target_path)
            if not success:
                return False, status
            
            # 验证文件是否成功传输
            if self._verify_file_transfer(device_id, target_path):
                return True, "SUCCESS"
            else:
                return False, "VERIFICATION_FAILED"
                
        except Exception as e:
            logger.error(f"文件传输验证失败: {str(e)}")
            return False, "FAILED"

    def _verify_file_transfer(self, device_id, target_path):
        """验证文件传输是否成功"""
        try:
            # 使用ADB检查文件是否存在且大小正确
            command = [
                ADB_COMMAND,
                '-s', device_id,
                'shell',
                f'ls -l "{target_path}"'
            ]
            
            result = subprocess.run(command, capture_output=True, text=True)
            return result.returncode == 0 and len(result.stdout.strip()) > 0
            
        except Exception:
            return False

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
