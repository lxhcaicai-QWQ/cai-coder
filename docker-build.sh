#!/bin/bash

# Docker 构建和运行脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 函数：打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    print_error "Docker 未安装，请先安装 Docker"
    exit 1
fi

# 检查 Docker Compose 是否安装
if ! command -v docker-compose &> /dev/null; then
    print_warning "Docker Compose 未安装，将使用 Docker 命令"
fi

# 构建镜像
print_info "开始构建 Docker 镜像..."
docker build -t cai-coder:latest .

if [ $? -eq 0 ]; then
    print_success "Docker 镜像构建成功"
else
    print_error "Docker 镜像构建失败"
    exit 1
fi

# 显示镜像信息
print_info "镜像信息："
docker images | grep cai-coder

# 询问是否要运行容器
echo
read -p "是否要运行容器？(y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "启动容器..."
    
    # 检查是否有 .env 文件
    if [ ! -f .env ]; then
        print_warning ".env 文件不存在，将创建一个示例文件"
        cp .env.example .env
        print_warning "请编辑 .env 文件并设置正确的环境变量"
    fi
    
    # 使用 docker-compose 启动（如果可用）
    if command -v docker-compose &> /dev/null; then
        docker-compose up -d
        print_success "容器已启动"
        print_info "查看日志：docker-compose logs -f"
        print_info "停止容器：docker-compose down"
    else
        # 使用 docker 命令启动
        docker run -d \
            --name cai-coder \
            -e OPENAI_BASE_URL="${OPENAI_BASE_URL:-https://api.openai.com/v1}" \
            -e OPENAI_API_KEY="${OPENAI_API_KEY}" \
            -e OPENAI_MODEL="${OPENAI_MODEL:-gpt-3.5-turbo}" \
            -p 8000:8000 \
            cai-coder:latest
        
        if [ $? -eq 0 ]; then
            print_success "容器已启动"
            print_info "查看日志：docker logs -f cai-coder"
            print_info "进入容器：docker exec -it cai-coder bash"
            print_info "停止容器：docker stop cai-coder"
        else
            print_error "容器启动失败"
        fi
    fi
fi

echo
print_info "使用说明："
echo "1. 构建：docker build -t cai-coder:latest ."
echo "2. 运行：docker run -it cai-coder:latest"
echo "3. 交互式：docker run -it cai-coder:latest bash"
echo "4. 查看日志：docker logs cai-coder"