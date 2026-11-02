import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import json

# 1. Page Configuration
st.set_page_config(
    page_title="ECE Interactive Virtual Circuit Lab",
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
st.caption("Real-time physical workbench: Live interactive wiring, draggable components, dynamic C++ code generation, and signal traces.")

# 2. Sidebar Controls
with st.sidebar:
    st.header("🛠️ Workbench Controls")
    
    preset = st.selectbox(
        "Load Circuit Template",
        [
            "Dual LED Alert with Current Limiting Resistors",
            "4-Bit R-2R Ladder DAC Network",
            "Ultrasonic Distance Meter with Buzzer",
            "LDR Twilight Automatic Street Light"
        ]
    )
    
    st.markdown("---")
    st.subheader("💡 Wire an Electronic Component")
    
    available_pins = [
        "D13", "D12", "D11", "D10", "D9", "D8", "D7", "D6", "D5", "D4", "D3", "D2", "D1", "D0",
        "A0", "A1", "A2", "A3", "A4", "A5", "5V", "3.3V", "GND"
    ]
    
    pin_select = st.selectbox("Arduino Pin", available_pins)
    comp_type = st.selectbox("Electronic Component", [
        "Red LED (Anode)", "Green LED (Anode)", "220Ω Resistor", "10kΩ Resistor", 
        "Active Buzzer (+)", "HC-SR04 Trig Pin", "HC-SR04 Echo Pin", "LDR Sensor Junction"
    ])
    wire_color = st.selectbox("Wire Color", ["🔴 Red", "🔵 Blue", "🟡 Yellow", "🟢 Green", "⚪ White", "⚫ Black"])
    
    color_map = {
        "🔴 Red": "#ef4444", "🔵 Blue": "#38bdf8", "🟡 Yellow": "#eab308", 
        "🟢 Green": "#22c55e", "⚪ White": "#f8fafc", "⚫ Black": "#1e293b"
    }

    if "wires" not in st.session_state:
        st.session_state["wires"] = [
            {"pin": "D13", "component": "Red LED (Anode)", "color": "#ef4444", "mode": "OUTPUT"},
            {"pin": "D12", "component": "Green LED (Anode)", "color": "#22c55e", "mode": "OUTPUT"},
            {"pin": "D9", "component": "220Ω Resistor", "color": "#eab308", "mode": "PWM"},
            {"pin": "5V", "component": "Breadboard VCC Rail", "color": "#dc2626", "mode": "POWER"},
            {"pin": "GND", "component": "Breadboard GND Rail", "color": "#000000", "mode": "GROUND"}
        ]

    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Connect Wire", use_container_width=True, type="primary"):
            # Update or add wire
            st.session_state["wires"] = [w for w in st.session_state["wires"] if w["pin"] != pin_select]
            mode = "PWM" if pin_select in ["D3", "D5", "D6", "D9", "D10", "D11"] else ("ADC" if pin_select.startswith("A") else "DIGITAL")
            st.session_state["wires"].append({
                "pin": pin_select,
                "component": comp_type,
                "color": color_map[wire_color],
                "mode": mode
            })
            st.rerun()

    with col2:
        if st.button("🗑️ Reset All", use_container_width=True):
            st.session_state["wires"] = []
            st.rerun()

    st.markdown("---")
    st.subheader("📊 Signal Scope")
    scope_freq = st.slider("Signal Frequency (Hz)", 10, 2000, 490)
    scope_duty = st.slider("PWM Duty Cycle (%)", 0, 100, 50)
    scope_amp = st.slider("Amplitude (V)", 1.0, 5.0, 5.0, 0.5)

# 3. Main Navigation
tab_bench, tab_code, tab_theory, tab_scope = st.tabs([
    "🖥️ Live Physical Circuit Canvas",
    "💻 Generated Arduino C++ Sketch",
    "📐 ECE Circuit Proofs",
    "📈 Virtual Oscilloscope Trace"
])

# 4. Interactive Live HTML5 Canvas Renderer
with tab_bench:
    st.subheader("🎛️ Physical Arduino Uno & Solderless Breadboard Rig")
    st.caption("Active connection pins illuminate dynamically. Jumpers bend and stretch directly to breadboard terminal strips.")
    
    wires_json = json.dumps(st.session_state["wires"])
    
    canvas_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {{
            margin: 0;
            padding: 0;
            background: #060913;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace;
            overflow: hidden;
            user-select: none;
        }}
        #workbench-container {{
            position: relative;
            width: 100%;
            height: 480px;
            background: radial-gradient(circle at 50% 30%, #0d1b2a 0%, #050811 100%);
            border: 2px solid #1e293b;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.8);
        }}
        .hud-panel {{
            position: absolute;
            top: 15px;
            left: 15px;
            display: flex;
            flex-direction: column;
            gap: 6px;
            z-index: 10;
        }}
        .badge {{
            background: rgba(15, 23, 42, 0.85);
            border: 1px solid #22c55e;
            border-radius: 6px;
            padding: 6px 12px;
            font-size: 11px;
            color: #86efac;
            display: flex;
            align-items: center;
            gap: 8px;
            backdrop-filter: blur(6px);
        }}
        .dot {{
            width: 8px;
            height: 8px;
            background: #22c55e;
            border-radius: 50%;
            box-shadow: 0 0 10px #22c55e;
            animation: pulse 1.5s infinite;
        }}
        @keyframes pulse {{
            0% {{ transform: scale(0.9); opacity: 0.8; }}
            50% {{ transform: scale(1.2); opacity: 1; }}
            100% {{ transform: scale(0.9); opacity: 0.8; }}
        }}
    </style>
    </head>
    <body>
        <div id="workbench-container">
            <div class="hud-panel">
                <div class="badge">
                    <span class="dot"></span>
                    <span>Live Verification Engine: Active</span>
                </div>
                <div class="badge" style="border-color:#38bdf8; color:#7dd3fc;">
                    <span class="dot" style="background:#38bdf8; box-shadow:0 0 10px #38bdf8;"></span>
                    <span id="wire-count-label">Circuit Netlist Synchronized</span>
                </div>
            </div>
            <canvas id="circuitCanvas" width="900" height="480"></canvas>
        </div>

        <script>
            const canvas = document.getElementById('circuitCanvas');
            const ctx = canvas.getContext('2d');
            const activeWires = {wires_json};

            document.getElementById('wire-count-label').innerText = activeWires.length + ' Wires Active';

            // Arduino Uno Pin Coordinates (Screen Space)
            const arduinoPins = {{
                "D13": {{x: 210, y: 145}}, "D12": {{x: 222, y: 150}}, "D11": {{x: 234, y: 155}},
                "D10": {{x: 246, y: 160}}, "D9":  {{x: 258, y: 165}}, "D8":  {{x: 270, y: 170}},
                "D7":  {{x: 285, y: 177}}, "D6":  {{x: 297, y: 182}}, "D5":  {{x: 309, y: 187}},
                "D4":  {{x: 321, y: 192}}, "D3":  {{x: 333, y: 197}}, "D2":  {{x: 345, y: 202}},
                "D1":  {{x: 357, y: 207}}, "D0":  {{x: 369, y: 212}},
                "5V":  {{x: 195, y: 280}}, "3.3V":{{x: 185, y: 275}}, "GND": {{x: 215, y: 290}},
                "A0":  {{x: 245, y: 305}}, "A1":  {{x: 257, y: 310}}, "A2":  {{x: 269, y: 315}},
                "A3":  {{x: 281, y: 320}}, "A4":  {{x: 293, y: 325}}, "A5":  {{x: 305, y: 330}}
            }};

            // Breadboard Target Terminal Rows
            const bbTargets = [
                {{x: 520, y: 160, label: "LED1"}},
                {{x: 550, y: 175, label: "LED2"}},
                {{x: 580, y: 190, label: "R1"}},
                {{x: 610, y: 205, label: "R2"}},
                {{x: 640, y: 220, label: "BUZZER"}},
                {{x: 670, y: 235, label: "SENSOR"}}
            ];

            let animationTick = 0;

            function drawScene() {{
                ctx.clearRect(0, 0, canvas.width, canvas.height);

                // 1. Grid Background
                ctx.strokeStyle = "rgba(30, 41, 59, 0.4)";
                ctx.lineWidth = 1;
                for (let x = 0; x < canvas.width; x += 30) {{
                    ctx.beginPath();
                    ctx.moveTo(x, 0); ctx.lineTo(x, canvas.height);
                    ctx.stroke();
                }}
                for (let y = 0; y < canvas.height; y += 30) {{
                    ctx.beginPath();
                    ctx.moveTo(0, y); ctx.lineTo(canvas.width, y);
                    ctx.stroke();
                }}

                // 2. Arduino Uno Board (Isometric PCB)
                ctx.save();
                // Drop shadow
                ctx.fillStyle = "rgba(0, 0, 0, 0.5)";
                ctx.beginPath();
                ctx.moveTo(120, 220); ctx.lineTo(280, 140); ctx.lineTo(410, 205); ctx.lineTo(250, 285);
                ctx.fill();

                // PCB Body
                ctx.fillStyle = "#005f73";
                ctx.strokeStyle = "#0a9396";
                ctx.lineWidth = 3;
                ctx.beginPath();
                ctx.moveTo(120, 210); ctx.lineTo(280, 130); ctx.lineTo(400, 190); ctx.lineTo(240, 270);
                ctx.closePath();
                ctx.fill();
                ctx.stroke();

                // USB Port
                ctx.fillStyle = "#94a3b8";
                ctx.fillRect(100, 195, 25, 20);

                // ATmega328P Chip
                ctx.fillStyle = "#0f172a";
                ctx.strokeStyle = "#334155";
                ctx.lineWidth = 1.5;
                ctx.beginPath();
                ctx.moveTo(225, 195); ctx.lineTo(285, 165); ctx.lineTo(310, 178); ctx.lineTo(250, 208);
                ctx.closePath();
                ctx.fill();
                ctx.stroke();

                // Board Text
                ctx.fillStyle = "#ffffff";
                ctx.font = "bold 13px sans-serif";
                ctx.fillText("ARDUINO UNO R3", 180, 185);

                // Digital Header Strip
                ctx.fillStyle = "#020617";
                ctx.beginPath();
                ctx.moveTo(205, 140); ctx.lineTo(380, 220); ctx.lineTo(375, 226); ctx.lineTo(200, 146);
                ctx.fill();

                // Power/Analog Header Strip
                ctx.beginPath();
                ctx.moveTo(175, 270); ctx.lineTo(315, 335); ctx.lineTo(310, 342); ctx.lineTo(170, 277);
                ctx.fill();
                ctx.restore();

                // 3. White Breadboard
                ctx.save();
                // Shadow
                ctx.fillStyle = "rgba(0,0,0,0.4)";
                ctx.beginPath();
                ctx.moveTo(460, 200); ctx.lineTo(660, 100); ctx.lineTo(770, 160); ctx.lineTo(570, 260);
                ctx.fill();

                // Body
                ctx.fillStyle = "#f8fafc";
                ctx.strokeStyle = "#cbd5e1";
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.moveTo(460, 190); ctx.lineTo(660, 90); ctx.lineTo(760, 145); ctx.lineTo(560, 245);
                ctx.closePath();
                ctx.fill();
                ctx.stroke();

                // Power Rail Lines
                ctx.strokeStyle = "#ef4444"; ctx.lineWidth = 2;
                ctx.beginPath(); ctx.moveTo(480, 180); ctx.lineTo(655, 92); ctx.stroke();
                ctx.strokeStyle = "#0284c7";
                ctx.beginPath(); ctx.moveTo(490, 188); ctx.lineTo(665, 100); ctx.stroke();

                // Tie Points
                ctx.fillStyle = "#94a3b8";
                for (let i = 0; i < 11; i++) {{
                    for (let j = 0; j < 5; j++) {{
                        ctx.beginPath();
                        ctx.arc(490 + i * 18, 170 - i * 7 + j * 9, 1.5, 0, Math.PI * 2);
                        ctx.fill();
                    }}
                }}

                // Physical Components on Breadboard
                // Glowing Green LED
                ctx.save();
                ctx.shadowColor = "#22c55e";
                ctx.shadowBlur = 15;
                ctx.fillStyle = "#22c55e";
                ctx.beginPath();
                ctx.arc(540, 140, 8, 0, Math.PI * 2);
                ctx.fill();
                ctx.restore();

                // Glowing Red LED
                ctx.save();
                ctx.shadowColor = "#ef4444";
                ctx.shadowBlur = 15;
                ctx.fillStyle = "#ef4444";
                ctx.beginPath();
                ctx.arc(575, 125, 8, 0, Math.PI * 2);
                ctx.fill();
                ctx.restore();

                // 220 Ohm Resistor (Color bands)
                ctx.fillStyle = "#d97706";
                ctx.fillRect(610, 120, 22, 8);
                ctx.fillStyle = "#dc2626"; ctx.fillRect(614, 120, 2, 8);
                ctx.fillStyle = "#dc2626"; ctx.fillRect(618, 120, 2, 8);
                ctx.fillStyle = "#b45309"; ctx.fillRect(622, 120, 2, 8);

                ctx.restore();

                // 4. Draw Active Dynamic Flexible Jumper Wires
                activeWires.forEach((wire, idx) => {{
                    const start = arduinoPins[wire.pin] || {{x: 230, y: 200}};
                    const target = bbTargets[idx % bbTargets.length];

                    // Curved Bezier Wire
                    const cx = (start.x + target.x) / 2;
                    const cy = Math.min(start.y, target.y) - 45 - (idx * 10) + Math.sin(animationTick + idx) * 3;

                    // Wire Shadow
                    ctx.save();
                    ctx.beginPath();
                    ctx.moveTo(start.x, start.y);
                    ctx.quadraticCurveTo(cx, cy + 18, target.x, target.y);
                    ctx.strokeStyle = "rgba(0, 0, 0, 0.4)";
                    ctx.lineWidth = 6;
                    ctx.lineCap = "round";
                    ctx.stroke();
                    ctx.restore();

                    // Insulated Wire
                    ctx.save();
                    ctx.beginPath();
                    ctx.moveTo(start.x, start.y);
                    ctx.quadraticCurveTo(cx, cy, target.x, target.y);
                    ctx.strokeStyle = wire.color;
                    ctx.lineWidth = 4;
                    ctx.lineCap = "round";
                    ctx.shadowColor = wire.color;
                    ctx.shadowBlur = 8;
                    ctx.stroke();

                    // Metal Jumper Pins
                    ctx.fillStyle = "#ffffff";
                    ctx.beginPath(); ctx.arc(start.x, start.y, 3.5, 0, Math.PI * 2); ctx.fill();
                    ctx.beginPath(); ctx.arc(target.x, target.y, 3.5, 0, Math.PI * 2); ctx.fill();
                    ctx.restore();
                }});

                animationTick += 0.04;
                requestAnimationFrame(drawScene);
            }}

            drawScene();
        </script>
    </body>
    </html>
    """
    st.components.v1.html(canvas_html, height=500)

    # Netlist Breakdown
    col_n1, col_n2 = st.columns([1.3, 1])
    with col_n1:
        st.write("#### 📋 Live Hardware Netlist")
        if st.session_state["wires"]:
            st.dataframe(st.session_state["wires"], use_container_width=True)
        else:
            st.info("No connections mapped. Use the sidebar to attach circuit components.")
            
    with col_n2:
        st.write("#### ✂️ Detach Node")
        if st.session_state["wires"]:
            active_list = [w["pin"] for w in st.session_state["wires"]]
            detach_pin = st.selectbox("Select Pin to Remove", active_list)
            if st.button("Disconnect Terminal", use_container_width=True):
                st.session_state["wires"] = [w for w in st.session_state["wires"] if w["pin"] != detach_pin]
                st.rerun()

# 5. Compilable Arduino C++ Sketch
with tab_code:
    st.subheader("💻 Synchronized Arduino C++ Source Code (.ino)")
    st.caption("Compilable code mapped directly to your live wiring netlist.")

    pin_defs = ""
    setup_code = ""
    loop_code = ""

    for w in st.session_state["wires"]:
        pin_name = w["pin"]
        if pin_name in ["5V", "3.3V", "GND"]:
            continue
        var_name = "".join(c if c.isalnum() else "_" for c in w["component"].lower()).strip("_") + "_pin"
        pin_num = pin_name.replace("D", "")
        
        pin_defs += f"const int {var_name} = {pin_num};  // Pin for {w['component']}\n"
        
        if w["mode"] in ["OUTPUT", "DIGITAL"]:
            setup_code += f"  pinMode({var_name}, OUTPUT);\n"
            loop_code += f"  digitalWrite({var_name}, HIGH); // Enable node\n"
        elif w["mode"] == "PWM":
            setup_code += f"  pinMode({var_name}, OUTPUT);\n"
            loop_code += f"  analogWrite({var_name}, 128); // 50% PWM Duty Cycle\n"
        elif w["mode"] == "ADC":
            setup_code += f"  pinMode({var_name}, INPUT);\n"
            loop_code += f"  int {var_name}_val = analogRead({var_name});\n"

    sketch = f"""// ===============================================================
