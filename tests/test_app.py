import unittest
from pathlib import Path
from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "app.py"


class AppTests(unittest.TestCase):
    def setUp(self):
        self.app = AppTest.from_file(str(APP), default_timeout=30).run()
        self.assertFalse(self.app.exception)

    def navigate(self, index):
        self.app.radio(key="navigation").set_value(self.app.radio(key="navigation").options[index]).run()
        self.assertFalse(self.app.exception)

    def test_every_page_and_charts(self):
        expected = [5, 2, 3, 1, 2, 2, 1, 1, 0]
        for index, count in enumerate(expected):
            with self.subTest(page=index):
                self.navigate(index)
                self.assertEqual(len(self.app.get("imgs")), count)

    def test_inputs_recompute_and_persist(self):
        changes = [(1, "soc", 40, "Available energy", "20.0 kWh"),
                   (2, "ac", 0.0, "Estimated range", "125.0 km"),
                   (3, "target", 40, "Estimated charging time", "0.00 h"),
                   (4, "regen", 0, "Total recovered", "0.000 kWh"),
                   (5, "rpm", 0, "Motor power", "0 W"),
                   (6, "load", 0, "Temperature · 60 min", "25.0 °C"),
                   (7, "inverter", 0, "Energy at wheels", "0.00 kWh")]
        for page, key, value, label, expected in changes:
            with self.subTest(page=page):
                self.navigate(page)
                self.app.slider(key="input_"+key).set_value(value).run()
                self.assertFalse(self.app.exception)
                self.assertIn(expected, [m.value for m in self.app.metric if m.label == label])
        self.navigate(1)
        self.assertEqual(self.app.slider(key="input_soc").value, 40)

    def test_invalid_charging_and_recovery(self):
        self.navigate(3)
        self.app.slider(key="input_target").set_value(10).run()
        self.assertTrue(self.app.error)
        self.assertFalse(self.app.exception)
        self.app.slider(key="input_target").set_value(100).run()
        self.assertFalse(self.app.error)
        self.assertTrue(self.app.metric)

    def test_preset_reset_and_challenges(self):
        self.app.selectbox[0].set_value("Large EV").run()
        next(b for b in self.app.button if b.label == "Apply preset").click().run()
        self.assertEqual(self.app.session_state["scenario"]["capacity"], 85)
        self.navigate(8)
        self.app.button(key="choice_0_0").click().run()
        self.assertTrue(self.app.warning)
        for i, answer in enumerate([1, 1, 2, 1, 0]):
            self.app.button(key=f"choice_{i}_{answer}").click().run()
            self.assertFalse(self.app.exception)
            self.assertTrue(self.app.session_state[f"solved_{i}"])
        next(b for b in self.app.button if b.label == "Reset all experiments").click().run()
        self.assertEqual(self.app.session_state["scenario"]["capacity"], 50)
        self.assertNotIn("solved_0", self.app.session_state)

    def test_extreme_slider_values(self):
        for index in range(1, 8):
            self.navigate(index)
            keys = [widget.key for widget in self.app.slider]
            for endpoint in ("min", "max"):
                with self.subTest(page=index, endpoint=endpoint):
                    for key in keys:
                        widget = self.app.slider(key=key)
                        widget.set_value(getattr(widget, endpoint))
                    self.app.run()
                    self.assertFalse(self.app.exception)
                    self.assertFalse(self.app.error if index != 6 else [])


if __name__ == "__main__":
    unittest.main()
