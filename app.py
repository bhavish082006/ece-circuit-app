import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="ECE 3D Arduino Lab", page_icon="🔌", layout="wide")
st.title("🔌 ECE 3D Arduino Circuit Lab")
st.caption("Interactive 3D wiring workspace — select two pins to connect them.")

st.info(
    "How to use: click a pin on a component, then click a second pin. "
    "A wire will appear and the connection list will update. Click Clear Wires to reset."
)

html = r"""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
html,body { margin:0; background:#0b1020; color:#eaf1ff; font-family:Arial,sans-serif; }
#toolbar { padding:10px 12px; display:flex; flex-wrap:wrap; gap:8px; align-items:center; background:#121a2e; }
button { background:#1d3557; color:white; border:1px solid #49658a; border-radius:8px; padding:8px 12px; cursor:pointer; }
button:hover { background:#285078; }
#status { color:#6ee7d8; font-weight:bold; }
#layout { display:grid; grid-template-columns:minmax(0,1fr) 260px; height:560px; }
#scene { min-width:0; height:560px; }
#panel { background:#121a2e; border-left:1px solid #26334d; padding:12px; overflow:auto; }
h3 { margin:5px 0 10px; color:#6ee7d8; }
#connections { font-size:13px; line-height:1.6; }
.hint { color:#aab8d1; font-size:12px; }
@media(max-width:650px) { #layout { grid-template-columns:1fr; height:auto; } #scene{height:430px;} #panel{height:200px;} }
</style>
</head>
<body>
<div id="toolbar">
  <button onclick="clearWires()">Clear Wires</button>
  <button onclick="resetCamera()">Reset View</button>
  <button onclick="showExample()">Load Example: Arduino GND → Battery −</button>
  <span id="status">Select a pin to begin.</span>
</div>
<div id="layout">
  <div id="scene"></div>
  <div id="panel">
    <h3>Connection Inspector</h3>
    <div class="hint">Click a pin, then another pin. Select a wire in the list to inspect it.</div>
    <hr>
    <div id="connections">No connections yet.</div>
    <hr>
    <div id="detail" class="hint">Pin details will appear here.</div>
  </div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
const sceneDiv = document.getElementById('scene');
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0b1020);
scene.fog = new THREE.Fog(0x0b1020, 16, 35);
const camera = new THREE.PerspectiveCamera(45, sceneDiv.clientWidth/sceneDiv.clientHeight, 0.1, 100);
camera.position.set(8,8,11);
const renderer = new THREE.WebGLRenderer({antialias:true});
renderer.setSize(sceneDiv.clientWidth, sceneDiv.clientHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio,2));
sceneDiv.appendChild(renderer.domElement);
const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
scene.add(new THREE.HemisphereLight(0xffffff,0x334466,2));
const light = new THREE.DirectionalLight(0xffffff,2); light.position.set(5,10,7); scene.add(light);

const mat = (color, metal=0.1) => new THREE.MeshStandardMaterial({color, metalness:metal, roughness:0.45});
const green = mat(0x147d55), blue = mat(0x1769aa), black = mat(0x20242d), red = mat(0xe34b4b);
const gold = mat(0xe7b84b,0.65), white = mat(0xeaf1ff);
const board = new THREE.Mesh(new THREE.BoxGeometry(5.4,0.22,3.2), mat(0x16845b));
board.position.set(0,0,0); scene.add(board);
const boardTop = new THREE.Mesh(new THREE.BoxGeometry(5.25,0.03,3.05), mat(0x1c9a6b));
boardTop.position.y=0.13; scene.add(boardTop);

// Breadboard center trench and rails
const trench = new THREE.Mesh(new THREE.BoxGeometry(5.2,0.04,0.16), mat(0x0b4b36));
trench.position.set(0,0.16,0); scene.add(trench);
for(let x=-2.45;x<=2.46;x+=0.22){
  for(let z of [-1.25,-1.02,1.02,1.25]){
    const hole = new THREE.Mesh(new THREE.CylinderGeometry(0.035,0.035,0.025,10), mat(0x083b2c));
    hole.position.set(x,0.17,z); scene.add(hole);
  }
}

const parts = {};
const pins = [];
function addPin(id,label,kind,pos,color){
  const mesh = new THREE.Mesh(new THREE.SphereGeometry(0.105,16,12),mat(color,0.25));
  mesh.position.copy(pos); mesh.userData={pinId:id,label,kind};
  scene.add(mesh); pins.push(mesh); parts[id]=mesh;
  const ring = new THREE.Mesh(new THREE.TorusGeometry(0.14,0.018,8,20),mat(0xffffff));
  ring.rotation.x=Math.PI/2; ring.position.copy(pos); ring.position.y+=0.015; scene.add(ring);
  return mesh;
}
function box(name,size,pos,material){
  const m=new THREE.Mesh(new THREE.BoxGeometry(...size),material);
  m.position.set(...pos); scene.add(m); return m;
}
function label(text,pos,color="#ffffff"){
 const c=document.createElement('canvas'); c.width=256;c.height=64;
 const ctx=c.getContext('2d'); ctx.fillStyle="rgba(5,12,25,.75)";
 ctx.fillRect(0,0,256,64); ctx.font="bold 26px Arial"; ctx.fillStyle=color;
 ctx.fillText(text,8,42);
 const tex=new THREE.CanvasTexture(c);
 const sprite=new THREE.Sprite(new THREE.SpriteMaterial({map:tex,transparent:true}));
 sprite.position.set(...pos); sprite.scale.set(1.25,.32,1); scene.add(sprite);
}

// Arduino Uno board
box("Arduino", [3.1,.25,1.65],[-0.5,.42,0],blue);
box("USB port",[.55,.32,.5],[-2.15,.48,.1],gold);
box("Power jack",[.42,.3,.42],[-1.8,.48,.62],black);
label("ARDUINO UNO",[-.5,.78,0],"#6ee7d8");
const arduinoPins=[
 ["GND","Arduino GND","GND",[-1.55,.65,-.72],0x222222],
 ["5V","Arduino 5V","POWER",[-1.25,.65,-.72],0xe34b4b],
 ["D13","Arduino D13","DIGITAL",[-.95,.65,-.72],0xe7b84b],
 ["D12","Arduino D12","DIGITAL",[-.65,.65,-.72],0xe7b84b],
 ["A0","Arduino A0","ANALOG",[.65,.65,.72],0x6ee7d8],
 ["GND2","Arduino GND (2)","GND",[.95,.65,.72],0x222222]
];
arduinoPins.forEach(p=>addPin(p[0],p[1],p[2],new THREE.Vector3(...p[3]),p[4]));

// Battery
box("Battery",[1.35,.55,.85],[3.05,.42,-.1],black);
box("Battery top",[1.25,.08,.75],[3.05,.72,-.1],mat(0x333b48));
label("BATTERY", [3.05,1.2,-.1]);
addPin("BAT+","Battery positive (+)","POWER",new THREE.Vector3(2.72,.9,-.45),0xe34b4b);
addPin("BAT-","Battery negative (−)","GROUND",new THREE.Vector3(3.38,.9,-.45),0x222222);

// LED and resistor
const ledBody=new THREE.Mesh(new THREE.SphereGeometry(.22,20,16),red);
ledBody.scale.set(1,1.25,1); ledBody.position.set(1.5,.55,1.25); scene.add(ledBody);
label("LED",[1.5,1.05,1.25]);
addPin("LED_A","LED anode","LED",new THREE.Vector3(1.25,.45,1.25),0xe34b4b);
addPin("LED_K","LED cathode","LED",new THREE.Vector3(1.75,.45,1.25),0x222222);
box("Resistor",[.7,.14,.2],[.25,.45,1.25],gold);
label("220 Ω",[.25,.85,1.25]);
addPin("R1_A","Resistor pin 1","RESISTOR",new THREE.Vector3(-.1,.45,1.25),0xe7b84b);
addPin("R1_B","Resistor pin 2","RESISTOR",new THREE.Vector3(.6,.45,1.25),0xe7b84b);

const wireGroup=new THREE.Group(); scene.add(wireGroup);
let wires=[], selectedPin=null;
const raycaster=new THREE.Raycaster(), mouse=new THREE.Vector2();
function wireBetween(a,b,color=0x6ee7d8){
 const start=parts[a].position.clone(), end=parts[b].position.clone();
 const mid1=start.clone().add(new THREE.Vector3(0,.45,0));
 const mid2=end.clone().add(new THREE.Vector3(0,.45,0));
 const curve=new THREE.CatmullRomCurve3([start,mid1,mid2,end]);
 const mesh=new THREE.Mesh(new THREE.TubeGeometry(curve,24,.035,8,false),mat(color,.15));
 wireGroup.add(mesh); return mesh;
}
function renderConnections(){
 const el=document.getElementById("connections");
 if(!wires.length){el.innerHTML="No connections yet.";return;}
 el.innerHTML=wires.map((w,i)=>`<div style="margin:7px 0;padding:7px;background:#1b2942;border-radius:7px">
 <button onclick="inspectWire(${i})">Wire ${i+1}</button><br>${w.aLabel} ↔ ${w.bLabel}</div>`).join("");
}
window.inspectWire=function(i){
 const w=wires[i];
 document.getElementById("detail").innerHTML=`<b>${w.aLabel}</b> connected to <b>${w.bLabel}</b><br>
 Pin types: ${w.aKind} ↔ ${w.bKind}<br>
 <span style="color:#f4c66a">Connection is recorded visually. Electrical behavior is not yet simulated.</span>`;
};
function addConnection(a,b){
 if(a===b){document.getElementById("status").textContent="Choose two different pins.";return;}
 if(wires.some(w=>(w.a===a&&w.b===b)||(w.a===b&&w.b===a))){
  document.getElementById("status").textContent="Those pins are already connected.";return;
 }
 const pa=parts[a].userData, pb=parts[b].userData;
 const colors=(pa.kind==="GND"||pa.kind==="GROUND"||pb.kind==="GND"||pb.kind==="GROUND")?0x222222:0x6ee7d8;
 wireBetween(a,b,colors);
 wires.push({a,b,aLabel:pa.label,bLabel:pb.label,aKind:pa.kind,bKind:pb.kind});
 renderConnections(); inspectWire(wires.length-1);
 document.getElementById("status").textContent="Connected: "+pa.label+" ↔ "+pb.label;
}
function onClick(event){
 const rect=renderer.domElement.getBoundingClientRect();
 mouse.x=((event.clientX-rect.left)/rect.width)*2-1;
 mouse.y=-((event.clientY-rect.top)/rect.height)*2+1;
 raycaster.setFromCamera(mouse,camera);
 const hits=raycaster.intersectObjects(pins);
 if(!hits.length)return;
 const p=hits[0].object.userData;
 if(!selectedPin){
  selectedPin=p.pinId;
  document.getElementById("status").textContent="Selected "+p.label+". Now select destination pin.";
  document.getElementById("detail").innerHTML=`Selected pin: <b>${p.label}</b><br>Type: ${p.kind}`;
  hits[0].object.material=mat(0xffffff);
 } else {
  addConnection(selectedPin,p.pinId);
  selectedPin=null;
  pins.forEach(pin=>pin.material=mat(pin.userData.kind==="GND"||pin.userData.kind==="GROUND"?0x222222:
      pin.userData.kind==="POWER"?0xe34b4b:
      pin.userData.kind==="DIGITAL"||pin.userData.kind==="RESISTOR"?0xe7b84b:
      pin.userData.kind==="LED"?0xe34b4b:0x6ee7d8,0.25));
 }
}
renderer.domElement.addEventListener("click",onClick);
window.clearWires=function(){while(wireGroup.children.length){wireGroup.remove(wireGroup.children[0]);}
 wires=[];selectedPin=null;renderConnections();document.getElementById("detail").textContent="Connection list cleared.";
 document.getElementById("status").textContent="Select a pin to begin.";};
window.resetCamera=function(){camera.position.set(8,8,11);controls.target.set(0,0,0);controls.update();};
window.showExample=function(){clearWires();addConnection("GND","BAT-");};
function animate(){requestAnimationFrame(animate);controls.update();renderer.render(scene,camera);}
animate();
window.addEventListener("resize",()=>{
 const w=sceneDiv.clientWidth,h=sceneDiv.clientHeight;
 camera.aspect=w/h;camera.updateProjectionMatrix();renderer.setSize(w,h);
});
</script>
</body>
</html>
"""

components.html(html, height=680, scrolling=True)

st.markdown("### What this prototype does")
st.write(
    "- Displays a 3D Arduino, battery, LED, resistor, and breadboard.\n"
    "- Click any pin, then another pin to draw a wire.\n"
    "- Lists the selected connection and pin types.\n"
    "- Includes a one-click example for Arduino GND → battery negative."
)
st.warning(
    "Prototype limitation: this records visual wiring only. It does not yet solve "
    "electrical circuits, check voltage/current, or run Arduino firmware. "
    "Use safe low-voltage supplies and verify real wiring against datasheets."
)
