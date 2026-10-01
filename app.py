"""Code Bridge Technology · interactive EV workshop."""
import inspect
import html
import numpy as np
import pandas as pd
import streamlit as st
from modules import battery, range as ev_range, charging, regenerative, motor, thermal, energy
from visualizations import battery_plots, range_plots, charging_plots, energy_plots
from visualizations.style import line, bars
import matplotlib.pyplot as plt
from landing import render_landing

st.set_page_config(page_title="EV Energy & Simulation Lab", page_icon="⚡", layout="wide")
st.markdown("""<style>
.block-container {max-width:1320px;padding-top:2rem;padding-bottom:3rem;}
h1 {font-size:2.5rem!important;letter-spacing:-.055rem;}
h2 {font-size:1.55rem!important;} h3 {font-size:1.12rem!important;}
[data-testid="stMetric"] {background:#F3F6F3;border:1px solid #E1E8E1;border-radius:12px;padding:15px;}
[data-testid="stMetricValue"] {font-size:1.7rem;}
.eyebrow {font-size:.75rem;letter-spacing:.16em;font-weight:700;color:#54725E;margin-bottom:10px;}
.hero {background:#153F30;color:white;border-radius:18px;padding:30px;margin:12px 0 24px;}
.hero h2 {color:white;font-size:2rem!important;max-width:620px;}
.hero p {color:#D6E4DA;max-width:720px;}
.flow {display:flex;flex-wrap:wrap;align-items:center;gap:9px;margin:16px 0 24px;}
.node {border:1px solid #CCDCD0;border-radius:10px;background:#F3F7F3;padding:14px 18px;font-weight:600;}
.arrow {color:#A57327;font-weight:bold;} .battery {border:3px solid #236448;border-radius:14px;padding:7px;max-width:460px;margin:16px 0;}
.fill {height:46px;background:#73A58B;border-radius:6px;}
.caption {color:#62736A;font-size:.85rem;}
@media(max-width:640px){h1{font-size:1.85rem!important;}.hero{padding:20px;}.node{padding:9px;}}
</style>""", unsafe_allow_html=True)

DEFAULTS = dict(capacity=50, soc=80, voltage=400, current=100, consumption=0.16,
                speed=50, ac=1.0, condition="City", target=90, charger=7.0, efficiency=90,
                price=8.0, mass=1600, regen=65, events=10, torque=180, rpm=3000,
                initial=25, ambient=25, cooling=60, load=40, flow_energy=40.0,
                inverter=95, motor_eff=94, gear=97)
PRESETS = {"Small EV": dict(capacity=30, mass=1100, consumption=0.12, torque=110),
           "Medium EV": dict(capacity=50, mass=1600, consumption=0.16, torque=180),
           "Large EV": dict(capacity=85, mass=2200, consumption=0.21, torque=300)}
if "scenario" not in st.session_state:
    st.session_state.scenario = DEFAULTS.copy()


def reset(preset=None):
    st.session_state.scenario = DEFAULTS.copy()
    if preset:
        st.session_state.scenario.update(PRESETS[preset])
    for key in list(st.session_state):
        if key.startswith(("input_", "answer_", "solved_")):
            del st.session_state[key]


def update(key):
    st.session_state.scenario[key] = st.session_state["input_" + key]


def slider(label, key, low, high, step=1):
    widget = "input_" + key
    if widget not in st.session_state:
        st.session_state[widget] = st.session_state.scenario[key]
    return st.slider(label, low, high, step=step, key=widget, on_change=update, args=(key,))


def flow(labels):
    st.markdown('<div class="flow">' + '<span class="arrow">→</span>'.join(
        f'<span class="node">{html.escape(label)}</span>' for label in labels) + '</div>', unsafe_allow_html=True)


def plot(fig):
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)


def metrics(items):
    cols = st.columns(len(items))
    for col, (label, value) in zip(cols, items):
        col.metric(label, value)


def intro(title, question, formula):
    st.header(title)
    st.subheader("1. What are we calculating?")
    st.write(question)
    with st.expander("2. Formula", expanded=True):
        st.code(formula, language="text")


