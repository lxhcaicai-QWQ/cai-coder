from agent.bus.bus import MessageBus
from agent.bus.events import OutMessage
from agent.integration.feishu.bot import FeishuChannel


def _make_channel() -> FeishuChannel:
    channel = FeishuChannel(MessageBus())
    return channel


def test_feishu_channel():
    feishu = _make_channel()
    feishu._handle_message(
        chat_id="chat_id",
        content="input content",
        metadata={
            "chat_id": "chat_id",
            "message_id": "message_id",
            "text": "data: input content",
            "reaction_id": "reaction_id",
        }
    )

    msg = feishu.bus.consume_inbound()

    assert msg.channel == "feishu"
    assert msg.chat_id == "chat_id"
    assert msg.content == "input content"
    assert msg.metadata == {
            "chat_id": "chat_id",
            "message_id": "message_id",
            "text": "data: input content",
            "reaction_id": "reaction_id",
        }

    out_message = OutMessage(
        channel=msg.channel,
        chat_id="chat_id",
        content="response content",
        metadata=msg.metadata
    )

    feishu.bus.publish_outbound(out_message)

    output_messages = feishu.bus.consume_outbound()

    assert output_messages.channel == "feishu"
    assert output_messages.chat_id == "chat_id"
    assert output_messages.content == "response content"
    assert output_messages.metadata == {
            "chat_id": "chat_id",
            "message_id": "message_id",
            "text": "data: input content",
            "reaction_id": "reaction_id",
        }





