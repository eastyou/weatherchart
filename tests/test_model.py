"""weatherchart 核心逻辑测试。"""

import unittest

from weatherchart.model import (
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


class RecordTests(unittest.TestCase):
    def test_valid_record(self):
        record = Record("2026-03-01", "晴", 18, 6)
        self.assertEqual(record.high, 18)
        self.assertEqual(record.low, 6)

    def test_accepts_float(self):
        record = Record("2026-03-01", "多云", 18.5, 6.5)
        self.assertAlmostEqual(record.high, 18.5)

    def test_rejects_bad_date(self):
        with self.assertRaises(ValueError):
            Record("2026-13-01", "晴", 18, 6)

    def test_rejects_bad_date_format(self):
        with self.assertRaises(ValueError):
            Record("03/01/2026", "晴", 18, 6)

    def test_rejects_non_string_date(self):
        with self.assertRaises(TypeError):
            Record(20260301, "晴", 18, 6)  # type: ignore[arg-type]

    def test_rejects_unknown_weather(self):
        with self.assertRaises(ValueError):
            Record("2026-03-01", "沙尘暴", 18, 6)

    def test_rejects_high_below_low(self):
        with self.assertRaises(ValueError):
            Record("2026-03-01", "晴", 5, 6)

    def test_rejects_text_temperature(self):
        with self.assertRaises(TypeError):
            Record("2026-03-01", "晴", "18", 6)  # type: ignore[arg-type]

    def test_rejects_bool_temperature(self):
        with self.assertRaises(TypeError):
            Record("2026-03-01", "晴", True, 6)  # type: ignore[arg-type]

    def test_rejects_too_hot(self):
        with self.assertRaises(ValueError):
            Record("2026-03-01", "晴", 80, 6)

    def test_rejects_too_cold(self):
        with self.assertRaises(ValueError):
            Record("2026-03-01", "晴", 10, -80)

    def test_equal_high_low_allowed(self):
        record = Record("2026-03-01", "阴", 10, 10)
        self.assertEqual(record.high, record.low)


class ParseTests(unittest.TestCase):
    def test_parse_record(self):
        record = parse_record("2026-03-01,晴,18,6")
        self.assertEqual(record.weather, "晴")
        self.assertEqual(record.high, 18)

    def test_parse_with_spaces(self):
        record = parse_record(" 2026-03-01 , 多云 , 17 , 8 ")
        self.assertEqual(record.weather, "多云")

    def test_parse_wrong_field_count(self):
        with self.assertRaises(ValueError):
            parse_record("2026-03-01,晴,18")

    def test_parse_non_numeric(self):
        with self.assertRaises(ValueError):
            parse_record("2026-03-01,晴,热,冷")

    def test_parse_empty_weather(self):
        with self.assertRaises(ValueError):
            parse_record("2026-03-01,,18,6")

    def test_parse_non_string(self):
        with self.assertRaises(TypeError):
            parse_record(None)  # type: ignore[arg-type]


class CsvTests(unittest.TestCase):
    def test_load_basic(self):
        records = load_csv("2026-03-01,晴,18,6\n2026-03-02,小雨,14,9\n")
        self.assertEqual(len(records), 2)

    def test_load_skips_header(self):
        records = load_csv("日期,天气,最高温,最低温\n2026-03-01,晴,18,6\n")
        self.assertEqual(len(records), 1)

    def test_load_skips_blank_and_comments(self):
        records = load_csv("# 注释\n\n2026-03-01,晴,18,6\n")
        self.assertEqual(len(records), 1)

    def test_load_reports_line_number(self):
        with self.assertRaises(ValueError) as ctx:
            load_csv("2026-03-01,晴,18,6\n2026-03-02,暴雨,14,9\n")
        self.assertIn("第 2 行", str(ctx.exception))

    def test_load_empty(self):
        with self.assertRaises(ValueError):
            load_csv("")

    def test_load_non_string(self):
        with self.assertRaises(TypeError):
            load_csv(123)  # type: ignore[arg-type]

    def test_to_csv_has_header(self):
        text = to_csv(demo_records())
        self.assertTrue(text.startswith("日期,天气,最高温,最低温"))

    def test_round_trip(self):
        original = demo_records()
        self.assertEqual(load_csv(to_csv(original)), original)

    def test_to_csv_empty(self):
        with self.assertRaises(ValueError):
            to_csv([])


class SummaryTests(unittest.TestCase):
    def setUp(self):
        self.records = demo_records()

    def test_days(self):
        self.assertEqual(summary(self.records)["days"], 14)

    def test_weather_counts_cover_all(self):
        counts = summary(self.records)["weather_counts"]
        self.assertEqual(set(counts), set(WEATHERS))

    def test_sunny_days(self):
        counts = summary(self.records)["weather_counts"]
        self.assertEqual(counts["晴"], 4)

    def test_rainy_days(self):
        data = summary(self.records)
        self.assertEqual(data["rainy_days"], 4)

    def test_snowy_days(self):
        self.assertEqual(summary(self.records)["snowy_days"], 1)

    def test_average_high(self):
        data = summary(self.records)
        self.assertAlmostEqual(data["avg_high"], 16.3)

    def test_max_high(self):
        data = summary(self.records)
        self.assertEqual(data["max_high"], 22)
        self.assertEqual(data["max_high_date"], "2026-03-12")

    def test_min_low(self):
        data = summary(self.records)
        self.assertEqual(data["min_low"], -2)
        self.assertEqual(data["min_low_date"], "2026-03-14")

    def test_empty_records(self):
        with self.assertRaises(ValueError):
            summary([])

    def test_single_record(self):
        data = summary([Record("2026-03-01", "晴", 10, 2)])
        self.assertEqual(data["avg_high"], 10)
        self.assertEqual(data["days"], 1)


class HelperTests(unittest.TestCase):
    def test_filter_by_weather(self):
        records = filter_by_weather(demo_records(), "小雨")
        self.assertEqual(len(records), 2)

    def test_filter_unknown_weather(self):
        with self.assertRaises(ValueError):
            filter_by_weather(demo_records(), "暴雨")

    def test_date_range(self):
        self.assertEqual(
            date_range(demo_records()), "2026-03-01 至 2026-03-14"
        )

    def test_date_range_empty(self):
        with self.assertRaises(ValueError):
            date_range([])


if __name__ == "__main__":
    unittest.main()
