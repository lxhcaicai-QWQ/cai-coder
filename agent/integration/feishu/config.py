import os


class FeishuBotConfig:
    """飞书机器人配置"""

    # 飞书应用凭证
    FEISHU_APP_ID = os.getenv("FEISHU_APP_ID", "")
    FEISHU_APP_SECRET = os.getenv("FEISHU_APP_SECRET", "")

    # 会话配置
    SESSION_TIMEOUT = int(os.getenv("SESSION_TIMEOUT", "3600"))  # 会话超时时间（秒），默认1小时

    @classmethod
    def validate(cls):
        """验证配置是否完整"""
        if not cls.FEISHU_APP_ID or not cls.FEISHU_APP_SECRET:
            raise ValueError("FEISHU_APP_ID 和 FEISHU_APP_SECRET 必须配置")