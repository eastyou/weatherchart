"""天气统计图表与报告页渲染。"""

from __future__ import annotations

import html
from typing import Dict, Sequence

from .model import WEATHERS, WEATHER_COLORS, Record, summary


def _safe(text: object) -> str:
    return html.escape(str(text), quote=True)


def bar_chart_svg(counts: Dict[str, int]) -> str:
    """绘制天气天数柱状图。"""
    if not counts:
        raise ValueError("至少需要一种天气")
    width, height = 720, 260
    left, right, top, bottom = 48, 24, 36, 52
    plot_w = width - left - right
    plot_h = height - top - bottom
    maximum = max(1, max(counts.values()))
    slot = plot_w / float(len(counts))
    bar_w = slot * 0.56
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 260" '
        'role="img" aria-label="天气天数柱状图">',
        '<rect width="720" height="260" fill="#f8fafc"/>',
    ]
    for index, (weather, count) in enumerate(counts.items()):
        bar_h = plot_h * count / float(maximum)
        x = left + slot * index + (slot - bar_w) / 2
        y = top + plot_h - bar_h
        color = WEATHER_COLORS.get(weather, "#2563eb")
        parts.append(
            '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="6" fill="%s"/>'
            % (x, y, bar_w, max(bar_h, 1.0), color)
        )
        parts.append(
            '<text x="%.1f" y="%.1f" font-size="12" fill="#0f172a" '
            'text-anchor="middle">%d</text>' % (x + bar_w / 2, y - 6, count)
        )
        parts.append(
            '<text x="%.1f" y="%.1f" font-size="12" fill="#475569" '
            'text-anchor="middle">%s</text>' % (x + bar_w / 2, top + plot_h + 22, _safe(weather))
        )
    parts.append("</svg>")
    return "\n".join(parts)


