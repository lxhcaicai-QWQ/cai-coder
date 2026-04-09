import uuid

from agent import server

def run():
    config = {"configurable": {"thread_id": str(uuid.uuid4())  }}
    while True:
        content = input("> ")
        if not content.strip():
            continue

        if content.strip().lower() == "exit":
            break

        agent = server.get_agent()
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