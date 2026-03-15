"""Markdown report generator"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from .base import BaseReport


class MarkdownReport(BaseReport):
    """Generate Markdown format report"""

    def generate(self) -> str:
        """Generate markdown report"""
        drug_name = self.data.get('drug_name', 'Unknown')
        mode = self.data.get('mode', 'unknown')
        report_content = self.data.get('report', '')
        sources = self.data.get('sources', [])
        sources_count = self.data.get('sources_count', len(sources))

        lines = [
            f"# {drug_name} 早期肿瘤管线分析报告",
            "",
            f"**生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**研究模式:** 6轮分维度深度搜索 (6-Round Deep Search)",
            f"**数据来源:** {sources_count} 个公开来源",
            "",
            "---",
            "",
        ]

        # Main report content
        lines.append(report_content)
        lines.append("")
        lines.append("---")
        lines.append("")

        # Sources section
        lines.append("## 数据来源")
        lines.append("")

        for i, source in enumerate(sources, 1):
            title = source.get('title', 'Untitled')
            url = source.get('url', '')
            score = source.get('score', 0)
            lines.append(f"{i}. [{title}]({url})" + (f" (相关度: {score:.2f})" if score else ""))

        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("*本报告由 AI 自动生成，仅供参考。关键数据请通过官方渠道验证。*")

        return '\n'.join(lines)

    def save(self, filepath: str) -> str:
        """Save markdown report to file"""
        content = self.generate()
        Path(filepath).write_text(content, encoding='utf-8')
        return filepath
