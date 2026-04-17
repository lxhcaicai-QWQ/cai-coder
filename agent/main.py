import threading

from agent import webapp
from agent.integration.feishu.bot import FeishuBot
from agent.utils.logger import get_logger

logger = get_logger("main")

if __name__ == "__main__":
    logger.info("=" * 50)
    logger.info("Cai-Coder 服务启动中...")
    logger.info("=" * 50)

    def run():
        bot = FeishuBot()
        bot.start()
    thread = threading.Thread(target=run, daemon=True)
    thread.start()

    webapp.start()