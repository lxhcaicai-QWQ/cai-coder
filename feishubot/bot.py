"""
飞书长连接机器人
"""
import lark_oapi as lark
import json
import time
from typing import Dict
from datetime import datetime, timedelta
from config import FeishuBotConfig
from client import CaiCoderClient


class FeishuBot:
    """飞书长连接机器人"""

    def __init__(self):
        # 验证配置
        FeishuBotConfig.validate()

        # 初始化 cai-coder 客户端
        self.cai_coder = CaiCoderClient()

        # 会话过期时间
        self.session_timeout = FeishuBotConfig.SESSION_TIMEOUT

        # 会话最后活跃时间记录
        self.session_last_active: Dict[str, datetime] = {}

        # 创建事件处理器
        self.event_handler = self._create_event_handler()

        # 创建长连接客户端
        self.client = lark.ws.Client(
            FeishuBotConfig.FEISHU_APP_ID,
            FeishuBotConfig.FEISHU_APP_SECRET,
            event_handler=self.event_handler,
            log_level=lark.LogLevel.DEBUG
        )

    def _create_event_handler(self):
        """创建事件处理器"""
        return (
            lark.EventDispatcherHandler.builder("", "")
            .register_p2_im_message_receive_v1(self._handle_message_receive)
            .build()
        )

    async def _handle_message_receive(self, data: lark.im.v1.P2ImMessageReceiveV1):
        """
        处理接收消息事件

        Args:
            data: 飞书消息事件数据
        """
        try:
            # 提取消息信息
            event = data.event
            message = event.message
            content = message.content
            chat_id = message.chat_id
            message_id = message.message_id
            sender = event.sender

            # 解析消息内容（飞书消息是 JSON 格式）
            content_dict = json.loads(content)
            text = content_dict.get("text", "")

            if not text:
                return

            print(f"[收到消息] chat_id={chat_id}, message_id={message_id}, sender={sender.user_id}, text={text}")

            # 获取或创建会话 ID（使用 chat_id 作为会话 ID，支持群聊）
            session_id = chat_id

            # 更新会话活跃时间
            self._update_session_active_time(session_id)

            # 清理过期会话
            self._clean_expired_sessions()

            # 调用 cai-coder 获取回复
            reply = await self.cai_coder.chat(session_id, text)

            # 发送回复
            await self._send_message(chat_id, reply)

            print(f"[发送回复] chat_id={chat_id}, reply={reply}")

        except Exception as e:
            print(f"处理消息时出错: {e}")
            import traceback
            traceback.print_exc()

    async def _send_message(self, chat_id: str, text: str):
        """
        发送消息到飞书

        Args:
            chat_id: 聊天 ID
            text: 消息文本
        """
        try:
            # 创建消息客户端
            message_client = lark.api.Message.client(FeishuBotConfig.FEISHU_APP_ID, FeishuBotConfig.FEISHU_APP_SECRET)

            # 构建消息内容
            content = json.dumps({
                "text": text
            })

            # 发送消息
            request = lark.api.message.v1.CreateMessageRequest.builder() \
                .receive_id_type("chat_id") \
                .request_body(lark.api.message.v1.CreateMessageRequestBody.builder()
                    .receive_id(chat_id)
                    .msg_type("text")
                    .content(content)
                    .build()) \
                .build()

            response = await message_client.create_message(request)

            if response.code != 0:
                print(f"发送消息失败: code={response.code}, msg={response.msg}")
            else:
                print(f"发送消息成功: message_id={response.data.message_id}")

        except Exception as e:
            print(f"发送消息时出错: {e}")
            import traceback
            traceback.print_exc()

    def _update_session_active_time(self, session_id: str):
        """更新会话活跃时间"""
        self.session_last_active[session_id] = datetime.now()

    def _clean_expired_sessions(self):
        """清理过期会话"""
        now = datetime.now()
        expired_sessions = []

        for session_id, last_active in self.session_last_active.items():
            if now - last_active > timedelta(seconds=self.session_timeout):
                expired_sessions.append(session_id)

        # 清除过期会话
        for session_id in expired_sessions:
            print(f"[清理过期会话] session_id={session_id}")
            self.cai_coder.clear_session(session_id)
            del self.session_last_active[session_id]

    def start(self):
        """启动机器人"""
        print("=" * 50)
        print("飞书长连接机器人启动中...")
        print(f"APP_ID: {FeishuBotConfig.FEISHU_APP_ID}")
        print(f"CAICODER_API_URL: {FeishuBotConfig.CAICODER_API_URL}")
        print(f"会话超时时间: {self.session_timeout} 秒")
        print("=" * 50)

        try:
            self.client.start()
        except KeyboardInterrupt:
            print("\n机器人已停止")
        except Exception as e:
            print(f"机器人运行出错: {e}")
            import traceback
            traceback.print_exc()


def main():
    """主函数"""
    bot = FeishuBot()
    bot.start()


if __name__ == "__main__":
    main()
