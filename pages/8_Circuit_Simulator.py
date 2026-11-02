import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="ECE Circuit Simulator",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ ECE Circuit Simulator")

st.markdown("""
### Design and simulate electronic circuits

Draw circuits, connect components, modify values,
and observe electrical behavior.
""")

st.info(
    "This simulator is free to use and runs inside your website."
)

components.html(
    """
    <iframe
        src="https://www.falstad.com/circuit/circuitjs.html"
        width="100%"
        height="750"
        style="border:2px solid #26334d;
               border-radius:12px;"
        allowfullscreen>
    </iframe>
    """,
    height=770,
    scrolling=True
)

st.markdown("""
### Available experiments

- RC and RL circuits
- Diode and rectifier circuits
- BJT and MOSFET circuits
- Op-Amp circuits
- Filters and oscillators
- Digital logic circuits
""")
