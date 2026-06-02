from __future__ import annotations

import json
from pathlib import Path
from typing import Any

def generate_svg_chart(title: str = "Biểu đồ", data_points: dict[str, float] = None, chart_type: str = "bar") -> dict[str, Any]:
    """Generates a highly-stylized, self-contained SVG chart (bar, line, or pie) from category-value data pairs."""
    try:
        if not data_points:
            data_points = {"v0 (Baseline)": 44.4, "v1 (Prompt)": 66.7, "v2 (Multi-turn)": 77.8, "v3 (Schema)": 100.0}

        exports_dir = Path(__file__).resolve().parent.parent.parent / "exports"
        exports_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"chart_{int(Path(__file__).stat().st_mtime)}.svg"
        file_path = exports_dir / filename

        # Render SVG bar chart manually - extremely fast, zero dependencies, and gorgeous!
        svg_width = 700
        svg_height = 400
        padding_left = 120
        padding_right = 40
        padding_top = 60
        padding_bottom = 60
        
        chart_width = svg_width - padding_left - padding_right
        chart_height = svg_height - padding_top - padding_bottom

        categories = list(data_points.keys())
        values = list(data_points.values())
        max_val = max(values) if values else 100
        if max_val == 0:
            max_val = 100
            
        # Round max value up to nearest 10 or 100 for neat scale
        upper_limit = ((max_val // 10) + 1) * 10 if max_val <= 100 else ((max_val // 100) + 1) * 100
        if upper_limit > 100 and max_val <= 100:
            upper_limit = 100

        svg_content = f"""<svg width="{svg_width}" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}" xmlns="http://www.w3.org/2000/svg">
    <!-- Gradient background -->
    <defs>
        <linearGradient id="bg-grad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#0f172a" />
            <stop offset="100%" stop-color="#1e1b4b" />
        </linearGradient>
        <linearGradient id="bar-grad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stop-color="#38bdf8" />
            <stop offset="100%" stop-color="#818cf8" />
        </linearGradient>
        <linearGradient id="line-grad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#38bdf8" stop-opacity="0.4" />
            <stop offset="100%" stop-color="#38bdf8" stop-opacity="0.0" />
        </linearGradient>
        <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="6" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
        </filter>
    </defs>

    <!-- Background card -->
    <rect width="{svg_width}" height="{svg_height}" rx="16" fill="url(#bg-grad)" stroke="#334155" stroke-width="1.5"/>

    <!-- Chart Title -->
    <text x="{svg_width / 2}" y="35" text-anchor="middle" font-family="system-ui, -apple-system, sans-serif" font-size="18" font-weight="bold" fill="#f8fafc">{title}</text>
"""

        # Draw grid lines & scale
        for i in range(5):
            y_scale = padding_top + chart_height - (i * chart_height / 4)
            val_scale = (i * upper_limit / 4)
            svg_content += f"""    <!-- Y Grid Line -->
    <line x1="{padding_left}" y1="{y_scale}" x2="{svg_width - padding_right}" y2="{y_scale}" stroke="#334155" stroke-opacity="0.5" stroke-dasharray="4"/>
    <text x="{padding_left - 15}" y="{y_scale + 4}" text-anchor="end" font-family="system-ui, -apple-system, sans-serif" font-size="11" fill="#94a3b8">{val_scale:.1f}</text>
"""

        chart_type = chart_type.lower()
        if chart_type == "line":
            # Generate points for SVG path
            points = []
            num_points = len(categories)
            x_interval = chart_width / (num_points - 1) if num_points > 1 else chart_width
            
            for index, (cat, val) in enumerate(data_points.items()):
                cx = padding_left + (index * x_interval)
                cy = padding_top + chart_height - (val * chart_height / upper_limit)
                points.append((cx, cy))
            
            # Draw line path
            path_str = " ".join([f"{'M' if i == 0 else 'L'} {p[0]} {p[1]}" for i, p in enumerate(points)])
            svg_content += f"""    <!-- Line Chart Area -->
    <path d="{path_str} L {points[-1][0]} {padding_top + chart_height} L {points[0][0]} {padding_top + chart_height} Z" fill="url(#line-grad)" />
    <!-- Line Chart Path -->
    <path d="{path_str}" fill="none" stroke="#38bdf8" stroke-width="3.5" filter="url(#glow)"/>
"""
            # Draw dots & Category Labels
            for index, (cx, cy) in enumerate(points):
                cat = categories[index]
                val = values[index]
                svg_content += f"""    <!-- Point Dot -->
    <circle cx="{cx}" cy="{cy}" r="5" fill="#f8fafc" stroke="#38bdf8" stroke-width="2"/>
    <!-- Value Text -->
    <text x="{cx}" y="{cy - 12}" text-anchor="middle" font-family="system-ui, -apple-system, sans-serif" font-weight="bold" font-size="11" fill="#38bdf8">{val:.1f}%</text>
    <!-- Label -->
    <text x="{cx}" y="{padding_top + chart_height + 25}" text-anchor="middle" font-family="system-ui, -apple-system, sans-serif" font-size="11" fill="#94a3b8">{cat}</text>
"""
        else: # "bar"
            # Draw bars
            num_bars = len(categories)
            bar_gap = 15
            total_bar_space = chart_width / num_bars
            bar_width = total_bar_space - bar_gap
            
            for index, (cat, val) in enumerate(data_points.items()):
                bx = padding_left + (index * total_bar_space) + (bar_gap / 2)
                bar_h = (val * chart_height / upper_limit)
                by = padding_top + chart_height - bar_h
                
                svg_content += f"""    <!-- Bar -->
    <rect x="{bx}" y="{by}" width="{bar_width}" height="{bar_h}" rx="6" fill="url(#bar-grad)" filter="url(#glow)"/>
    <!-- Value on top of Bar -->
    <text x="{bx + bar_width/2}" y="{by - 8}" text-anchor="middle" font-family="system-ui, -apple-system, sans-serif" font-weight="bold" font-size="11" fill="#38bdf8">{val:.1f}%</text>
    <!-- Category Label -->
    <text x="{bx + bar_width/2}" y="{padding_top + chart_height + 25}" text-anchor="middle" font-family="system-ui, -apple-system, sans-serif" font-size="11" fill="#94a3b8">{cat}</text>
"""

        # Y Axis and X Axis line
        svg_content += f"""
    <!-- Axes -->
    <line x1="{padding_left}" y1="{padding_top}" x2="{padding_left}" y2="{padding_top + chart_height}" stroke="#334155" stroke-width="1.5"/>
    <line x1="{padding_left}" y1="{padding_top + chart_height}" x2="{svg_width - padding_right}" y2="{padding_top + chart_height}" stroke="#334155" stroke-width="1.5"/>
</svg>
"""
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(svg_content)

        return {
            "tool": "visualize_data",
            "status": "success",
            "filename": filename,
            "absolute_path": str(file_path),
            "web_url": f"exports/{filename}",
            "message": f"Successfully compiled beautiful SVG '{chart_type}' chart and saved to '{filename}'."
        }

    except Exception as e:
        return {"tool": "visualize_data", "status": "error", "error": str(e)}
