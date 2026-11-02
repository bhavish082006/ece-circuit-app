import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# ---------------------------------------------------------
# 1. PAGE SETUP & WORKBENCH STYLING
# ---------------------------------------------------------
st.set_page_config(
    page_title="ECE Virtual Circuit & Arduino Workbench",
    page_icon="⚡",
    layout="wide"
)

st.markdown("""
<style>
    .workbench-card {
        background-color: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .board-header {
        background-color: #005c8a;
        color: white;
        padding: 8px 14px;
        border-radius: 6px;
        font-weight: bold;
        font-size: 14px;
        letter-spacing: 1px;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚡ ECE Circuit & Custom Arduino Workbench")
st.caption("Virtual interactive laboratory for circuit topology, dynamic pin wiring, ECE formulas, and signal visualization.")

# ---------------------------------------------------------
# 2. DEFAULT WORKBENCH SAMPLES
# ---------------------------------------------------------
PRESET_PROJECTS = {
    "Custom Workbench (Blank / User Ideology)": {
        "summary": "Design your own custom circuit by connecting pins and discrete ECE components using the left sidebar.",
        "connections": [],
        "calculations": [
            {"title": "Ohm's Law Current Limiting", "formula": r"R = \frac{V_{CC} - V_{drop}}{I_{forward}}", "note": "Standard resistor sizing for safe semiconductor drive."}
        ],
        "default_wave": "Square / PWM"
    },
    "4-Bit R-2R Ladder DAC (Digital to Analog)": {
        "summary": "Converts binary digital output words from Arduino pins into a discrete analog voltage using an R-2R matched resistor ladder network and Op-Amp buffer.",
        "connections": [
            {"pin": "D0 (RX)", "component": "2R Branch Resistor (Bit 0 - LSB)", "wire_color": "🔵 Blue", "role": "Digital Output"},
            {"pin": "D1 (TX)", "component": "2R Branch Resistor (Bit 1)", "wire_color": "🔵 Blue", "role": "Digital Output"},
            {"pin": "D2", "component": "2R Branch Resistor (Bit 2)", "wire_color": "🔵 Blue", "role": "Digital Output"},
            {"pin": "D3~", "component": "2R Branch Resistor (Bit 3 - MSB)", "wire_color": "🔵 Blue", "role": "Digital Output"},
            {"pin": "GND", "component": "R-2R Termination Ground Rail", "wire_color": "⚫ Black", "role": "Ground (0V)"},
            {"pin": "5V", "component": "LM741 VCC+ Rail", "wire_color": "🔴 Red", "role": "Power (5V)"}
        ],
        "calculations": [
            {"title": "DAC Resolution / Step Size", "formula": r"V_{step} = \frac{V_{ref}}{2^N} = \frac{5.0\,\text{V}}{2^4} = 0.3125\,\text{V}", "note": "Step resolution per discrete digital count."},
            {"title": "Full-Scale Maximum Output", "formula": r"V_{out(max)} = V_{ref} \left(1 - \frac{1}{2^N}\right) = 5.0\,\text{V} \times \left(\frac{15}{16}\right) = 4.6875\,\text{V}", "note": "Peak achievable analog voltage at digital state 1111."}
        ],
        "default_wave": "DAC Staircase Ramp"
    },
    "Ultrasonic Distance Meter with Alert Stage": {
        "summary": "Acoustic time-of-flight sensor measuring reflection travel time to trigger digital LED indicators and a piezo transducer.",
        "connections": [
            {"pin": "D9~", "component": "HC-SR04 Trigger (10us Pulse)", "wire_color": "🟡 Yellow", "role": "Digital Output"},
            {"pin": "D10~", "component": "HC-SR04 Echo (Return Pulse)", "wire_color": "⚪ White", "role": "Digital Input"},
            {"pin": "D13", "component": "Red Warning LED (+)", "wire_color": "🔴 Red", "role": "Digital Output"},
            {"pin": "D8", "component": "Piezo Buzzer (+)", "wire_color": "🟡 Yellow", "role": "PWM Control (~)"},
            {"pin": "5V", "component": "HC-SR04 VCC (+5V)", "wire_color": "🔴 Red", "role": "Power (5V)"},
            {"pin": "GND", "component": "Common Ground Rail", "wire_color": "⚫ Black", "role": "Ground (0V)"}
        ],
        "calculations": [
            {"title": "Time of Flight Ranging Equation", "formula": r"\text{Distance (cm)} = \frac{\Delta t \times 0.0343\,\text{cm/\mu s}}{2}", "note": "Division by 2 accounts for two-way acoustic path."},
            {"title": "LED Ballast Resistor", "formula": r"R = \frac{5.0\,\text{V} - 2.0\,\text{V}}{0.02\,\text{A}} = 150\,\Omega \implies \text{Select } 220\,\Omega", "note": "Safely limits microcontroller port sink/source to ~13.6 mA."}
        ],
        "default_wave": "Square / PWM"
    },
    "IR Proximity Sensor Automatic Street Luminaire": {
        "summary": "Autonomous luminaire dimming system that samples digital infrared reflected telemetry to regulate illumination via pulse-width modulation.",
        "connections": [
            {"pin": "D2", "component": "FC-51 IR Obstacle Sensor (OUT)", "wire_color": "🔵 Blue", "role": "Digital Input"},
            {"pin": "D6~", "component": "NPN Switching Transistor Base / LED", "wire_color": "🟡 Yellow", "role": "PWM Control (~)"},
            {"pin": "5V", "component": "IR Sensor VCC Rail", "wire_color": "🔴 Red", "role": "Power (5V)"},
            {"pin": "GND", "component": "Common Ground Rail", "wire_color": "⚫ Black", "role": "Ground (0V)"}
        ],
        "calculations": [
            {"title": "PWM Energy Efficiency Savings", "formula": r"P_{\text{standby}} = D \times P_{\text{full}} = 0.15 \times P_{\text{full}}", "note": "85% energy saved during idle standby operation."},
            {"title": "Transistor Base Drive Resistor", "formula": r"I_B = \frac{I_C}{\beta} = \frac{200\,\text{mA}}{100} = 2\,\text{mA} \implies R_B = \frac{5.0\,\text{V} - 0.7\,\text{V}}{0.002\,\text{A}} = 2.15\,\text{k}\Omega", "note": "Ensures full saturation switching operation."}
        ],
        "default_wave": "Square / PWM"
    }
}

# ---------------------------------------------------------
# 3. STATE INITIALIZATION
# ---------------------------------------------------------
if "current_circuit" not in st.session_state:
    st.session_state["current_circuit"] = PRESET_PROJECTS["4-Bit R-2R Ladder DAC (Digital to Analog)"]["connections"].copy()

if "calcs" not in st.session_state:
    st.session_state["calcs"] = PRESET_PROJECTS["4-Bit R-2R Ladder DAC (Digital to Analog)"]["calculations"].copy()

# ---------------------------------------------------------
# 4. SIDEBAR: CUSTOM IDEOLOGY BUILDER
# ---------------------------------------------------------
with st.sidebar:
    st.header("🛠️ Circuit Controls")
    
    preset_choice = st.selectbox("Load Project Preset", list(PRESET_PROJECTS.keys()), index=1)
    if st.button("📥 Load Preset Template", use_container_width=True):
        st.session_state["current_circuit"] = PRESET_PROJECTS[preset_choice]["connections"].copy()
        st.session_state["calcs"] = PRESET_PROJECTS[preset_choice]["calculations"].copy()
        st.rerun()

    st.markdown("---")
    st.subheader("💡 Design Your Own Ideology")
    st.caption("Manually route physical pins to any component:")

    all_pins = [
        "D0 (RX)", "D1 (TX)", "D2", "D3~", "D4", "D5~", "D6~", "D7",
        "D8", "D9~", "D10~", "D11~", "D12", "D13", "AREF",
        "A0", "A1", "A2", "A3", "A4", "A5",
        "5V", "3.3V", "GND", "RESET", "VIN"
    ]

    selected_pin = st.selectbox("Select Pin", all_pins)
    custom_comp = st.text_input("Component Label", value="220Ω Resistor to Red LED")
    comp_role = st.selectbox("Component Function", [
        "Digital Output", "Digital Input", "PWM Control (~)", "Analog Input (ADC)", "Power (5V)", "Ground (0V)"
    ])
    wire_color = st.selectbox("Wire Color", ["🔴 Red", "🔵 Blue", "🟡 Yellow", "🟢 Green", "⚪ White", "⚫ Black"])

    col_add, col_reset = st.columns(2)
    with col_add:
        if st.button("➕ Connect Wire", use_container_width=True, type="primary"):
            if custom_comp.strip():
                # Replace existing wire if pin is reused
                st.session_state["current_circuit"] = [
                    c for c in st.session_state["current_circuit"] if c["pin"] != selected_pin
                ]
                st.session_state["current_circuit"].append({
                    "pin": selected_pin,
                    "component": custom_comp.strip(),
                    "wire_color": wire_color,
                    "role": comp_role
                })
                st.rerun()
    with col_reset:
        if st.button("🗑️ Clear All", use_container_width=True):
            st.session_state["current_circuit"] = []
            st.rerun()

    st.markdown("---")
    st.subheader("📊 Oscilloscope Generator")
    wave_type = st.selectbox("Signal Topology", ["Square / PWM", "Sinusoidal AC", "Triangular Wave", "DAC Staircase Ramp"])
    freq = st.slider("Frequency (Hz)", 10, 2000, 500)
    v_peak = st.slider("Peak Amplitude (V)", 1.0, 5.0, 5.0, 0.5)
    duty = st.slider("Duty Cycle (%)", 5, 95, 50)

# ---------------------------------------------------------
# 5. LAB BENCH TABS
# ---------------------------------------------------------
tab_board, tab_code, tab_theory, tab_scope = st.tabs([
    "🔌 Visual Pinout & Hardware Workbench",
    "💻 Compilable Arduino C++ Code",
    "📐 ECE Theoretical Derivations",
    "📈 Virtual Scope Telemetry"
])

# Quick lookup dictionary for pinned connections
netlist = {c["pin"].split()[0].replace("~", "").upper(): c for c in st.session_state["current_circuit"]}

# --- TAB 1: VISUAL BOARD & WIRING ---
with tab_board:
    st.subheader("🎛️ Physical Arduino Uno R3 Header Netlist")
    st.caption("Active connection points reflect wire colors and linked circuit components.")

    col_hardware, col_netlist = st.columns([1.1, 1])

    with col_hardware:
        st.markdown('<div class="board-header">ARDUINO UNO R3 - PHYSICAL TERMINALS</div>', unsafe_allow_html=True)
        st.write("")
        
        col_analog, col_digital = st.columns(2)
        
        with col_analog:
            st.markdown("##### 🔌 Power & Analog In")
            analog_side = ["RESET", "3.3V", "5V", "GND", "VIN", "A0", "A1", "A2", "A3", "A4", "A5"]
            for p in analog_side:
                clean_name = p.upper()
                if clean_name in netlist:
                    wire = netlist[clean_name]
                    st.success(f"🟢 **{p}** ➔ {wire['component']} ({wire['wire_color']})")
                else:
                    st.caption(f"⚪ **{p}** : [Open / NC]")

        with col_digital:
            st.markdown("##### ⚡ Digital I/O & PWM (~)")
            digital_side = ["AREF", "GND", "D13", "D12", "D11~", "D10~", "D9~", "D8", "D7", "D6~", "D5~", "D4", "D3~", "D2", "D1 (TX)", "D0 (RX)"]
            for p in digital_side:
                clean_name = p.split()[0].replace("~", "").upper()
                if clean_name in netlist:
                    wire = netlist[clean_name]
                    st.success(f"🟢 **{p}** ➔ {wire['component']} ({wire['wire_color']})")
                else:
                    st.caption(f"⚪ **{p}** : [Open / NC]")

    with col_netlist:
        st.markdown("##### 📋 Wire Interconnection Netlist")
        if st.session_state["current_circuit"]:
            table_records = [
                {
                    "Header Pin": c["pin"],
                    "Connected Element": c["component"],
                    "Lead Color": c["wire_color"],
                    "Electrical Role": c["role"]
                }
                for c in st.session_state["current_circuit"]
            ]
            st.dataframe(table_records, use_container_width=True)

            st.write("---")
            st.markdown("###### Disconnect Terminal Wire")
            pins_in_use = [c["pin"] for c in st.session_state["current_circuit"]]
            pin_to_remove = st.selectbox("Select Pin to Detach", pins_in_use)
            if st.button("✂️ Disconnect Selected Wire"):
                st.session_state["current_circuit"] = [c for c in st.session_state["current_circuit"] if c["pin"] != pin_to_remove]
                st.rerun()
        else:
            st.info("No connections added yet. Use the sidebar on the left to route circuit wires!")

# --- TAB 2: ARDUINO C++ GENERATION ---
with tab_code:
    st.subheader("💻 Auto-Generated C++ Sketch")
    st.caption("Directly synchronizes pin mode declarations with your active workbench wiring.")

    pin_declarations = ""
    setup_lines = ""
    loop_lines = ""

    for item in st.session_state["current_circuit"]:
        pin_raw = item["pin"].split()[0].replace("~", "")
        # Filter dedicated power pins
        if pin_raw in ["5V", "3.3V", "GND", "RESET", "VIN", "AREF"]:
            continue
            
        clean_var = "".join(ch if ch.isalnum() else "_" for ch in item["component"].lower()).strip("_") + "_pin"
        pin_num = pin_raw.replace("D", "")

        pin_declarations += f"const int {clean_var} = {pin_num};  // Pin routed to {item['component']}\n"

        if "Output" in item["role"] or "PWM" in item["role"]:
            setup_lines += f"  pinMode({clean_var}, OUTPUT);\n"
            if "PWM" in item["role"]:
                loop_lines += f"  analogWrite({clean_var}, 128); // Standard 50% PWM test\n"
            else:
                loop_lines += f"  digitalWrite({clean_var}, HIGH); // Enable node output\n"
        elif "Input" in item["role"] or "ADC" in item["role"]:
            setup_lines += f"  pinMode({clean_var}, INPUT);\n"
            if "ADC" in item["role"]:
                loop_lines += f"  int {clean_var}_reading = analogRead({clean_var});\n"
            else:
                loop_lines += f"  int {clean_var}_reading = digitalRead({clean_var});\n"

    sketch_content = f"""// ===============================================================
// ECE Workbench Automatic Code Generation
// Topology: {preset_choice}
// ===============================================================

{pin_declarations if pin_declarations else "// No digital/analog microcontroller pins mapped.\\n"}
void setup() {{
  Serial.begin(9600);
{setup_lines}
  Serial.println("System Hardware Initialized Successfully.");
}}

void loop() {{
{loop_lines if loop_lines else "  // Custom control ideology executes here"}
  delay(100);
}}
"""
    st.code(sketch_content, language="cpp", line_numbers=True)

# --- TAB 3: ECE FORMULAS & PROOFS ---
with tab_theory:
    st.subheader("📐 Theoretical ECE Circuit Proofs")
    for formula_item in st.session_state["calcs"]:
        with st.expander(f"🔹 {formula_item['title']}", expanded=True):
            st.latex(formula_item["formula"])
            st.info(formula_item["note"])

# --- TAB 4: OSCILLOSCOPE SIGNAL TELEMETRY ---
with tab_scope:
    st.subheader("📈 Virtual Oscilloscope Trace")
    
    t = np.linspace(0, 0.01, 1000)  # 10 millisecond window
    period = 1.0 / freq if freq > 0 else 0.002
    
    if wave_type == "Square / PWM":
        duty_frac = duty / 100.0
        wave = np.where((t % period) < (period * duty_frac), v_peak, 0.0)
    elif wave_type == "Sinusoidal AC":
        wave = (v_peak / 2.0) + (v_peak / 2.0) * np.sin(2 * np.pi * freq * t)
    elif wave_type == "Triangular Wave":
        phase = (t % period) / period
        wave = v_peak * (2 * np.abs(phase - 0.5))
    else:  # DAC Staircase
        steps = 16
        wave = np.floor(((t % period) / period) * steps) * (v_peak / steps)

    fig, ax = plt.subplots(figsize=(9, 3.4))
    ax.plot(t * 1000, wave, color="#00ffcc", linewidth=2.2, label=f"CH1: {wave_type} ({freq} Hz)")
    ax.set_xlabel("Time (milliseconds)", color="#cbd5e1")
    ax.set_ylabel("Amplitude (Volts)", color="#cbd5e1")
    ax.set_ylim(-0.5, v_peak + 1.2)
    ax.grid(True, linestyle="--", alpha=0.3, color="#64748b")
    ax.set_facecolor("#0b0f19")
    fig.patch.set_facecolor("#0f172a")
    ax.tick_params(colors="#cbd5e1")
    for spine in ax.spines.values():
        spine.set_color("#334155")
    ax.legend(facecolor="#1e293b", edgecolor="#334155", labelcolor="#f8fafc")

    st.pyplot(fig)