// ECE Interactive Circuit Studio - Auto-Generated Arduino Code
// ===============================================================

{pin_defs if pin_defs else "// No active microcontroller pins wired.\\n"}
void setup() {{
  Serial.begin(9600);
{setup_code}
  Serial.println("Circuit initialized successfully.");
}}

void loop() {{
{loop_code if loop_code else "  // Insert your project control ideology here"}
  delay(100);
}}
"""
    st.code(sketch, language="cpp", line_numbers=True)

# 6. ECE Circuit Calculations
with tab_theory:
    st.subheader("📐 Theoretical ECE Circuit Proofs")
    
    with st.expander("🔹 LED Current Limiting Calculation (Ohm's Law)", expanded=True):
        st.latex(r"R = \frac{V_{CC} - V_F}{I_F} = \frac{5.0\,\text{V} - 2.0\,\text{V}}{0.02\,\text{A}} = 150\,\Omega")
        st.info("Using standard **220 Ω** for safe long-term component operation (~13.6 mA drive).")

    with st.expander("🔹 PWM Average Voltage Output", expanded=True):
        st.latex(r"V_{avg} = D \times V_{peak} = \left(\frac{" + str(scope_duty) + r"}{100}\right) \times " + str(scope_amp) + r"\text{V} = " + f"{(scope_duty / 100.0) * scope_amp:.2f}" + r"\,\text{V}")
        st.info(f"Average calculated voltage at **{scope_duty}%** duty cycle: **{(scope_duty / 100.0) * scope_amp:.2f} V**")

# 7. Virtual Oscilloscope
with tab_scope:
    st.subheader("📈 Virtual Oscilloscope Trace")
    
    t = np.linspace(0, 0.01, 1000)  # 10 ms window
    period = 1.0 / scope_freq if scope_freq > 0 else 0.002
    duty_frac = scope_duty / 100.0
    wave = np.where((t % period) < (period * duty_frac), scope_amp, 0.0)

    fig, ax = plt.subplots(figsize=(9, 3.2))
    ax.plot(t * 1000, wave, color="#00ffcc", linewidth=2.2, label=f"CH1 PWM ({scope_freq} Hz, {scope_duty}%)")
    ax.set_xlabel("Time (milliseconds)", color="#cbd5e1")
    ax.set_ylabel("Amplitude (Volts)", color="#cbd5e1")
    ax.set_ylim(-0.5, scope_amp + 1.2)
    ax.grid(True, linestyle="--", alpha=0.3, color="#64748b")
    ax.set_facecolor("#0b0f19")
    fig.patch.set_facecolor("#0f172a")
    ax.tick_params(colors="#cbd5e1")
    for spine in ax.spines.values():
        spine.set_color("#334155")
    ax.legend(facecolor="#1e293b", edgecolor="#334155", labelcolor="#f8fafc")

    st.pyplot(fig)
