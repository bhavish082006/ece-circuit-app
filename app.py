import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# 1. Page Configuration
st.set_page_config(
    page_title="ECE Circuit & Custom Arduino Designer",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ ECE Circuit & Custom Arduino Designer")
st.caption("Custom hardware wiring mapper, automatic C++ sketch generator, and waveform simulator (Zero API key needed).")

# 2. Session State for Connections
if "custom_circuit" not in st.session_state:
    st.session_state["custom_circuit"] = [
        {"pin": "D13", "component": "Red Warning LED (+)", "wire_color": "🔴 Red", "role": "Digital Output"},
        {"pin": "D9~", "component": "Piezo Buzzer (+)", "wire_color": "🟡 Yellow", "role": "PWM Control (~)"},
        {"pin": "D2", "component": "IR Obstacle Sensor (OUT)", "wire_color": "🔵 Blue", "role": "Digital Input"},
        {"pin": "5V", "component": "Sensor VCC Rail", "wire_color": "🔴 Red", "role": "Power (5V)"},
        {"pin": "GND", "component": "Common Ground Rail", "wire_color": "🟢 Green", "role": "Ground (0V)"}
    ]

# 3. Sidebar: Design Your Own Ideology
with st.sidebar:
    st.header("🛠️ Design Your Own Ideology")
    st.markdown("Add custom hardware connections to your project:")
    
    available_pins = [
        "D0 (RX)", "D1 (TX)", "D2", "D3~", "D4", "D5~", "D6~", "D7", 
        "D8", "D9~", "D10~", "D11~", "D12", "D13", "A0", "A1", "A2", 
        "A3", "A4", "A5", "5V", "3.3V", "GND", "RESET", "VIN"
    ]
    
    sel_pin = st.selectbox("Select Board Pin", available_pins)
    comp_name = st.text_input("Component Name", value="HC-SR04 Trig Pin")
    comp_role = st.selectbox(
        "Signal / Function Role", 
        ["Digital Output", "Digital Input", "PWM Control (~)", "Analog Input (ADC)", "Power (5V)", "Ground (0V)"]
    )
    wire_color = st.selectbox("Wire Color", ["🔴 Red", "🔵 Blue", "🟡 Yellow", "🟢 Green", "⚪ White", "⚫ Black"])
    
    col_add, col_clear = st.columns(2)
    with col_add:
        if st.button("➕ Add Wire", use_container_width=True, type="primary"):
            if comp_name.strip():
                # Avoid duplicate pin entries by replacing if already present
                existing = [i for i, c in enumerate(st.session_state["custom_circuit"]) if c["pin"] == sel_pin]
                new_entry = {
                    "pin": sel_pin,
                    "component": comp_name.strip(),
                    "wire_color": wire_color,
                    "role": comp_role
                }
                if existing:
                    st.session_state["custom_circuit"][existing[0]] = new_entry
                else:
                    st.session_state["custom_circuit"].append(new_entry)
                st.rerun()
    with col_clear:
        if st.button("🗑️ Reset All", use_container_width=True):
            st.session_state["custom_circuit"] = []
            st.rerun()

    st.divider()
    st.markdown("### 🎛️ Oscilloscope Settings")
    sig_freq = st.slider("Signal Frequency (Hz)", 10, 2000, 490)
    sig_duty = st.slider("PWM Duty Cycle (%)", 0, 100, 50)
    sig_vpeak = st.slider("Peak Voltage (V)", 1.0, 5.0, 5.0, 0.5)

# 4. Main Navigation Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🔌 Visual Board & Wiring Map", 
    "💻 Generated Arduino Code", 
    "📐 ECE Calculations", 
    "📈 Virtual Oscilloscope"
])

conn_list = st.session_state["custom_circuit"]
pin_lookup = {c["pin"].split()[0].replace("~", "").upper(): c for c in conn_list}

