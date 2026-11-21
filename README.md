# weatherchart

[![CI](https://github.com/eastyou/weatherchart/actions/workflows/ci.yml/badge.svg)](https://github.com/eastyou/weatherchart/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)

天气记录统计工具：CSV 校验、天气分布、气温极值与图表报告。

## 功能

- 严格校验日期、天气类型和温度范围（-50℃ ~ 60℃）
- 自动检查最高温不低于最低温
- 读取带表头/注释的 UTF-8 CSV，错误精确到行号
- 统计天气天数、平均高低温、极值日期、有雨/下雪天数
- 生成天气天数柱状图和最高/最低温折线图（纯 SVG）
- 输出含 KPI 卡片、图表和每日明细的单文件 HTML 报告
- 内置两周示例数据，一条命令即可体验

## 安装

```bash
pip install -e .
```

也可以直接运行 `python -m weatherchart`。

## 使用

```bash
# 统计 CSV
weatherchart stats data.csv

# 校验 CSV
weatherchart check data.csv

# 导出示例 CSV
weatherchart sample -o examples/sample.csv

# 用示例数据生成报告
weatherchart demo -o examples/sheet.html --title "三月天气记录"
```

CSV 格式：

```csv
日期,天气,最高温,最低温
2026-03-01,晴,18,6
2026-03-02,小雨,14,9
```

天气取值：晴、多云、阴、小雨、中雨、大雨、雷阵雨、雪。

## 作为库使用

```python
from weatherchart import demo_records, summary, report_html

records = demo_records()
stats = summary(records)
assert stats["days"] == 14
assert stats["rainy_days"] == 4
page = report_html(records, title="三月天气")
```

## 示例

[examples/sheet.html](examples/sheet.html) 是示例数据生成的完整天气报告。

## 测试

```bash
python -m unittest discover -s tests -v
```

共 75 项单元测试，覆盖记录校验、CSV 往返、行号报错、统计口径、SVG 图表和命令行错误处理。CI 覆盖 Python 3.9 ~ 3.13 与 Linux/macOS/Windows。

## 许可

MIT © 2026 eastyou
