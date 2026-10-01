"""Self-contained, offline 3D landing experience."""
from pathlib import Path
import base64
import streamlit as st
import streamlit.components.v1 as components

ASSETS = Path(__file__).resolve().parent / "assets"
MODEL = ASSETS / "models" / "reference_car.json"
CAR_IMAGE = ASSETS / "reference-car-hero.png"


@st.cache_data
def _template(asset_version):
    template = (ASSETS / "ev_landing.html").read_text(encoding="utf-8")
    engine = (ASSETS / "vendor" / "three.min.js").read_text(encoding="utf-8")
    model = MODEL.read_text(encoding="utf-8")
    image = base64.b64encode(CAR_IMAGE.read_bytes()).decode("ascii")
    parts = (ASSETS / "car_parts.js").read_text(encoding="utf-8")
    return (template.replace("/* THREE_ENGINE */", engine)
            .replace("/* BLENDER_MODEL */", model)
            .replace("/* CAR_PARTS */", parts)
            .replace("__CAR_IMAGE__", f"data:image/png;base64,{image}"))


def render_landing(scenario):
    asset_version = (MODEL.stat().st_mtime_ns, (ASSETS / "ev_landing.html").stat().st_mtime_ns,
                     CAR_IMAGE.stat().st_mtime_ns, (ASSETS / "car_parts.js").stat().st_mtime_ns)
    document = _template(asset_version).replace("__CAPACITY__", str(scenario["capacity"]))
    document = document.replace("__SOC__", str(scenario["soc"]))
    components.html(document, height=1020, scrolling=False)
