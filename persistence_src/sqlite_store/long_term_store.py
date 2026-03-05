"""
LongTermMemoryStore: 长期记忆存 memory/*.md。

按 user_id 分子目录，每个文件为 Markdown，支持可选 YAML frontmatter。
"""

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


# frontmatter 正则：---\n...\n---
FM_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)


def _parse_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    """解析 YAML frontmatter，返回 (metadata, body)。无 yaml 时用简单 key: value 解析。"""
    m = FM_PATTERN.match(content.strip())
    if not m:
        return {}, content
    raw_fm = m.group(1).strip()
    try:
        import yaml
        meta = yaml.safe_load(raw_fm) or {}
    except Exception:
        meta = {}
        for line in raw_fm.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip().strip('"\'')
    return meta, m.group(2).strip()


def _format_frontmatter(meta: dict[str, Any], body: str) -> str:
    """生成带 frontmatter 的 md 内容。"""
    try:
        import yaml
        fm = yaml.dump(meta, allow_unicode=True, sort_keys=False).strip()
    except Exception:
        fm = "\n".join(f"{k}: {v}" for k, v in meta.items())
    return f"---\n{fm}\n---\n\n{body}"


class LongTermMemoryStore:
    """
    长期记忆：Markdown 文件存储在 memory/ 目录下。
    """

    def __init__(self, base_dir: str | Path = "memory"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _user_dir(self, user_id: str) -> Path:
        safe = "".join(c if c.isalnum() or c in "_-" else "_" for c in user_id)
        return self.base_dir / safe

    def put(
        self,
        user_id: str,
        filename: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> Path:
        """
        写入长期记忆文件。
        filename: 如 preferences.md, facts.md, 2025-03-05_topic.md
        content: 正文 Markdown
        metadata: 可选 frontmatter 字段，自动添加 user_id、updated_at
        """
        meta = dict(metadata or {})
        meta["user_id"] = user_id
        meta["updated_at"] = _utc_now()
        dirpath = self._user_dir(user_id)
        dirpath.mkdir(parents=True, exist_ok=True)
        path = dirpath / filename
        path.write_text(_format_frontmatter(meta, content), encoding="utf-8")
        return path

    def get(self, user_id: str, filename: str) -> dict[str, Any] | None:
        """
        读取长期记忆文件，返回 {metadata, content, path}。
        若文件不存在返回 None。
        """
        path = self._user_dir(user_id) / filename
        if not path.exists():
            return None
        raw = path.read_text(encoding="utf-8")
        meta, body = _parse_frontmatter(raw)
        return {"metadata": meta, "content": body or raw, "path": str(path)}

    def list_files(self, user_id: str | None = None) -> list[dict[str, Any]]:
        """
        列出长期记忆文件。
        user_id 为空时列出所有用户目录下的文件。
        """
        out = []
        if user_id:
            dirpath = self._user_dir(user_id)
            if not dirpath.exists():
                return []
            for p in dirpath.glob("*.md"):
                raw = p.read_text(encoding="utf-8")
                meta, _ = _parse_frontmatter(raw)
                out.append({"path": str(p), "filename": p.name, "metadata": meta})
        else:
            for user_dir in self.base_dir.iterdir():
                if user_dir.is_dir():
                    for p in user_dir.glob("*.md"):
                        raw = p.read_text(encoding="utf-8")
                        meta, _ = _parse_frontmatter(raw)
                        out.append({"path": str(p), "filename": p.name, "metadata": meta})
        return out
