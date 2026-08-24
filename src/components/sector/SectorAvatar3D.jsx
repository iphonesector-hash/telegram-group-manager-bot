import {useEffect,useRef,useState} from 'react'

const PALETTE={
 scrap:{metal:0x766a62,panel:0x403833,accent:0xc97b4d},patched:{metal:0xb8c1ca,panel:0x354250,accent:0x55d8ff},core:{metal:0xcbd5e1,panel:0x243850,accent:0x4fc7ff},advanced:{metal:0xc9d0e8,panel:0x303457,accent:0x7c7bff},elite:{metal:0xded2ee,panel:0x432e5b,accent:0xb779ff},mythic:{metal:0xfff0c5,panel:0x4a3b22,accent:0xffe16b}
}
const BODY={blue_shell:0x2f6fb5,gold_shell:0xcda63d,patched_vest:0x72533f,utility_jacket:0x41566d,officer_coat:0x243e6e,neon_armor:0x413671,royal_chassis:0x65426f,singularity_core:0x282433}

function webglAvailable(){try{const c=document.createElement('canvas');return Boolean(c.getContext('webgl2')||c.getContext('webgl'))}catch(_){return false}}

export default function SectorAvatar3D({pet,previewItem,compact=false,onReady}){
 const host=useRef(null),[fallback,setFallback]=useState(false)
 const stage=pet?.visual_stage?.id||'scrap',mood=pet?.mood?.id||pet?.mood?.key||'happy'
 const appearance={...(pet?.appearance||{})};if(previewItem?.slot)appearance[previewItem.slot]=previewItem.id
 const appearanceKey=JSON.stringify(appearance)

 useEffect(()=>{
  if(!host.current||!webglAvailable()){setFallback(true);return}
  let disposed=false,frame=0,observer,visibilityObserver,cleanupPointers=()=>{},cleanupVisibility=()=>{}
  import('three').then(THREE=>{
   if(disposed||!host.current)return
   const el=host.current,scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(34,1,.1,100)
   camera.position.set(0,.25,7.4)
   const renderer=new THREE.WebGLRenderer({alpha:true,antialias:devicePixelRatio<2,powerPreference:'high-performance'})
   renderer.setPixelRatio(Math.min(devicePixelRatio||1,1.65));renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.18
   renderer.domElement.className='sector-3d__canvas';renderer.domElement.setAttribute('aria-label',`${pet?.name||'سکتور کوچولو'} سه‌بعدی؛ برای چرخاندن لمس کنید`);renderer.domElement.setAttribute('role','img');el.appendChild(renderer.domElement)
   const cfg=PALETTE[stage]||PALETTE.scrap,root=new THREE.Group();root.position.y=-.2;scene.add(root)
   const mat=(color,metal=.72,rough=.25,emissive=0)=>new THREE.MeshStandardMaterial({color,metalness:metal,roughness:rough,emissive,emissiveIntensity:emissive?.32:0})
   const metal=mat(cfg.metal),dark=mat(0x151b25,.85,.2),panel=mat(BODY[appearance.body]||cfg.panel,.7,.28),glow=mat(cfg.accent,.28,.18,cfg.accent),glass=new THREE.MeshPhysicalMaterial({color:0x07101e,metalness:.25,roughness:.08,transmission:.12,clearcoat:1})
   const add=(geometry,material,parent=root,pos=[0,0,0],scale=[1,1,1])=>{const mesh=new THREE.Mesh(geometry,material);mesh.position.set(...pos);mesh.scale.set(...scale);mesh.castShadow=true;mesh.receiveShadow=true;parent.add(mesh);return mesh}
   const body=add(new THREE.SphereGeometry(1,32,22),metal,root,[0,-.55,0],[1.12,1.15,.8]);add(new THREE.SphereGeometry(.82,28,18),panel,root,[0,-.55,.68],[1,.9,.18]);add(new THREE.OctahedronGeometry(.3,0),glow,root,[0,-.48,1.02],[.72,1,.5])
   const head=add(new THREE.SphereGeometry(1.15,36,24),metal,root,[0,1.05,0],[1.15,.85,.85]);add(new THREE.SphereGeometry(.91,32,20),glass,root,[0,1.03,.68],[1.15,.62,.17])
   const eyeShape=mood.includes('love')?new THREE.OctahedronGeometry(.12,0):new THREE.SphereGeometry(.12,16,10)
   const eyeY=mood.includes('sad')?1.08:mood.includes('angry')?1.16:1.1
   ;[-.38,.38].forEach(x=>add(eyeShape,glow,root,[x,eyeY,.91],[1,mood.includes('sleep')?.18:1,.45]))
   add(new THREE.CylinderGeometry(.04,.04,.43,12),dark,root,[0,2.02,0]);add(new THREE.OctahedronGeometry(.15,0),glow,root,[0,2.27,0])
   const limb=(x)=>{const arm=new THREE.Group();arm.position.set(x,-.18,0);root.add(arm);add(new THREE.SphereGeometry(.23,18,12),dark,arm);const lower=add(new THREE.CapsuleGeometry(.18,.72,7,14),metal,arm,[x<0?-.12:.12,-.48,0]);lower.rotation.z=x<0?-.18:.18;return arm}
   limb(-1.12);limb(1.12)
   ;[-.48,.48].forEach(x=>{add(new THREE.CapsuleGeometry(.25,.48,7,14),metal,root,[x,-1.55,0]);add(new THREE.SphereGeometry(.3,18,12),dark,root,[x,-2,.13],[1.25,.55,1.5])})
   if(stage==='scrap'){add(new THREE.TorusGeometry(.17,.04,8,18),mat(0x8b5036,.2,.7),root,[-.58,1.38,.75]);body.rotation.z=.025}
   if(stage==='elite'||stage==='mythic')add(new THREE.TorusGeometry(.72,.045,10,40),glow,root,[0,2.42,0],[1,.35,1]).rotation.x=Math.PI/2
   if(appearance.head){const crown=add(new THREE.ConeGeometry(.72,.48,appearance.head==='elite_crown'?5:24),mat(appearance.head==='elite_crown'?0xffd455:cfg.accent),root,[0,2.02,0]);crown.rotation.y=.3}
   if(appearance.back){const back=new THREE.Group();back.position.set(0,-.45,-.72);root.add(back);[-.72,.72].forEach(x=>{const wing=add(new THREE.BoxGeometry(.58,1.25,.12),appearance.back==='jetpack'?dark:glow,back,[x,0,0]);wing.rotation.z=x<0?-.38:.38})}
   if(appearance.hand){const tool=add(new THREE.CylinderGeometry(.07,.07,1.15,12),dark,root,[1.47,-.7,.45]);tool.rotation.z=-.18;add(new THREE.SphereGeometry(.15,14,10),glow,root,[1.58,-.14,.45])}
   if(appearance.aura){const aura=add(new THREE.TorusGeometry(1.72,.025,12,64),glow,root);aura.rotation.x=Math.PI/2;aura.scale.y=.65}
   const floor=add(new THREE.CylinderGeometry(1.85,2.1,.16,48),mat(0x101827,.55,.34),scene,[0,-2.28,0]);add(new THREE.TorusGeometry(1.58,.025,10,64),glow,scene,[0,-2.18,0],[1,.45,1]).rotation.x=Math.PI/2
   scene.add(new THREE.HemisphereLight(0xb9e6ff,0x100c24,1.9));const key=new THREE.DirectionalLight(0xffffff,3);key.position.set(-3,5,5);scene.add(key);const rim=new THREE.PointLight(cfg.accent,13,8);rim.position.set(2,1,-2);scene.add(rim)
   let dragging=false,lastX=0,targetY=.18,currentY=.18,targetX=0,currentX=0
   const down=e=>{dragging=true;lastX=e.clientX;renderer.domElement.setPointerCapture?.(e.pointerId)}
   const move=e=>{if(!dragging)return;targetY+=(e.clientX-lastX)*.012;targetX=Math.max(-.25,Math.min(.25,targetX-(e.clientY-(renderer.domElement._lastY||e.clientY))*.006));lastX=e.clientX;renderer.domElement._lastY=e.clientY}
   const up=()=>{dragging=false;renderer.domElement._lastY=null}
   renderer.domElement.addEventListener('pointerdown',down);renderer.domElement.addEventListener('pointermove',move);renderer.domElement.addEventListener('pointerup',up);renderer.domElement.addEventListener('pointercancel',up)
   cleanupPointers=()=>{renderer.domElement.removeEventListener('pointerdown',down);renderer.domElement.removeEventListener('pointermove',move);renderer.domElement.removeEventListener('pointerup',up);renderer.domElement.removeEventListener('pointercancel',up)}
   const resize=()=>{const w=el.clientWidth,h=el.clientHeight;if(!w||!h)return;renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix()};observer=new ResizeObserver(resize);observer.observe(el);resize()
   const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches,start=performance.now();let inView=true
   const tick=t=>{if(disposed||!inView||document.hidden)return;currentY+=(targetY-currentY)*.1;currentX+=(targetX-currentX)*.1;root.rotation.y=currentY;root.rotation.x=currentX;root.position.y=-.2+(reduced?0:Math.sin((t-start)/900)*.045);glow.emissiveIntensity=.25+(reduced?0:Math.sin((t-start)/420)*.08);renderer.render(scene,camera);frame=requestAnimationFrame(tick)}
   const resume=()=>{cancelAnimationFrame(frame);if(inView&&!document.hidden&&!disposed)frame=requestAnimationFrame(tick)}
   const visibilityChange=()=>resume();document.addEventListener('visibilitychange',visibilityChange)
   visibilityObserver=new IntersectionObserver(entries=>{inView=Boolean(entries[0]?.isIntersecting);resume()},{rootMargin:'80px'});visibilityObserver.observe(el)
   cleanupVisibility=()=>{document.removeEventListener('visibilitychange',visibilityChange);visibilityObserver?.disconnect()}
   resume();onReady?.()
   el._dispose=()=>{cancelAnimationFrame(frame);observer?.disconnect();cleanupPointers();cleanupVisibility();scene.traverse(o=>{o.geometry?.dispose?.();if(Array.isArray(o.material))o.material.forEach(m=>m.dispose());else o.material?.dispose?.()});renderer.dispose();renderer.domElement.remove()}
  }).catch(()=>setFallback(true))
  return()=>{disposed=true;cancelAnimationFrame(frame);host.current?._dispose?.();if(host.current)delete host.current._dispose}
 },[stage,mood,appearanceKey,compact,onReady,pet?.name])
 if(fallback)return null
 return <div ref={host} className={`sector-3d${compact?' sector-3d--compact':''}`}><span className="sector-3d__hint">برای چرخش لمس کن</span></div>
}