def meaning(text, function, results=None):
    st.subheader("4. What does this mean in an EV?")
    st.info(text)
    with st.expander("See the Python Behind This Calculation"):
        st.code(inspect.getsource(function), language="python")
    if results:
        csv = pd.DataFrame([results]).to_csv(index=False).encode("utf-8")
        st.download_button("Download calculated results · CSV", csv, "ev_results.csv", "text/csv")


PAGES = ["🏠 EV Learning Hub", "🔋 1. Battery Simulator", "🚗 2. Range Simulator",
         "⚡ 3. Charging Simulator", "♻️ 4. Regenerative Braking", "⚙️ 5. Motor & Power",
         "🌡️ 6. Thermal Management", "📊 7. EV Energy Flow", "🧪 8. Student Challenge"]
with st.sidebar:
    st.markdown("### ⚡ CODE BRIDGE\nTechnology · Workshop series")
    st.divider()
    page = st.radio("EXPLORE THE LAB", PAGES, key="navigation")
    st.divider()
    preset = st.selectbox("Educational vehicle preset", list(PRESETS), index=1)
    st.button("Apply preset", on_click=reset, args=(preset,), use_container_width=True)
    st.button("Reset all experiments", on_click=reset, use_container_width=True)
    st.caption("Shared settings carry between topics. Presets are illustrative, not manufacturer specifications.")

s = st.session_state.scenario
if page != PAGES[0]:
    st.markdown('<div class="eyebrow">CODE BRIDGE TECHNOLOGY / EV WORKSHOP</div>', unsafe_allow_html=True)
    st.title("Electric Vehicle Energy & Simulation Lab")
    st.write("Learn EV Technology Through Python, Calculations & Visual Simulation")
    st.caption("INTERACTIVE LAB  /  8 LEARNING MODULES  /  LIVE PYTHON CALCULATIONS")
    st.divider()



