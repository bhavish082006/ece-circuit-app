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

# Custom Styling for modern dark theme
st.markdown("""
<style>
    .metric-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .stCodeBlock {
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚡ ECE Circuit & AI Arduino Designer")
st.write("Generate interactive pinouts, theoretical ECE calculations, Arduino C++ sketches, and virtual oscilloscope waveforms.")

# 2. Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Gemini API Key", type="password", help="Get a free key from https://aistudio.google.com")
    
    st.subheader("Project Settings")
    project_title = st.text_input(
        "Project Topic", 
        value="Ultrasonic Distance Meter with LED and Buzzer Alert"
    )
    
    example_prompts = [
        "Select an example...",
        "4-Bit R-2R Ladder DAC using Op-Amp 741",
        "Variable Dual Voltage Regulator using LM317",
        "Pushbutton Controlled Digital Counter with 7-Segment Display",
        "IR Sensor Automatic Street Light using Arduino"
    ]
    selected_example = st.selectbox("Quick Examples", example_prompts)
    if selected_example != "Select an example...":
        project_title = selected_example

    generate_btn = st.button("🚀 Generate Project", type="primary", use_container_width=True)

# 3. AI Service Function
def generate_ece_project(title: str, key: str):
    client = genai.Client(api_key=key)
    prompt = f"""
    Act as a senior Electronics and Communication Engineering (ECE) professor.
    Design a comprehensive hardware implementation for: "{title}".
    
    Return ONLY a raw JSON object (no markdown formatting, no backticks, no comments) matching this schema:
    {{
      "title": "{title}",
      "summary": "2-sentence technical summary of the circuit operating principle.",
      "components": [
        {{
          "name": "Component Name (e.g., Arduino Uno R3, 220 Ohm Resistor)",
          "voltage": "e.g., 5V DC or 2.0V Forward Drop",
          "current": "e.g., 15mA",
          "purpose": "Precise hardware function in this circuit",
          "connections": "Detailed pin-to-pin wiring (e.g., Anode -> Pin 13, Cathode -> GND rail)"
        }}
      ],
      "wiring_table": [
        {{"from": "Board Pin / Node", "to": "Target Component Pin", "signal_type": "Power / Ground / Digital I/O / Analog / PWM"}}
      ],
      "calculations": [
        {{
          "title": "Parameter Name (e.g., Current Limiting Resistor)",
          "formula": "LaTeX formula (e.g., R = (V_{{cc}} - V_f) / I_d)",
          "steps": "Step-by-step substitution of values",
          "result": "Final value with standard component choice"
        }}
      ],
      "arduino_code": "Full, complete, compilable Arduino C++ sketch (.ino) with setup() and loop()",
      "waveform": {{
        "signal_type": "digital_pwm" or "analog_sine" or "pulse",
        "frequency": "Frequency in Hz or description",
        "voltage_peak": 5.0,
        "description": "Expected oscilloscope signal explanation"
      }}
    }}
    """
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={"response_mime_type": "application/json"}
    )
    return json.loads(response.text)

# 4. State Management
if generate_btn:
    if not api_key:
        st.error("⚠️ Please enter your Gemini API Key in the sidebar.")
    else:
        with st.spinner("Analyzing circuit topology, calculating parameters, and writing code..."):
            try:
                result = generate_ece_project(project_title, api_key)
                st.session_state["project_data"] = result
                st.success("Project generated successfully!")
            except Exception as e:
                st.error(f"Generation failed: {str(e)}")

# 5. Main Dashboard Display
if "project_data" in st.session_state:
    data = st.session_state["project_data"]

    st.subheader(f"📌 {data.get('title', project_title)}")
    st.info(data.get("summary", ""))

    tab1, tab2, tab3, tab4 = st.tabs([
        "🔌 Components & Pinouts", 
        "📝 Arduino Code", 
        "📐 Theoretical Calculations", 
        "📈 Signal & Oscilloscope"
    ])

    # --- TAB 1: COMPONENTS & PIN CONNECTION TABLE ---
    with tab1:
        st.write("### Active Component Bill of Materials (BOM)")
        
        comps = data.get("components", [])
        num_cols = min(len(comps), 3) if comps else 1
        cols = st.columns(num_cols)
        
        for idx, comp in enumerate(comps):
            with cols[idx % num_cols]:
                st.markdown(f"""
                <div class="metric-card">
                    <h4 style="color:#38bdf8; margin:0 0 8px 0;">{comp.get('name')}</h4>
                    <p style="font-size: 13px; color:#94a3b8; margin:0 0 10px 0;">{comp.get('purpose')}</p>
                    <p style="margin:2px 0; font-size:13px;">⚡ <b>Voltage:</b> {comp.get('voltage')}</p>
                    <p style="margin:2px 0; font-size:13px;">🔋 <b>Current:</b> {comp.get('current')}</p>
                    <p style="margin:6px 0 0 0; font-size:12px; color:#cbd5e1;">📍 <b>Wiring:</b> {comp.get('connections')}</p>
                </div>
                """, unsafe_allow_html=True)

        st.write("### Pin-to-Pin Interconnection Netlist")
        wiring = data.get("wiring_table", [])
        if wiring:
            st.table(wiring)

    # --- TAB 2: ARDUINO C++ CODE ---
    with tab2:
        st.write("### Embedded Arduino C++ Sketch")
        st.caption("Ready to paste directly into the Arduino IDE or upload to an ATmega328P board.")
        arduino_code = data.get("arduino_code", "// No code generated")
        st.code(arduino_code, language="cpp", line_numbers=True)

    # --- TAB 3: THEORETICAL CALCULATIONS ---
    with tab3:
        st.write("### ECE Design Proofs & Mathematical Formulas")
        calcs = data.get("calculations", [])
        for c in calcs:
            with st.expander(f"🔹 {c.get('title')}", expanded=True):
                st.latex(c.get("formula"))
                st.write(f"**Step-by-step substitution:** {c.get('steps')}")
                st.success(f"**Final Component Choice / Value:** {c.get('result')}")

    # --- TAB 4: SIGNAL PLOTTING & OSCILLOSCOPE ---
    with tab4:
        st.write("### Virtual Oscilloscope Trace")
        wave_info = data.get("waveform", {})
        st.caption(f"**Signal Description:** {wave_info.get('description', 'Signal output')}")
        
        # Signal Generation with NumPy
        t = np.linspace(0, 0.05, 1000) # 50 ms window
        sig_type = wave_info.get("signal_type", "digital_pwm")
        peak_v = float(wave_info.get("voltage_peak", 5.0))

        fig, ax = plt.subplots(figsize=(10, 3.5))
        
        if sig_type == "analog_sine":
            y = (peak_v / 2) * np.sin(2 * np.pi * 100 * t) + (peak_v / 2)
            ax.set_title("Analog Signal Output (Sine Wave)")
        elif sig_type == "pulse":
            y = np.zeros_like(t)
            y[(t >= 0.01) & (t <= 0.015)] = peak_v
            y[(t >= 0.03) & (t <= 0.035)] = peak_v
            ax.set_title("Trigger / Echo Acoustic Pulse Waveform")
        else: # Default: Digital PWM / Square Wave
            y = (np.sign(np.sin(2 * np.pi * 80 * t)) * 0.5 + 0.5) * peak_v
            ax.set_title("Digital Logic / PWM Output (0V - 5V)")

        ax.plot(t * 1000, y, color="#00ffcc", linewidth=2.5, label="Channel 1 (CH1)")
        ax.set_xlabel("Time (ms)", color="#cbd5e1")
        ax.set_ylabel("Voltage (V)", color="#cbd5e1")
        ax.set_ylim(-0.5, peak_v + 1.0)
        ax.grid(True, linestyle="--", alpha=0.3, color="#64748b")
        
        # Dark theme graph styling
        ax.set_facecolor("#0b0f19")
        fig.patch.set_facecolor("#0f172a")
        ax.tick_params(colors="#cbd5e1")
        for spine in ax.spines.values():
            spine.set_color("#334155")
            
        ax.legend(facecolor="#1e293b", edgecolor="#334155", labelcolor="#f8fafc")
        st.pyplot(fig)
else:
    st.info("👈 Enter your Gemini API key and project title in the sidebar, then click **Generate Project**.")
