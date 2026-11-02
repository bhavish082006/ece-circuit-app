import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import json

# 1. Page Configuration
st.set_page_config(
    page_title="ECE Virtual Circuit & Hardware Studio",
    page_icon="⚡",
    layout="wide"
)

st.markdown("""
<style>
    .reportview-container, .main {
        background-color: #0b0f19;
        color: #f1f5f9;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1e293b;
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

st.title("⚡ ECE Interactive Virtual Circuit Workbench")
st.caption("Live physical circuit lab: Dynamic hardware layout, real component placement, jumper routing, and C++ code generator.")

# 2. Complete Project Blueprints Database
TEMPLATES = {
    "Dual LED Alert with Current Limiting Resistors": {
        "wires": [
            {"pin": "D13", "component": "Red Indicator LED", "type": "led_red", "color": "#ef4444", "role": "Digital Output"},
            {"pin": "D12", "component": "Green Safe LED", "type": "led_green", "color": "#22c55e", "role": "Digital Output"},
            {"pin": "D9", "component": "220Ω Ceramic Resistor", "type": "resistor", "color": "#eab308", "role": "PWM Control (~)"},
            {"pin": "5V", "component": "Breadboard VCC Rail", "type": "power", "color": "#dc2626", "role": "Power Supply (5V)"},
            {"pin": "GND", "component": "Breadboard Common GND", "type": "gnd", "color": "#1e293b", "role": "Ground Rail (0V)"}
        ],
        "calcs": [
            {"title": "Ohm's Law LED Ballast Resistor", "formula": r"R = \frac{V_{CC} - V_F}{I_F} = \frac{5.0\,\text{V} - 2.0\,\text{V}}{0.02\,\text{A}} = 150\,\Omega", "note": "Standard 220 Ω selected to protect diode junction (~13.6 mA continuous)."}
        ]
    },
    "Ultrasonic Distance Meter with Buzzer Alert": {
        "wires": [
            {"pin": "D9", "component": "HC-SR04 Ultrasonic Sensor", "type": "ultrasonic", "color": "#38bdf8", "role": "Digital Output (Trig)"},
            {"pin": "D10", "component": "HC-SR04 Echo Return", "type": "sensor_pin", "color": "#0ea5e9", "role": "Digital Input (Echo)"},
            {"pin": "D8", "component": "Active Piezo Buzzer", "type": "buzzer", "color": "#f59e0b", "role": "PWM Tone Output"},
            {"pin": "D13", "component": "Red Warning LED", "type": "led_red", "color": "#ef4444", "role": "Digital Output"},
            {"pin": "5V", "component": "HC-SR04 5V VCC", "type": "power", "color": "#dc2626", "role": "Power Supply (5V)"},
            {"pin": "GND", "component": "Sensor Common GND", "type": "gnd", "color": "#1e293b", "role": "Ground Rail (0V)"}
        ],
        "calcs": [
            {"title": "Time-of-Flight Ranging Equation", "formula": r"\text{Distance (cm)} = \frac{\Delta t \times 0.0343\,\text{cm/\mu s}}{2}", "note": "Calculates object distance from pulse round-trip travel time."}
        ]
    },
    "4-Bit R-2R Ladder Digital-to-Analog Converter (DAC)": {
        "wires": [
            {"pin": "D0", "component": "2R Branch Resistor (Bit 0 LSB)", "type": "resistor", "color": "#38bdf8", "role": "Digital Output"},
            {"pin": "D1", "component": "2R Branch Resistor (Bit 1)", "type": "resistor", "color": "#38bdf8", "role": "Digital Output"},
            {"pin": "D2", "component": "2R Branch Resistor (Bit 2)", "type": "resistor", "color": "#38bdf8", "role": "Digital Output"},
            {"pin": "D3", "component": "2R Branch Resistor (Bit 3 MSB)", "type": "resistor", "color": "#38bdf8", "role": "Digital Output"},
            {"pin": "5V", "component": "Op-Amp VCC Positive Rail", "type": "power", "color": "#dc2626", "role": "Power Supply (5V)"},
            {"pin": "GND", "component": "R-2R Termination Ground", "type": "gnd", "color": "#1e293b", "role": "Ground Rail (0V)"}
        ],
        "calcs": [
            {"title": "DAC Discrete Output Resolution", "formula": r"V_{step} = \frac{V_{ref}}{2^N} = \frac{5.0\,\text{V}}{2^4} = 0.3125\,\text{V}", "note": "Each binary count step produces a 312.5 mV incremental voltage jump."}
        ]
    },
    "LDR Twilight Automatic Street Light with Dimming": {
        "wires": [
            {"pin": "A0", "component": "LDR Photoresistor Divider", "type": "ldr", "color": "#eab308", "role": "Analog Input (ADC)"},
            {"pin": "D6", "component": "High-Power White LED", "type": "led_green", "color": "#38bdf8", "role": "PWM Output (~)"},
            {"pin": "5V", "component": "Photoresistor VCC Rail", "type": "power", "color": "#dc2626", "role": "Power Supply (5V)"},
            {"pin": "GND", "component": "10kΩ Pull-down Resistor GND", "type": "gnd", "color": "#1e293b", "role": "Ground Rail (0V)"}
        ],
        "calcs": [
            {"title": "Voltage Divider Transfer Function", "formula": r"V_{out} = V_{CC} \times \frac{R_{fixed}}{R_{LDR} + R_{fixed}} = 5.0\,\text{V} \times \frac{10\,\text{k}\Omega}{R_{LDR} + 10\,\text{k}\Omega}", "note": "Node voltage drops into low-lux twilight thresholds."}
        ]
    }
}

# 3. State Setup
if "active_wires" not in st.session_state:
    st.session_state["active_wires"] = TEMPLATES["Dual LED Alert with Current Limiting Resistors"]["wires"].copy()
    st.session_state["active_calcs"] = TEMPLATES["Dual LED Alert with Current Limiting Resistors"]["calcs"].copy()

# 4. Sidebar Controls
with st.sidebar:
    st.header("🎛️ ECE Project Switcher")
    
    selected_template = st.selectbox("Select Project Blueprint", list(TEMPLATES.keys()))
    if st.button("⚡ Load Project Blueprint", type="primary", use_container_width=True):
        st.session_state["active_wires"] = TEMPLATES[selected_template]["wires"].copy()
        st.session_state["active_calcs"] = TEMPLATES[selected_template]["calcs"].copy()
        st.rerun()

    st.markdown("---")
    st.subheader("🛠️ Custom Ideology Builder")
    st.caption("Wire any component to your Arduino board:")

    all_pins = [
        "D13", "D12", "D11", "D10", "D9", "D8", "D7", "D6", "D5", "D4", "D3", "D2", "D1", "D0",
        "A0", "A1", "A2", "A3", "A4", "A5", "5V", "3.3V", "GND"
    ]
    
    sel_pin = st.selectbox("Arduino Header Pin", all_pins)
    comp_name = st.text_input("Component Label", value="Piezo Buzzer Alarm")
    comp_kind = st.selectbox("Component Type", ["buzzer", "led_red", "led_green", "resistor", "ultrasonic", "ldr"])
    comp_role = st.selectbox("Signal / Function Role", ["Digital Output", "PWM Control (~)", "Digital Input", "Analog Input (ADC)", "Power (5V)", "Ground (0V)"])
    wire_color_choice = st.selectbox("Wire Lead Color", ["🔴 Red", "🔵 Blue", "🟡 Yellow", "🟢 Green", "⚪ White", "⚫ Black"])
    
    hex_colors = {
        "🔴 Red": "#ef4444", "🔵 Blue": "#38bdf8", "🟡 Yellow": "#eab308",
        "🟢 Green": "#22c55e", "⚪ White": "#f8fafc", "⚫ Black": "#1e293b"
    }

    c_add, c_clear = st.columns(2)
    with c_add:
        if st.button("➕ Route Wire", use_container_width=True):
            if comp_name.strip():
                st.session_state["active_wires"] = [w for w in st.session_state["active_wires"] if w["pin"] != sel_pin]
                st.session_state["active_wires"].append({
                    "pin": sel_pin,
                    "component": comp_name.strip(),
                    "type": comp_kind,
                    "color": hex_colors[wire_color_choice],
                    "role": comp_role
                })
                st.rerun()
    with c_clear:
        if st.button("🗑️ Clear All", use_container_width=True):
            st.session_state["active_wires"] = []
            st.rerun()

    st.markdown("---")
    st.subheader("📊 Oscilloscope Controls")
    sig_f = st.slider("Frequency (Hz)", 10, 2000, 490)
    sig_d = st.slider("PWM Duty Cycle (%)", 0, 100, 50)
    sig_v = st.slider("Peak Amplitude (V)", 1.0, 5.0, 5.0, 0.5)

# 5. Interactive Physical Workbench
tab_bench, tab_code, tab_theory, tab_scope = st.tabs([
    "🖥️ Live Physical Circuit Canvas",
    "💻 Compilable Arduino C++ Sketch",
    "📐 Theoretical ECE Proofs",
    "📈 Virtual Oscilloscope Trace"
])

with tab_bench:
    st.subheader("🎛️ Real-Time Arduino & Breadboard Hardware Rig")
    
    wires_json = json.dumps(st.session_state["active_wires"])

    canvas_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {{
            margin: 0;
            padding: 0;
            background: #060913;
            font-family: monospace;
            overflow: hidden;
            user-select: none;
        }}
        #container {{
            position: relative;
            width: 100%;
            height: 480px;
            background: radial-gradient(circle at 50% 30%, #0d1b2a 0%, #050811 100%);
            border: 2px solid #1e293b;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.8);
        }}
        .hud-badge {{
            position: absolute;
            top: 15px;
            left: 15px;
            background: rgba(15, 23, 42, 0.85);
            border: 1px solid #22c55e;
            border-radius: 6px;
            padding: 6px 12px;
            font-size: 11px;
            color: #86efac;
            display: flex;
            align-items: center;
            gap: 8px;
            z-index: 10;
        }}
    </style>
    </head>
    <body>
        <div id="container">
            <div class="hud-badge">
                <span style="width:8px; height:8px; background:#22c55e; border-radius:50%; box-shadow:0 0 8px #22c55e;"></span>
                <span>Active Wires Connected: {len(st.session_state['active_wires'])}</span>
            </div>
            <canvas id="cv" width="920" height="480"></canvas>
        </div>

        <script>
            const cv = document.getElementById('cv');
            const ctx = cv.getContext('2d');
            const wires = {wires_json};

            const pinLocations = {{
                "D13": {{x: 210, y: 145}}, "D12": {{x: 222, y: 150}}, "D11": {{x: 234, y: 155}},
                "D10": {{x: 246, y: 160}}, "D9":  {{x: 258, y: 165}}, "D8":  {{x: 270, y: 170}},
                "D7":  {{x: 285, y: 177}}, "D6":  {{x: 297, y: 182}}, "D5":  {{x: 309, y: 187}},
                "D4":  {{x: 321, y: 192}}, "D3":  {{x: 333, y: 197}}, "D2":  {{x: 345, y: 202}},
                "D1":  {{x: 357, y: 207}}, "D0":  {{x: 369, y: 212}},
                "5V":  {{x: 195, y: 280}}, "3.3V":{{x: 185, y: 275}}, "GND": {{x: 215, y: 290}},
                "A0":  {{x: 245, y: 305}}, "A1":  {{x: 257, y: 310}}, "A2":  {{x: 269, y: 315}},
                "A3":  {{x: 281, y: 320}}, "A4":  {{x: 293, y: 325}}, "A5":  {{x: 305, y: 330}}
            }};

            let tick = 0;

            function draw() {{
                ctx.clearRect(0, 0, cv.width, cv.height);

                // 1. Grid
                ctx.strokeStyle = "rgba(30, 41, 59, 0.4)";
                ctx.lineWidth = 1;
                for (let x = 0; x < cv.width; x += 30) {{
                    ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, cv.height); ctx.stroke();
                }}
                for (let y = 0; y < cv.height; y += 30) {{
                    ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(cv.width, y); ctx.stroke();
                }}

                // 2. Arduino Uno PCB
                ctx.save();
                ctx.fillStyle = "rgba(0,0,0,0.5)";
                ctx.beginPath();
                ctx.moveTo(120, 220); ctx.lineTo(280, 140); ctx.lineTo(410, 205); ctx.lineTo(250, 285);
                ctx.fill();

                ctx.fillStyle = "#005f73";
                ctx.strokeStyle = "#0a9396";
                ctx.lineWidth = 3;
                ctx.beginPath();
                ctx.moveTo(120, 210); ctx.lineTo(280, 130); ctx.lineTo(400, 190); ctx.lineTo(240, 270);
                ctx.closePath();
                ctx.fill();
                ctx.stroke();

                // Chip
                ctx.fillStyle = "#0f172a";
                ctx.fillRect(230, 180, 70, 25);
                ctx.fillStyle = "#94a3b8";
                ctx.font = "9px monospace";
                ctx.fillText("ATMEGA328P", 235, 196);

                ctx.fillStyle = "#ffffff";
                ctx.font = "bold 13px sans-serif";
                ctx.fillText("ARDUINO UNO", 175, 180);

                // Pin Headers
                ctx.fillStyle = "#020617";
                ctx.fillRect(190, 135, 185, 10);
                ctx.fillRect(165, 270, 150, 10);
                ctx.restore();

                // 3. Solderless Breadboard
                ctx.save();
                ctx.fillStyle = "#f8fafc";
                ctx.strokeStyle = "#cbd5e1";
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.moveTo(460, 190); ctx.lineTo(670, 85); ctx.lineTo(780, 140); ctx.lineTo(570, 245);
                ctx.closePath();
                ctx.fill();
                ctx.stroke();

                // Tie Points
                ctx.fillStyle = "#94a3b8";
                for (let i = 0; i < 11; i++) {{
                    for (let j = 0; j < 5; j++) {{
                        ctx.beginPath();
                        ctx.arc(495 + i * 18, 170 - i * 7 + j * 9, 1.5, 0, Math.PI * 2);
                        ctx.fill();
                    }}
                }}
                ctx.restore();

                // 4. Render Physical Components on Breadboard based on active types
                wires.forEach((w, i) => {{
                    const cx = 520 + (i * 35);
                    const cy = 160 - (i * 8);

                    if (w.type === "led_red" || w.type === "led_green") {{
                        const ledCol = w.type === "led_red" ? "#ef4444" : "#22c55e";
                        ctx.save();
                        ctx.shadowColor = ledCol;
                        ctx.shadowBlur = 15;
                        ctx.fillStyle = ledCol;
                        ctx.beginPath();
                        ctx.arc(cx, cy, 9, 0, Math.PI * 2);
                        ctx.fill();
                        ctx.restore();
                        ctx.fillStyle = "#cbd5e1";
                        ctx.font = "8px monospace";
                        ctx.fillText("LED", cx - 7, cy + 18);
                    }} 
                    else if (w.type === "resistor") {{
                        ctx.fillStyle = "#d97706";
                        ctx.fillRect(cx - 10, cy - 4, 20, 8);
                        ctx.fillStyle = "#dc2626"; ctx.fillRect(cx - 6, cy - 4, 2, 8);
                        ctx.fillStyle = "#dc2626"; ctx.fillRect(cx - 2, cy - 4, 2, 8);
                        ctx.fillStyle = "#b45309"; ctx.fillRect(cx + 2, cy - 4, 2, 8);
                        ctx.fillStyle = "#cbd5e1";
                        ctx.font = "8px monospace";
                        ctx.fillText("220Ω", cx - 10, cy + 18);
                    }}
                    else if (w.type === "buzzer") {{
                        ctx.fillStyle = "#0f172a";
                        ctx.beginPath();
                        ctx.arc(cx, cy, 14, 0, Math.PI * 2);
                        ctx.fill();
                        ctx.fillStyle = "#000000";
                        ctx.beginPath();
                        ctx.arc(cx, cy, 5, 0, Math.PI * 2);
                        ctx.fill();
                        ctx.fillStyle = "#f59e0b";
                        ctx.font = "8px monospace";
                        ctx.fillText("BUZZER", cx - 14, cy + 24);
                    }}
                    else if (w.type === "ultrasonic") {{
                        ctx.fillStyle = "#0284c7";
                        ctx.fillRect(cx - 16, cy - 8, 32, 16);
                        ctx.fillStyle = "#cbd5e1";
                        ctx.beginPath(); ctx.arc(cx - 8, cy, 5, 0, Math.PI * 2); ctx.fill();
                        ctx.beginPath(); ctx.arc(cx + 8, cy, 5, 0, Math.PI * 2); ctx.fill();
                        ctx.fillStyle = "#38bdf8";
                        ctx.font = "7px monospace";
                        ctx.fillText("HC-SR04", cx - 14, cy + 22);
                    }}
                }});

                // 5. Dynamic Flexible Connecting Jumper Wires
                wires.forEach((w, idx) => {{
                    const start = pinLocations[w.pin] || {{x: 230, y: 200}};
                    const target = {{x: 520 + (idx * 35), y: 160 - (idx * 8)}};

                    const midX = (start.x + target.x) / 2;
                    const midY = Math.min(start.y, target.y) - 40 - (idx * 12) + Math.sin(tick + idx) * 3;

                    // Wire shadow
                    ctx.save();
                    ctx.beginPath();
                    ctx.moveTo(start.x, start.y);
                    ctx.quadraticCurveTo(midX, midY + 18, target.x, target.y);
                    ctx.strokeStyle = "rgba(0,0,0,0.4)";
                    ctx.lineWidth = 6;
                    ctx.lineCap = "round";
                    ctx.stroke();
                    ctx.restore();

                    // Wire Insulated Body
                    ctx.save();
                    ctx.beginPath();
                    ctx.moveTo(start.x, start.y);
                    ctx.quadraticCurveTo(midX, midY, target.x, target.y);
                    ctx.strokeStyle = w.color;
                    ctx.lineWidth = 4;
                    ctx.lineCap = "round";
                    ctx.shadowColor = w.color;
                    ctx.shadowBlur = 8;
                    ctx.stroke();

                    // Header pins
                    ctx.fillStyle = "#ffffff";
                    ctx.beginPath(); ctx.arc(start.x, start.y, 3.5, 0, Math.PI * 2); ctx.fill();
                    ctx.beginPath(); ctx.arc(target.x, target.y, 3.5, 0, Math.PI * 2); ctx.fill();
                    ctx.restore();
                }});

                tick += 0.04;
                requestAnimationFrame(draw);
            }}

            draw();
        </script>
    </body>
    </html>
    """
    st.components.v1.html(canvas_code, height=500)

    # Netlist table
    col_t1, col_t2 = st.columns([1.3, 1])
    with col_t1:
        st.write("#### 📋 Active Netlist & Connections")
        if st.session_state["active_wires"]:
            st.dataframe(st.session_state["active_wires"], use_container_width=True)
        else:
            st.warning("No wires connected. Add connections using the left sidebar!")
            
    with col_t2:
        st.write("#### ✂️ Detach Node")
        if st.session_state["active_wires"]:
            pins_now = [w["pin"] for w in st.session_state["active_wires"]]
            p_del = st.selectbox("Select Pin to Detach", pins_now)
            if st.button("Disconnect Wire", use_container_width=True):
                st.session_state["active_wires"] = [w for w in st.session_state["active_wires"] if w["pin"] != p_del]
                st.rerun()

with tab_code:
    st.subheader("💻 Auto-Generated Arduino C++ Sketch (.ino)")
    st.caption("Synchronized directly with the active circuit netlist above.")

    pin_defs = ""
    setup_code = ""
    loop_code = ""

    for w in st.session_state["active_wires"]:
        pin_name = w["pin"]
        if pin_name in ["5V", "3.3V", "GND"]:
            continue
        var_name = "".join(c if c.isalnum() else "_" for c in w["component"].lower()).strip("_") + "_pin"
        pin_num = pin_name.replace("D", "")
        
        pin_defs += f"const int {var_name} = {pin_num};  // Assigned to {w['component']}\n"
        
        if "Output" in w["role"] or "PWM" in w["role"]:
            setup_code += f"  pinMode({var_name}, OUTPUT);\n"
            if "PWM" in w["role"]:
                loop_code += f"  analogWrite({var_name}, 128); // 50% PWM Duty Cycle\n"
            else:
                loop_code += f"  digitalWrite({var_name}, HIGH); // Drive active HIGH\n"
        elif "Input" in w["role"] or "ADC" in w["role"]:
            setup_code += f"  pinMode({var_name}, INPUT);\n"
            if "ADC" in w["role"]:
                loop_code += f"  int {var_name}_val = analogRead({var_name});\n"
            else:
                loop_code += f"  int {var_name}_val = digitalRead({var_name});\n"

    sketch = f"""// ===============================================================
// ECE Interactive Circuit Studio - Auto-Generated Arduino Code
// ===============================================================

{pin_defs if pin_defs else "// No digital pins wired.\\n"}
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

with tab_theory:
    st.subheader("📐 Theoretical ECE Circuit Proofs")
    for item in st.session_state["active_calcs"]:
        with st.expander(f"🔹 {item['title']}", expanded=True):
            st.latex(item["formula"])
            st.info(item["note"])

with tab_scope:
    st.subheader("📈 Virtual Oscilloscope Trace")
    
    t = np.linspace(0, 0.01, 1000)
    period = 1.0 / sig_f if sig_f > 0 else 0.002
    duty_frac = sig_d / 100.0
    wave = np.where((t % period) < (period * duty_frac), sig_v, 0.0)

    fig, ax = plt.subplots(figsize=(9, 3.2))
    ax.plot(t * 1000, wave, color="#00ffcc", linewidth=2.2, label=f"CH1 PWM ({sig_f} Hz, {sig_d}%)")
    ax.set_xlabel("Time (milliseconds)", color="#cbd5e1")
    ax.set_ylabel("Amplitude (Volts)", color="#cbd5e1")
    ax.set_ylim(-0.5, sig_v + 1.2)
    ax.grid(True, linestyle="--", alpha=0.3, color="#64748b")
    ax.set_facecolor("#0b0f19")
    fig.patch.set_facecolor("#0f172a")
    ax.tick_params(colors="#cbd5e1")
    for spine in ax.spines.values():
        spine.set_color("#334155")
    ax.legend(facecolor="#1e293b", edgecolor="#334155", labelcolor="#f8fafc")

    st.pyplot(fig)
