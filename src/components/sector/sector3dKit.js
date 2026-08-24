export function addEquipment3D(THREE,{root,appearance,add,mat,dark,glow,cfg}){
 const bright=mat(0xdce8f4),gold=mat(0xffcf55),cyan=mat(0x55d8ff,.35,.16,0x55d8ff),violet=mat(0x9b72ff,.35,.16,0x9b72ff)
 const head=appearance.head
 if(head){
  if(head==='scrap_cap'){const m=add(new THREE.SphereGeometry(.72,18,10,0,Math.PI*2,0,Math.PI/2),mat(0x69523e,.35,.65),root,[0,1.87,0]);m.scale.y=.45;add(new THREE.BoxGeometry(.76,.08,.28),mat(0x69523e),root,[.28,1.84,.54])}
  if(head==='engineer_cap'){const m=add(new THREE.SphereGeometry(.74,24,12,0,Math.PI*2,0,Math.PI/2),gold,root,[0,1.88,0]);m.scale.y=.48;add(new THREE.BoxGeometry(.76,.11,.26),gold,root,[.24,1.84,.56]);add(new THREE.BoxGeometry(.28,.13,.08),dark,root,[0,2.08,.18])}
  if(head==='commander_cap'||head==='captain_hat'){const navy=mat(head==='captain_hat'?0x243e70:0x2c477b);const m=add(new THREE.CylinderGeometry(.63,.75,.3,24),navy,root,[0,1.98,0]);add(new THREE.BoxGeometry(1.02,.09,.36),navy,root,[0,1.85,.55]);add(new THREE.TorusGeometry(.29,.035,8,24,Math.PI),gold,root,[0,1.98,.66]).rotation.z=Math.PI/2}
  if(head==='elite_crown'){const crown=new THREE.Group();crown.position.set(0,1.96,0);root.add(crown);for(let i=0;i<5;i++){const p=add(new THREE.ConeGeometry(.14,.66,4),gold,crown,[(i-2)*.25,.27,0]);p.rotation.y=.78}add(new THREE.TorusGeometry(.63,.1,10,30),gold,crown)}
  if(head==='halo_core'){const halo=add(new THREE.TorusGeometry(.75,.055,10,48),gold,root,[0,2.43,0]);halo.rotation.x=Math.PI/2}
 }
 const face=appearance.face
 if(face){
  if(face==='welder_mask'){add(new THREE.BoxGeometry(1.38,.78,.13),mat(0x342d29,.6,.4),root,[0,1.02,.93]);add(new THREE.BoxGeometry(.8,.24,.05),mat(0x07121a,.2,.1,0xff9b42),root,[0,1.08,1.02])}
  if(face==='round_goggles')[-.39,.39].forEach(x=>add(new THREE.TorusGeometry(.25,.055,10,28),cyan,root,[x,1.1,.94]))
  if(face==='mono_visor'||face==='combat_visor')add(new THREE.BoxGeometry(1.35,.34,.12),face==='combat_visor'?violet:cyan,root,[0,1.08,.96])
 }
 const body=appearance.body
 if(body){
  if(body==='patched_vest'){[-.45,.38].forEach((x,i)=>{const p=add(new THREE.BoxGeometry(.52,.6,.1),mat(i?0x72533f:0x87634c,.3,.7),root,[x,-.5,1.01]);p.rotation.z=i?-.12:.1})}
  if(body==='utility_jacket'){add(new THREE.BoxGeometry(1.35,.22,.12),mat(0x41566d),root,[0,-.65,1.02]);[-.42,.42].forEach(x=>add(new THREE.BoxGeometry(.3,.28,.14),dark,root,[x,-.9,1.08]))}
  if(body==='officer_coat'){add(new THREE.BoxGeometry(1.38,.16,.12),mat(0x243e6e),root,[0,-.22,1.01]);[-.43,.43].forEach(x=>{const lapel=add(new THREE.ConeGeometry(.22,.72,3),mat(0x36558d),root,[x,-.52,1.06]);lapel.rotation.z=x<0?.35:-.35});add(new THREE.BoxGeometry(.66,.07,.08),gold,root,[0,-.88,1.12])}
  if(body==='neon_armor'){[-.58,.58].forEach(x=>add(new THREE.BoxGeometry(.24,.72,.13),violet,root,[x,-.48,.93]));add(new THREE.TorusGeometry(.4,.045,8,30),violet,root,[0,-.47,1.09])}
  if(body==='royal_chassis'){add(new THREE.TorusGeometry(.53,.08,10,30),gold,root,[0,-.48,1.08]);add(new THREE.BoxGeometry(.12,.68,.1),gold,root,[0,-.48,1.06])}
  if(body==='singularity_core'){add(new THREE.SphereGeometry(.29,24,16),mat(0x05060a,.2,.08),root,[0,-.48,1.12]);add(new THREE.TorusGeometry(.36,.04,10,36),gold,root,[0,-.48,1.14])}
  if(body==='blue_shell'||body==='gold_shell')[-.64,.64].forEach(x=>add(new THREE.SphereGeometry(.25,18,12),body==='gold_shell'?gold:mat(0x2f6fb5),root,[x,-.33,.72]))
 }
 const back=appearance.back
 if(back){
  const group=new THREE.Group();group.position.set(0,-.45,-.72);root.add(group)
  if(back==='tool_pack')[-.55,.55].forEach(x=>add(new THREE.BoxGeometry(.42,1.03,.35),mat(0x514536,.55,.5),group,[x,0,0]))
  if(back==='jetpack')[-.58,.58].forEach(x=>{add(new THREE.CylinderGeometry(.25,.3,1.14,16),dark,group,[x,0,0]);add(new THREE.ConeGeometry(.19,.6,16),cyan,group,[x,-.82,0]).rotation.x=Math.PI})
  if(back==='mini_cape'){const cape=add(new THREE.ConeGeometry(1.15,1.8,22,1,true),mat(0x632f68,.15,.65),group,[0,-.28,-.05]);cape.rotation.x=Math.PI}
  if(back==='neon_wings'||back==='ion_wings')[-1,1].forEach(side=>{const wing=add(new THREE.ConeGeometry(.66,1.75,3),back==='ion_wings'?violet:cyan,group,[side*.92,.16,0]);wing.rotation.z=side*-.55;wing.rotation.y=side*.2})
 }
 const hand=appearance.hand
 if(hand){
  const tool=new THREE.Group();tool.position.set(1.47,-.72,.46);tool.rotation.z=-.18;root.add(tool)
  if(hand==='wrench'){add(new THREE.CylinderGeometry(.07,.09,1.04,12),bright,tool);add(new THREE.TorusGeometry(.18,.06,8,18,Math.PI*1.45),bright,tool,[0,.58,0])}
  if(hand==='data_pad'){const pad=add(new THREE.BoxGeometry(.57,.8,.08),dark,tool,[0,.1,0]);pad.rotation.z=.18;add(new THREE.PlaneGeometry(.42,.62),cyan,tool,[0,.1,.05]).rotation.z=.18}
  if(hand==='game_pad'){const pad=add(new THREE.BoxGeometry(.72,.4,.17),violet,tool,[0,.05,0]);pad.rotation.z=.2;[-.18,.18].forEach(x=>add(new THREE.SphereGeometry(.055,10,8),cyan,tool,[x,.05,.12]))}
  if(hand==='plasma_tool'){add(new THREE.CylinderGeometry(.07,.09,1.03,12),dark,tool);add(new THREE.ConeGeometry(.17,.5,18),violet,tool,[0,.74,0])}
 }
 const aura=appearance.aura
 if(aura){
  const material=aura==='star_aura'?gold:aura==='quantum_aura'?violet:cyan
  const ring=add(new THREE.TorusGeometry(1.72,.035,12,64),material,root);ring.rotation.x=Math.PI/2;ring.scale.y=.65
  if(aura==='quantum_aura')add(new THREE.TorusKnotGeometry(1.45,.018,80,8,2,3),material,root)
  if(aura==='star_aura')for(let i=0;i<7;i++){const a=i/7*Math.PI*2;add(new THREE.OctahedronGeometry(.1),material,root,[Math.cos(a)*1.55,Math.sin(a)*1.5,0])}
  if(aura==='pulse_aura')add(new THREE.TorusGeometry(1.36,.025,10,56),material,root).rotation.x=Math.PI/2
 }
}

