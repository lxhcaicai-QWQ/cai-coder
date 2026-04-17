import datetime
import json
import queue
import random
import threading
from typing import Dict

from lark_oapi.api.im.v1 import CreateMessageRequest, CreateMessageRequestBody, ReplyMessageRequest, \
    ReplyMessageRequestBody, CreateMessageReactionRequest, CreateMessageReactionRequestBuilder, EmojiBuilder, \
    CreateMessageReactionRequestBody, Emoji, DeleteMessageReactionRequest

from agent.integration.feishu.config import FeishuBotConfig
from agent.server import get_agent
import lark_oapi as lark

class CaiCoderClient:
    def __init__(self):
        self.agent = get_agent()

    def chat(self, session_id :str, content:str) -> str:
        config = {"configurable": {"thread_id": session_id}}
        response = self.agent.invoke({"messages": [{"role": "user", "content": content}]}, config=config)
        return response["messages"][-1].content


class FeishuBot:
    """飞书长连接机器人"""

    def __init__(self):

        # 同步阻塞队列， 处理100条消息
        self.task_queue = queue.Queue(maxsize=100)

        self._consumer_thread = threading.Thread(target=self._consumer, daemon=True)
        self._consumer_thread.start()

        # 验证配置
        FeishuBotConfig.validate()

        # 初始化 cai-coder 客户端
        self.cai_coder = CaiCoderClient()

        self.task_db = set()

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

        self.client2 = lark.Client.builder() \
            .app_id(FeishuBotConfig.FEISHU_APP_ID,) \
            .app_secret(FeishuBotConfig.FEISHU_APP_SECRET) \
            .log_level(lark.LogLevel.DEBUG) \
            .build()

    def _create_event_handler(self):
        """创建事件处理器"""
        return (
            lark.EventDispatcherHandler.builder("", "")
            .register_p2_im_message_receive_v1(self._handle_message_receive)
            .build()
        )

    def _handle_message_receive(self, data: lark.im.v1.P2ImMessageReceiveV1):
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

            # 检查是否是重启命令
            if text.strip().lower() in ["/restart", "重启服务", "重启"]:
                self._handle_restart_command(chat_id, message_id)
                return

            # 消息已经回复过，直接跳过，避免长链接重放
            if message_id in self.task_db:
                print(f"[消息重复] message_id={message_id} 已经跳过")
                return

            final_text = text
            # 获取 mentions 数组（如果没有@任何人，这个字段可能为空）
            mentions = event.message.mentions

            if mentions:
                for mention in mentions:
                    key = mention.key
                    name = mention.name

                    final_text = final_text.replace(key, f"@{name}")


            # print(f"[收到消息] chat_id={chat_id}, message_id={message_id}, sender={sender.user_id}, text={text}")
            print(f"[收到消息] chat_id={chat_id}, message_id={message_id}, sender={sender.sender_id.user_id}, text={final_text}")

            # 表情回复
            reaction_id = self._reply_message_reaction_create(message_id=message_id)

            # 放入同步阻塞队列处理
            self.task_queue.put({
                "chat_id":chat_id,
                "message_id":message_id,
                "text": final_text,
                "reaction_id":reaction_id,
            })

            self.task_db.add(message_id)

        except Exception as e:
            print(f"处理消息时出错: {e}")
            import traceback
            traceback.print_exc()

    def _consumer(self):
        """消费者"""
        while True:
            item = self.task_queue.get()
            try:
                # 获取或创建会话 ID（使用 chat_id 作为会话 ID，支持群聊）
                session_id = item["chat_id"]

                message_id = item["message_id"]
                text = item["text"]
                reaction_id = item["reaction_id"]

                # 调用 cai-coder 获取回复
                reply = self.cai_coder.chat(session_id, text)

                # 删除表情
                self._reply_message_reaction_delete(message_id=message_id, reaction_id=reaction_id)

                # 发送回复
                self._reply_message(message_id, reply)

                print(f"[发送回复] message_id={message_id}, reply={reply}")

            finally:
                self.task_queue.task_done()

    def _reply_message_reaction_create(self, message_id: str) -> str:
        emojis = ["MeMeMe","Typing","OneSecond","SLIGHT","ClownFace","SHOCKED","HUG","EMBARRASSED","SMIRK","WOW","KISS"]
        emoji_type = random.choice(emojis)
        request = (
            CreateMessageReactionRequest.builder()
            .message_id(message_id)
            .request_body(
                CreateMessageReactionRequestBody.builder()
                .reaction_type(
                    Emoji.builder().emoji_type(emoji_type).build()
                ).build()
            )
            .build()
        )

        response = self.client2.im.v1.message_reaction.create(request)

        if not response.success():
            print(f"添加表情失败: code={response.code}, msg={response.msg}")
            return ""
        else:
            print("添加表情成功 👍")
            return response.data.reaction_id

    def _reply_message_reaction_delete(self, message_id: str, reaction_id: str):
        request = (
            DeleteMessageReactionRequest.builder()
            .message_id(message_id)
            .reaction_id(reaction_id)
            .build()
        )

        response = self.client2.im.v1.message_reaction.delete(request)

        if not response.success():
            print(f"删除表情失败: code={response.code}, msg={response.msg}")
        else:
            print("删除表情成功 👍")


    def _reply_message(self, message_id: str, text: str):
        """
        发送消息到飞书

        Args:
            chat_id: 聊天 ID
            text: 消息文本
        """
        reply = {
            "zh_cn": {
                "content": [
                    [{
                        "tag": "md",
                        "text": text
                    }]
                ]
            }
        }


        content = json.dumps(reply, ensure_ascii=False, indent=2)
        try:
            request = ReplyMessageRequest.builder() \
                .message_id(message_id) \
                .request_body(ReplyMessageRequestBody.builder()
                              .msg_type("post") # 指定消息类型为文本
                              .content(content)  # 填入 JSON 字符串
                              .build()) \
                .build()

            response = self.client2.im.v1.message.reply(request)

            if not response.success():
                raise Exception(
                    f"client.im.v1.message.reply failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")

        except Exception as e:
            print(f"发送消息时出错: {e}")
            import traceback
            traceback.print_exc()

    def _send_message(self, chat_id: str, text: str):
        """
        发送消息到飞书

        Args:
            chat_id: 聊天 ID
            text: 消息文本
        """
        reply = {"text": text}
        content = json.dumps(reply, ensure_ascii=False, indent=2)
        try:
            request = CreateMessageRequest.builder() \
                .receive_id_type("chat_id") \
                .request_body(CreateMessageRequestBody.builder()
                              .receive_id(chat_id)
                              .msg_type("text")
                              .content(content)
                              .build()) \
                .build()

            response = self.client2.im.v1.message.create(request)

            if not response.success():
                raise Exception(
                    f"client.im.v1.chat.create failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")

        except Exception as e:
            print(f"发送消息时出错: {e}")
            import traceback
            traceback.print_exc()

    def _handle_restart_command(self, chat_id: str, message_id: str):
        """处理重启命令 - 通过 agent 调用重启工具"""
        try:
            # 使用 agent 调用重启工具
            restart_message = "请使用 restart_service 工具重启服务，延迟时间设置为 3 秒"
            restart_response = self.cai_coder.chat(chat_id, restart_message)

            # 发送重启确认消息
            self._reply_message(message_id, f"🔄 {restart_response}")

        except Exception as e:
            print(f"处理重启命令时出错: {e}")
            import traceback
            traceback.print_exc()
            error_msg = f"重启命令处理失败: {str(e)}"
            self._reply_message(message_id, error_msg)

    def start(self):
        """启动机器人"""
        print("=" * 50)
        print("飞书长连接机器人启动中...")
        print(f"APP_ID: {FeishuBotConfig.FEISHU_APP_ID}")
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