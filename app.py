import streamlit as st
import numpy as np
import plotly.graph_objects as go
import streamlit.components.v1 as components

st.set_page_config(
    page_title="ECE Engineering Hub",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------- THEME --------------------
st.markdown("""
<style>
.stApp { background: #0b1020; color: #edf3ff; }
[data-testid="stSidebar"] { background: #121a2e; }
.hero {
    padding: 28px; border: 1px solid #26334d; border-radius: 18px;
    background: linear-gradient(120deg,#121a2e,#192744);
}
.hero h1 { color: #6ee7d8; font-size: 42px; margin-bottom: 5px; }
.hero p { color: #aab8d1; font-size: 17px; }
.card {
    padding: 18px; border: 1px solid #26334d; border-radius: 14px;
    background: #121a2e; margin-bottom: 12px;
}
.small { color: #9eacc7; font-size: 13px; }
</style>
""", unsafe_allow_html=True)

# -------------------- DATA --------------------
SUBJECTS = {
    "Analog Electronics": [
        "Diodes and Rectifiers", "BJT and FET", "Amplifiers",
        "Operational Amplifiers", "RC Filters", "Oscillators"
    ],
    "Digital Electronics": [
        "Logic Gates", "Boolean Algebra", "Flip-Flops",
        "Counters", "Registers", "ADC and DAC"
    ],
    "Communication Systems": [
        "AM Modulation", "FM Modulation", "PM Modulation",
        "PCM", "ASK", "FSK", "PSK"
    ],
    "Signals and Systems": [
        "Signal Generation", "Convolution", "Fourier Transform",
        "Laplace Transform", "Z-Transform", "Sampling"
    ],
    "Microprocessors and Embedded Systems": [
        "8086 Microprocessor", "8051 Microcontroller",
        "Arduino", "ESP32", "Sensor Interfacing"
    ],
    "Control Systems": [
        "Transfer Functions", "Block Diagrams", "Time Response",
        "Stability", "Root Locus", "PID Controllers"
    ],
    "Electromagnetic Theory": [
        "Electric Fields", "Magnetic Fields", "Transmission Lines",
        "Waveguides", "Antennas"
    ],
    "VLSI and Semiconductor Devices": [
        "MOSFET", "CMOS Logic", "Digital IC Design",
        "Semiconductor Fabrication"
    ]
}

EXPERIMENTS = {
    "RC Low-Pass Filter": {
        "subject": "Analog Electronics",
        "theory": "An RC low-pass filter passes low-frequency signals and attenuates high-frequency signals.",
        "formula": "fc = 1 / (2πRC)",
        "components": ["Resistor", "Capacitor", "AC signal source", "Ground"],
        "connections": [
            "Input source → Resistor → Output node",
            "Output node → Capacitor → Ground",
            "Source ground → Circuit ground"
        ],
        "python": """import numpy as np
import matplotlib.pyplot as plt

R = 1000       # Resistance in ohms
C = 100e-9     # Capacitance in farads

f = np.logspace(1, 6, 500)
fc = 1 / (2 * np.pi * R * C)
gain = 1 / np.sqrt(1 + (f / fc)**2)

plt.semilogx(f, 20 * np.log10(gain))
plt.xlabel("Frequency (Hz)")
plt.ylabel("Gain (dB)")
plt.title("RC Low-Pass Filter")
plt.grid(True)
plt.show()
""",
        "arduino": "// Basic Arduino analog input reading\nconst int inputPin = A0;\n\nvoid setup() {\n  Serial.begin(9600);\n}\n\nvoid loop() {\n  int value = analogRead(inputPin);\n  Serial.println(value);\n  delay(100);\n}\n"
    },
    "Logic Gates": {
        "subject": "Digital Electronics",
        "theory": "Logic gates perform Boolean operations on binary inputs and produce binary outputs.",
        "formula": "AND: Y = A·B | OR: Y = A+B | XOR: Y = A⊕B",
        "components": ["Logic gate IC", "Input switches", "LED", "Current-limiting resistor"],
        "connections": [
            "Connect input switches to gate inputs",
            "Connect gate output to LED through a resistor",
            "Connect power and ground according to the IC datasheet"
        ],
        "python": """from itertools import product

print("A B | AND OR XOR")
for A, B in product([0, 1], repeat=2):
    print(A, B, "| ", A & B, " ", A | B, " ", A ^ B)
""",
        "arduino": """const int A = 2;
const int B = 3;
const int outputPin = 8;

void setup() {
  pinMode(A, INPUT);
  pinMode(B, INPUT);
  pinMode(outputPin, OUTPUT);
}

void loop() {
  int a = digitalRead(A);
  int b = digitalRead(B);
  digitalWrite(outputPin, a && b); // AND gate
}
"""
    },
    "Arduino Sensor Lab": {
        "subject": "Microprocessors and Embedded Systems",
        "theory": "Arduino reads sensor voltage using its ADC and can transmit readings to a computer over USB serial.",
        "formula": "Voltage ≈ ADC count × Vref / (2^N − 1)",
        "components": ["Arduino Uno", "Analog sensor", "Breadboard", "Jumper wires", "USB cable"],
        "connections": [
            "Sensor VCC → Arduino supply (check sensor specifications)",
            "Sensor GND → Arduino GND",
            "Sensor signal → Arduino A0"
        ],
        "python": """import serial
import time

# Change COM3 to your Arduino port.
# Linux example: /dev/ttyACM0
arduino = serial.Serial("COM3", 9600, timeout=1)
time.sleep(2)

while True:
    line = arduino.readline().decode(errors="ignore").strip()
    if line:
        print("Sensor reading:", line)
""",
        "arduino": """const int sensorPin = A0;

void setup() {
  Serial.begin(9600);
}

void loop() {
  int reading = analogRead(sensorPin);
  Serial.println(reading);
  delay(250);
}
"""
    },
    "AM Modulation": {
        "subject": "Communication Systems",
        "theory": "Amplitude modulation varies the carrier amplitude according to the message signal.",
        "formula": "s(t) = Ac[1 + μ cos(2πfmt)] cos(2πfct)",
        "components": ["Message signal", "Carrier signal", "Modulator", "Oscilloscope"],
        "connections": [
            "Apply message signal to the modulator input",
            "Apply carrier signal to the carrier input",
            "Observe the modulated output using an oscilloscope"
        ],
        "python": """import numpy as np
import matplotlib.pyplot as plt

fs = 100000
t = np.arange(0, 0.005, 1/fs)
fm, fc, mu = 1000, 10000, 0.7
message = np.cos(2*np.pi*fm*t)
carrier = np.cos(2*np.pi*fc*t)
am = (1 + mu*message) * carrier

plt.plot(t, am)
plt.xlabel("Time (s)")
plt.ylabel("Amplitude")
plt.title("AM Modulated Signal")
plt.grid(True)
plt.show()
""",
        "arduino": "// AM signal generation requires suitable external hardware.\n// Do not connect RF circuits directly to Arduino pins."
    }
}

# -------------------- SIDEBAR --------------------
st.sidebar.markdown("# ⚡ ECE Hub")
st.sidebar.caption("Virtual + Physical Engineering Laboratory")
page = st.sidebar.radio(
    "Navigate",
    ["Dashboard", "ECE Subjects", "Experiment Lab", "Circuit Builder",
     "Graph Lab", "Arduino Lab", "Coding Lab"]
)
st.sidebar.markdown("---")
st.sidebar.info("Learning platform for ECE students")

# -------------------- DASHBOARD --------------------
if page == "Dashboard":
    st.markdown("""
    <div class="hero">
      <h1>ECE Engineering Hub</h1>
      <p>Learn. Build. Simulate. Connect real hardware.</p>
      <p>One platform for ECE theory, circuit connections, experiments,
      coding, graphs, and Arduino projects.</p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Explore Engineering Labs")
    cols = st.columns(4)
    highlights = [
        ("📘", "ECE Theory", "Concepts and formulas"),
        ("🔌", "Circuit Lab", "Components and connections"),
        ("📈", "Graph Lab", "Interactive engineering plots"),
        ("🤖", "Arduino Lab", "Physical hardware projects")
    ]
    for col, item in zip(cols, highlights):
        with col:
            st.markdown(
                f'<div class="card"><h2>{item[0]}</h2><b>{item[1]}</b>'
                f'<p class="small">{item[2]}</p></div>',
                unsafe_allow_html=True
            )

    st.subheader("Featured Experiments")
    for name, exp in EXPERIMENTS.items():
        with st.expander(f"🔬 {name} — {exp['subject']}"):
            st.write(exp["theory"])
            st.code(exp["formula"])

# -------------------- SUBJECTS --------------------
elif page == "ECE Subjects":
    st.title("📚 ECE Subject Library")
    st.write("Select a subject to explore its topics.")
    subject = st.selectbox("Choose ECE subject", list(SUBJECTS.keys()))
    st.subheader(subject)
    for topic in SUBJECTS[subject]:
        st.markdown(f"- {topic}")
    st.info("You can expand this library by adding notes, diagrams, experiments, and quizzes for each topic.")

# -------------------- EXPERIMENT LAB --------------------
elif page == "Experiment Lab":
    st.title("🔬 Experiment Laboratory")
    selected = st.selectbox("Select experiment", list(EXPERIMENTS.keys()))
    exp = EXPERIMENTS[selected]

    st.subheader("1. Theory")
    st.write(exp["theory"])

    st.subheader("2. Formula / Principle")
    st.code(exp["formula"])

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("3. Required Components")
        for component in exp["components"]:
            st.write(f"• {component}")
    with col2:
        st.subheader("4. Connection Details")
        for connection in exp["connections"]:
            st.write(f"• {connection}")

    st.subheader("5. Python Code")
    st.code(exp["python"], language="python")

    st.subheader("6. Arduino Code")
    st.code(exp["arduino"], language="cpp")

    st.caption("Hardware safety: verify voltage, polarity, current limits, and datasheets before connecting components.")

# -------------------- CIRCUIT BUILDER --------------------
elif page == "Circuit Builder":
    st.title("🔌 Circuit Builder")
    st.write("Starter component workspace. Select components and arrange your circuit plan.")
    component_types = ["Resistor", "Capacitor", "Inductor", "Diode", "LED",
                       "BJT", "MOSFET", "Op-Amp", "Arduino Uno", "Ground", "AC Source"]
    selected_components = st.multiselect("Add components to your workspace", component_types)
    if selected_components:
        st.subheader("Your Components")
        cols = st.columns(4)
        for i, component in enumerate(selected_components):
            with cols[i % 4]:
                st.markdown(
                    f'<div class="card"><h3>🔧 {component}</h3>'
                    '<p class="small">Component added to design</p></div>',
                    unsafe_allow_html=True
                )
    st.warning("This is a component-planning interface. Electrical wire routing and circuit simulation require a dedicated simulator integration.")
    st.markdown("**Next integration:** CircuitJS or ngspice for real electrical simulation.")

# -------------------- GRAPH LAB --------------------
elif page == "Graph Lab":
    st.title("📈 Interactive Graph Lab")
    experiment = st.selectbox("Choose graph", ["RC Low-Pass Filter", "AM Modulation", "Sine Wave"])
    if experiment == "RC Low-Pass Filter":
        R = st.number_input("Resistance (Ω)", min_value=1.0, value=1000.0)
        C = st.number_input("Capacitance (F)", min_value=1e-12, value=100e-9, format="%.10f")
        f = np.logspace(1, 7, 600)
        fc = 1 / (2 * np.pi * R * C)
        gain = 1 / np.sqrt(1 + (f / fc)**2)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=f, y=20*np.log10(gain), mode="lines", name="Gain"))
        fig.update_layout(title=f"RC Low-Pass Filter | Cutoff = {fc:.2f} Hz",
                         xaxis_title="Frequency (Hz)", yaxis_title="Gain (dB)",
                         xaxis_type="log", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
    elif experiment == "AM Modulation":
        fm = st.slider("Message frequency (Hz)", 100, 2000, 500)
        fc = st.slider("Carrier frequency (Hz)", 2000, 20000, 8000)
        mu = st.slider("Modulation index", 0.0, 1.0, 0.7)
        t = np.linspace(0, 0.01, 5000)
        signal = (1 + mu*np.cos(2*np.pi*fm*t))*np.cos(2*np.pi*fc*t)
        fig = go.Figure(go.Scatter(x=t, y=signal, mode="lines", name="AM"))
        fig.update_layout(title="AM Waveform", xaxis_title="Time (s)",
                         yaxis_title="Amplitude", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
    else:
        frequency = st.slider("Frequency (Hz)", 1, 100, 10)
        t = np.linspace(0, 1, 1000)
        y = np.sin(2*np.pi*frequency*t)
        fig = go.Figure(go.Scatter(x=t, y=y, mode="lines"))
        fig.update_layout(title="Sine Wave", xaxis_title="Time (s)",
                         yaxis_title="Amplitude", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

# -------------------- ARDUINO LAB --------------------
elif page == "Arduino Lab":
    st.title("🤖 Arduino Hardware Lab")
    st.write("Use this section to plan and document physical Arduino experiments.")
    st.markdown("""
    **Basic connection workflow**
    1. Connect Arduino to your computer using USB.
    2. Upload the Arduino sketch using Arduino IDE.
    3. Run a Python serial program on the computer to receive measurements.
    4. Display the incoming values as a live graph.
    """)
    st.warning("Streamlit Cloud runs on a remote server and usually cannot access USB devices connected to your personal computer. For direct hardware access, run the app locally or use a browser Web Serial interface.")
    st.code("""# Install locally
pip install pyserial

# List serial ports
python -m serial.tools.list_ports
""", language="bash")
    st.markdown("**Example Arduino sketch:**")
    st.code(EXPERIMENTS["Arduino Sensor Lab"]["arduino"], language="cpp")
    st.markdown("**Example Python receiver:**")
    st.code(EXPERIMENTS["Arduino Sensor Lab"]["python"], language="python")

# -------------------- CODING LAB --------------------
elif page == "Coding Lab":
    st.title("💻 ECE Coding Lab")
    language = st.selectbox("Choose language", ["Python", "Arduino C++", "C"])
    starter_code = {
        "Python": "import numpy as np\\n\\n# Write your ECE program here\\n",
        "Arduino C++": "void setup() {\\n  Serial.begin(9600);\\n}\\n\\nvoid loop() {\\n  // Write your Arduino code here\\n}\\n",
        "C": "#include <stdio.h>\\n\\nint main() {\\n    // Write your C program here\\n    return 0;\\n}\\n"
    }
    user_code = st.text_area("Code editor", value=starter_code[language], height=280)
    st.caption("This starter editor displays code. Secure code execution can be added later using a sandboxed execution service.")
    st.download_button(
        "Download code",
        data=user_code,
        file_name={"Python": "ece_program.py", "Arduino C++": "ece_sketch.ino", "C": "ece_program.c"}[language],
        mime="text/plain"
    )

# -------------------- FOOTER --------------------
st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:#9eacc7'>⚡ ECE Engineering Hub | "
    "Built with Python + Streamlit</p>",
    unsafe_allow_html=True
)