export function addRoom3D(THREE,{scene,room,add,mat,dark,glow}){
 const group=new THREE.Group();group.position.z=-1.3;scene.add(group)
 const floor=add(new THREE.CircleGeometry(4.8,48),mat(0x0b1220,.35,.62),group,[0,-2.36,0],[1,1,1]);floor.rotation.x=-Math.PI/2
 const addScreen=(x,y,z,color=glow)=>{const frame=add(new THREE.BoxGeometry(1.45,.82,.08),dark,group,[x,y,z]);frame.rotation.y=x<0?.22:-.22;const screen=add(new THREE.PlaneGeometry(1.25,.63),color,group,[x,y,z+.05]);screen.rotation.y=frame.rotation.y;return screen}
 if(room==='workshop_bg'){[-2.5,2.5].forEach(x=>{add(new THREE.BoxGeometry(.22,3.8,.22),mat(0x6d4b35),group,[x,-.25,0]);for(let y=-1.6;y<1.8;y+=.75)add(new THREE.BoxGeometry(1.2,.09,.12),mat(0x8c765f),group,[x,y,.1])});addScreen(-2,1,-.1,mat(0xff9d43,.3,.2,0xff9d43))}
 if(room==='neon_city_bg'){for(let i=0;i<9;i++){const x=-4+i;const h=1.5+(i%4)*.55;add(new THREE.BoxGeometry(.7,h,.7),mat(i%2?0x182b57:0x261a4c),group,[x,-2.35+h/2,-1.2]);for(let y=-1.8;y<-1.8+h-.25;y+=.45)add(new THREE.BoxGeometry(.3,.08,.03),i%2?glow:mat(0xff4fd8,.25,.15,0xff4fd8),group,[x,y,-.82])}}
 if(room==='orbit_bg'){const planet=add(new THREE.SphereGeometry(.72,28,18),mat(0x345fc9,.15,.55),group,[2.7,1.55,-1]);const ring=add(new THREE.TorusGeometry(1.05,.035,10,48),mat(0x9ca8ff,.2,.25,0x516dff),group,[2.7,1.55,-1]);ring.rotation.x=1.25;planet.rotation.z=.2;for(let i=0;i<22;i++){const a=i*2.4;add(new THREE.SphereGeometry(.018+(i%3)*.008,6,5),mat(0xffffff,0,1,0xffffff),group,[Math.sin(a)*4,Math.cos(a*.7)*2.8,-1.7])}}
 if(room==='command_room_bg'||!room){add(new THREE.BoxGeometry(5.7,3.8,.12),mat(0x17243a),group,[0,-.1,-1.2]);addScreen(-1.8,.8,-1.05);addScreen(1.8,.8,-1.05);add(new THREE.TorusGeometry(1.15,.055,12,64),glow,group,[0,.15,-.95])}
 return {group,floor}
}

