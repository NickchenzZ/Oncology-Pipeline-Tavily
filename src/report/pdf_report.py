"""PDF report generator using Markdown → HTML → PDF pipeline"""

import io
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from .base import BaseReport

try:
    import markdown
    from xhtml2pdf import pisa
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


# CSS stylesheet for PDF rendering
PDF_CSS = """
@page {
    size: A4;
    margin: 2cm;
}

body {
    font-family: "Microsoft YaHei", "SimSun", "SimHei", "PingFang SC", "Noto Sans CJK SC", sans-serif;
    font-size: 11px;
    line-height: 1.6;
    color: #333;
}

h1 {
    font-size: 22px;
    color: #1a1a2e;
    border-bottom: 2px solid #1a1a2e;
    padding-bottom: 6px;
    margin-top: 20px;
    margin-bottom: 10px;
}

h2 {
    font-size: 18px;
    color: #16213e;
    border-bottom: 1px solid #ccc;
    padding-bottom: 4px;
    margin-top: 16px;
    margin-bottom: 8px;
}

h3 {
    font-size: 14px;
    color: #0f3460;
    margin-top: 12px;
    margin-bottom: 6px;
}

h4, h5 {
    font-size: 12px;
    color: #333;
    margin-top: 10px;
    margin-bottom: 4px;
}

table {
    border-collapse: collapse;
    width: 100%;
    margin: 10px 0;
    font-size: 10px;
}

th {
    background-color: #1a1a2e;
    color: #fff;
    font-weight: bold;
    padding: 6px 8px;
    border: 1px solid #555;
    text-align: left;
}

td {
    padding: 5px 8px;
    border: 1px solid #ccc;
    text-align: left;
}

tr:nth-child(even) td {
    background-color: #f5f5f5;
}

ul, ol {
    margin: 6px 0;
    padding-left: 24px;
}

li {
    margin-bottom: 3px;
}

a {
    color: #0066cc;
    text-decoration: none;
}

hr {
    border: none;
    border-top: 1px solid #ccc;
    margin: 16px 0;
}

p {
    margin: 6px 0;
}

code {
    background-color: #f0f0f0;
    padding: 1px 4px;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 10px;
}

pre {
    background-color: #f5f5f5;
    padding: 10px;
    border: 1px solid #ddd;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 10px;
    overflow: hidden;
}

.title-page {
    text-align: center;
    padding-top: 60px;
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
    margin-top: 30px;
}

.disclaimer {
    font-size: 9px;
    color: #999;
    font-style: italic;
    margin-top: 20px;
    border-top: 1px solid #eee;
    padding-top: 8px;
}

.sources-section {
    font-size: 10px;
}

.sources-section li {
    margin-bottom: 2px;
}
"""


def _find_cjk_font() -> Optional[str]:
    """Find a CJK-capable font on the system"""
    font_paths = [
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simsun.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/System/Library/Fonts/PingFang.ttc",
    ]
    for p in font_paths:
        if Path(p).exists():
            return p
    return None


def _build_html(data: Dict[str, Any]) -> str:
    """Build complete HTML document from research data"""
    drug_name = data.get('drug_name', 'Unknown')
    report_content = data.get('report', '')
    sources = data.get('sources', [])
    sources_count = data.get('sources_count', len(sources))

    # Convert markdown report to HTML
    md = markdown.Markdown(extensions=['tables', 'fenced_code', 'nl2br'])
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

    # Font face declaration for CJK
    font_face = ""
    cjk_font = _find_cjk_font()
    if cjk_font:
        font_face = f"""
        @font-face {{
            font-family: "CJKFont";
            src: url("file:///{cjk_font.replace(chr(92), '/')}");
        }}
        """

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
{font_face}
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
    """Generate PDF report via Markdown → HTML → PDF pipeline"""

    def __init__(self, data: Dict[str, Any]):
        super().__init__(data)
        if not PDF_AVAILABLE:
            raise ImportError("markdown and xhtml2pdf not installed. Run: pip install markdown xhtml2pdf")

    def generate(self) -> str:
        """Generate HTML content for PDF"""
        return _build_html(self.data)

    def save(self, filepath: str) -> str:
        """Save PDF report to file"""
        if not PDF_AVAILABLE:
            raise ImportError("markdown and xhtml2pdf not installed")

        html = _build_html(self.data)

        with open(filepath, "wb") as f:
            pisa_status = pisa.CreatePDF(html, dest=f, encoding='utf-8')

        if pisa_status.err:
            raise RuntimeError(f"PDF generation failed with {pisa_status.err} errors")

        return filepath


def generate_pdf(data: Dict[str, Any], filepath: str) -> Optional[str]:
    """Helper function to generate PDF report"""
    if not PDF_AVAILABLE:
        return None

    try:
        report = PDFReport(data)
        return report.save(filepath)
    except Exception as e:
        print(f"[WARN] PDF generation failed: {e}")
        return None