def line_chart_svg(records: Sequence[Record]) -> str:
    """绘制最高温与最低温折线图。"""
    if not records:
        raise ValueError("至少需要一条记录")
    width, height = 720, 280
    left, right, top, bottom = 56, 24, 30, 48
    plot_w = width - left - right
    plot_h = height - top - bottom
    ordered = sorted(records, key=lambda item: item.date)
    values = [item.high for item in ordered] + [item.low for item in ordered]
    low_value = min(values)
    high_value = max(values)
    span = max(1.0, high_value - low_value)

    def point(index: int, value: float) -> str:
        x = left + (
            plot_w * index / float(len(ordered) - 1) if len(ordered) > 1 else plot_w / 2
        )
        y = top + (high_value - value) / span * plot_h
        return "%.1f,%.1f" % (x, y)

    high_points = " ".join(
        point(index, record.high) for index, record in enumerate(ordered)
    )
    low_points = " ".join(
        point(index, record.low) for index, record in enumerate(ordered)
    )
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 280" '
        'role="img" aria-label="气温折线图">',
        '<rect width="720" height="280" fill="#f8fafc"/>',
    ]
    for step in range(4):
        y = top + plot_h * step / 3.0
        parts.append(
            '<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="#e2e8f0"/>'
            % (left, y, width - right, y)
        )
    step = max(1, len(ordered) // 7)
    for index, record in enumerate(ordered):
        if index % step:
            continue
        x = left + (
            plot_w * index / float(len(ordered) - 1) if len(ordered) > 1 else plot_w / 2
        )
        parts.append(
            '<text x="%.1f" y="%d" font-size="10" fill="#64748b" '
            'text-anchor="middle">%s</text>'
            % (x, height - 20, _safe(record.date[5:]))
        )
    parts.append(
        '<polyline points="%s" fill="none" stroke="#ef4444" stroke-width="2.5"/>'
        % high_points
    )
    parts.append(
        '<polyline points="%s" fill="none" stroke="#2563eb" stroke-width="2.5"/>'
        % low_points
    )
    parts.append(
        '<text x="%d" y="22" font-size="12" fill="#ef4444">最高温</text>'
        '<text x="%d" y="22" font-size="12" fill="#2563eb">最低温</text>'
        % (left, left + 70)
    )
    parts.append("</svg>")
    return "\n".join(parts)


def report_html(records: Sequence[Record], title: str = "天气记录报告") -> str:
    """生成包含统计卡片、图表和明细表的完整报告。"""
    if not records:
        raise ValueError("至少需要一条记录")
    safe_title = _safe(title or "天气记录报告")
    stats = summary(records)
    counts = stats["weather_counts"]  # type: ignore[assignment]
    rows = "".join(
        "<tr><td>%s</td><td><span class=\"badge\" style=\"background:%s\">%s</span></td>"
        "<td>%s</td><td>%s</td></tr>"
        % (
            _safe(record.date),
            WEATHER_COLORS.get(record.weather, "#64748b"),
            _safe(record.weather),
            _safe(_temp(record.high)),
            _safe(_temp(record.low)),
        )
        for record in sorted(records, key=lambda item: item.date)
    )
    distribution = "，".join(
        "%s %d 天" % (weather, int(counts[weather]))
        for weather in WEATHERS
        if counts[weather]
    )
    cards = (
        ("记录天数", "%d 天" % stats["days"]),
        ("平均最高温", _temp(stats["avg_high"])),
        ("平均最低温", _temp(stats["avg_low"])),
        ("有雨天数", "%d 天" % stats["rainy_days"]),
    )
    card_html = "".join(
        "<div class=\"kpi\"><span>%s</span><strong>%s</strong></div>" % (_safe(name), _safe(value))
        for name, value in cards
    )
    return (
        "<!DOCTYPE html>\n<html lang=\"zh-CN\">\n<head>\n<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        "<title>%s</title>\n<style>\n"
        "body{font-family:-apple-system,'PingFang SC','Microsoft YaHei',sans-serif;"
        "background:#f8fafc;margin:0;padding:24px;color:#0f172a}\n"
        ".card{max-width:780px;margin:0 auto 20px;background:#fff;border-radius:16px;"
        "padding:24px;box-shadow:0 10px 24px rgba(15,23,42,.08)}\n"
        "h1{font-size:22px;margin:0 0 16px}h2{font-size:16px;margin:20px 0 10px}\n"
        ".kpis{display:flex;gap:12px;flex-wrap:wrap}\n"
        ".kpi{flex:1 1 150px;background:#f1f5f9;border-radius:12px;padding:12px}\n"
        ".kpi span{display:block;font-size:12px;color:#64748b}\n"
        ".kpi strong{font-size:20px}\n"
        "table{width:100%%;border-collapse:collapse;font-size:14px}\n"
        "th,td{border-bottom:1px solid #e2e8f0;padding:8px;text-align:left}\n"
        "th{background:#f1f5f9}\n"
        ".badge{color:#fff;border-radius:999px;padding:2px 10px;font-size:12px}\n"
        "footer{font-size:12px;color:#64748b;margin-top:14px}\n"
        "</style>\n</head>\n<body>\n"
        "<section class=\"card\"><h1>%s</h1><div class=\"kpis\">%s</div>"
        "<p>天气分布：%s</p><h2>天气天数</h2>%s<h2>气温变化</h2>%s"
        "<h2>每日明细</h2><table><thead><tr><th>日期</th><th>天气</th>"
        "<th>最高温</th><th>最低温</th></tr></thead><tbody>%s</tbody></table>"
        "<footer>由 weatherchart 生成 · 数据来自本地 CSV</footer></section>\n"
        "</body>\n</html>"
        % (
            safe_title,
            safe_title,
            card_html,
            _safe(distribution),
            bar_chart_svg(counts),
            line_chart_svg(records),
            rows,
        )
    )


def _temp(value: object) -> str:
    text = "%.1f" % float(value)
    if text.endswith(".0"):
        text = text[:-2]
    return "%s℃" % text