export function actionPose(action,t,parts,baseY){
 const {root,leftArm,rightArm,head,core}=parts,phase=t*.006
 root.position.y=baseY+Math.sin(phase*.55)*.045;root.rotation.z=0;root.scale.setScalar(1);leftArm.rotation.set(0,0,0);rightArm.rotation.set(0,0,0);head.rotation.set(0,0,0)
 if(action==='feed'){rightArm.rotation.z=-1.1+Math.sin(phase)*.18;head.rotation.x=.12}
 if(action==='clean'){leftArm.rotation.z=Math.sin(phase*2)*.75;rightArm.rotation.z=-Math.sin(phase*2)*.75}
 if(action==='sleep'){root.rotation.z=-.2;root.position.y=baseY-.22;head.rotation.z=-.12}
 if(action==='repair'){rightArm.rotation.z=-.8+Math.sin(phase*3)*.35}
 if(action==='charge'){core.scale.setScalar(1+Math.sin(phase*2)*.18)}
 if(action==='play'){leftArm.rotation.z=.7+Math.sin(phase*2)*.2;rightArm.rotation.z=-.7-Math.sin(phase*2)*.2}
 if(action==='train'){leftArm.rotation.z=Math.sin(phase*2)*1.05;rightArm.rotation.z=-Math.sin(phase*2)*1.05;root.position.y=baseY+Math.abs(Math.sin(phase*2))*.12}
 if(action==='learn'){head.rotation.y=Math.sin(phase)*.25;core.rotation.z=phase}
 if(action==='evolution'){root.rotation.y=phase*.65;root.scale.setScalar(.94+Math.sin(phase*2)*.08);core.scale.setScalar(1.2+Math.sin(phase*3)*.25)}
}
