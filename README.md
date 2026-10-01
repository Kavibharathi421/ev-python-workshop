# Electric Vehicle Energy & Simulation Lab

A beginner-friendly Python + EV workshop by **Code Bridge Technology**. Students adjust controls, follow formulas, inspect Python, and interpret live Matplotlib visualizations. No database, API keys, or external assets are needed.

## Install and run

Use Python 3.10 or later. Open a terminal in `EV_Python_Workshop`:

```bash
python -m venv .venv
```

Activate it on Windows with `.venv\Scripts\activate`, or on macOS/Linux with `source .venv/bin/activate`. Then:

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

Open the local URL printed by Streamlit. Stop the server with Ctrl+C. If the `streamlit` command is unavailable, use `python -m streamlit run app.py`.

## Workshop guide

1. Start in **EV Learning Hub**. Choose Small, Medium, or Large EV in the sidebar and click **Apply preset**.
2. Explore the energy path from battery to wheels and the dashboard. Battery capacity, SOC, and speed are shared across relevant experiments.
3. Open a topic, read the question and formula, predict a result, and move one slider at a time.
4. Compare the graphs and read the engineering interpretation. Open **See the Python Behind This Calculation** to connect variables with results.
5. Download a CSV to record an experiment. Each export includes shared scenario inputs and the selected module's results; column names include units where relevant.
6. Complete the five Student Challenges. Wrong answers reveal a worked formula and allow another attempt. Progress records concepts solved during the session.
7. Use **Reset all experiments** to return to the default medium vehicle and clear challenge progress. Applying a preset also resets experiments and challenge progress.

Settings are session-local, survive page navigation, and are not saved to a database. Reloading a new browser session starts fresh. The dashboard combines independent experiments: it is not a time-stepped simulation of one drive.

## Topics and models

| Topic | Calculation / learning objective |
|---|---|
| Battery | Capacity × SOC gives available kWh; voltage × current gives watts |
| Range | Available energy / total consumption; speed, AC, and condition comparison |
| Charging | Required energy, grid losses, constant-power duration, and electricity cost in INR |
| Regeneration | Kinetic energy, joules-to-kWh conversion, repeated complete stops |
| Motor | Torque × angular speed; constant-torque comparison curves |
| Thermal | Analytic toy heat-balance model over 60 minutes; passive-cooling comparison |
| Energy flow | Sequential conversion efficiencies and conservation of energy |
| Challenges | Five multiple-choice problems with feedback and Python snippets |

### Model assumptions

This application uses simplified engineering models for educational demonstration. Real EV systems involve additional variables, control algorithms, battery characteristics, environmental conditions, and manufacturer-specific behavior.

- **Battery:** nominal capacity and voltage; no degradation, reserve, or voltage sag.
- **Range:** base consumption is referenced to 50 km/h with no AC. The illustrative speed multiplier is `0.75 + 0.25 × (speed/50)²`. Condition factors are City 1.00, Highway 1.05, Traffic 1.15, Aggressive 1.30. AC adds `AC kW / speed km/h`. These are teaching choices, not calibrated vehicle predictions. Speed stays above zero to avoid division by zero. No terrain or changing drive cycle.
- **Charging:** charger power is grid input. Both time and cost use grid energy after efficiency losses. No tapering or temperature limits. Equal start/target gives zero duration; a lower target produces an actionable error.
- **Regeneration:** each event is a full stop from the selected speed. Acceleration between events consumes energy; repeated stops do not create free energy. 100% efficiency is an ideal boundary only.
- **Motor:** the plots assume constant torque at every RPM to isolate the relationship, not a real motor's operating envelope.
- **Thermal:** load adds `0.012 × load` °C/min, while heat transfer coefficient is `0.008 + 0.072 × cooling/100` per minute. Analytic solution avoids numerical integration instability. Cooling exchanges heat with ambient and cannot guarantee a temperature decrease. No thermostat, refrigeration, cold-temperature performance, or cell chemistry. Status bands (35, 45, 55°C) are educational labels, not manufacturer limits.
- **Energy flow:** fixed stage efficiencies, no auxiliary loads or road resistance. Wheel energy plus conversion losses equals input energy.

## Folder structure

```text
EV_Python_Workshop/
├── app.py
├── requirements.txt
├── README.md
├── .streamlit/config.toml
├── modules/
│   ├── __init__.py
│   ├── validation.py
│   ├── battery.py
│   ├── range.py
│   ├── charging.py
│   ├── regenerative.py
│   ├── motor.py
│   ├── thermal.py
│   └── energy.py
├── visualizations/
│   ├── __init__.py
│   ├── style.py
│   ├── battery_plots.py
│   ├── range_plots.py
│   ├── charging_plots.py
│   └── energy_plots.py
├── tests/
│   ├── test_models.py
│   └── test_app.py
└── assets/README.md
```

Calculation modules contain pure validated functions independent of Streamlit. Plot functions return Matplotlib figures; the app closes each figure after rendering. `app.py` owns navigation, shared session state, and teaching content. Charts use NumPy arrays, and CSV/table output uses Pandas.

## Verification

From the project directory, after installing requirements:

```bash
python -m unittest discover -s tests -v
```

Tests include known numerical answers, invalid and boundary inputs, conservation of energy, every navigation item and chart, changes to each module, shared state, presets, reset, charging validation, and challenge feedback through Streamlit AppTest. Browser layout should also be reviewed at the workshop's display size; AppTest verifies execution and rendered elements, not pixel layout.

## Streamlit Community Cloud

1. Commit the project to a GitHub repository. Do not commit virtual environments or secrets.
2. In Streamlit Community Cloud, select **Create app** and select the repository and branch.
3. Set the entrypoint to `EV_Python_Workshop/app.py` if uploading this enclosing workspace, or `app.py` if the project itself is the repository root. Dependencies are alongside the entrypoint.
4. Select a supported Python version compatible with the requirements (Python 3.11 was used for local validation).
5. Deploy. No secrets or database configuration are required.

For theme configuration discovery, using the project folder as the repository root is recommended. Local startup should likewise run from that folder.

References: [official deployment guide](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app) and [official AppTest documentation](https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest).

Deployment is prepared but does not happen automatically; publishing requires your own repository and Streamlit account.
