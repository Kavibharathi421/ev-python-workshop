import unittest
import numpy as np
from modules import battery, range as ev_range, charging, regenerative, motor, thermal, energy


class ModelTests(unittest.TestCase):
    def test_known_answers(self):
        self.assertEqual(battery.calculate(50, 80, 400, 100), {"available_kwh": 40, "power_kw": 40})
        self.assertEqual(ev_range.calculate(50, 80, .16, 50, 0, "City")["range_km"], 250)
        c = charging.calculate(50, 20, 60, 10, 80, 8)
        self.assertEqual((c["grid_kwh"], c["hours"], c["cost_inr"]), (25, 2.5, 200))
        self.assertAlmostEqual(motor.calculate(100, 3000)["power_kw"], 31.4159265)
        r = regenerative.calculate(1000, 36, 60, 3)
        self.assertEqual(r["kinetic_j"], 50000)
        self.assertAlmostEqual(r["total_kwh"], .025)

    def test_boundaries(self):
        self.assertEqual(battery.calculate(50, 0)["available_kwh"], 0)
        self.assertEqual(battery.calculate(50, 100)["available_kwh"], 50)
        self.assertEqual(ev_range.calculate(50, 0, .16, 50, 1, "City")["range_km"], 0)
        self.assertEqual(charging.calculate(50, 100, 100, 1, 100, 0)["hours"], 0)
        self.assertEqual(motor.calculate(100, 0)["power_w"], 0)
        self.assertEqual(regenerative.calculate(0, 0, 0, 0)["total_kwh"], 0)

    def test_invalid_inputs(self):
        cases = [(battery.calculate, (0, 80)), (battery.calculate, (50, 101)),
                 (battery.calculate, (float("nan"), 50)), (battery.calculate, (50, -1)),
                 (charging.calculate, (50, 80, 20, 10, 90, 8)),
                 (charging.calculate, (50, 20, 80, 0, 90, 8)),
                 (charging.calculate, (50, 20, 80, 10, 0, 8)),
                 (ev_range.calculate, (50, 80, 0, 50, 0, "City")),
                 (ev_range.calculate, (50, 80, .16, 0, 0, "City")),
                 (regenerative.calculate, (-1, 50, 60, 1)),
                 (regenerative.calculate, (1000, 50, 60, 1.5)),
                 (motor.calculate, (-1, 1000)), (energy.calculate, (40, 101, 90, 90)),
                 (thermal.simulate, (25, 25, -1, 40))]
        for fn, args in cases:
            with self.subTest(fn=fn.__module__, args=args), self.assertRaises(ValueError):
                fn(*args)

    def test_trends_and_conservation(self):
        values, losses = energy.calculate(40, 95, 94, 97)
        self.assertAlmostEqual(values[-1] + sum(losses), 40)
        self.assertAlmostEqual(values[-1], 40 * .95 * .94 * .97)
        self.assertEqual(energy.calculate(0, 0, 0, 0), ([0, 0, 0, 0], [0, 0, 0]))
        _, cold = thermal.simulate(25, 25, 100, 40)
        _, hot = thermal.simulate(25, 25, 0, 40)
        self.assertLess(cold[-1], hot[-1])
        self.assertEqual(cold[0], 25)
        _, steady = thermal.simulate(25, 25, 50, 0)
        np.testing.assert_allclose(steady, 25)
        r = lambda ac: ev_range.calculate(50, 80, .16, 50, ac, "City")["range_km"]
        self.assertLess(r(2), r(0))
        for temp, label in [(34, "Normal Temperature"), (35, "Warm"), (45, "High Temperature"), (55, "Critical")]:
            self.assertEqual(thermal.status(temp), label)


if __name__ == "__main__":
    unittest.main()
