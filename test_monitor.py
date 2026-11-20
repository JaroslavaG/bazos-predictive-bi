import os
import tempfile
import unittest
from datetime import datetime, date
import monitor


class TestBazosPredictiveBI(unittest.TestCase):

    def test_01_easter_calculation(self):
        """Overí presný výpočet Veľkej noci pre roky 2026 a 2027."""
        self.assertEqual(monitor.get_easter_sunday(2026), date(2026, 4, 5))
        self.assertEqual(monitor.get_easter_sunday(2027), date(2027, 3, 28))

    def test_02_holidays_sk_vs_cz(self):
        """Overí rozlíšenie štátnych sviatkov v SR a ČR (vrátane pohyblivých)."""
        dt_snp = datetime(2026, 8, 29, 18, 0)
        cal_sk = monitor.get_calendar_context(dt_snp, country="SK")
        cal_cz = monitor.get_calendar_context(dt_snp, country="CZ")
        self.assertTrue(cal_sk["is_holiday"])
        self.assertIn("SNP", cal_sk["holiday_name"])
        self.assertFalse(cal_cz["is_holiday"])

        dt_cz_state = datetime(2026, 10, 28, 18, 0)
        cal_cz_2 = monitor.get_calendar_context(dt_cz_state, country="CZ")
        cal_sk_2 = monitor.get_calendar_context(dt_cz_state, country="SK")
        self.assertTrue(cal_cz_2["is_holiday"])
        self.assertFalse(cal_sk_2["is_holiday"])

        dt_easter_mon = datetime(2026, 4, 6, 18, 0)
        self.assertTrue(monitor.get_calendar_context(dt_easter_mon, "SK")["is_holiday"])
        self.assertTrue(monitor.get_calendar_context(dt_easter_mon, "CZ")["is_holiday"])

    def test_03_payday_window_detection(self):
        """Overí detekciu výplatného okna (10. až 18. deň v mesiaci)."""
        self.assertTrue(monitor.get_calendar_context(datetime(2026, 11, 14), "SK")["is_payday_window"])
        self.assertFalse(monitor.get_calendar_context(datetime(2026, 11, 25), "SK")["is_payday_window"])

    def test_04_bazos_html_parsing_and_location(self):
        """Overí parsovanie videní, PSČ, GPS súradníc a kvality inzerátu z HTML."""
        sample_html = """
        <html><body>
            <h1>Kompletný set Adamex Barletta 3v1</h1>
            <img src="https://www.bazos.sk/img/1/713/197710713.jpg">
            <img src="https://www.bazos.sk/img/2/713/197710713.jpg">
            <img src="https://www.bazos.sk/img/3/713/197710713.jpg">
            <img src="https://www.bazos.sk/img/4/713/197710713.jpg">
            <img src="https://www.bazos.sk/img/5/713/197710713.jpg">
            <img src="https://www.bazos.sk/img/6/713/197710713.jpg">
            <div>Extra veľká vanička (80 × 36 × 23 cm), šírka 60 cm.</div>
            <a href="https://www.google.com/maps/place/48.716733,21.210737/@48.716733,21.210737,12z">040 23</a>
            <a href="https://deti.bazos.sk/inzeraty/kosice/">Košice</a>
            <div>Videlo: 42 ľudí</div>
            <div>Cena: V texte</div>
        </body></html>
        """
        res = monitor.parse_bazos_html(
            sample_html,
            "https://deti.bazos.sk/inzerat/197710713/mega-komplet-adamex-barletta.php"
        )
        self.assertEqual(res["status"], "active")
        self.assertEqual(res["views"], 42)
        self.assertEqual(res["price_mode"], "V texte")
        self.assertEqual(res["location"]["country"], "SK")
        self.assertEqual(res["location"]["psc"], "040 23")
        self.assertAlmostEqual(res["location"]["lat"], 48.716733, places=4)
        self.assertTrue(res["has_dimensions"])
        self.assertGreaterEqual(res["quality_score"], 75)

    def test_05_inactive_ad_detection(self):
        """Overí bezpečné rozpoznanie vymazaného inzerátu."""
        deleted_html = "<html><body><div>Inzerát bol vymazaný.</div></body></html>"
        res = monitor.parse_bazos_html(deleted_html, "https://deti.bazos.sk/inzerat/000/test.php")
        self.assertEqual(res["status"], "inactive")

    def test_06_sale_probability_model(self):
        """Overí logiku pravdepodobnostného modelu (rast v špičke vs. pokles pri únave publika)."""
        ad = {"kategoria": "kocik", "benchmark_videni": 150, "aktualna_cena": 260, "cielova_cena": 240}
        cal_sunday_payday = monitor.get_calendar_context(datetime(2026, 11, 15, 19, 0), "SK")
        weather_rain = {"is_bad_weather": True, "summary": "🌧️ Dážď", "location_label": "040 23 Košice (SK)"}

        prob_high = monitor.calculate_sale_probability(
            ad, views=45, daily_gain=12, days_active=4, velocity=11.2,
            quality_score=90, cal=cal_sunday_payday, weather=weather_rain
        )
        prob_low = monitor.calculate_sale_probability(
            ad, views=210, daily_gain=1, days_active=18, velocity=1.8,
            quality_score=40, cal=cal_sunday_payday, weather=weather_rain
        )
        self.assertGreater(prob_high, 85)
        self.assertLess(prob_low, 55)

    def test_07_price_elasticity_calculation(self):
        """Overí detekciu úpravy ceny a výpočet zmeny denného prírastku."""
        rows = [
            {"datum": "2026-11-18", "videnia": "20", "narast": "4", "cena": "280"},
            {"datum": "2026-11-19", "videnia": "24", "narast": "4", "cena": "280"},
            {"datum": "2026-11-20", "videnia": "34", "narast": "10", "cena": "260"},
        ]
        el = monitor.analyze_price_elasticity(rows, 260)
        self.assertIsNotNone(el)
        self.assertEqual(el["old_price"], 280)
        self.assertEqual(el["new_price"], 260)
        self.assertEqual(el["lift_pct"], 150)

    def test_08_end_to_end_dashboard_generation(self):
        """Integračný test: overí zápis do CSV a vygenerovanie validného HTML dashboardu."""
        ads = [{
            "id": "197710713", "kategoria": "kocik", "nazov": "Adamex Barletta 3v1",
            "url": "https://deti.bazos.sk/inzerat/197710713/test.php",
            "aktualna_cena": 260, "cielova_cena": 240, "min_denny_narast": 3, "benchmark_videni": 150
        }]
        rows = [{
            "datum": "2026-11-20", "krajina": "SK", "lokalita": "040 23 Košice (SK)",
            "den": "Piatok", "typ_dna": "Pracovný deň (SK)", "pocasie": "⛅ Oblačno (8°C, 0 mm)",
            "id": "197710713", "kategoria": "kocik", "nazov": "Adamex Barletta 3v1",
            "videnia": "25", "narast": "5", "cena": "260", "sanca_predaja_pct": "84"
        }]
        details = {"views": 25, "price_mode": "V texte", "quality_score": 88, "img_count": 12}
        cal = monitor.get_calendar_context(datetime(2026, 11, 20), "SK")
        weather = {"location_label": "040 23 Košice (SK)", "summary": "⛅ Oblačno", "is_bad_weather": False}
        summary = monitor.build_automated_summary(ads[0], details, 5, 1, 25.0, cal, weather)

        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = os.path.join(tmpdir, "test.csv")
            html_path = os.path.join(tmpdir, "index.html")
            monitor.save_all_rows(rows, filepath=csv_path)
            loaded = monitor.load_all_rows(filepath=csv_path)
            self.assertEqual(len(loaded), 1)

            monitor.generate_html_dashboard(
                ads, loaded, {"197710713": summary},
                {"197710713": {"details": details, "cal": cal, "weather": weather}},
                filepath=html_path
            )
            with open(html_path, "r", encoding="utf-8") as f:
                html_out = f.read()
            self.assertIn("Adamex Barletta 3v1", html_out)
            self.assertIn("Pravdepodobnosť predaja", html_out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
