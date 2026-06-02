from __future__ import annotations

import os
from pathlib import Path
from typing import Any

# Ensure markdown module is imported, if we can parse it to HTML, otherwise we can wrap it with styled tags or simple regex parser for basic styling
# To avoid any extra library dependency (like markdown), we can do a very simple and robust regex-based parser, or even better, we can inject a markdown rendering JS library (like Marked.js) inside the HTML template so it renders natively in the browser perfectly without needing any python dependencies!
# That is a brilliant design decision! Embedding Marked.js via CDN in the generated HTML guarantees 100% accurate, rich markdown rendering, support for code blocks, tables, and lists, and absolutely zero extra python dependencies!

def export_premium_report(title: str = "Báo cáo", content_markdown: str = "", theme: str = "glassmorphism") -> dict[str, Any]:
    """Compiles and exports markdown text or research findings into a beautifully-styled, standalone HTML report file."""
    try:
        exports_dir = Path(__file__).resolve().parent.parent.parent / "exports"
        exports_dir.mkdir(parents=True, exist_ok=True)
        
        # Clean title for filename
        safe_title = "".join([c if c.isalnum() or c in (" ", "-", "_") else "" for c in title]).strip()
        filename = f"{safe_title.lower().replace(' ', '_')}_{int(Path(__file__).stat().st_mtime)}.html"
        file_path = exports_dir / filename

        # Choose theme colors and CSS styles
        css_styles = ""
        if theme.lower() == "glassmorphism":
            css_styles = """
            body {
                background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
                color: #f8fafc;
                font-family: 'Inter', 'Outfit', sans-serif;
                min-height: 100vh;
                margin: 0;
                padding: 40px 20px;
                display: flex;
                justify-content: center;
            }
            .container {
                max-width: 900px;
                width: 100%;
                background: rgba(30, 41, 59, 0.45);
                backdrop-filter: blur(16px);
                -webkit-backdrop-filter: blur(16px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 24px;
                padding: 40px;
                box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
            }
            h1 {
                color: #38bdf8;
                border-bottom: 2px solid rgba(56, 189, 248, 0.3);
                padding-bottom: 15px;
                font-weight: 800;
            }
            h2, h3 {
                color: #818cf8;
                margin-top: 30px;
            }
            pre {
                background: rgba(15, 23, 42, 0.7) !important;
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 12px;
                padding: 16px;
                overflow-x: auto;
            }
            code {
                font-family: 'Fira Code', 'Consolas', monospace;
                color: #38bdf8;
            }
            blockquote {
                border-left: 4px solid #818cf8;
                background: rgba(129, 140, 248, 0.1);
                margin: 20px 0;
                padding: 10px 20px;
                border-radius: 0 12px 12px 0;
            }
            a { color: #38bdf8; text-decoration: none; }
            a:hover { text-decoration: underline; }
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }
            th, td {
                padding: 12px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                text-align: left;
            }
            th { background: rgba(56, 189, 248, 0.1); }
            """
        elif theme.lower() == "slate":
            css_styles = """
            body {
                background-color: #0f172a;
                color: #cbd5e1;
                font-family: 'Inter', sans-serif;
                margin: 0;
                padding: 50px 20px;
                display: flex;
                justify-content: center;
            }
            .container {
                max-width: 850px;
                width: 100%;
                background: #1e293b;
                border: 1px solid #334155;
                border-radius: 16px;
                padding: 40px;
                box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.5);
            }
            h1 {
                color: #f8fafc;
                border-bottom: 1px solid #334155;
                padding-bottom: 12px;
            }
            h2, h3 { color: #f1f5f9; }
            pre {
                background: #0f172a !important;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 15px;
            }
            code { color: #fb7185; }
            blockquote {
                border-left: 4px solid #fb7185;
                background: rgba(251, 113, 133, 0.05);
                padding: 10px 20px;
            }
            a { color: #38bdf8; }
            """
        else: # "corporate"
            css_styles = """
            body {
                background-color: #f8fafc;
                color: #334155;
                font-family: system-ui, -apple-system, sans-serif;
                margin: 0;
                padding: 60px 20px;
                display: flex;
                justify-content: center;
            }
            .container {
                max-width: 800px;
                width: 100%;
                background: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 50px;
                box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
            }
            h1 {
                color: #0f172a;
                border-bottom: 2px solid #0f172a;
                padding-bottom: 10px;
                font-weight: 700;
            }
            h2, h3 { color: #1e293b; }
            pre {
                background: #f1f5f9 !important;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                padding: 15px;
            }
            code { color: #0284c7; }
            blockquote {
                border-left: 4px solid #0284c7;
                background: #f0f9ff;
                padding: 10px 20px;
            }
            a { color: #0284c7; }
            """

        # Escape backticks, backslashes, and dollars outside the f-string to ensure compatibility across all Python versions
        escaped_markdown = content_markdown.replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$')

        # Build fully self-contained HTML using Marked.js CDN to parse markdown beautifully!
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=Outfit:wght@500;800&family=Fira+Code&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        {css_styles}
        .footer {{
            margin-top: 40px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            padding-top: 20px;
            font-size: 0.85em;
            color: #64748b;
            display: flex;
            justify-content: space-between;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div id="content">Loading report content...</div>
        
        <div class="footer">
            <span>Generated dynamically by Antigravity Research Agent Explorer</span>
            <span>Theme: {theme.capitalize()}</span>
        </div>
    </div>

    <script>
        // Raw Markdown content from Python
        const rawMarkdown = `{escaped_markdown}`;
        
        // Parse and render markdown dynamically using Marked.js
        document.getElementById('content').innerHTML = marked.parse(rawMarkdown);
    </script>
</body>
</html>
"""
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        return {
            "tool": "export_report",
            "status": "success",
            "filename": filename,
            "absolute_path": str(file_path),
            "web_url": f"exports/{filename}",
            "message": f"Successfully compiled and exported premium HTML report to '{filename}' using theme '{theme}'."
        }

    except Exception as e:
        return {"tool": "export_report", "status": "error", "error": str(e)}
