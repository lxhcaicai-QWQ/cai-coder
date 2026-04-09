import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agent.tools.http_request import http_request, http_get, http_post


def demo_http_get():
    """演示 GET 请求"""
    print("=== GET 请求演示 ===")
    result = http_get("https://httpbin.org/get")
    if result["success"]:
        print(f"状态码: {result['status_code']}")
        print(f"请求URL: {result['url']}")
        print(f"响应时间: {result['elapsed_time']:.2f}s")
        print(f"响应数据: {result['json']}")
    else:
        print(f"请求失败: {result['error']}")


def demo_http_post():
    """演示 POST 请求"""
    print("\n=== POST 请求演示 ===")
    data = {"name": "cai-coder", "version": "1.0.0", "author": "lxhcaicai-QWQ"}
    result = http_post("https://httpbin.org/post", json_data=data)
    if result["success"]:
        print(f"状态码: {result['status_code']}")
        print(f"发送的数据: {result['json']['json']}")
    else:
        print(f"请求失败: {result['error']}")


def demo_http_with_headers():
    """演示带请求头的请求"""
    print("\n=== 带请求头的请求演示 ===")
    headers = {
        "User-Agent": "cai-coder/1.0.0",
        "Accept": "application/json",
        "X-Custom-Header": "test-value"
    }
    result = http_get("https://httpbin.org/headers", headers=headers)
    if result["success"]:
        print(f"请求头: {result['json']['headers']}")
    else:
        print(f"请求失败: {result['error']}")


def demo_api_call():
    """演示调用真实 API"""
    print("\n=== API 调用演示 ===")
    
    # 获取 GitHub 用户信息
    result = http_get("https://api.github.com/users/lxhcaicai-QWQ")
    if result["success"]:
        user_info = result['json']
        print(f"用户名: {user_info.get('login')}")
        print(f"公开仓库数: {user_info.get('public_repos')}")
        print(f"关注者: {user_info.get('followers')}")
        print(f"创建时间: {user_info.get('created_at')}")
    else:
        print(f"获取用户信息失败: {result['error']}")


if __name__ == "__main__":
    print("HTTP 请求工具演示")
    print("=" * 50)
    
    demo_http_get()
    demo_http_post()
    demo_http_with_headers()
    demo_api_call()
    
    print("\n演示完成!")