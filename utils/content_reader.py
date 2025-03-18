#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from utils.logger import get_logger
import os

logger = get_logger(__name__)

class ContentReader:
    @staticmethod
    def read_content_file(content_path):
        """
        读取内容文件，返回标题和正文
        格式：
        标题：xxx
        正文：xxx
        """
        try:
            with open(content_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 分割标题和正文
            parts = content.split('\n', 2)  # 最多分割2次
            
            title = ""
            body = ""
            
            # 解析标题
            if len(parts) >= 1:
                title_line = parts[0]
                if title_line.startswith("标题："):
                    title = title_line[3:].strip()
            
            # 解析正文
            if len(parts) >= 2:
                body_start = parts[1]
                if body_start.startswith("正文："):
                    body = parts[1][3:] + "\n" + parts[2] if len(parts) > 2 else parts[1][3:]
            
            return title, body.strip()
            
        except Exception as e:
            logger.error(f"读取内容文件失败: {str(e)}")
            return None, None 