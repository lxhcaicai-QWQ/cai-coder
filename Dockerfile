# 使用 Python 3.11 精简版镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖和编译工具
# build-essential: 编译工具包（gcc, g++, make等）
# curl: 用于下载和测试
# git: 版本控制
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 复制依赖文件（先复制依赖文件以利用 Docker 缓存）
COPY requirements.txt .

# 安装 Python 依赖
# --no-cache-dir: 减少镜像大小
# --compile: 编译 .pyc 文件，提高运行时性能
RUN pip install --no-cache-dir --compile -r requirements.txt

# 复制项目代码
COPY . .

# 创建非 root 用户（安全最佳实践）
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# 暴露端口（如果需要）
EXPOSE 8000

# 设置默认命令
CMD ["python", "-m", "agent.cli"]

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import langchain; print('OK')" || exit 1