def hub():
    render_landing(s)
    start, explore = st.columns(2)
    with start:
        st.button("Start with the battery ?", type="primary", use_container_width=True,
                  on_click=lambda: st.session_state.update(navigation=PAGES[1]))
    with explore:
        st.button("Explore range & motion ?", use_container_width=True,
                  on_click=lambda: st.session_state.update(navigation=PAGES[2]))
    st.caption("Drag the 3D model to explore. Select Battery view to reveal the underfloor pack. Vehicle geometry is an educational concept, not a manufacturer replica.")
    st.subheader("Your vehicle · live dashboard")
    with st.expander("Adjust your shared vehicle", expanded=True):
        a, b, c = st.columns(3)
        with a: slider("Battery capacity (kWh)", "capacity", 10, 100)
        with b: slider("State of charge (%)", "soc", 0, 100)
        with c: slider("Vehicle speed (km/h)", "speed", 5, 150)
    b = battery.calculate(s["capacity"], s["soc"])
    r = ev_range.calculate(s["capacity"], s["soc"], s["consumption"], s["speed"], s["ac"], s["condition"])
    m = motor.calculate(s["torque"], s["rpm"])
    re = regenerative.calculate(s["mass"], s["speed"], s["regen"], s["events"])
    minutes, temperatures = thermal.simulate(s["initial"], s["ambient"], s["cooling"], s["load"])
    flow_values, flow_losses = energy.calculate(s["flow_energy"], s["inverter"], s["motor_eff"], s["gear"])
    valid_target = s["target"] >= s["soc"]
    ch = charging.calculate(s["capacity"], s["soc"], s["target"], s["charger"], s["efficiency"], s["price"]) if valid_target else None
    metrics([("SOC", f'{s["soc"]}%'), ("Battery energy", f'{b["available_kwh"]:.1f} kWh'),
             ("Estimated range", f'{r["range_km"]:.0f} km'), ("Charging time", f'{ch["hours"]:.1f} h' if ch else "—")])
    st.write("")
    metrics([("Motor power", f'{m["power_kw"]:.1f} kW'), ("Recovered · all stops", f'{re["total_kwh"]:.3f} kWh'),
             ("Battery temp · 60 min", f'{temperatures[-1]:.1f} °C')])
    if not valid_target:
        st.warning("Charging target is below current SOC. Update the target in Charging Simulator.")
    st.info(f'At {s["soc"]}% SOC, your {s["capacity"]} kWh pack holds {b["available_kwh"]:.1f} kWh. '
            f'With {s["condition"].lower()} conditions at {s["speed"]} km/h and {s["ac"]:.1f} kW AC, '
            f'this model estimates {r["range_km"]:.0f} km. Each dashboard value reflects its own experiment settings.')
    st.subheader("Dashboard visual overview")
    chart_a, chart_b = st.columns(2)
    with chart_a:
        plot(energy_plots.energy_flow(flow_values, flow_losses))
    with chart_b:
        plot(range_plots.comparison(s["capacity"], s["soc"], s["consumption"], s["speed"], s["ac"]))
    chart_c, chart_d = st.columns(2)
    with chart_c:
        plot(battery_plots.capacity_chart(s["capacity"], b["available_kwh"]))
    with chart_d:
        recovery_events = np.arange(s["events"] + 1)
        plot(line("Recovered energy from repeated stops", "Full stops (count)", "Recovered energy (kWh)",
                   recovery_events, recovery_events * re["recovered_kwh"]))
    st.subheader("Battery temperature · next 60 minutes")
    plot(line("Thermal response", "Elapsed time (min)", "Temperature (°C)", minutes, temperatures))
    st.subheader("EV architecture · from stored energy to motion")
    flow(["Battery", "Inverter", "Motor", "Gear Reduction", "Wheels"])
    st.caption("The inverter controls electrical power to the motor. Reduction gears trade motor speed for wheel torque.")
    st.subheader("Recovering energy when you slow down")
    flow(["Braking", "Motor as Generator", "Electrical Energy", "Battery"])
    st.subheader("What students will learn")
    cards = [("01 / Store", "Battery energy, SOC, and electrical power"),
             ("02 / Travel", "Range estimation and driving conditions"),
             ("03 / Recharge", "Charging time, efficiency, and cost"),
             ("04 / Recover", "Kinetic energy and regenerative braking"),
             ("05 / Drive", "Torque, motor speed, and power"),
             ("06 / Connect", "Thermal management and EV energy flow")]
    for i in range(0, 6, 3):
        for col, (title, text) in zip(st.columns(3), cards[i:i+3]):
            with col, st.container(border=True):
                st.subheader(title)
                st.write(text)
    st.subheader("How This Simulator Works")
    flow(["Change Input", "Python Calculates", "Matplotlib Visualizes", "Student Interprets Result"])


def battery_page():
    intro("01 / Battery Simulator", "How much energy is in the pack, and how quickly can it deliver energy?",
          "Available energy (kWh) = capacity (kWh) × SOC / 100\nPower (kW) = voltage (V) × current (A) / 1000")
    a, b = st.columns(2)
    with a:
        slider("Battery capacity (kWh)", "capacity", 10, 100)
        slider("State of charge (%)", "soc", 0, 100)
    with b:
        slider("Battery voltage (V)", "voltage", 200, 800)
        slider("Current (A)", "current", 0, 300)
    r = battery.calculate(s["capacity"], s["soc"], s["voltage"], s["current"])
    st.subheader("3. Live Result")
    metrics([("Battery capacity", f'{s["capacity"]} kWh'), ("Current SOC", f'{s["soc"]}%'),
             ("Available energy", f'{r["available_kwh"]:.1f} kWh'), ("Battery power", f'{r["power_kw"]:.1f} kW')])
    st.markdown(f'<div class="battery" role="img" aria-label="{s["soc"]} percent state of charge"><div class="fill" style="width:{s["soc"]}%"></div></div>', unsafe_allow_html=True)
    st.caption(f'{s["soc"]}% SOC · Higher SOC → more available energy')
    a, b = st.columns(2)
    with a: plot(battery_plots.capacity_chart(s["capacity"], r["available_kwh"]))
    with b: plot(battery_plots.power_chart(s["voltage"], s["current"]))
    meaning("kWh measures stored energy; kW measures the rate of energy transfer. This model assumes nominal capacity and voltage, with no battery aging or voltage sag.", battery.calculate, {**s, **r})


