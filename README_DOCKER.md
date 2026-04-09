# Docker 部署指南

本项目支持 Docker 容器化部署，方便在不同环境中快速运行和测试。

## 🐳 快速开始

### 1. 构建镜像

```bash
# 克隆项目
git clone https://github.com/lxhcaicai-QWQ/cai-coder.git
cd cai-coder

# 切换到 feature_docker 分支
git checkout feature_docker

# 使用构建脚本（推荐）
./docker-build.sh

# 或手动构建
docker build -t cai-coder:latest .
```

### 2. 运行容器

#### 交互式运行（推荐用于测试）
```bash
# 启动容器并进入 bash
docker run -it --rm cai-coder:latest bash

# 在容器中运行代理
python -m agent.cli
```

#### 后台运行
```bash
# 使用 docker-compose（推荐）
cp .env.example .env
# 编辑 .env 文件设置环境变量
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

#### 直接运行
```bash
docker run -d \
  --name cai-coder \
  -e OPENAI_BASE_URL=https://api.openai.com/v1 \
  -e OPENAI_API_KEY=your_api_key \
  -e OPENAI_MODEL=gpt-3.5-turbo \
  -p 8000:8000 \
  cai-coder:latest
```

## 🔧 环境变量

创建 `.env` 文件并设置以下环境变量：

```bash
# OpenAI 配置
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-3.5-turbo

# 可选配置
DEBUG=false
LOG_LEVEL=INFO
```

## 📁 项目结构

```
cai-coder/
├── Dockerfile              # Docker 镜像定义
├── docker-compose.yml      # Docker Compose 配置
├── .dockerignore          # Docker 构建排除文件
├── .env.example           # 环境变量示例
├── docker-build.sh        # 构建脚本
├── agent/                 # 核心代理代码
├── tests/                 # 测试代码
└── requirements.txt       # Python 依赖
```

## 🏗️ Docker 镜像特性

### 基础镜像
- 使用 `python:3.11-slim` 精简版镜像
- 镜像大小优化，包含必要的编译工具

### 安装的依赖
- Python 3.11
- build-essential (编译工具)
- curl (网络工具)
- git (版本控制)
- 项目 Python 依赖

### 安全特性
- 使用非 root 用户运行
- 最小权限原则

### 性能优化
- 编译 Python 字节码
- 多阶段构建（可扩展）
- 优化镜像层数

## 🚀 开发工作流

### 本地开发
```bash
# 运行容器并挂载本地代码
docker run -it --rm \
  -v $(pwd):/app \
  -e OPENAI_API_KEY=your_api_key \
  cai-coder:latest bash
```

### 运行测试
```bash
# 在容器中运行测试
docker run --rm cai-coder:latest python -m pytest tests/

# 运行 HTTP 工具测试
docker run --rm cai-coder:latest python demo_http_tool.py
```

### 构建优化
```bash
# 多阶段构建示例（如果需要）
docker build -f Dockerfile.optimized -t cai-coder:optimized .
```

## 🔍 常用命令

### 查看镜像
```bash
docker images | grep cai-coder
```

### 查看容器
```bash
docker ps | grep cai-coder
```

### 查看日志
```bash
docker logs cai-coder
```

### 进入容器
```bash
docker exec -it cai-coder bash
```

### 清理资源
```bash
# 停止并删除容器
docker stop cai-coder && docker rm cai-coder

# 删除镜像
docker rmi cai-coder:latest

# 清理未使用的资源
docker system prune -f
```

## 🐛 故障排除

### 1. 构建失败
- 检查 Docker 是否正确安装
- 确保网络连接正常
- 查看构建错误日志

### 2. 容器启动失败
- 检查环境变量是否正确设置
- 查看容器日志：`docker logs cai-coder`

### 3. 权限问题
- 确保当前用户有 Docker 执行权限
- 在 Linux 上可能需要：`sudo usermod -aG docker $USER`

### 4. 网络问题
- 检查防火墙设置
- 确保端口未被占用

## 📝 更新日志

- v1.0.0: 初始 Docker 支持
  - Python 3.11 精简镜像
  - 包含编译工具
  - 优化的 Dockerfile
  - Docker Compose 支持

---

如有问题或建议，请提交 Issue 或 Pull Request。