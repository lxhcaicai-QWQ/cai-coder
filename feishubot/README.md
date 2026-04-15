# 飞书长连接机器人

基于飞书长连接接入 cai-coder AI 编程助手的机器人服务。

## 功能特性

- ✅ 使用飞书长连接模式接收消息（无需公网 IP）
- ✅ 调用 cai-coder Web API 获取回复
- ✅ 支持多轮对话和会话记忆
- ✅ 会话自动过期清理
- ✅ 支持群聊和私聊

## 前置条件

1. **cai-coder Web API 已启动**
   ```bash
   cd /root/.openclaw/workspace/cai-coder
   python -m agent.webapp
   ```
   默认运行在 `http://localhost:8000`

2. **飞书企业自建应用**
   - 登录 [飞书开放平台](https://open.feishu.cn/app)
   - 创建企业自建应用
   - 获取 App ID 和 App Secret
   - 配置事件订阅（选择「使用长连接接收事件」）
   - 订阅 `im.message.receive_v1` 事件（接收消息）

## 安装步骤

1. **安装依赖**
   ```bash
   cd /root/.openclaw/workspace/cai-coder/feishubot
   pip install -r requirements.txt
   ```

2. **配置环境变量**
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，填入你的配置
   vim .env
   ```

   配置说明：
   - `FEISHU_APP_ID`: 飞书应用的 App ID
   - `FEISHU_APP_SECRET`: 飞书应用的 App Secret
   - `CAICODER_API_URL`: cai-coder Web API 地址
   - `CAICODER_API_KEY`: cai-coder API 密钥（如果需要认证）
   - `SESSION_TIMEOUT`: 会话超时时间（秒），默认 3600 秒（1 小时）

3. **配置飞书事件订阅**

   在飞书开放平台配置事件订阅：
   1. 进入应用详情页 → 事件与回调 → 事件配置
   2. 添加事件：`im.message.receive_v1`（接收消息）
   3. 订阅方式选择「使用长连接接收事件」
   4. 保存配置（注意：必须先启动机器人服务，才能保存成功）

## 启动机器人

```bash
cd /root/.openclaw/workspace/cai-coder/feishubot
python bot.py
```

启动成功后，会看到：
```
==================================================
飞书长连接机器人启动中...
APP_ID: cli_xxxx
CAICODER_API_URL: http://localhost:8000/v1/chat/completions
会话超时时间: 3600 秒
==================================================
connected to wss://open.feishu.cn/ws/v3/...
```

## 使用说明

1. **在飞书中使用**

   - 将机器人添加到群聊或私聊
   - 发送消息给机器人
   - 机器人会调用 cai-coder 进行回复

2. **多轮对话**

   - 支持上下文记忆，可连续提问
   - 会话超时后自动清理（默认 1 小时）

3. **支持的消息类型**

   - 文本消息
   - @机器人（群聊中）

## 项目结构

```
feishubot/
├── bot.py              # 机器人主程序
├── client.py           # cai-coder API 客户端
├── config.py           # 配置管理
├── requirements.txt    # Python 依赖
├── .env.example        # 环境变量模板
└── README.md          # 说明文档
```

## 常见问题

### Q: 保存事件订阅配置失败？
A: 请确保机器人服务已启动，且能够访问公网。长连接需要先建立连接才能保存配置。

### Q: 机器人不回复？
A: 检查以下几点：
- cai-coder Web API 是否正常运行
- .env 配置是否正确
- 飞书应用是否订阅了 `im.message.receive_v1` 事件

### Q: 如何调试？
A: 机器人默认使用 `LogLevel.DEBUG`，会在控制台输出详细日志。

## 技术架构

```
飞书平台 → 长连接 (WebSocket) → 飞书机器人 → cai-coder Web API → cai-coder Agent
                                ↓
                         会话管理 & 消息转发
```

## 相关文档

- [飞书长连接接入文档](https://open.feishu.cn/document/server-docs/event-subscription-guide/event-subscription-configure-/request-url-configuration-case)
- [cai-coder Web API](/root/.openclaw/workspace/cai-coder/agent/webapp.py)
