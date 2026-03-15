"""PDF report generator using Markdown → HTML → Browser headless print"""

import os
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from .base import BaseReport

try:
    import markdown
    MD_AVAILABLE = True
except ImportError:
    MD_AVAILABLE = False


def _find_browser() -> Optional[str]:
    """Find Chrome or Edge browser executable"""
    candidates = [
        # Edge
        "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
        "C:/Program Files/Microsoft/Edge/Application/msedge.exe",
        # Chrome
        "C:/Program Files/Google/Chrome/Application/chrome.exe",
        "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
        # Linux
        "/usr/bin/google-chrome",
        "/usr/bin/chromium-browser",
        "/usr/bin/microsoft-edge",
        # macOS
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    ]
    for p in candidates:
        if Path(p).exists():
            return p
    return None


# CSS stylesheet for PDF rendering
PDF_CSS = """
@page {
    size: A4;
    margin: 2cm;
}

body {
    font-family: "Microsoft YaHei", "SimHei", "PingFang SC", "Noto Sans CJK SC", sans-serif;
    font-size: 12px;
    line-height: 1.7;
    color: #333;
}

h1 {
    font-size: 22px;
    color: #1a1a2e;
    border-bottom: 2px solid #1a1a2e;
    padding-bottom: 6px;
    margin-top: 24px;
    margin-bottom: 12px;
}

h2 {
    font-size: 18px;
    color: #16213e;
    border-bottom: 1px solid #ccc;
    padding-bottom: 4px;
    margin-top: 20px;
    margin-bottom: 10px;
}

h3 {
    font-size: 15px;
    color: #0f3460;
    margin-top: 14px;
    margin-bottom: 6px;
}

h4, h5 {
    font-size: 13px;
    color: #333;
    margin-top: 10px;
    margin-bottom: 4px;
}

table {
    border-collapse: collapse;
    width: 100%;
    margin: 12px 0;
    font-size: 11px;
}

th {
    background-color: #1a1a2e;
    color: #fff;
    font-weight: bold;
    padding: 8px 10px;
    border: 1px solid #555;
    text-align: left;
}

td {
    padding: 6px 10px;
    border: 1px solid #ddd;
    text-align: left;
}

tr:nth-child(even) td {
    background-color: #f8f8f8;
}

ul, ol {
    margin: 8px 0;
    padding-left: 28px;
}

li {
    margin-bottom: 4px;
}

a {
    color: #0066cc;
    text-decoration: none;
}

hr {
    border: none;
    border-top: 1px solid #ccc;
    margin: 20px 0;
}

p {
    margin: 6px 0;
}

strong {
    font-weight: bold;
}

em {
    font-style: italic;
}

code {
    background-color: #f0f0f0;
    padding: 2px 5px;
    border-radius: 3px;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 11px;
}

pre {
    background-color: #f5f5f5;
    padding: 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 11px;
    overflow-x: auto;
}

blockquote {
    border-left: 4px solid #1a1a2e;
    margin: 10px 0;
    padding: 8px 16px;
    background-color: #f9f9f9;
    color: #555;
}

.title-page {
    text-align: center;
    padding-top: 40px;
    margin-bottom: 20px;
}

.title-page h1 {
    font-size: 28px;
    border: none;
    color: #1a1a2e;
}

.title-page .subtitle {
    font-size: 16px;
    color: #555;
    margin-top: 10px;
}

.metadata {
    font-size: 12px;
    color: #666;
    margin-top: 20px;
}

.disclaimer {
    font-size: 10px;
    color: #999;
    font-style: italic;
    margin-top: 24px;
    border-top: 1px solid #eee;
    padding-top: 10px;
}

.sources-section {
    font-size: 11px;
}

.sources-section li {
    margin-bottom: 3px;
    word-break: break-all;
}
"""


def _build_html(data: Dict[str, Any]) -> str:
    """Build complete HTML document from research data"""
    drug_name = data.get('drug_name', 'Unknown')
    report_content = data.get('report', '')
    sources = data.get('sources', [])
    sources_count = data.get('sources_count', len(sources))

    # Convert markdown report to HTML
    md = markdown.Markdown(extensions=['tables', 'fenced_code'])
    report_html = md.convert(report_content)

    # Build sources HTML
    sources_html = ""
    if sources:
        sources_html = '<div class="sources-section"><h2>数据来源</h2><ol>'
        for source in sources:
            title = source.get('title', 'Untitled')
            url = source.get('url', '')
            score = source.get('score', 0)
            score_str = f" (相关度: {score:.2f})" if score else ""
            sources_html += f'<li><a href="{url}">{title}</a>{score_str}</li>'
        sources_html += '</ol></div>'

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
{PDF_CSS}
</style>
</head>
<body>

<div class="title-page">
    <h1>{drug_name}</h1>
    <div class="subtitle">早期肿瘤管线分析报告</div>
    <div class="metadata">
        <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>研究模式: 6轮分维度深度搜索 (6-Round Deep Search)</p>
        <p>数据来源: {sources_count} 个公开来源</p>
    </div>
</div>

<hr>

{report_html}

<hr>

{sources_html}

<div class="disclaimer">
本报告由 AI 自动生成，仅供参考。关键数据请通过官方渠道验证。
</div>

</body>
</html>"""

    return html


class PDFReport(BaseReport):
    """Generate PDF report via Markdown → HTML → Browser headless print"""

    def __init__(self, data: Dict[str, Any]):
        super().__init__(data)
        if not MD_AVAILABLE:
            raise ImportError("markdown not installed. Run: pip install markdown")

    def generate(self) -> str:
        return _build_html(self.data)

    def save(self, filepath: str) -> str:
        if not MD_AVAILABLE:
            raise ImportError("markdown not installed")

        browser = _find_browser()
        if not browser:
            raise RuntimeError("No Chrome/Edge browser found for PDF generation")

        html = _build_html(self.data)

        # Write HTML to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html',
                                         delete=False, encoding='utf-8') as f:
            f.write(html)
            html_path = f.name

        try:
            abs_pdf = str(Path(filepath).resolve())
            result = subprocess.run(
                [browser, '--headless', '--disable-gpu',
                 f'--print-to-pdf={abs_pdf}',
                 '--no-pdf-header-footer',
                 html_path],
                capture_output=True, timeout=60
            )
            if not Path(abs_pdf).exists():
                raise RuntimeError(f"PDF not created. stderr: {result.stderr.decode(errors='ignore')[:200]}")
        finally:
            os.unlink(html_path)

        return filepath


def generate_pdf(data: Dict[str, Any], filepath: str) -> Optional[str]:
    """Helper function to generate PDF report"""
    if not MD_AVAILABLE:
        return None

    try:
        report = PDFReport(data)
        return report.save(filepath)
    except Exception as e:
        print(f"[WARN] PDF generation failed: {e}")
        return None
