from utils.logger import get_logger
import uiautomator2 as u2
import time

logger = get_logger(__name__)

class AndroidAutomation:
    def __init__(self, device_id):
        self.device_id = device_id
        self.d = None
        
    def connect_device(self):
        """连接设备"""
        try:
            self.d = u2.connect(self.device_id)
            logger.info(f"成功连接设备: {self.device_id}")
            return True
        except Exception as e:
            logger.error(f"设备连接失败: {str(e)}")
            return False
            
    def post_content(self, title, content, image_paths):
        """发布内容"""
        try:
            # 解锁屏幕
            self._unlock_screen()
            
            # 启动小红书
            self._start_app()
            
            # 选择并上传图片（必需）
            self._upload_images(image_paths)
            
            # 填写标题和内容（可选）
            if title or content:  # 只有在有标题或正文时才调用
                self._input_content(title, content)
            
            # 发布
            self._publish()
            
            logger.info("内容发布成功")
            return True, "SUCCESS"
            
        except Exception as e:
            logger.error(f"发布失败: {str(e)}")
            return False, "AUTOMATION_FAILED"
    
    def _unlock_screen(self):
        """解锁屏幕"""
        try:
            self.d.screen_on()
            self.d.swipe(500, 2500, 500, 500, duration=1.0)
            # 输入密码
            for _ in range(6):
                self.d(resourceId="com.android.systemui:id/digit_text", text="0").click()
        except Exception as e:
            logger.error(f"解锁屏幕失败: {str(e)}")
            raise
    
    def _start_app(self):
        """启动小红书应用"""
        try:
            self.d.app_start("com.xingin.xhs")
            self.d.wait_activity("com.xingin.xhs", timeout=5)
        except Exception as e:
            logger.error(f"启动应用失败: {str(e)}")
            raise
            
    # ... 其他辅助方法实现 ... 