def range_page():
    intro("02 / Range Simulator", "How far could this battery take us under a chosen set of driving assumptions?",
          "Available energy = capacity × SOC / 100\nSpeed factor = 0.75 + 0.25 × (speed / 50)²\nTotal consumption = base consumption × condition factor × speed factor + AC power / speed\nEstimated range (km) = available energy (kWh) / total consumption (kWh/km)")
    a, b = st.columns(2)
    with a:
        slider("Battery capacity (kWh)", "capacity", 10, 100)
        slider("State of charge (%)", "soc", 0, 100)
        slider("Base energy consumption (kWh/km)", "consumption", 0.08, 0.40, 0.01)
    with b:
        slider("Vehicle speed (km/h)", "speed", 5, 150)
        slider("AC usage · electrical power (kW)", "ac", 0.0, 5.0, 0.1)
        key = "input_condition"
        if key not in st.session_state: st.session_state[key] = s["condition"]
        st.selectbox("Driving condition", list(ev_range.CONDITIONS), key=key, on_change=update, args=("condition",))
    r = ev_range.calculate(s["capacity"], s["soc"], s["consumption"], s["speed"], s["ac"], s["condition"])
    st.caption("Teaching assumptions: City ×1.00 · Highway ×1.05 · Traffic ×1.15 · Aggressive ×1.30. Base consumption is referenced to 50 km/h without AC. These factors are illustrative.")
    st.subheader("3. Live Result")
    metrics([("Estimated range", f'{r["range_km"]:.1f} km'), ("Available energy", f'{r["available_kwh"]:.1f} kWh'),
             ("Total consumption", f'{r["consumption_kwh_km"]:.3f} kWh/km')])
    plot(range_plots.soc_curve(s["soc"], r["range_km"]))
    a, b = st.columns(2)
    with a: plot(range_plots.comparison(s["capacity"], s["soc"], s["consumption"], s["speed"], s["ac"]))
    with b: plot(range_plots.consumption_curve(r["available_kwh"]))
    meaning("Higher consumption means fewer kilometers from the same energy. AC uses energy over time, so its cost per kilometer increases at low speed. Try doubling SOC while keeping other settings fixed. Terrain, weather, battery reserves, and real driving cycles are not modeled.", ev_range.calculate, {**s, **r})


def charging_page():
    intro("03 / Charging Simulator", "How long does a charging session take, and what does the electricity cost?",
          "Energy required = capacity × (target SOC − starting SOC) / 100\nIdeal time = energy required / charger power\nGrid energy = energy required / (efficiency / 100)\nEstimated time = grid energy / charger power\nCost (₹) = grid energy × price per kWh")
    a, b = st.columns(2)
    with a:
        slider("Battery capacity (kWh)", "capacity", 10, 100)
        slider("Starting SOC (%)", "soc", 0, 100)
        slider("Target SOC (%)", "target", 0, 100)
    with b:
        slider("Charger power · grid input (kW)", "charger", 1.0, 250.0, 0.5)
        slider("Charging efficiency (%)", "efficiency", 50, 100)
        slider("Electricity price (₹/kWh)", "price", 0.0, 30.0, 0.5)
    st.subheader("3. Live Result")
    try:
        r = charging.calculate(s["capacity"], s["soc"], s["target"], s["charger"], s["efficiency"], s["price"])
    except ValueError as exc:
        st.error(str(exc))
        meaning("Charging adds energy, so the target must be at least the starting SOC.", charging.calculate)
        return
    metrics([("Energy required", f'{r["required_kwh"]:.1f} kWh'), ("Charging power", f'{s["charger"]:.1f} kW'),
             ("Estimated charging time", f'{r["hours"]:.2f} h'), ("Electricity cost", f'₹{r["cost_inr"]:.2f}')])
    st.progress(s["soc"] / 100, text=f'Start: {s["soc"]}% → target: {s["target"]}% · projected session')
    st.caption(f'Grid energy: {r["grid_kwh"]:.2f} kWh · Ideal loss-free time: {r["ideal_hours"]:.2f} hours')
    plot(charging_plots.charging_curve(s["soc"], s["target"], r["hours"]))
    meaning("The grid supplies more energy than the battery stores because charging has losses. This constant-power estimate excludes high-SOC tapering, temperature limits, and charger limits; real sessions can take longer. Equal start and target SOC require no charging.", charging.calculate, {**s, **r})


