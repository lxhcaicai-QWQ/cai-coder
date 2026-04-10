## cai-coder 项目指南

### 项目概述
cai-coder 是一个基于 LangChain/LangGraph 的 AI 编码助手，可以帮助用户完成代码编写、文件操作、HTTP 请求等任务。

### 项目结构
```
cai-coder/
├── agent/              # 核心代理代码
│   ├── __init__.py
│   ├── cli.py         # CLI 入口程序
│   ├── server.py      # Agent 服务，包含 LLM 和工具配置
│   ├── prompt.py      # 系统提示词构建
│   └── tools/         # 工具函数集合
│       ├── __init__.py
│       ├── bash.py    # Bash 命令执行
│       ├── files.py   # 文件读写操作
│       └── http.py    # HTTP 请求工具
├── app/               # 应用代码（示例：snake-game）
├── tests/             # 测试代码
│   ├── test_agent.py
│   ├── test_agent_generate_code.py
│   ├── test_http_request.py
│   └── test_tools.py
├── requirements.txt   # Python 依赖
├── pytest.ini         # pytest 配置
├── .example.env       # 环境变量示例
├── Dockerfile         # Docker 构建文件
└── AGENTS.md          # 本文件：AI 代理项目指南
```

### 环境配置
1. 复制环境变量文件：
   ```bash
   cp .example.env .env
   ```

2. 编辑 `.env` 文件，填入你的配置：
   ```
   OPENAI_BASE_URL=https://api.your-service.com/v1
   OPENAI_API_KEY=your-api-key-here
   OPENAI_MODEL=gpt-4
   ```

### 常用命令
- 安装依赖: `pip install -r requirements.txt`
- 运行 CLI: `python -m agent.cli`
- 运行所有测试: `pytest tests/`
- 运行特定测试: `pytest tests/test_agent.py -v`

### 代码风格
- 使用 type hints
- 遵循 PEP 8 规范
- 文档字符串使用 Google Style
- 函数命名使用 snake_case
- 类名使用 PascalCase

### 开发注意事项
- 新增工具需要在 `agent/server.py` 的 `get_agent()` 中注册
- 系统提示词由基础部分（agent/prompt.py）+ AGENTS.md 组成
- 记忆系统使用 LangGraph 的 InMemorySaver（会话级别）
- 工具函数放在 `agent/tools/` 目录下

### AI 代理能力
当前集成的工具包括：
- **文件操作**: read_file, write_file, ls
- **Bash 执行**: bash
- **HTTP 请求**: http_request, http_get, http_post
- **天气查询**: get_weather

### 已知限制
- 当前仅支持会话级记忆，重启后会丢失
- 暂不支持多会话共享记忆

### Docker 支持
项目支持 Docker 容器化部署：
- 构建镜像: `docker build -t cai-coder .`
- 运行容器: `docker run -it cai-coder`
