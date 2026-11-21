"""weatherchart 命令行测试。"""

import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from weatherchart.cli import main


def run(args):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = main(args)
    return code, out.getvalue(), err.getvalue()


SAMPLE = "日期,天气,最高温,最低温\n2026-03-01,晴,18,6\n2026-03-02,小雨,14,9\n"


class StatsCommandTests(unittest.TestCase):
    def test_stats_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "data.csv"
            path.write_text(SAMPLE, encoding="utf-8")
            code, out, _ = run(["stats", str(path)])
            self.assertEqual(code, 0)
            self.assertIn("记录天数：2 天", out)
            self.assertIn("有雨天数：1 天", out)

    def test_stats_missing_file(self):
        code, _, err = run(["stats", "/no/such/file.csv"])
        self.assertEqual(code, 2)
        self.assertIn("不存在", err)

    def test_stats_bad_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.csv"
            path.write_text("2026-03-01,暴雨,18,6\n", encoding="utf-8")
            code, _, err = run(["stats", str(path)])
            self.assertEqual(code, 2)
            self.assertIn("天气", err)


class CheckCommandTests(unittest.TestCase):
    def test_check_valid(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "data.csv"
            path.write_text(SAMPLE, encoding="utf-8")
            code, out, _ = run(["check", str(path)])
            self.assertEqual(code, 0)
            self.assertIn("数据有效", out)
            self.assertIn("2026-03-01 至 2026-03-02", out)

    def test_check_missing(self):
        code, _, err = run(["check", "/no/such.csv"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)


class DemoCommandTests(unittest.TestCase):
    def test_creates_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "report.html"
            code, out, _ = run(["demo", "-o", str(output)])
            self.assertEqual(code, 0)
            self.assertTrue(output.exists())
            self.assertIn("14 天", out)

    def test_report_contains_svg(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "report.html"
            run(["demo", "-o", str(output)])
            self.assertIn("<svg", output.read_text(encoding="utf-8"))

    def test_custom_title(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "report.html"
            run(["demo", "-o", str(output), "--title", "春季天气"])
            self.assertIn("春季天气", output.read_text(encoding="utf-8"))

    def test_requires_output(self):
        with self.assertRaises(SystemExit) as ctx:
            with redirect_stderr(io.StringIO()):
                main(["demo"])
        self.assertEqual(ctx.exception.code, 2)


class SampleCommandTests(unittest.TestCase):
    def test_creates_csv(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "sample.csv"
            code, out, _ = run(["sample", "-o", str(output)])
            self.assertEqual(code, 0)
            self.assertTrue(output.exists())
            self.assertIn("已生成示例 CSV", out)

    def test_csv_has_header(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "sample.csv"
            run(["sample", "-o", str(output)])
            text = output.read_text(encoding="utf-8")
            self.assertTrue(text.startswith("日期,天气"))

    def test_sample_can_be_read_back(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "sample.csv"
            run(["sample", "-o", str(output)])
            code, out, _ = run(["check", str(output)])
            self.assertEqual(code, 0)
            self.assertIn("14 条记录", out)


class ParserTests(unittest.TestCase):
    def test_help(self):
        with self.assertRaises(SystemExit) as ctx:
            with redirect_stdout(io.StringIO()):
                main(["--help"])
        self.assertEqual(ctx.exception.code, 0)

    def test_no_command(self):
        with self.assertRaises(SystemExit) as ctx:
            with redirect_stderr(io.StringIO()):
                main([])
        self.assertEqual(ctx.exception.code, 2)

    def test_unknown_command(self):
        with self.assertRaises(SystemExit) as ctx:
            with redirect_stderr(io.StringIO()):
                main(["forecast"])
        self.assertEqual(ctx.exception.code, 2)

    def test_sample_requires_output(self):
        with self.assertRaises(SystemExit) as ctx:
            with redirect_stderr(io.StringIO()):
                main(["sample"])
        self.assertEqual(ctx.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
