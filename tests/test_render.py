"""weatherchart 渲染测试。"""

import unittest

from weatherchart.model import Record, demo_records, summary
from weatherchart.render import bar_chart_svg, line_chart_svg, report_html


class BarChartTests(unittest.TestCase):
    def setUp(self):
        self.counts = summary(demo_records())["weather_counts"]

    def test_svg(self):
        svg = bar_chart_svg(self.counts)
        self.assertTrue(svg.startswith("<svg"))
        self.assertTrue(svg.endswith("</svg>"))

    def test_contains_weather_labels(self):
        svg = bar_chart_svg(self.counts)
        self.assertIn("晴", svg)
        self.assertIn("雪", svg)

    def test_contains_counts(self):
        svg = bar_chart_svg(self.counts)
        self.assertIn(">4<", svg)

    def test_rejects_empty(self):
        with self.assertRaises(ValueError):
            bar_chart_svg({})

    def test_zero_counts(self):
        svg = bar_chart_svg({"晴": 0, "阴": 0})
        self.assertIn("<rect", svg)


class LineChartTests(unittest.TestCase):
    def test_svg(self):
        svg = line_chart_svg(demo_records())
        self.assertTrue(svg.startswith("<svg"))
        self.assertIn("</svg>", svg)

    def test_contains_polylines(self):
        svg = line_chart_svg(demo_records())
        self.assertEqual(svg.count("<polyline"), 2)

    def test_contains_legend(self):
        svg = line_chart_svg(demo_records())
        self.assertIn("最高温", svg)
        self.assertIn("最低温", svg)

    def test_single_record(self):
        svg = line_chart_svg([Record("2026-03-01", "晴", 10, 2)])
        self.assertIn("<polyline", svg)

    def test_rejects_empty(self):
        with self.assertRaises(ValueError):
            line_chart_svg([])


class ReportTests(unittest.TestCase):
    def test_full_document(self):
        page = report_html(demo_records())
        self.assertTrue(page.startswith("<!DOCTYPE html>"))
        self.assertIn("</html>", page)

    def test_contains_kpis(self):
        page = report_html(demo_records())
        self.assertIn("记录天数", page)
        self.assertIn("平均最高温", page)

    def test_contains_table_rows(self):
        page = report_html(demo_records())
        self.assertIn("2026-03-01", page)
        self.assertIn("2026-03-14", page)

    def test_contains_charts(self):
        page = report_html(demo_records())
        self.assertEqual(page.count("<svg"), 2)

    def test_custom_title(self):
        page = report_html(demo_records(), title="三月天气")
        self.assertIn("三月天气", page)

    def test_escapes_title(self):
        page = report_html(demo_records(), title="<b>天气</b>")
        self.assertNotIn("<b>", page)

    def test_rejects_empty(self):
        with self.assertRaises(ValueError):
            report_html([])

    def test_contains_temperature_unit(self):
        self.assertIn("℃", report_html(demo_records()))


if __name__ == "__main__":
    unittest.main()
