import requests
import json
from typing import Optional, Dict, Any

from langchain_core.tools import tool


def _http_request_impl(
    url: str,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, str]] = None,
    data: Optional[Dict[str, Any]] = None,
    json_data: Optional[Dict[str, Any]] = None,
    timeout: int = 30
) -> Dict[str, Any]:
    """
    发送 HTTP 请求的实现函数

    Args:
        url: 请求的 URL
        method: HTTP 方法 (GET, POST, PUT, DELETE, etc.)
        headers: 请求头字典
        params: URL 查询参数
        data: 表单数据
        json_data: JSON 数据
        timeout: 超时时间（秒）

    Returns:
        包含响应信息的字典
    """
    try:
        # 统一处理方法名为大写
        method = method.upper()

        # 默认请求头
        if headers is None:
            headers = {}

        # 如果有 JSON 数据，自动设置 Content-Type
        if json_data is not None and 'Content-Type' not in headers:
            headers['Content-Type'] = 'application/json'

        # 发送请求
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            data=data,
            json=json_data,
            timeout=timeout
        )

        # 尝试解析 JSON 响应
        try:
            response_json = response.json()
        except json.JSONDecodeError:
            response_json = None

        # 返回结构化的响应信息
        return {
            "success": True,
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "content": response.text,
            "json": response_json,
            "url": response.url,
            "elapsed_time": response.elapsed.total_seconds()
        }

    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }


@tool
def http_request(
    url: str,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, str]] = None,
    data: Optional[Dict[str, Any]] = None,
    json_data: Optional[Dict[str, Any]] = None,
    timeout: int = 30
) -> Dict[str, Any]:
    """
    发送 HTTP 请求的工具

    Args:
        url: 请求的 URL
        method: HTTP 方法 (GET, POST, PUT, DELETE, etc.)
        headers: 请求头字典
        params: URL 查询参数
        data: 表单数据
        json_data: JSON 数据
        timeout: 超时时间（秒）

    Returns:
        包含响应信息的字典
    """
    return _http_request_impl(
        url=url,
        method=method,
        headers=headers,
        params=params,
        data=data,
        json_data=json_data,
        timeout=timeout
    )


@tool
def http_get(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, str]] = None,
    timeout: int = 30
) -> Dict[str, Any]:
    """发送 GET 请求的便捷方法"""
    # 使用 invoke 方法调用 http_request
    return http_request.invoke({
        "url": url,
        "method": "GET",
        "headers": headers,
        "params": params,
        "timeout": timeout
    })


@tool
def http_post(
    url: str,
    data: Optional[Dict[str, Any]] = None,
    json_data: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 30
) -> Dict[str, Any]:
    """发送 POST 请求的便捷方法"""
    # 使用 invoke 方法调用 http_request
    return http_request.invoke({
        "url": url,
        "method": "POST",
        "headers": headers,
        "data": data,
        "json_data": json_data,
        "timeout": timeout
    })