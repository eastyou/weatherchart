"""天气记录：数据校验、CSV 读写与统计。"""

from __future__ import annotations

import datetime as _dt
import math
from dataclasses import dataclass
from typing import Dict, List, Sequence

WEATHERS = ("晴", "多云", "阴", "小雨", "中雨", "大雨", "雷阵雨", "雪")

WEATHER_COLORS = {
    "晴": "#f59e0b",
    "多云": "#94a3b8",
    "阴": "#64748b",
    "小雨": "#38bdf8",
    "中雨": "#0ea5e9",
    "大雨": "#2563eb",
    "雷阵雨": "#7c3aed",
    "雪": "#818cf8",
}

MIN_TEMP = -50.0
MAX_TEMP = 60.0


@dataclass(frozen=True)
class Record:
    """一天的天气记录。"""

    date: str
    weather: str
    high: float
    low: float

    def __post_init__(self) -> None:
        if not isinstance(self.date, str):
            raise TypeError("日期必须是字符串")
        try:
            _dt.date.fromisoformat(self.date.strip())
        except ValueError:
            raise ValueError("日期格式应为 YYYY-MM-DD，当前为 %r" % self.date) from None
        if not isinstance(self.weather, str) or self.weather not in WEATHERS:
            raise ValueError(
                "天气必须是以下之一：%s" % "、".join(WEATHERS)
            )
        for name, value in (("最高温", self.high), ("最低温", self.low)):
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise TypeError("%s 必须是数字" % name)
            if not math.isfinite(float(value)):
                raise ValueError("%s 必须是有限数字" % name)
            if value < MIN_TEMP or value > MAX_TEMP:
                raise ValueError("%s 应在 %d 到 %d 之间" % (name, MIN_TEMP, MAX_TEMP))
        if self.high < self.low:
            raise ValueError("最高温不能低于最低温")


def parse_record(line: str) -> Record:
    """解析 ``日期,天气,最高温,最低温`` 一行。"""
    if not isinstance(line, str):
        raise TypeError("记录必须是字符串")
    fields = [part.strip() for part in line.split(",")]
    if len(fields) != 4:
        raise ValueError("每行需要 4 个字段：日期,天气,最高温,最低温")
    date, weather, high_text, low_text = fields
    if not date or not weather:
        raise ValueError("日期和天气不能为空")
    try:
        high = float(high_text)
        low = float(low_text)
    except ValueError:
        raise ValueError("温度必须是数字，当前为 %r 和 %r" % (high_text, low_text)) from None
    return Record(date=date, weather=weather, high=high, low=low)


def load_csv(text: str) -> List[Record]:
    """读取 CSV 文本，忽略空行和注释行。"""
    if not isinstance(text, str):
        raise TypeError("CSV 内容必须是字符串")
    records: List[Record] = []
    for index, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if index == 1 and ("日期" in line or line.lower().startswith("date")):
            continue
        try:
            records.append(parse_record(line))
        except (TypeError, ValueError) as exc:
            raise ValueError("第 %d 行：%s" % (index, exc)) from None
    if not records:
        raise ValueError("没有读取到任何天气记录")
    return records


def to_csv(records: Sequence[Record]) -> str:
    """序列化成带表头的 CSV。"""
    if not records:
        raise ValueError("至少需要一条记录")
    lines = ["日期,天气,最高温,最低温"]
    for record in records:
        lines.append(
            "%s,%s,%s,%s"
            % (
                record.date,
                record.weather,
                _trim(record.high),
                _trim(record.low),
            )
        )
    return "\n".join(lines) + "\n"


def _trim(value: float) -> str:
    number = float(value)
    if abs(number - round(number)) < 1e-9:
        return str(int(round(number)))
    return ("%.1f" % number).rstrip("0").rstrip(".")


def filter_by_weather(records: Sequence[Record], weather: str) -> List[Record]:
    if weather not in WEATHERS:
        raise ValueError("未知天气：%s" % weather)
    return [record for record in records if record.weather == weather]


def summary(records: Sequence[Record]) -> Dict[str, object]:
    """汇总天气分布、平均气温与极值。"""
    if not records:
        raise ValueError("至少需要一条记录")
    counts = {weather: 0 for weather in WEATHERS}
    for record in records:
        counts[record.weather] += 1
    hottest = max(records, key=lambda item: item.high)
    coldest = min(records, key=lambda item: item.low)
    rainy = sum(1 for record in records if "雨" in record.weather)
    snowy = sum(1 for record in records if record.weather == "雪")
    return {
        "days": len(records),
        "weather_counts": counts,
        "avg_high": round(sum(record.high for record in records) / len(records), 1),
        "avg_low": round(sum(record.low for record in records) / len(records), 1),
        "max_high": hottest.high,
        "max_high_date": hottest.date,
        "min_low": coldest.low,
        "min_low_date": coldest.date,
        "rainy_days": rainy,
        "snowy_days": snowy,
    }


def demo_records() -> List[Record]:
    """内置两周示例数据，便于直接体验。"""
    rows = [
        ("2026-03-01", "晴", 18, 6),
        ("2026-03-02", "多云", 17, 8),
        ("2026-03-03", "小雨", 14, 9),
        ("2026-03-04", "阴", 15, 8),
        ("2026-03-05", "晴", 19, 7),
        ("2026-03-06", "晴", 21, 9),
        ("2026-03-07", "多云", 20, 11),
        ("2026-03-08", "中雨", 16, 10),
        ("2026-03-09", "小雨", 13, 8),
        ("2026-03-10", "阴", 14, 7),
        ("2026-03-11", "多云", 18, 9),
        ("2026-03-12", "晴", 22, 10),
        ("2026-03-13", "雷阵雨", 17, 12),
        ("2026-03-14", "雪", 4, -2),
    ]
    return [Record(*row) for row in rows]


def date_range(records: Sequence[Record]) -> str:
    """返回记录覆盖的日期范围，用于快速核对。"""
    if not records:
        raise ValueError("至少需要一条记录")
    dates = sorted(record.date for record in records)
    return "%s 至 %s" % (dates[0], dates[-1])
