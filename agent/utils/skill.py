import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List

import yaml


@dataclass
class SkillRecord:
    name: str
    description: str
    location: Path  # SKILL.md 绝对路径
    body: Optional[str] = None  # 激活时再读也可以；这里支持在发现时就读入

    @property
    def skill_dir(self) -> Path:
        return self.location.parent


# 默认跳过的目录名（避免扫描过深）
SKIP_DIRS = {
    ".git", ".svn", "__pycache__", "node_modules", "venv", ".venv", ".tox"
}

def find_skill_dirs_in_root(
    root: Path,
    max_depth: int = 4,
) -> List[Path]:
    """
    在 root 下寻找包含 SKILL.md 的子目录（≤ max_depth 层）。
    简化版：不严格处理符号环，可通过 max_depth 限制规模。
    """
    skill_dirs: List[Path] = []

    def walk(current: Path, depth: int):
        if depth > max_depth:
            return
        try:
            entries = list(current.iterdir())
        except Exception:
            return  # 权限/不存在等

        for entry in entries:
            if not entry.is_dir():
                continue
            if entry.name in SKIP_DIRS:
                continue
            # 如果目录下直接有 SKILL.md，则视为技能目录
            if (entry / "SKILL.md").is_file():
                skill_dirs.append(entry)
            else:
                # 否则继续向下搜索
                walk(entry, depth + 1)

    walk(root, 0)
    return skill_dirs



def parse_skill_md(
    skill_md_path: Path,
    *,
    read_body_now: bool = False,
) -> SkillRecord:
    """
    解析单个 SKILL.md：
    - 提取 YAML frontmatter（name/description）
    - 提取 body（markdown 部分）
    - 宽松兼容：常见“未加引号冒号”等问题会尝试修复重试
    - 返回 (SkillRecord)
    """
    text = skill_md_path.read_text(encoding="utf-8")

    # 分割 frontmatter 与 body
    parts = re.split(r"^-{3,}\s*$", text, flags=re.MULTILINE)
    if len(parts) < 3:
        # 尝试只有一行开头 --- 的情况（不太常见）
        if text.startswith("---"):
            parts2 = re.split(r"^-{3,}\s*$", text[3:], flags=re.MULTILINE)
            if len(parts2) >= 2:
                parts = [""] + parts2

    yaml_part = parts[1].strip()
    body_part = ("\n".join(parts[2:])).strip()

    # 尝试解析 YAML；失败时做简单的“给值加引号”重试
    data = yaml.safe_load(yaml_part) or {}

    name = str(data.get("name", "")).strip()
    description = str(data.get("description", "")).strip()

    record = SkillRecord(
        name=name,
        description=description,
        location=skill_md_path,
        body=body_part if read_body_now else None,
    )
    return record


def render_skills_json(
    root_path: Path,
    expose_location: bool = True,
) -> Optional[str]:
    pathlist = find_skill_dirs_in_root(root_path)

    items = []
    for path in pathlist:
        skill_md = path / "SKILL.md"
        skill_record = parse_skill_md(skill_md)
        item: dict = {"name": skill_record.name, "description": skill_record.description}
        if expose_location:
            item["location"] = str(skill_record.location)
        items.append(item)

    if not items:
        return None

    return json.dumps({"available_skills":items}, ensure_ascii=False, indent=2)