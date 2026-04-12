import uuid

from langgraph.checkpoint.sqlite import SqliteSaver

from agent import server

def run():
    config = {"configurable": {"thread_id": "1234" }}
    with SqliteSaver.from_conn_string("../cai-coder-sqlite.db") as checkpointer:
        agent = server.get_agent(checkpointer)

        while True:
            content = input("> ")
            if not content.strip():
                continue

            if content.strip().lower() == "exit":
                break

            for chunk in agent.stream(
                    {"messages": [{"role": "user", "content": f"{content}"}]},
                    stream_mode=["messages"],
                    version="v2",
                    config= config
            ):
                if chunk["type"] == "messages":
                    token, metadata = chunk["data"]
                    print(token.content, end='', flush=True)

            print("\n")

if __name__ == "__main__":
    run()