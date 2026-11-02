import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# 1. Page Configuration
st.set_page_config(
    page_title="ECE Circuit & Arduino Designer",
    page_icon="⚡",
    layout="wide"
)

# Dark styling for the hardware lab look
st.markdown("""
<style>
    .metric-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 8px;
    }
    .board-frame {
        background: #090d16;
        border: 2px solid #1e293b;
        border-radius: 12px;
        padding: 16px;
        font-family: monospace;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚡ ECE Circuit & Custom Arduino Designer")
st.caption("Custom hardware wiring mapper, automatic C++ sketch generator, and waveform simulator (Zero API key needed).")

# 2. Session State for Custom Circuit Ideology
if "custom_circuit" not in st.session_state:
    st.session_state["custom_circuit"] = [
        {"pin": "D13", "component": "Red Warning LED (+)", "wire_color": "#ef4444", "role": "Digital Output (Current limited via 220Ω)"},
        {"pin": "D9", "component": "Piezo Buzzer (+)", "wire_color": "#f59e0b", "role": "PWM Tone Generation"},
        {"pin": "D2", "component": "IR Obstacle Sensor (OUT)", "wire_color": "#38bdf8", "role": "External Interrupt / Digital Input"},
        {"pin": "5V", "component": "Sensor VCC Rail", "wire_color": "#ef4444", "role": "5V Logic Supply"},
        {"pin": "GND", "component": "Common Ground Rail", "wire_color": "#10b981", "role": "0V Reference"}
    ]

# 3. Sidebar: Custom Ideology Builder
with st.sidebar:
    st.header("🛠️ Design Your Own Ideology")
    st.markdown("Add custom hardware connections to your project:")
    
    available_pins = [
        "D0 (RX)", "D1 (TX)", "D2", "D3~", "D4", "D5~", "D6~", "D7", 
        "D8", "D9~", "D10~", "D11~", "D12", "D13", "A0", "A1", "A2", 
        "A3", "A4", "A5", "5V", "3.3V", "GND", "RESET", "VIN"
    ]
    
    sel_pin = st.selectbox("Select Board Pin", available_pins)
    comp_name = st.text_input("Component Name", value="Ultrasonic Trig Pin")
    comp_role = st.selectbox("Signal / Function Role", ["Digital Output", "Digital Input", "PWM Control (~)", "Analog Input (ADC)", "Power (VCC)", "Ground (0V)"])
    wire_color = st.color_picker("Wire Color", "#38bdf8")
    
    col_add, col_clear = st.columns(2)
    with col_add:
        if st.button("➕ Add Wire", use_container_width=True, type="primary"):
            if comp_name.strip():
                st.session_state["custom_circuit"].append({
                    "pin": sel_pin,
                    "component": comp_name.strip(),
                    "wire_color": wire_color,
                    "role": comp_role
                })
                st.rerun()
    with col_clear:
        if st.button("🗑️ Reset All", use_container_width=True):
            st.session_state["custom_circuit"] = []
            st.rerun()

    st.divider()
    st.markdown("### 🎛️ Virtual Scope Controls")
    sig_freq = st.slider("Signal Frequency (Hz)", 10, 2000, 490)
    sig_duty = st.slider("PWM Duty Cycle (%)", 0, 100, 50)
    sig_vpeak = st.slider("Peak Voltage (V)", 1.0, 5.0, 5.0, 0.5)

# 4. Main Lab View
tab1, tab2, tab3, tab4 = st.tabs([
    "🔌 Visual Board & Wiring Map", 
    "💻 Generated Arduino Code", 
    "📐 ECE Calculations", 
    "📈 Virtual Oscilloscope"
])

# --- TAB 1: VISUAL BOARD & WIRING ---
with tab1:
    st.subheader("🎛️ Arduino Uno R3 Pin Mapping & Wiring Netlist")
    
    conn_list = st.session_state["custom_circuit"]
    # Map connections by base pin name
    active_pin_map = {}
    for c in conn_list:
        clean_key = c["pin"].replace("~", "").split()[0].upper()
        active_pin_map[clean_key] = c

    digital_pins = ["AREF", "GND", "D13", "D12", "D11~", "D10~", "D9~", "D8", "D7", "D6~", "D5~", "D4", "D3~", "D2", "D1 (TX)", "D0 (RX)"]
    analog_power_pins = ["RESET", "3.3V", "5V", "GND", "VIN", "A0", "A1", "A2", "A3", "A4", "A5"]

    def generate_pin_column(pin_array):
        html_rows = ""
        for p in pin_array:
            base_p = p.replace("~", "").split()[0].upper()
            if base_p in active_pin_map:
                wire_info = active_pin_map[base_p]
                wire_col = wire_info["wire_color"]
                c_target = wire_info["component"]
                html_rows += f"""
                <div style="display:flex; justify-content:space-between; align-items:center; background:#1e293b; border-left:6px solid {wire_col}; padding:5px 8px; margin:3px 0; border-radius:4px; font-size:11px; color:#ffffff;">
                    <span style="font-weight:bold; color:#38bdf8;">{p}</span>
                    <span style="background:#065f46; color:#a7f3d0; padding:2px 5px; border-radius:3px;">➔ {c_target}</span>
                </div>
                """
            else:
                html_rows += f"""
                <div style="display:flex; justify-content:space-between; align-items:center; background:#0b1120; border-left:4px solid #334155; padding:5px 8px; margin:3px 0; border-radius:4px; font-size:11px; color:#64748b;">
                    <span>{p}</span>
                    <span style="font-size:10px;">NC</span>
                </div>
                """
        return html_rows

    col_board, col_table = st.columns([1.3, 1])

    with col_board:
        st.markdown(f"""
        <div class="board-frame">
            <div style="text-align:center; padding-bottom:8px; border-bottom:1px solid #334155; margin-bottom:12px;">
                <span style="font-weight:bold; font-size:14px; color:#38bdf8;">ARDUINO UNO R3 - DYNAMIC PINOUT</span>
                <p style="margin:2px 0 0 0; font-size:11px; color:#94a3b8;">Active connections lit up with custom wire colors</p>
            </div>
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:16px;">
                <div>
                    <div style="font-size:11px; font-weight:bold; color:#f59e0b; margin-bottom:6px;">POWER & ANALOG</div>
                    {generate_pin_column(analog_power_pins)}
                </div>
                <div>
                    <div style="font-size:11px; font-weight:bold; color:#38bdf8; margin-bottom:6px;">DIGITAL I/O & PWM (~)</div>
                    {generate_pin_column(digital_pins)}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_table:
        st.write("### 📋 Active Wire Connection Table")
        if conn_list:
            st.table([
                {
                    "Arduino Pin": item["pin"],
                    "Target Component": item["component"],
                    "Function / Mode": item["role"]
                }
                for item in conn_list
            ])
        else:
            st.warning("No wires connected yet. Use the sidebar to add connections!")

# --- TAB 2: DYNAMIC ARDUINO CODE ---
with tab2:
    st.subheader("💻 Auto-Generated Arduino C++ Sketch")
    st.caption("Matches your custom hardware pinout dynamically.")

    # Generate custom sketch dynamically based on user's custom pins
    pin_declarations = ""
    pin_modes = ""
    loop_actions = ""

    for idx, c in enumerate(conn_list):
        pin_clean = c["pin"].replace("~", "").split()[0]
        var_name = c["component"].lower().replace(" ", "_").replace("(", "").replace(")", "").replace("-", "_").replace("+", "") + "_pin"
        
        # Avoid power/ground in code pin declaration
        if pin_clean in ["5V", "3.3V", "GND", "RESET", "VIN", "AREF"]:
            continue
            
        pin_num = pin_clean.replace("D", "").replace("A", "A")
        pin_declarations += f"const int {var_name} = {pin_num};  // Connected to {c['component']}\n"
        
        if "Output" in c["role"] or "PWM" in c["role"]:
            pin_modes += f"  pinMode({var_name}, OUTPUT);\n"
            if "PWM" in c["role"]:
                loop_actions += f"  analogWrite({var_name}, 128); // 50% PWM Duty Cycle\n"
            else:
                loop_actions += f"  digitalWrite({var_name}, HIGH); // Trigger output\n"
        elif "Input" in c["role"] or "ADC" in c["role"]:
            pin_modes += f"  pinMode({var_name}, INPUT);\n"
            loop_actions += f"  int {var_name}_val = digitalRead({var_name});\n"

    dynamic_sketch = f"""// Auto-Generated Arduino Sketch for Custom Circuit
{pin_declarations}
void setup() {{
  Serial.begin(9600);
{pin_modes}
  Serial.println("System Initialized Successfully.");
}}

void loop() {{
{loop_actions if loop_actions else "  // Add your logic code here"}
  delay(100);
}}
"""
    st.code(dynamic_sketch, language="cpp", line_numbers=True)

# --- TAB 3: THEORETICAL CALCULATIONS ---
with tab3:
    st.subheader("📐 Theoretical ECE Circuit Proofs")
    
    with st.expander("🔹 LED Current Limiting Calculation (Ohm's Law)", expanded=True):
        st.latex(r"R_{limit} = \frac{V_{CC} - V_F}{I_F} = \frac{5.0\text{V} - 2.0\text{V}}{0.02\text{A}} = 150\,\Omega")
        st.info("Using standard **220 Ω** for safe long-term component operation (~13.6 mA).")

    with st.expander("🔹 PWM Average Voltage & Duty Cycle", expanded=True):
        st.latex(r"V_{avg} = D \times V_{peak} = \left(\frac{" + str(sig_duty) + r"}{100}\right) \times " + str(sig_vpeak) + r"\text{V} = " + f"{(sig_duty / 100.0) * sig_vpeak:.2f}" + r"\,\text{V}")
        st.info(f"Calculated average voltage at **{sig_duty}%** duty cycle: **{(sig_duty / 100.0) * sig_vpeak:.2f} V**")

# --- TAB 4: OSCILLOSCOPE ---
with tab4:
    st.subheader("📈 Virtual Oscilloscope Signal Simulator")
    
    t = np.linspace(0, 0.01, 1000)  # 10 ms window
    period = 1.0 / sig_freq if sig_freq > 0 else 0.002
    duty_ratio = sig_duty / 100.0
    y = np.where((t % period) < (period * duty_ratio), sig_vpeak, 0.0)

    fig, ax = plt.subplots(figsize=(9, 3.2))
    ax.plot(t * 1000, y, color="#00ffcc", linewidth=2.2, label=f"CH1 PWM ({sig_freq} Hz, {sig_duty}%)")
    ax.set_xlabel("Time (ms)", color="#cbd5e1")
    ax.set_ylabel("Voltage (V)", color="#cbd5e1")
    ax.set_ylim(-0.5, sig_vpeak + 1.0)
    ax.grid(True, linestyle="--", alpha=0.3, color="#64748b")
    ax.set_facecolor("#0b0f19")
    fig.patch.set_facecolor("#0f172a")
    ax.tick_params(colors="#cbd5e1")
    for spine in ax.spines.values():
        spine.set_color("#334155")
    ax.legend(facecolor="#1e293b", edgecolor="#334155", labelcolor="#f8fafc")
    st.pyplot(fig)
