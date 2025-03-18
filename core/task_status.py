from enum import Enum

class TaskStatus(Enum):
    NEW = "新建"
    PENDING = "待处理"
    PROCESSING = "处理中"
    SUCCESS = "完成"
    FAILED = "失败"
    EXPIRED = "已过期"
    
    @classmethod
    def can_modify(cls, status):
        """检查任务是否可以修改"""
        return status in [cls.NEW, cls.PENDING] 