#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
Excel备份模块：
负责Excel文件的定期备份和管理
"""

import os
import shutil
from datetime import datetime, timedelta
from config.settings import EXCEL_CONFIG
from utils.logger import get_logger

logger = get_logger(__name__)

class ExcelBackup:
    def __init__(self):
        self.backup_path = EXCEL_CONFIG['BACKUP_PATH']
        os.makedirs(self.backup_path, exist_ok=True)
        
    def create_backup(self):
        """创建Excel备份"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = os.path.join(
                self.backup_path, 
                f"content_backup_{timestamp}.xlsx"
            )
            shutil.copy2(EXCEL_CONFIG['PATH'], backup_file)
            logger.info(f"创建Excel备份: {backup_file}")
            
            # 清理过期备份
            self.cleanup_old_backups()
            
        except Exception as e:
            logger.error(f"创建Excel备份失败: {str(e)}")
    
    def cleanup_old_backups(self):
        """清理过期备份文件"""
        try:
            cutoff_date = datetime.now() - timedelta(days=EXCEL_CONFIG['KEEP_BACKUP_DAYS'])
            for file in os.listdir(self.backup_path):
                file_path = os.path.join(self.backup_path, file)
                if os.path.getctime(file_path) < cutoff_date.timestamp():
                    os.remove(file_path)
                    logger.debug(f"删除过期备份: {file}")
        except Exception as e:
            logger.error(f"清理备份失败: {str(e)}") 