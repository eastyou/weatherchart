"""weatherchart：天气记录统计与图表生成。"""

from .model import (
    WEATHERS,
    Record,
    date_range,
    demo_records,
    filter_by_weather,
    load_csv,
    parse_record,
    summary,
    to_csv,
)
from .render import bar_chart_svg, line_chart_svg, report_html

__all__ = [
    "WEATHERS",
    "Record",
    "date_range",
    "demo_records",
    "filter_by_weather",
    "load_csv",
    "parse_record",
    "summary",
    "to_csv",
    "bar_chart_svg",
    "line_chart_svg",
    "report_html",
]

__version__ = "0.1.0"
