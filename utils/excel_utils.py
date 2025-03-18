import os
import time
import win32file
import pandas as pd
from utils.logger import get_logger

logger = get_logger(__name__)

class ExcelUtils:
    @staticmethod
    def is_file_locked(file_path):
        """
        检查文件是否被占用
        """
        try:
            # 尝试以写入模式打开文件
            handle = win32file.CreateFile(
                file_path,
                win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                0,  # 不共享
                None,
                win32file.OPEN_EXISTING,
                win32file.FILE_ATTRIBUTE_NORMAL,
                None
            )
            
            # 如果成功打开，则关闭句柄
            if handle:
                win32file.CloseHandle(handle)
                return False
                
        except Exception:
            return True
            
        return False

    @staticmethod
    def wait_for_file_unlock(file_path, timeout=300, check_interval=2):
        """
        等待文件解除占用
        
        Args:
            file_path: Excel文件路径
            timeout: 超时时间（秒）
            check_interval: 检查间隔（秒）
        
        Returns:
            bool: 文件是否可用
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if not ExcelUtils.is_file_locked(file_path):
                return True
            
            logger.debug(f"Excel文件被占用，等待解锁: {file_path}")
            time.sleep(check_interval)
        
        logger.error(f"等待Excel文件解锁超时: {file_path}")
        return False

    @staticmethod
    def safe_write_excel(file_path, df, max_retries=3, retry_interval=5):
        """
        安全写入Excel文件
        
        Args:
            file_path: Excel文件路径
            df: 要写入的DataFrame
            max_retries: 最大重试次数
            retry_interval: 重试间隔（秒）
            
        Returns:
            bool: 是否写入成功
        """
        for attempt in range(max_retries):
            try:
                # 等待文件可用
                if not ExcelUtils.wait_for_file_unlock(file_path):
                    continue
                
                # 创建临时文件（确保使用.xlsx扩展名）
                temp_file = f"{file_path}.temp.xlsx"
                
                # 写入临时文件
                df.to_excel(temp_file, index=False, engine='openpyxl')
                
                # 如果原文件存在，则先删除
                if os.path.exists(file_path):
                    os.remove(file_path)
                
                # 重命名临时文件
                os.rename(temp_file, file_path)
                
                logger.info("Excel文件更新成功")
                return True
                
            except Exception as e:
                logger.error(f"写入Excel失败 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
                
                # 清理临时文件
                if os.path.exists(f"{file_path}.temp.xlsx"):
                    try:
                        os.remove(f"{file_path}.temp.xlsx")
                    except:
                        pass
                
                if attempt < max_retries - 1:
                    time.sleep(retry_interval)
                    
        return False 