def regen_page():
    intro("04 / Regenerative Braking", "How much motion energy can be returned to the battery when the vehicle stops?",
          "Speed (m/s) = speed (km/h) / 3.6\nKinetic energy (J) = 0.5 × mass (kg) × speed (m/s)²\nRecovered energy (kWh) = kinetic energy × efficiency / 100 / 3,600,000\nTotal recovered = recovered energy per stop × braking events")
    flow(["Vehicle Moving", "Kinetic Energy", "Braking", "Motor as Generator", "Electrical Energy", "Battery"])
    a, b = st.columns(2)
    with a:
        slider("Vehicle mass (kg)", "mass", 500, 3500, 50)
        slider("Vehicle speed (km/h)", "speed", 5, 150)
    with b:
        slider("Regeneration efficiency (%)", "regen", 0, 100)
        slider("Full-stop braking events (count)", "events", 0, 100)
    r = regenerative.calculate(s["mass"], s["speed"], s["regen"], s["events"])
    st.subheader("3. Live Result")
    metrics([("Kinetic energy per stop", f'{r["kinetic_kwh"]:.3f} kWh'), ("Recovered per stop", f'{r["recovered_kwh"]:.3f} kWh'),
             ("Total recovered", f'{r["total_kwh"]:.3f} kWh')])
    a, b = st.columns(2)
    with a: plot(bars("Energy of one full stop", "Energy destination", "Energy (kWh)", ["Kinetic", "Recovered", "Not recovered"], [r["kinetic_kwh"], r["recovered_kwh"], r["kinetic_kwh"]-r["recovered_kwh"]]))
    with b:
        events = np.arange(s["events"] + 1)
        plot(line("Energy accumulates over repeated stops", "Full stops (count)", "Recovered energy (kWh)", events, events*r["recovered_kwh"]))
    meaning("Not all kinetic energy can be recovered in a real EV. Each event here means a complete stop from the selected speed; the vehicle must accelerate again between stops. Friction braking, battery acceptance, and motor limits reduce recovery. 100% is an ideal limit.", regenerative.calculate, {**s, **r})


def motor_page():
    intro("05 / Motor & Power", "How do turning force and rotational speed combine to produce mechanical power?",
          "Angular speed (rad/s) = 2π × RPM / 60\nPower (W) = torque (N·m) × angular speed (rad/s)\nPower (kW) = power (W) / 1000")
    a, b = st.columns(2)
    with a: slider("Motor torque (N·m)", "torque", 0, 500, 5)
    with b: slider("Motor speed (RPM)", "rpm", 0, 12000, 100)
    r = motor.calculate(s["torque"], s["rpm"])
    st.subheader("3. Live Result")
    metrics([("Angular speed", f'{r["omega_rad_s"]:.1f} rad/s'), ("Motor power", f'{r["power_w"]:.0f} W'), ("Motor power", f'{r["power_kw"]:.2f} kW')])
    x = np.linspace(0, 12000, 120)
    a, b = st.columns(2)
    with a: plot(line("Torque vs RPM · assumed constant torque", "Motor speed (RPM)", "Torque (N·m)", x, np.full_like(x, s["torque"])))
    with b: plot(line("Power vs RPM · assumed constant torque", "Motor speed (RPM)", "Mechanical power (kW)", x, s["torque"] * 2 * np.pi * x / 60 / 1000))
    meaning("Torque is turning force, RPM is rotational speed, and power is the rate of doing work. At zero RPM, mechanical power is zero even with torque. These curves hold torque constant to isolate the formula; real motors have torque and power limits and losses.", motor.calculate, {**s, **r})


