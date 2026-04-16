import threading

from agent import webapp
from agent.integration.feishu.bot import FeishuBot

if __name__ == "__main__":
    def run():
        bot = FeishuBot()
        bot.start()
    thread = threading.Thread(target=run, daemon=True)
    thread.start()

    webapp.start()