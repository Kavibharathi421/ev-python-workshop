import numpy as np
from .validation import check


def calculate(torque, rpm):
    check(torque, "Torque")
    check(rpm, "RPM")
    omega = 2 * np.pi * rpm / 60
    return {"omega_rad_s": omega, "power_w": torque * omega,
            "power_kw": torque * omega / 1000}
