"""weatherchart 命令行入口。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional, Sequence

from .model import (
    WEATHERS,
    date_range,
    demo_records,
    load_csv,
    summary,
    to_csv,
)
from .render import report_html


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="weatherchart", description="天气记录：CSV 统计、图表与报告生成"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    stats = sub.add_parser("stats", help="统计天气记录")
    stats.add_argument("file", help="CSV 文件路径")

    check = sub.add_parser("check", help="校验 CSV 文件")
    check.add_argument("file", help="CSV 文件路径")

    demo = sub.add_parser("demo", help="用示例数据生成报告")
    demo.add_argument("-o", "--output", required=True)
    demo.add_argument("--title", default="天气记录报告")

    sample = sub.add_parser("sample", help="导出示例 CSV")
    sample.add_argument("-o", "--output", required=True)

    return parser


def _read_records(path_text: str):
    path = Path(path_text)
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise ValueError("文件不存在：%s" % path_text) from None
    except UnicodeDecodeError:
        raise ValueError("文件不是 UTF-8 编码：%s" % path_text) from None
    except OSError as exc:
        raise ValueError("无法读取文件 %s：%s" % (path_text, exc)) from None
    return load_csv(text)


def _run(args: argparse.Namespace) -> int:
    if args.command == "stats":
        records = _read_records(args.file)
        data = summary(records)
        counts = data["weather_counts"]  # type: ignore[assignment]
        print("记录天数：%d 天" % data["days"])
        print(
            "天气分布：%s"
            % "，".join(
                "%s %d 天" % (weather, counts[weather])
                for weather in WEATHERS
                if counts[weather]
            )
        )
        print("平均最高温：%.1f℃" % data["avg_high"])
        print("平均最低温：%.1f℃" % data["avg_low"])
        print(
            "最高温：%.1f℃（%s）" % (data["max_high"], data["max_high_date"])
        )
        print("最低温：%.1f℃（%s）" % (data["min_low"], data["min_low_date"]))
        print("有雨天数：%d 天" % data["rainy_days"])
        return 0
    if args.command == "check":
        records = _read_records(args.file)
        print("数据有效：%d 条记录，日期 %s" % (len(records), date_range(records)))
        return 0
    if args.command == "demo":
        records = demo_records()
        Path(args.output).write_text(
            report_html(records, title=args.title), encoding="utf-8"
        )
        print("已生成天气报告：%s（%d 天）" % (args.output, len(records)))
        return 0
    if args.command == "sample":
        Path(args.output).write_text(to_csv(demo_records()), encoding="utf-8")
        print("已生成示例 CSV：%s" % args.output)
        return 0
    raise ValueError("未知命令：%s" % args.command)


def _ensure_utf8_console() -> None:
    """Windows 控制台默认编码可能无法输出中文，尽量切换为 UTF-8。"""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except (ValueError, OSError):
            continue


def main(argv: Optional[Sequence[str]] = None) -> int:
    _ensure_utf8_console()
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return _run(args)
    except (TypeError, ValueError) as exc:
        print("错误：%s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
