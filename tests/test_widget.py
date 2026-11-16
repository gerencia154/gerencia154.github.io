"""Offline contracts for the public, embeddable ranking."""
import importlib.util
import io
import json
from pathlib import Path
import runpy
import re
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def strategy(position, **overrides):
    row = dict(position=position, strategy_alias=f"Estrategia {position}",
               broker="Bróker público", platform="MT5", tl_score=91.2,
               drawdown_max=4.5, report_url=f"https://trading-latam.com/report/{position}/",
               tl_rating="A", trades_count=100, owner_email="private@example.com")
    return dict(row, **overrides)


def dataset(rows=None):
    return dict(date_modified="2026-11-15", strategies=rows if rows is not None else [strategy(i) for i in range(1, 8)])


class WidgetTests(unittest.TestCase):
    def render(self, data):
        path = ROOT / "scripts" / "widget.py"
        self.assertTrue(path.exists(), "The static widget renderer does not exist yet")
        spec = importlib.util.spec_from_file_location("widget", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.render_widget(data)

    def test_five_public_rows_in_source_order_and_report_links(self):
        out = self.render(dataset())
        self.assertEqual(out.count('<li class="entry">'), 5)
        for i in range(1, 6):
            self.assertIn(f"Estrategia {i}", out)
            self.assertIn(f'https://trading-latam.com/report/{i}/', out)
        self.assertNotIn("Estrategia 6", out)
        self.assertNotIn("private@example.com", out)
        self.assertIn("Bróker público", out)
        self.assertIn("MT5", out)

    def test_escapes_aliases_and_urls_and_rejects_active_url_schemes(self):
        out = self.render(dataset([strategy(1, strategy_alias='<img src=x onerror="alert(1)">',
                                          report_url='https://example.com/report?a=1&b="x"'),
                                   strategy(2, report_url="javascript:alert(1)"),
                                   strategy(3, report_url="//example.com/report")]))
        self.assertIn('&lt;img src=x onerror=&quot;alert(1)&quot;&gt;', out)
        self.assertIn('href="https://example.com/report?a=1&amp;b=&quot;x&quot;"', out)
        self.assertNotIn("javascript:", out)
        self.assertNotIn('href="//', out)
        self.assertNotIn("<img", out)

    def test_missing_metrics_remain_unavailable_while_real_zero_survives(self):
        out = self.render(dataset([strategy(1, tl_score=None, drawdown_max=None),
                                   strategy(2, tl_score=0, drawdown_max=0),
                                   {"strategy_alias": "Sin datos"}]))
        self.assertEqual(out.count('title="No disponible"'), 4)
        self.assertIn('>0</strong>', out)
        self.assertIn('>0%</span>', out)
        self.assertNotIn("None", out)

    def test_empty_ranking_is_explicit(self):
        out = self.render(dataset([]))
        self.assertIn("No hay estrategias públicas disponibles", out)
        self.assertNotIn('<li class="entry">', out)

    def test_source_date_attribution_and_no_active_content(self):
        out = self.render(dataset())
        self.assertIn('datetime="2026-11-15"', out)
        self.assertIn("2026-11-15", out)
        self.assertIn('href="https://trading-latam.com/ranking-toptraders/"', out)
        self.assertIn("Fuente: Trading Latam", re.sub(r"<[^>]+>", "", out))
        self.assertIn("CC BY 4.0", out)
        self.assertNotIn("<script", out)
        self.assertNotIn("<form", out)
        self.assertNotIn("{{", out)
        missing = self.render({"strategies": []})
        self.assertIn("Fecha no disponible", missing)
        self.assertNotIn('datetime=""', missing)

    def test_daily_build_generates_both_pages_with_one_fetch(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            shutil.copytree(ROOT / "scripts", root / "scripts")
            with patch.object(sys, "path", [str(root / "scripts"), *sys.path]), \
                    patch("urllib.request.urlopen", return_value=io.BytesIO(json.dumps(dataset()).encode())) as fetch:
                runpy.run_path(str(root / "scripts" / "build.py"), run_name="__main__")
            self.assertEqual(fetch.call_count, 1)
            self.assertTrue((root / "index.html").is_file())
            self.assertTrue((root / "widget" / "index.html").is_file(), "Daily build must also generate /widget/")
            self.assertIn("Top 15 de hoy", (root / "index.html").read_text())
            self.assertEqual((root / "widget" / "index.html").read_text(), self.render(dataset()))


if __name__ == "__main__":
    unittest.main()