# --- TAB 1: VISUAL PINOUT & WIRING ---
with tab1:
    st.subheader("🎛️ Arduino Uno R3 Pin Mapping & Wiring Netlist")
    
    col_board, col_table = st.columns([1.1, 1])

    with col_board:
        st.markdown("#### ⚡ Arduino Hardware Headers")
        
        c1, c2 = st.columns(2)
        
        with c1:
            st.info("**POWER & ANALOG IN**")
            analog_power = ["RESET", "3.3V", "5V", "GND", "VIN", "A0", "A1", "A2", "A3", "A4", "A5"]
            for p in analog_power:
                clean_p = p.upper()
                if clean_p in pin_lookup:
                    item = pin_lookup[clean_p]
                    st.success(f"**{p}** ➔ {item['component']} ({item['wire_color']})")
                else:
                    st.caption(f"⚪ {p} : [Unconnected]")

        with c2:
            st.info("**DIGITAL I/O & PWM (~)**")
            digital_pins = ["AREF", "GND", "D13", "D12", "D11~", "D10~", "D9~", "D8", "D7", "D6~", "D5~", "D4", "D3~", "D2", "D1 (TX)", "D0 (RX)"]
            for p in digital_pins:
                clean_p = p.split()[0].replace("~", "").upper()
                if clean_p in pin_lookup:
                    item = pin_lookup[clean_p]
                    st.success(f"**{p}** ➔ {item['component']} ({item['wire_color']})")
                else:
                    st.caption(f"⚪ {p} : [Unconnected]")

    with col_table:
        st.markdown("#### 📋 Active Connections Table")
        if conn_list:
            display_data = [
                {
                    "Arduino Pin": c["pin"],
                    "Connected Component": c["component"],
                    "Wire Color": c["wire_color"],
                    "Mode / Function": c["role"]
                }
                for c in conn_list
            ]
            st.dataframe(display_data, use_container_width=True)
            
            # Allow user to delete individual connections
            st.markdown("##### Remove a Wire")
            rem_pin = st.selectbox("Select Pin to Remove", [c["pin"] for c in conn_list], key="rem_pin_box")
            if st.button("❌ Disconnect Wire"):
                st.session_state["custom_circuit"] = [c for c in conn_list if c["pin"] != rem_pin]
                st.rerun()
        else:
            st.warning("No wires connected yet. Use the sidebar to add connections!")

# --- TAB 2: DYNAMIC ARDUINO C++ CODE ---
with tab2:
    st.subheader("💻 Compilable Arduino C++ Sketch")
    st.caption("Configured automatically to match your active pin assignments.")

    pin_defs = ""
    setup_code = ""
    loop_code = ""

    for c in conn_list:
        base_pin = c["pin"].split()[0].replace("~", "")
        # Ignore dedicated power/ground pins in C++ code
        if base_pin in ["5V", "3.3V", "GND", "RESET", "VIN", "AREF"]:
            continue
            
        var_name = "".join(ch if ch.isalnum() else "_" for ch in c["component"].lower()).strip("_") + "_pin"
        pin_num = base_pin.replace("D", "")
        
        pin_defs += f"const int {var_name} = {pin_num};  // Pin for {c['component']}\n"
        
        if "Output" in c["role"] or "PWM" in c["role"]:
            setup_code += f"  pinMode({var_name}, OUTPUT);\n"
            if "PWM" in c["role"]:
                loop_code += f"  analogWrite({var_name}, 128);  // 50% PWM Duty Cycle\n"
            else:
                loop_code += f"  digitalWrite({var_name}, HIGH); // Active State\n"
        elif "Input" in c["role"] or "ADC" in c["role"]:
            setup_code += f"  pinMode({var_name}, INPUT);\n"
            if "ADC" in c["role"]:
                loop_code += f"  int {var_name}_val = analogRead({var_name});\n"
            else:
                loop_code += f"  int {var_name}_val = digitalRead({var_name});\n"

    generated_sketch = f"""// Auto-Generated Arduino Sketch for Custom Circuit
{pin_defs}
void setup() {{
  Serial.begin(9600);
{setup_code}
  Serial.println("System Initialized Successfully.");
}}

void loop() {{
{loop_code if loop_code else "  // Insert your custom logic here"}
  delay(100);
}}
"""
    st.code(generated_sketch, language="cpp", line_numbers=True)

# --- TAB 3: THEORETICAL CALCULATIONS ---
with tab3:
    st.subheader("📐 Theoretical ECE Circuit Proofs")
    
    with st.expander("🔹 LED Current Limiting Calculation (Ohm's Law)", expanded=True):
        st.latex(r"R_{limit} = \frac{V_{CC} - V_F}{I_F} = \frac{5.0\text{V} - 2.0\text{V}}{0.02\text{A}} = 150\,\Omega")
        st.info("Using standard **220 Ω** for safe long-term operation (~13.6 mA drive).")

    with st.expander("🔹 PWM Average Voltage Output", expanded=True):
        st.latex(r"V_{avg} = D \times V_{peak} = \left(\frac{" + str(sig_duty) + r"}{100}\right) \times " + str(sig_vpeak) + r"\text{V} = " + f"{(sig_duty / 100.0) * sig_vpeak:.2f}" + r"\,\text{V}")
        st.info(f"Average calculated voltage at **{sig_duty}%** duty cycle: **{(sig_duty / 100.0) * sig_vpeak:.2f} V**")

# --- TAB 4: OSCILLOSCOPE ---
with tab4:
    st.subheader("📈 Virtual Oscilloscope Signal Simulator")
    
    t = np.linspace(0, 0.01, 1000)
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
