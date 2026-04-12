import pytest
from agent.tools.http_request import http_get, http_post


def test_http_get():
    """测试 GET 请求"""
    # 使用 httpbin.org 测试
    result = http_get.invoke({"url": "https://httpbin.org/get"})
    assert result["success"] is True
    assert result["status_code"] == 200
    assert "json" in result
    assert result["json"]["url"] == "https://httpbin.org/get"


def test_http_post():
    """测试 POST 请求"""
    # 使用 httpbin.org 测试
    test_data = {"name": "test", "value": 123}
    result = http_post.invoke({"url": "https://httpbin.org/post", "json_data": test_data})
    assert result["success"] is True
    assert result["status_code"] == 200
    assert result["json"]["json"] == test_data


def test_http_with_headers():
    """测试带请求头的请求"""
    headers = {"User-Agent": "test-agent", "Accept": "application/json"}
    result = http_get.invoke({"url": "https://httpbin.org/headers", "headers": headers})
    assert result["success"] is True
    assert result["status_code"] == 200
    assert "headers" in result


def test_http_with_params():
    """测试带查询参数的请求"""
    params = {"param1": "value1", "param2": "value2"}
    result = http_get.invoke({"url": "https://httpbin.org/get", "params": params})
    assert result["success"] is True
    assert result["status_code"] == 200
    assert result["json"]["args"] == params


def test_http_error_handling():
    """测试错误处理"""
    # 测试不存在的 URL
    result = http_get.invoke({"url": "https://nonexistent-domain-12345.com"})
    assert result["success"] is False
    assert "error" in result


def test_http_404_error():
    """测试 404 错误"""
    result = http_get.invoke({"url": "https://httpbin.org/status/404"})
    assert result["success"] is True  # 请求成功，只是状态码是 404
    assert result["status_code"] == 404