# 使用 Python 3.11 精简版镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 复制依赖文件（先复制依赖文件以利用 Docker 缓存）
COPY pyproject.toml .

RUN pip install --no-cache-dir \
    -i https://pypi.tuna.tsinghua.edu.cn/simple \
    --compile \
    -e ".[dev]"

# 复制项目代码
COPY . .

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import langchain; print('OK')" || exit 1

CMD ["python", "agent/main.py"]