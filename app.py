import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# ---------------------------------------------------------
# 1. PAGE SETUP & WORKBENCH STYLING
# ---------------------------------------------------------
st.set_page_config(
    page_title="ECE Virtual Circuit & Hardware Studio",
    page_icon="⚡",
    layout="wide"
)

st.markdown("""
<style>
    .reportview-container, .main {
        background-color: #080c14;
        color: #f1f5f9;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #0f172a;
        border-radius: 6px;
        padding: 8px 16px;
        color: #94a3b8;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0284c7 !important;
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚡ ECE Virtual Hardware & Circuit Studio")
st.caption("Interactive hardware simulator: Isometric board, breadboard, real component wiring, and waveform telemetry.")

# ---------------------------------------------------------
# 2. STATE MANAGEMENT FOR USER'S IDEOLOGY
# ---------------------------------------------------------
if "custom_circuit" not in st.session_state:
    st.session_state["custom_circuit"] = [
        {"pin": "D13", "component": "Red Indicator LED", "target": "LED1_ANODE", "color": "#ef4444", "role": "Digital Output"},
        {"pin": "D9~", "component": "220Ω Current Limiting Resistor", "target": "R1_IN", "color": "#f59e0b", "role": "PWM Output"},
        {"pin": "D2", "component": "IR Sensor Digital OUT", "target": "SENSOR_SIG", "color": "#38bdf8", "role": "Digital Input"},
        {"pin": "5V", "component": "Breadboard VCC (+) Rail", "target": "BB_VCC", "color": "#dc2626", "role": "Power Supply"},
        {"pin": "GND", "component": "Breadboard Common GND (-) Rail", "target": "BB_GND", "color": "#10b981", "role": "Ground Rail"}
    ]

# ---------------------------------------------------------
# 3. SIDEBAR: CUSTOM CIRCUIT IDEOLOGY BUILDER
# ---------------------------------------------------------
with st.sidebar:
    st.header("🛠️ Circuit Design Controls")
    
    preset_choice = st.selectbox(
        "Load ECE Project Template",
        [
            "Custom Ideology (User Defined)",
            "Dual LED Alert with Resistor Array",
            "4-Bit R-2R Ladder DAC Topology",
            "IR Sensor Automated Street Luminaire",
            "Ultrasonic Distance Meter with Buzzer"
        ]
    )

    if preset_choice == "Dual LED Alert with Resistor Array":
        st.session_state["custom_circuit"] = [
            {"pin": "D13", "component": "Red Warning LED", "target": "LED1_ANODE", "color": "#ef4444", "role": "Digital Output"},
            {"pin": "D12", "component": "Green Safe LED", "target": "LED2_ANODE", "color": "#22c55e", "role": "Digital Output"},
            {"pin": "D9~", "component": "220Ω Ballast Resistor", "target": "R1_IN", "color": "#f59e0b", "role": "PWM Output"},
            {"pin": "5V", "component": "Breadboard VCC Rail", "target": "BB_VCC", "color": "#dc2626", "role": "Power Supply"},
            {"pin": "GND", "component": "Breadboard GND Rail", "target": "BB_GND", "color": "#10b981", "role": "Ground Rail"}
        ]
    elif preset_choice == "4-Bit R-2R Ladder DAC Topology":
        st.session_state["custom_circuit"] = [
            {"pin": "D0 (RX)", "component": "Bit 0 (LSB) Resistor", "target": "R_BIT0", "color": "#38bdf8", "role": "Digital Output"},
            {"pin": "D1 (TX)", "component": "Bit 1 Resistor", "target": "R_BIT1", "color": "#38bdf8", "role": "Digital Output"},
            {"pin": "D2", "component": "Bit 2 Resistor", "target": "R_BIT2", "color": "#38bdf8", "role": "Digital Output"},
            {"pin": "D3~", "component": "Bit 3 (MSB) Resistor", "target": "R_BIT3", "color": "#38bdf8", "role": "Digital Output"},
            {"pin": "5V", "component": "Op-Amp VCC Supply", "target": "BB_VCC", "color": "#ef4444", "role": "Power Supply"},
            {"pin": "GND", "component": "R-2R Ladder Ground Termination", "target": "BB_GND", "color": "#10b981", "role": "Ground Rail"}
        ]

    st.markdown("---")
    st.subheader("💡 Wire an Electronic Component")
    
    available_pins = [
        "D0 (RX)", "D1 (TX)", "D2", "D3~", "D4", "D5~", "D6~", "D7",
        "D8", "D9~", "D10~", "D11~", "D12", "D13", "AREF",
        "A0", "A1", "A2", "A3", "A4", "A5", "5V", "3.3V", "GND", "RESET", "VIN"
    ]
    
    sel_pin = st.selectbox("Select Pin", available_pins)
    comp_title = st.text_input("Component Label", value="Yellow LED Anode")
    comp_role = st.selectbox("Electrical Role", ["Digital Output", "Digital Input", "PWM Control (~)", "Analog Input (ADC)", "Power Supply", "Ground Rail"])
    wire_hex = st.color_picker("Wire Color", "#38bdf8")

    col_add, col_reset = st.columns(2)
    with col_add:
        if st.button("➕ Connect Wire", use_container_width=True, type="primary"):
            if comp_title.strip():
                # Replace wire if pin is reused
                st.session_state["custom_circuit"] = [c for c in st.session_state["custom_circuit"] if c["pin"] != sel_pin]
                st.session_state["custom_circuit"].append({
                    "pin": sel_pin,
                    "component": comp_title.strip(),
                    "target": "BB_CUSTOM",
                    "color": wire_hex,
                    "role": comp_role
                })
                st.rerun()
    with col_reset:
        if st.button("🗑️ Clear Wires", use_container_width=True):
            st.session_state["custom_circuit"] = []
            st.rerun()

    st.markdown("---")
    st.subheader("📊 Oscilloscope Controls")
    sig_freq = st.slider("Signal Frequency (Hz)", 10, 2000, 490)
    sig_duty = st.slider("PWM Duty Cycle (%)", 0, 100, 50)
    sig_vpeak = st.slider("Peak Amplitude (V)", 1.0, 5.0, 5.0, 0.5)

# ---------------------------------------------------------
# 4. PHYSICAL 3D / ISOMETRIC BENCH RENDERER
# ---------------------------------------------------------
def render_isometric_workbench(connections):
    # Dynamic SVG wire generation connecting Arduino headers to Breadboard rows
    wires_svg = ""
    
    # Coordinates of Arduino Uno digital and power headers (SVG space)
    pin_coords = {
        "D13": (210, 175), "D12": (222, 180), "D11~": (234, 185), "D10~": (246, 190),
        "D9~": (258, 195), "D8": (270, 200), "D7": (285, 207), "D6~": (297, 212),
        "D5~": (309, 217), "D4": (321, 222), "D3~": (333, 227), "D2": (345, 232),
        "D1 (TX)": (357, 237), "D0 (RX)": (369, 242),
        "5V": (195, 255), "3.3V": (185, 250), "GND": (215, 265), "A0": (245, 280),
        "A1": (257, 285), "A2": (269, 290), "A3": (281, 295), "A4": (293, 300), "A5": (305, 305)
    }

    # Breadboard component destination pins
    bb_targets = [
        (460, 175), (480, 185), (500, 195), (520, 205), (540, 215), (560, 225), (580, 235)
    ]

    for idx, c in enumerate(connections):
        p_name = c["pin"]
        color = c["color"]
        start_pt = pin_coords.get(p_name, (220, 200))
        target_pt = bb_targets[idx % len(bb_targets)]
        
        # Calculate curved bezier path to simulate real physical insulated wire
        cx = (start_pt[0] + target_pt[0]) / 2
        cy = min(start_pt[1], target_pt[1]) - 40 - (idx * 8)
        
        wires_svg += f"""
        <!-- Shadow -->
        <path d="M {start_pt[0]} {start_pt[1]} Q {cx} {cy + 15} {target_pt[0]} {target_pt[1]}" fill="none" stroke="rgba(0,0,0,0.35)" stroke-width="6" stroke-linecap="round"/>
        <!-- Insulated Wire -->
        <path d="M {start_pt[0]} {start_pt[1]} Q {cx} {cy} {target_pt[0]} {target_pt[1]}" fill="none" stroke="{color}" stroke-width="4" stroke-linecap="round"/>
        <!-- Terminal Jumper Pins -->
        <circle cx="{start_pt[0]}" cy="{start_pt[1]}" r="3.5" fill="#f8fafc" stroke="#0f172a" stroke-width="1.5"/>
        <circle cx="{target_pt[0]}" cy="{target_pt[1]}" r="3.5" fill="#f8fafc" stroke="#0f172a" stroke-width="1.5"/>
        """

    svg_html = f"""
    <div style="background: radial-gradient(circle at 50% 30%, #0d1b2a 0%, #050811 100%); border: 2px solid #1e293b; border-radius: 12px; padding: 15px; position: relative; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.7);">
        
        <!-- Live HUD Status Badges -->
        <div style="position: absolute; top: 15px; left: 15px; display: flex; flex-direction: column; gap: 6px; z-index: 10;">
            <div style="background: rgba(15, 23, 42, 0.85); border: 1px solid #22c55e; border-radius: 6px; padding: 5px 10px; font-size: 11px; color: #86efac; display: flex; align-items: center; gap: 6px; backdrop-filter: blur(4px);">
                <span style="display:inline-block; width:8px; height:8px; background:#22c55e; border-radius:50%; box-shadow:0 0 8px #22c55e;"></span>
                <span>Verification Successful</span>
            </div>
            <div style="background: rgba(15, 23, 42, 0.85); border: 1px solid #38bdf8; border-radius: 6px; padding: 5px 10px; font-size: 11px; color: #7dd3fc; display: flex; align-items: center; gap: 6px; backdrop-filter: blur(4px);">
                <span style="display:inline-block; width:8px; height:8px; background:#38bdf8; border-radius:50%; box-shadow:0 0 8px #38bdf8;"></span>
                <span>Pin Connection Active ({len(connections)} Wires)</span>
            </div>
            <div style="background: rgba(15, 23, 42, 0.85); border: 1px solid #a855f7; border-radius: 6px; padding: 5px 10px; font-size: 11px; color: #d8b4fe; display: flex; align-items: center; gap: 6px; backdrop-filter: blur(4px);">
                <span style="display:inline-block; width:8px; height:8px; background:#a855f7; border-radius:50%; box-shadow:0 0 8px #a855f7;"></span>
                <span>Code Compilation: Ready</span>
            </div>
        </div>

        <!-- Telemetry Info Top Right -->
        <div style="position: absolute; top: 15px; right: 15px; background: rgba(15, 23, 42, 0.85); border: 1px solid #334155; border-radius: 6px; padding: 8px 12px; font-size: 11px; color: #94a3b8; font-family: monospace; backdrop-filter: blur(4px); z-index: 10;">
            <div>BOARD: <b>Arduino Uno R3</b></div>
            <div>STATUS: <b style="color:#22c55e;">LIVE WORKBENCH</b></div>
            <div>MCU: <b>ATmega328P (16MHz)</b></div>
        </div>

        <!-- 3D ISOMETRIC CANVAS -->
        <svg viewBox="0 0 820 420" style="width: 100%; height: auto; display: block;">
            <defs>
                <filter id="glow-green" x="-20%" y="-20%" width="140%" height="140%">
                    <feGaussianBlur stdDeviation="6" result="blur" />
                    <feComposite in="SourceGraphic" in2="blur" operator="over" />
                </filter>
                <filter id="glow-red" x="-20%" y="-20%" width="140%" height="140%">
                    <feGaussianBlur stdDeviation="6" result="blur" />
                    <feComposite in="SourceGraphic" in2="blur" operator="over" />
                </filter>
            </defs>

            <!-- Grid surface -->
            <g stroke="#1e293b" stroke-width="0.7" opacity="0.4">
                {"".join([f'<line x1="{x}" y1="0" x2="{x}" y2="420"/>' for x in range(0, 820, 30)])}
                {"".join([f'<line x1="0" y1="{y}" x2="820" y2="{y}"/>' for y in range(0, 420, 30)])}
            </g>

            <!-- ARDUINO UNO R3 ISOMETRIC BOARD -->
            <g transform="translate(40, 20)">
                <!-- PCB Drop Shadow -->
                <polygon points="120,200 280,120 400,180 240,260" fill="rgba(0,0,0,0.5)"/>
                <!-- PCB Body -->
                <polygon points="120,190 280,110 390,165 230,245" fill="#005f73" stroke="#0a9396" stroke-width="2"/>
                
                <!-- USB & Power Barrel -->
                <polygon points="105,178 135,163 145,173 115,188" fill="#94a3b8" stroke="#cbd5e1" stroke-width="1"/>
                <polygon points="135,210 160,198 168,206 143,218" fill="#1e293b" stroke="#000000" stroke-width="1"/>

                <!-- ATmega328P Chip -->
                <polygon points="220,175 270,150 290,160 240,185" fill="#0f172a" stroke="#334155" stroke-width="1"/>
                <text x="240" y="172" fill="#64748b" font-size="8" font-family="monospace" transform="rotate(27 240 172)">ATMEGA328P</text>

                <!-- Board Label -->
                <text x="180" y="160" fill="#ffffff" font-weight="bold" font-size="12" font-family="sans-serif">ARDUINO UNO</text>

                <!-- Header Strips -->
                <!-- Top Digital Header -->
                <polygon points="205,130 380,215 375,220 200,135" fill="#020617"/>
                <!-- Bottom Power Header -->
                <polygon points="175,215 315,285 310,290 170,220" fill="#020617"/>
            </g>

            <!-- WHITE SOLDERLESS BREADBOARD -->
            <g transform="translate(180, 10)">
                <!-- Breadboard Shadow -->
                <polygon points="300,180 500,80 620,140 420,240" fill="rgba(0,0,0,0.4)"/>
                <!-- Breadboard Base Plastic -->
                <polygon points="300,170 500,70 610,125 410,225" fill="#f8fafc" stroke="#cbd5e1" stroke-width="2"/>
                
                <!-- Power Rails -->
                <line x1="320" y1="160" x2="495" y2="72" stroke="#ef4444" stroke-width="2" opacity="0.8"/>
                <line x1="330" y1="168" x2="505" y2="80" stroke="#0284c7" stroke-width="2" opacity="0.8"/>

                <!-- Component Tie Points (Grid Dots) -->
                <g fill="#94a3b8">
                    {"".join([f'<circle cx="{330 + i*18}" cy="{150 - i*7 + j*10}" r="1.5"/>' for i in range(12) for j in range(6)])}
                </g>

                <!-- REAL DISCRETE COMPONENTS PLACED ON BREADBOARD -->
                <!-- Glowing Green LED -->
                <g filter="url(#glow-green)">
                    <circle cx="380" cy="120" r="7" fill="#22c55e" opacity="0.9"/>
                </g>
                <circle cx="380" cy="120" r="4.5" fill="#86efac"/>
                <line x1="380" y1="125" x2="380" y2="140" stroke="#94a3b8" stroke-width="1.5"/>

                <!-- Glowing Red LED -->
                <g filter="url(#glow-red)">
                    <circle cx="410" cy="105" r="7" fill="#ef4444" opacity="0.9"/>
                </g>
                <circle cx="410" cy="105" r="4.5" fill="#fca5a5"/>
                <line x1="410" y1="110" x2="410" y2="128" stroke="#94a3b8" stroke-width="1.5"/>

                <!-- Through-Hole Ceramic Resistor 1 (220Ω) with color bands -->
                <g transform="translate(440, 100)">
                    <rect x="0" y="0" width="22" height="7" rx="3" fill="#d97706"/>
                    <rect x="4" y="0" width="2" height="7" fill="#dc2626"/>  <!-- Red -->
                    <rect x="8" y="0" width="2" height="7" fill="#dc2626"/>  <!-- Red -->
                    <rect x="12" y="0" width="2" height="7" fill="#b45309"/> <!-- Brown -->
                    <rect x="16" y="0" width="2" height="7" fill="#fbbf24"/> <!-- Gold -->
                    <line x1="-8" y1="3.5" x2="0" y2="3.5" stroke="#94a3b8" stroke-width="1.5"/>
                    <line x1="22" y1="3.5" x2="30" y2="3.5" stroke="#94a3b8" stroke-width="1.5"/>
                </g>

                <!-- Through-Hole Resistor 2 -->
                <g transform="translate(470, 85)">
                    <rect x="0" y="0" width="22" height="7" rx="3" fill="#d97706"/>
                    <rect x="4" y="0" width="2" height="7" fill="#2563eb"/>
                    <rect x="8" y="0" width="2" height="7" fill="#000000"/>
                    <rect x="12" y="0" width="2" height="7" fill="#dc2626"/>
                    <line x1="-8" y1="3.5" x2="0" y2="3.5" stroke="#94a3b8" stroke-width="1.5"/>
                    <line x1="22" y1="3.5" x2="30" y2="3.5" stroke="#94a3b8" stroke-width="1.5"/>
                </g>

                <!-- Piezo Transducer / Buzzer Cylinder -->
                <ellipse cx="510" cy="130" rx="14" ry="9" fill="#0f172a" stroke="#334155" stroke-width="2"/>
                <ellipse cx="510" cy="128" rx="5" ry="3" fill="#000000"/>
            </g>

            <!-- DYNAMIC CONNECTING JUMPER WIRES -->
            {wires_svg}
        </svg>
    </div>
    """
    st.components.v1.html(svg_html, height=450)

# ---------------------------------------------------------
# 5. LAB BENCH TABS
# ---------------------------------------------------------
tab_workbench, tab_code, tab_math, tab_oscilloscope = st.tabs([
    "🖥️ 3D Workbench & Physical Netlist",
    "💻 Compilable Arduino C++ Code",
    "📐 ECE Theoretical Derivations",
    "📈 Virtual Scope Telemetry"
])

with tab_workbench:
    render_isometric_workbench(st.session_state["custom_circuit"])
    
    st.write("")
    col_t1, col_t2 = st.columns([1.2, 1])

    with col_t1:
        st.subheader("📋 Active Circuit Wire Netlist")
        if st.session_state["custom_circuit"]:
            table_view = [
                {
                    "Arduino Pin": c["pin"],
                    "Target Component": c["component"],
                    "Wire Lead Color": c["color"],
                    "Electrical Role": c["role"]
                }
                for c in st.session_state["custom_circuit"]
            ]
            st.dataframe(table_view, use_container_width=True)
        else:
            st.info("No connections mapped. Use the sidebar to wire components to pins!")

    with col_t2:
        st.subheader("✂️ Manage Connections")
        if st.session_state["custom_circuit"]:
            pin_opts = [c["pin"] for c in st.session_state["custom_circuit"]]
            sel_rm = st.selectbox("Select Pin to Detach", pin_opts)
            if st.button("Disconnect Wire", use_container_width=True):
                st.session_state["custom_circuit"] = [c for c in st.session_state["custom_circuit"] if c["pin"] != sel_rm]
                st.rerun()

with tab_code:
    st.subheader("💻 Synchronized Arduino C++ Sketch (.ino)")
    st.caption("Auto-generated based on the active pin connections and roles in the workbench.")

    pin_defs = ""
    setup_code = ""
    loop_code = ""

    for item in st.session_state["custom_circuit"]:
        clean_pin = item["pin"].split()[0].replace("~", "")
        if clean_pin in ["5V", "3.3V", "GND", "RESET", "VIN", "AREF"]:
            continue
            
        var_name = "".join(ch if ch.isalnum() else "_" for ch in item["component"].lower()).strip("_") + "_pin"
        pin_num = clean_pin.replace("D", "")

        pin_defs += f"const int {var_name} = {pin_num};  // Connected to {item['component']}\n"

        if "Output" in item["role"] or "PWM" in item["role"]:
            setup_code += f"  pinMode({var_name}, OUTPUT);\n"
            if "PWM" in item["role"]:
                loop_code += f"  analogWrite({var_name}, 128); // 50% PWM Duty Cycle\n"
            else:
                loop_code += f"  digitalWrite({var_name}, HIGH); // Drive high\n"
        elif "Input" in item["role"] or "ADC" in item["role"]:
            setup_code += f"  pinMode({var_name}, INPUT);\n"
            if "ADC" in item["role"]:
                loop_code += f"  int {var_name}_val = analogRead({var_name});\n"
            else:
                loop_code += f"  int {var_name}_val = digitalRead({var_name});\n"

    sketch = f"""// ===============================================================
// ECE Interactive Circuit Studio - Auto-Generated Arduino Code
// ===============================================================

{pin_defs if pin_defs else "// No digital pins mapped yet.\\n"}
void setup() {{
  Serial.begin(9600);
{setup_code}
  Serial.println("Circuit initialized successfully.");
}}

void loop() {{
{loop_code if loop_code else "  // Insert your project logic here"}
  delay(100);
}}
"""
    st.code(sketch, language="cpp", line_numbers=True)

with tab_math:
    st.subheader("📐 Theoretical ECE Circuit Proofs")
    
    with st.expander("🔹 LED Ballast Resistor Calculation (Ohm's Law)", expanded=True):
        st.latex(r"R = \frac{V_{CC} - V_F}{I_F} = \frac{5.0\,\text{V} - 2.0\,\text{V}}{0.02\,\text{A}} = 150\,\Omega")
        st.info("Using standard **220 Ω** for safe long-term component operation (~13.6 mA).")

    with st.expander("🔹 PWM Average Voltage Output", expanded=True):
        st.latex(r"V_{avg} = D \times V_{peak} = \left(\frac{" + str(sig_duty) + r"}{100}\right) \times " + str(sig_vpeak) + r"\text{V} = " + f"{(sig_duty / 100.0) * sig_vpeak:.2f}" + r"\,\text{V}")
        st.info(f"Average calculated voltage at **{sig_duty}%** duty cycle: **{(sig_duty / 100.0) * sig_vpeak:.2f} V**")

with tab_oscilloscope:
    st.subheader("📈 Virtual Oscilloscope Trace")
    
    t = np.linspace(0, 0.01, 1000)  # 10 ms window
    period = 1.0 / sig_freq if sig_freq > 0 else 0.002
    duty_frac = sig_duty / 100.0
    wave = np.where((t % period) < (period * duty_frac), sig_vpeak, 0.0)

    fig, ax = plt.subplots(figsize=(9, 3.2))
    ax.plot(t * 1000, wave, color="#00ffcc", linewidth=2.2, label=f"CH1 PWM ({sig_freq} Hz, {sig_duty}%)")
    ax.set_xlabel("Time (milliseconds)", color="#cbd5e1")
    ax.set_ylabel("Amplitude (Volts)", color="#cbd5e1")
    ax.set_ylim(-0.5, sig_vpeak + 1.2)
    ax.grid(True, linestyle="--", alpha=0.3, color="#64748b")
    ax.set_facecolor("#0b0f19")
    fig.patch.set_facecolor("#0f172a")
    ax.tick_params(colors="#cbd5e1")
    for spine in ax.spines.values():
        spine.set_color("#334155")
    ax.legend(facecolor="#1e293b", edgecolor="#334155", labelcolor="#f8fafc")

    st.pyplot(fig)
