# Feishu Bot for Cai-Coder

轻量级飞书机器人，将 Cai-Coder AI 能力接入飞书群聊和私聊。

支持两种连接模式：
- **Webhook 模式**（短连接）：飞书服务器主动推送消息
- **SSE 模式**（长连接）：主动连接飞书事件订阅服务

## 🏗️ 架构设计

### Webhook 模式
```
飞书消息 → 飞书机器人服务 → Cai-Coder Web API → LLM
                              ↓
                         飞书返回消息
```

### SSE 事件订阅模式
```
机器人服务 ←─ SSE 长连接 ─→ 飞书事件订阅服务
    ↓
Cai-Coder Web API → LLM
    ↓
飞书返回消息
```

## ✨ 功能特性

### 通用功能
- ✅ 接收和处理飞书文本消息
- ✅ 多轮对话记忆（基于会话 ID）
- ✅ 调用 Cai-Coder Web API 获取 AI 回复
- ✅ 自动会话过期清理（TTL 机制）
- ✅ 支持群聊和私聊
- ✅ 健康检查端点

### Webhook 模式
- ✅ 飞书事件签名验证
- ✅ 实时消息接收

### SSE 事件订阅模式
- ✅ 长连接实时通讯
- ✅ 不需要公网 IP
- ✅ 自动重连机制
- ✅ 双向通讯支持

## 📦 安装

### 1. 安装依赖

```bash
cd feishu-bot
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填入飞书应用信息
```

### 3. 确保已运行 Cai-Coder API

```bash
# 在另一个终端运行 Cai-Coder Web API
cd ..
python -m agent.webapp
```

## 🚀 使用

### 选择连接模式

编辑 `.env` 文件设置 `CONNECTION_MODE`：

```bash
# Webhook 模式（默认）- 需要公网 IP 或内网穿透
CONNECTION_MODE=webhook

# SSE 事件订阅模式 - 不需要公网 IP，长连接
CONNECTION_MODE=subscription
```

### Webhook 模式启动

```bash
cd feishu-bot
python bot.py
```

或使用启动脚本：

```bash
./start.sh
```

### SSE 事件订阅模式启动

```bash
cd feishu-bot
python bot_sse.py
```

或使用启动脚本：

```bash
./start_sse.sh
```

### 使用 uvicorn

```bash
# Webhook 模式
uvicorn bot:app --host 0.0.0.0 --port 8080

# SSE 模式
uvicorn bot_sse:app --host 0.0.0.0 --port 8080
```

### 配置飞书机器人

1. **创建飞书应用**

   访问 [飞书开放平台](https://open.feishu.cn/app) 创建新应用

2. **获取应用凭证**

   - App ID: `cli_xxxxxxxxxxxxxx`
   - App Secret: `xxxxxxxxxxxxxxxxxxxx`

3. **配置事件订阅**

   - 请求地址: `https://your-domain.com/feishu/events`
   - 事件类型: `im.message.receive_v1`

4. **配置机器人权限**

   - `im:message` - 接收消息
   - `im:message:send_as_bot` - 发送消息

5. **发布机器人**

   将应用发布到企业内部或公开版本

## 🔧 配置说明

| 环境变量 | 说明 | 默认值 |
|---------|------|--------|
| `FEISHU_APP_ID` | 飞书应用 ID | - |
| `FEISHU_APP_SECRET` | 飞书应用密钥 | - |
| `FEISHU_ENCRYPT_KEY` | 飞书加密密钥（可选） | - |
| `FEISHU_VERIFICATION_TOKEN` | 飞书验证令牌 | - |
| `CAICODER_API_URL` | Cai-Coder API 地址 | `http://localhost:8000` |
| `CAICODER_MODEL` | Cai-Coder 模型名称 | `cai-coder` |
| `CAICODER_STREAM` | 是否使用流式响应 | `False` |
| `BOT_NAME` | 机器人名称 | `cai-coder` |
| `BOT_PORT` | 机器人服务端口 | `8080` |
| `BOT_HOST` | 机器人服务地址 | `0.0.0.0` |
| `MAX_HISTORY` | 最大对话历史消息数 | `10` |
| `SESSION_TTL` | 会话过期时间（秒） | `3600` |
| `CONNECTION_MODE` | 连接模式 | `webhook` 或 `subscription` |

## 🧪 测试

### 健康检查

```bash
curl http://localhost:8080/health
```

预期响应：

**Webhook 模式：**
```json
{
  "status": "healthy",
  "caicoder_api": "connected",
  "active_sessions": 0
}
```

**SSE 模式：**
```json
{
  "status": "healthy",
  "caicoder_api": "connected",
  "connection_mode": "subscription (SSE)",
  "active_sessions": 0,
  "event_manager_running": true
}
```

### 发送测试消息

在飞书中@机器人，发送消息测试回复。

## 📁 项目结构

```
feishu-bot/
├── bot.py              # 主程序（Webhook 模式）
├── bot_sse.py          # 主程序（SSE 事件订阅模式）
├── client.py           # Cai-Coder API 客户端
├── config.py           # 配置管理
├── event_subscription.py  # 事件订阅服务（SSE）
├── requirements.txt    # Python 依赖
├── .env.example        # 环境变量模板
├── README.md          # 说明文档
├── start.sh            # Webhook 模式启动脚本
└── start_sse.sh        # SSE 模式启动脚本
```

## 🛠️ 技术栈

- **FastAPI**: Web 框架
- **Uvicorn**: ASGI 服务器
- **Pydantic**: 数据验证
- **Requests**: HTTP 客户端
- **Lark-oapi**: 飞书 SDK（用于扩展）

## 🔐 安全说明

- ✅ 支持飞书事件签名验证
- ✅ 使用环境变量存储敏感信息
- ⚠️ 生产环境建议使用 HTTPS
- ⚠️ 不要将 `.env` 文件提交到 Git

## 🚀 部署建议

### Docker 部署

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["python", "bot.py"]
```

### Nginx 反向代理（Webhook 模式）

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /feishu/events {
        proxy_pass http://localhost:8080/feishu/events;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### SSE 模式部署

SSE 模式不需要公网 IP，可以直接在内网运行：

```bash
# 启动机器人
cd feishu-bot
./start_sse.sh
```

确保防火墙允许出站连接（连接到飞书服务器）。

## 📝 下一步优化

- [ ] 支持流式响应
- [ ] 添加命令前缀支持（如 `/help`）
- [ ] 实现飞书富文本消息
- [ ] 添加消息发送重试机制
- [ ] 支持多机器人实例
- [ ] 添加监控和日志
- [ ] 实现 Docker Compose 部署
- [ ] 添加 SSE 模式的性能监控
- [ ] 实现双模式热切换

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License
