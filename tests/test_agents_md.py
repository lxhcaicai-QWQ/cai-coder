"""
测试 AGENTS.md 加载功能
"""
import os
import pytest
from unittest.mock import patch

from agent.prompt import construct_system_prompt, read_agents_md


class TestAgentsMdLoading:
    """测试 AGENTS.md 文件加载"""

    def test_read_agents_md_exists(self):
        """测试 AGENTS.md 存在时能正确读取"""
        content = read_agents_md()
        assert content is not None
        assert "cai-coder 项目指南" in content
        assert "项目结构" in content

    def test_read_agents_md_contains_key_sections(self):
        """测试 AGENTS.md 包含关键章节"""
        content = read_agents_md()
        assert "### 项目概述" in content
        assert "### 环境配置" in content
        assert "### 常用命令" in content
        assert "### 代码风格" in content

    def test_construct_system_prompt_includes_agents_md(self):
        """测试系统提示词包含 AGENTS.md 内容"""
        prompt = construct_system_prompt()
        assert "## Role & Objectives" in prompt  # 基础提示词
        assert "cai-coder 项目指南" in prompt  # AGENTS.md 内容

    def test_construct_system_prompt_has_separator(self):
        """测试系统提示词中基础内容和 AGENTS.md 之间有分隔线"""
        prompt = construct_system_prompt()
        assert "=" * 50 in prompt

    @patch('agent.prompt.os.path.exists')
    def test_read_agents_md_not_exists(self, mock_exists):
        """测试 AGENTS.md 不存在时返回 None"""
        mock_exists.return_value = False
        content = read_agents_md()
        assert content is None

    def test_agents_md_content_integrity(self):
        """测试 AGENTS.md 内容完整性"""
        content = read_agents_md()
        assert len(content) > 0
        assert "### 项目概述" in content
        assert "### 项目结构" in content
        assert "### 环境配置" in content
        assert "### 常用命令" in content
        assert "### 代码风格" in content
        assert "### 开发注意事项" in content
        assert "### AI 代理能力" in content
        assert "### 已知限制" in content
        assert "### Docker 支持" in content

    def test_system_prompt_order(self):
        """测试系统提示词的顺序正确：基础 -> 分隔线 -> AGENTS.md"""
        prompt = construct_system_prompt()

        # 找到各个部分的位置
        role_pos = prompt.find("## Role & Objectives")
        separator_pos = prompt.find("=" * 50)
        agents_md_pos = prompt.find("cai-coder 项目指南")

        # 验证顺序
        assert role_pos < separator_pos < agents_md_pos, \
            "系统提示词顺序应该是：基础提示词 -> 分隔线 -> AGENTS.md"