def thermal_page():
    intro("06 / Thermal Management", "How do battery load, ambient conditions, and cooling affect temperature over time?",
          "Simplified educational thermal model\nHeating rate = 0.012 × load (kW), in °C/min\nk = 0.008 + 0.072 × cooling / 100, in 1/min\nEquilibrium = ambient + heating rate / k\nT(t) = equilibrium + (initial − equilibrium) × exp(−k × t)")
    st.warning("Simplified educational thermal model. Constants and status bands are teaching choices, not battery specifications or operating guidance.")
    a, b = st.columns(2)
    with a:
        slider("Initial battery temperature (°C)", "initial", -20, 70)
        slider("Ambient temperature (°C)", "ambient", -20, 50)
    with b:
        slider("Cooling level (%)", "cooling", 0, 100)
        slider("Battery load (kW)", "load", 0, 200)
    t, temp = thermal.simulate(s["initial"], s["ambient"], s["cooling"], s["load"])
    st.subheader("3. Live Result")
    state = thermal.status(temp[-1])
    metrics([("Temperature · 60 min", f'{temp[-1]:.1f} °C'), ("Change from start", f'{temp[-1]-temp[0]:+.1f} °C'), ("Educational status", state)])
    {"Normal Temperature": st.success, "Warm": st.info, "High Temperature": st.warning, "Critical": st.error}[state](state + " · simulated endpoint")
    st.caption("Teaching bands: below 35°C Normal · 35–<45°C Warm · 45–<55°C High · 55°C+ Critical. Cold-temperature effects are not modeled.")
    fig = line("Battery temperature over 60 minutes", "Elapsed time (min)", "Temperature (°C)", t, temp)
    _, passive = thermal.simulate(s["initial"], s["ambient"], 0, s["load"])
    ax = fig.axes[0]
    ax.lines[0].set_label("Selected cooling")
    ax.plot(t, passive, color="#D49A36", linestyle="--", label="Passive cooling only")
    ax.legend(frameon=False)
    plot(fig)
    flow(["Battery load", "Heat generation", "Cooling removes heat", "Temperature responds"])
    meaning("More cooling increases heat transfer to ambient. Temperature falls only when cooling exceeds heat generation; a loaded pack can still warm up with cooling enabled. This model uses constant load and cooling and does not simulate a thermostat, cell chemistry, or refrigeration.", thermal.simulate, {**s, "final_temperature_c": float(temp[-1])})


def energy_page():
    intro("07 / EV Energy Flow", "How much battery energy reaches the wheels after each conversion stage?",
          "Stage output = stage input × efficiency / 100\nStage loss = stage input − stage output\nWheel energy = battery energy × inverter efficiency × motor efficiency × gear efficiency\n(Use efficiency fractions in the final expression.)")
    a, b = st.columns(2)
    with a:
        slider("Battery energy input (kWh)", "flow_energy", 0.0, 100.0, 1.0)
        slider("Inverter efficiency (%)", "inverter", 0, 100)
    with b:
        slider("Motor efficiency (%)", "motor_eff", 0, 100)
        slider("Gear efficiency (%)", "gear", 0, 100)
    values, losses = energy.calculate(s["flow_energy"], s["inverter"], s["motor_eff"], s["gear"])
    st.subheader("3. Live Result")
    metrics([("Energy at wheels", f'{values[-1]:.2f} kWh'), ("Total conversion losses", f'{sum(losses):.2f} kWh'),
             ("Combined efficiency", f'{s["inverter"]*s["motor_eff"]*s["gear"]/10000:.1f}%')])
    flow([f"Battery · {values[0]:.1f} kWh", f"Inverter · {values[1]:.1f} kWh", f"Motor · {values[2]:.1f} kWh", f"Reduction Gear · {values[3]:.1f} kWh", f"Wheels · {values[3]:.1f} kWh"])
    plot(energy_plots.energy_flow(values, losses))
    st.dataframe(pd.DataFrame({"Stage": ["Inverter", "Motor", "Reduction gear"], "Input (kWh)": values[:-1], "Output (kWh)": values[1:], "Loss (kWh)": losses}), hide_index=True, use_container_width=True)
    meaning("Efficiencies multiply, so even small losses accumulate. Wheel energy plus all stage losses equals the original battery energy. Energy is converted, not destroyed; losses largely become heat. Auxiliary loads and road resistance are outside this demonstration.", energy.calculate, {**s, "wheel_kwh": values[-1], "inverter_loss_kwh": losses[0], "motor_loss_kwh": losses[1], "gear_loss_kwh": losses[2]})


