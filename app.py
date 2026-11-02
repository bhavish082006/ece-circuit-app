import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import json
from google import genai

# 1. Page Configuration
st.set_page_config(
    page_title="ECE Circuit & Arduino AI Designer",
    page_icon="⚡",
    layout="wide"
)

st.markdown("""
<style>
    .metric-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 14px;
        margin-bottom: 10px;
    }
    .board-container {
        background: #090d16;
        border: 2px solid #334155;
        border-radius: 12px;
        padding: 20px;
        color: white;
        font-family: monospace;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚡ ECE Circuit & AI Arduino Designer")
st.caption("Fast 5-second generation with interactive hardware pin mapping, Arduino sketches, and signal plots.")

# 2. Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Gemini API Key", type="password", help="Paste your key from Google AI Studio")
    
    st.subheader("Project Settings")
    project_title = st.text_input(
        "Circuit Project Topic", 
        value="Ultrasonic Distance Meter with LED and Buzzer Alert"
    )
    
    selected_example = st.selectbox(
        "Quick Presets",
        [
            "Custom Topic",
            "IR Sensor Automatic Street Light using Arduino",
            "4-Bit R-2R Ladder DAC using Op-Amp 741",
            "Variable Dual Voltage Regulator using LM317",
            "Pushbutton 7-Segment Digital Counter"
        ]
    )
    if selected_example != "Custom Topic":
        project_title = selected_example

    generate_btn = st.button("🚀 Generate Project", type="primary", use_container_width=True)

# 3. High-Speed Generation Function (Optimized for 3-5 seconds)
def generate_circuit_data(topic: str, key: str):
    client = genai.Client(api_key=key)
    
    prompt = f"""
    Act as an expert ECE Professor. Provide a concise hardware blueprint for: "{topic}".
    Output ONLY a valid JSON object matching this schema:
    {{
      "title": "{topic}",
      "summary": "Short 2-sentence explanation of the circuit principle.",
      "components": [
        {{"name": "Part Name", "specs": "Voltage/Current rating", "pin": "Connected Board Pin"}}
      ],
      "connections": [
        {{"pin": "D13", "component": "LED Anode", "color": "#ef4444", "description": "Current limited via 220 Ohm"}},
        {{"pin": "D9", "component": "Buzzer (+)", "color": "#f59e0b", "description": "PWM tone output"}},
        {{"pin": "GND", "component": "Common Ground Rail", "color": "#000000", "description": "0V Reference"}},
        {{"pin": "5V", "component": "VCC Rail", "color": "#ef4444", "description": "Power Supply"}}
      ],
      "arduino_code": "// Complete working Arduino sketch\\nvoid setup() {{\\n\\n}}\\nvoid loop() {{\\n\\n}}",
      "calculations": [
        {{"title": "Calculation Name", "formula": "R = V / I", "result": "Calculated value"}}
      ],
      "signal": {{"type": "pwm", "freq_hz": 490, "voltage": 5.0, "duty_cycle": 50}}
    }}
    Ensure valid JSON without backticks or markdown fences.
    """
    
    # Fast model endpoint
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config={"response_mime_type": "application/json"}
    )
    return json.loads(response.text)

# 4. Handle Execution
if generate_btn:
    if not api_key:
        st.error("⚠️ Please enter your Gemini API Key in the sidebar.")
    else:
        with st.spinner("Synthesizing pin mapping and code (3-5s)..."):
            try:
                data = generate_circuit_data(project_title, api_key)
                st.session_state["circuit_data"] = data
                st.success("Design generated successfully!")
            except Exception as e:
                st.error(f"Generation error: {str(e)}")

# 5. Interactive Display
if "circuit_data" in st.session_state:
    data = st.session_state["circuit_data"]
    
    st.subheader(f"📌 {data.get('title', project_title)}")
    st.info(data.get("summary", ""))

    tab1, tab2, tab3, tab4 = st.tabs([
        "🔌 Hardware Pinout & Wiring", 
        "📝 Arduino Code", 
        "📐 Theoretical Calculations", 
        "📈 Signal & Oscilloscope"
    ])

    # --- TAB 1: VISUAL BOARD & DYNAMIC WIRING ---
    with tab1:
        st.markdown("### 🎛️ Interactive Arduino Uno Board & Pin Wiring Map")
        
        connections = data.get("connections", [])
        conn_dict = {c["pin"].strip().upper(): c for c in connections if "pin" in c}

        # Build interactive visual representation of the Arduino board
        digital_pins = ["AREF", "GND", "D13", "D12", "D11~", "D10~", "D9~", "D8", "D7", "D6~", "D5~", "D4", "D3~", "D2", "D1 (TX)", "D0 (RX)"]
        power_analog_pins = ["RESET", "3.3V", "5V", "GND", "VIN", "A0", "A1", "A2", "A3", "A4", "A5"]

        def render_pin_list(pins):
            html = ""
            for p in pins:
                clean_p = p.replace("~", "").split()[0].upper()
                is_connected = False
                matched_conn = None
                
                for k, v in conn_dict.items():
                    if clean_p in k or k in clean_p:
                        is_connected = True
                        matched_conn = v
                        break
                        
                if is_connected:
                    wire_color = matched_conn.get("color", "#22c55e")
                    comp_name = matched_conn.get("component", "Connected")
                    html += f'''
                    <div style="display:flex; justify-content:space-between; align-items:center; background:#1e293b; border-left:5px solid {wire_color}; padding:6px 10px; margin:4px 0; border-radius:4px; font-size:12px;">
                        <span style="font-weight:bold; color:#38bdf8;">{p}</span>
                        <span style="color:#f8fafc; background:#065f46; padding:2px 6px; border-radius:3px;">➔ {comp_name}</span>
                    </div>
                    '''
                else:
                    html += f'''
                    <div style="display:flex; justify-content:space-between; align-items:center; background:#0f172a; border-left:5px solid #334155; padding:5px 10px; margin:4px 0; border-radius:4px; font-size:12px; color:#64748b;">
                        <span>{p}</span>
                        <span>nc</span>
                    </div>
                    '''
            return html

        col_board, col_table = st.columns([1.2, 1])

        with col_board:
            st.markdown(f"""
            <div class="board-container">
                <div style="text-align:center; margin-bottom:12px;">
                    <span style="font-weight:bold; color:#38bdf8; font-size:15px;">ARDUINO UNO R3 - WIRING MAP</span>
                    <p style="margin:2px 0 0 0; font-size:11px; color:#94a3b8;">Active pins highlighted with connection targets</p>
                </div>
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:16px;">
                    <div>
                        <div style="color:#f59e0b; font-weight:bold; font-size:12px; margin-bottom:6px;">POWER & ANALOG</div>
                        {render_pin_list(power_analog_pins)}
                    </div>
                    <div>
                        <div style="color:#38bdf8; font-weight:bold; font-size:12px; margin-bottom:6px;">DIGITAL I/O & PWM</div>
                        {render_pin_list(digital_pins)}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_table:
            st.markdown("### 🔌 Exact Wire Interconnection Table")
            if connections:
                st.table([
                    {
                        "Board Pin": c.get("pin", ""),
                        "Target Component": c.get("component", ""),
                        "Function": c.get("description", "")
                    }
                    for c in connections
                ])
            else:
                st.info("No explicit wiring generated.")

        st.markdown("### 📦 Component Bill of Materials")
        comps = data.get("components", [])
        if comps:
            cols = st.columns(min(len(comps), 3) if len(comps) > 0 else 1)
            for idx, comp in enumerate(comps):
                with cols[idx % 3]:
                    st.markdown(f"""
                    <div class="metric-card">
                        <strong style="color:#38bdf8; font-size:14px;">{comp.get('name')}</strong>
                        <p style="font-size:12px; color:#cbd5e1; margin:6px 0 2px 0;">⚡ <b>Specs:</b> {comp.get('specs')}</p>
                        <p style="font-size:12px; color:#cbd5e1; margin:0;">📍 <b>Connection:</b> {comp.get('pin')}</p>
                    </div>
                    """, unsafe_allow_html=True)

    # --- TAB 2: ARDUINO C++ SKETCH ---
    with tab2:
        st.markdown("### 💻 Complete Arduino C++ Source Code (.ino)")
        st.caption("Compilable code configured to match the hardware pinout in Tab 1.")
        code = data.get("arduino_code", "// Code unavailable")
        st.code(code, language="cpp", line_numbers=True)

    # --- TAB 3: THEORETICAL CALCULATIONS ---
    with tab3:
        st.markdown("### 📐 ECE Circuit Proofs & Formulas")
        calcs = data.get("calculations", [])
        if calcs:
            for item in calcs:
                with st.expander(f"🔹 {item.get('title')}", expanded=True):
                    st.latex(item.get("formula", ""))
                    st.success(f"**Calculated Result:** {item.get('result', '')}")
        else:
            st.info("No theoretical calculations required for this circuit topology.")

    # --- TAB 4: SIGNAL GRAPHING ---
    with tab4:
        st.markdown("### 📈 Virtual Oscilloscope Channel")
        sig = data.get("signal", {})
        freq = float(sig.get("freq_hz", 490))
        peak = float(sig.get("voltage", 5.0))
        duty = float(sig.get("duty_cycle", 50)) / 100.0

        t = np.linspace(0, 0.01, 1000)  # 10 ms window
        # Generate PWM pulse wave
        period = 1.0 / freq if freq > 0 else 0.002
        y = np.where((t % period) < (period * duty), peak, 0.0)

        fig, ax = plt.subplots(figsize=(9, 3.2))
        ax.plot(t * 1000, y, color="#00ffcc", linewidth=2.2, label=f"CH1 PWM ({int(freq)} Hz)")
        ax.set_xlabel("Time (ms)", color="#cbd5e1")
        ax.set_ylabel("Voltage (V)", color="#cbd5e1")
        ax.set_ylim(-0.5, peak + 1.0)
        ax.grid(True, linestyle="--", alpha=0.3, color="#64748b")
        ax.set_facecolor("#0b0f19")
        fig.patch.set_facecolor("#0f172a")
        ax.tick_params(colors="#cbd5e1")
        for spine in ax.spines.values():
            spine.set_color("#334155")
        ax.legend(facecolor="#1e293b", edgecolor="#334155", labelcolor="#f8fafc")
        
        st.pyplot(fig)