CHALLENGES = [
    ("Battery energy", "A 60 kWh battery is at 50% SOC. How much energy is available?", ["15 kWh", "30 kWh", "60 kWh"], 1, "60 × 50 / 100 = 30 kWh", "available_energy = 60 * 50 / 100"),
    ("Range", "A 50 kWh EV has 80% SOC and total consumption of 0.16 kWh/km. What is its range?", ["200 km", "250 km", "320 km"], 1, "50 × 0.80 / 0.16 = 250 km", "range_km = (50 * 0.80) / 0.16"),
    ("Charging", "You need to store 20 kWh using a 10 kW charger at 80% efficiency. How long does it take?", ["1.6 hours", "2 hours", "2.5 hours"], 2, "Grid energy = 20 / 0.80 = 25 kWh; time = 25 / 10 = 2.5 hours", "hours = 20 / 0.80 / 10"),
    ("Motor power", "A motor delivers 100 N·m at 3,000 RPM. What is its approximate power?", ["3.14 kW", "31.4 kW", "300 kW"], 1, "100 × (2π × 3000 / 60) / 1000 ≈ 31.4 kW", "power_kw = 100 * (2 * np.pi * 3000 / 60) / 1000"),
    ("Regenerative braking", "A stop releases 0.20 kWh of kinetic energy. At 60% recovery, how much returns to the battery?", ["0.12 kWh", "0.20 kWh", "0.32 kWh"], 0, "0.20 × 0.60 = 0.12 kWh", "recovered_kwh = 0.20 * 0.60"),
]


def challenges_page():
    st.header("08 / Student Challenge")
    st.write("Five small experiments in engineering thinking. Use the simulators, make a prediction, then check your reasoning.")
    score = sum(st.session_state.get(f"solved_{i}", False) for i in range(5))
    st.progress(score / 5, text=f"{score} / 5 concepts solved")
    for i, (title, question, options, answer, explanation, code) in enumerate(CHALLENGES):
        with st.container(border=True):
            st.subheader(f"Challenge {i+1} · {title}")
            st.markdown("**1. What are we calculating?**")
            st.write(question)
            for j, col in enumerate(st.columns(3)):
                if col.button(options[j], key=f"choice_{i}_{j}", use_container_width=True):
                    st.session_state[f"answer_{i}"] = j
                    if j == answer: st.session_state[f"solved_{i}"] = True
                    st.rerun()
            chosen = st.session_state.get(f"answer_{i}")
            if chosen is not None:
                st.markdown("**3. Live Result**")
                if chosen == answer: st.success("Correct! You connected the concept to the calculation.")
                else: st.warning("Try Again. Use the formula below, then choose another answer.")
                st.markdown("**2. Formula**")
                st.code(explanation, language="text")
                st.markdown("**4. What does this mean in an EV?**")
                st.write(["SOC tells us what fraction of the pack's energy is available.", "Stored energy divided by energy per kilometer gives driving distance.", "Charging losses increase the energy bought and time needed.", "Torque and rotational speed together determine mechanical power.", "Regeneration returns only part of the energy of motion."][i])
                with st.expander("See the Python Behind This Calculation"):
                    st.code(code, language="python")
    if score == 5: st.success("Workshop complete · All five concepts solved. Try changing a preset and predicting the results before looking.")


pages = [hub, battery_page, range_page, charging_page, regen_page, motor_page, thermal_page, energy_page, challenges_page]
try:
    pages[PAGES.index(page)]()
except ValueError as exc:
    st.error(f"Please check your inputs: {exc}")

st.divider()
st.caption("This application uses simplified engineering models for educational demonstration. Real EV systems involve additional variables, control algorithms, battery characteristics, environmental conditions, and manufacturer-specific behavior.")
st.caption("CODE BRIDGE TECHNOLOGY · Learn by changing. Understand by observing.")
