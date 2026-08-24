import {useEffect,useRef,useState} from 'react'
import SectorIcon from '../ui/SectorIcon'
import {actionPose,addEquipment3D,addRoom3D} from './sector3dKit'

const PALETTE={scrap:{metal:0x766a62,panel:0x403833,accent:0xc97b4d},patched:{metal:0xb8c1ca,panel:0x354250,accent:0x55d8ff},core:{metal:0xcbd5e1,panel:0x243850,accent:0x4fc7ff},advanced:{metal:0xc9d0e8,panel:0x303457,accent:0x7c7bff},elite:{metal:0xded2ee,panel:0x432e5b,accent:0xb779ff},mythic:{metal:0xfff0c5,panel:0x4a3b22,accent:0xffe16b}}
const BODY={blue_shell:0x2f6fb5,gold_shell:0xcda63d,patched_vest:0x72533f,utility_jacket:0x41566d,officer_coat:0x243e6e,neon_armor:0x413671,royal_chassis:0x65426f,singularity_core:0x282433}
const ROOM_SCREEN={workshop_bg:'/assets/sector/missions-v3/craft.webp',neon_city_bg:'/assets/sector/social-v3/duel.webp',orbit_bg:'/assets/sector/story-v3/awakening.webp',command_room_bg:'/assets/sector/missions-v3/boss.webp'}
function webglAvailable(){try{const c=document.createElement('canvas');return Boolean(c.getContext('webgl2')||c.getContext('webgl'))}catch(_){return false}}
function autoQuality(){return navigator.connection?.saveData||(navigator.deviceMemory||4)<=2||(navigator.hardwareConcurrency||4)<=2?'low':'high'}
function initialQuality(){try{return localStorage.getItem('sector-3d-quality')||'auto'}catch(_){return'auto'}}

export default function SectorAvatar3D({pet,previewItem,compact=false,action='',onReady,onFallback}){
 const host=useRef(null),controls=useRef({}),actionRef=useRef(action),[fallback,setFallback]=useState(false),[retry,setRetry]=useState(0),[quality,setQuality]=useState(initialQuality),[expanded,setExpanded]=useState(false)
 actionRef.current=action
 const stage=pet?.visual_stage?.id||'scrap',mood=pet?.mood?.id||pet?.mood?.key||'happy',appearance={...(pet?.appearance||{})}
 if(previewItem?.slot)appearance[previewItem.slot]=previewItem.id
 const appearanceKey=JSON.stringify(appearance),room=appearance.background||'command_room_bg',effectiveQuality=quality==='auto'?autoQuality():quality
 useEffect(()=>{
  if(!host.current||!webglAvailable()){setFallback(true);onFallback?.();return}
  let disposed=false,frame=0,observer,visibilityObserver,cleanupPointers=()=>{},cleanupVisibility=()=>{},cleanupContext=()=>{}
  import('three').then(THREE=>{
   if(disposed||!host.current)return
   const el=host.current,scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(34,1,.1,100);camera.position.set(0,.25,7.4)
   const low=effectiveQuality==='low',renderer=new THREE.WebGLRenderer({alpha:true,antialias:!low,powerPreference:low?'low-power':'high-performance',preserveDrawingBuffer:true})
   renderer.setPixelRatio(Math.min(devicePixelRatio||1,low?1:1.65));renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.18
   renderer.domElement.className='sector-3d__canvas';renderer.domElement.setAttribute('aria-label',`${pet?.name||'سکتور کوچولو'} سه‌بعدی؛ برای چرخاندن لمس کنید`);renderer.domElement.setAttribute('role','img');el.appendChild(renderer.domElement)
   const cfg=PALETTE[stage]||PALETTE.scrap,root=new THREE.Group();root.position.y=-.2;scene.add(root)
   const mat=(color,metal=.72,rough=.25,emissive=0)=>new THREE.MeshStandardMaterial({color,metalness:metal,roughness:rough,emissive,emissiveIntensity:emissive?.32:0})
   const metal=mat(cfg.metal),dark=mat(0x151b25,.85,.2),panel=mat(BODY[appearance.body]||cfg.panel,.7,.28),glow=mat(cfg.accent,.28,.18,cfg.accent),glass=new THREE.MeshPhysicalMaterial({color:0x07101e,metalness:.25,roughness:.08,transmission:low?0:.12,clearcoat:low?.3:1})
   const add=(geometry,material,parent=root,pos=[0,0,0],scale=[1,1,1])=>{const mesh=new THREE.Mesh(geometry,material);mesh.position.set(...pos);mesh.scale.set(...scale);mesh.castShadow=!low;mesh.receiveShadow=!low;parent.add(mesh);return mesh}
   const roomParts=addRoom3D(THREE,{scene,room,add,mat,dark,glow})
   if(!low&&ROOM_SCREEN[room])new THREE.TextureLoader().load(ROOM_SCREEN[room],texture=>{if(disposed){texture.dispose();return}texture.colorSpace=THREE.SRGBColorSpace;add(new THREE.PlaneGeometry(1.5,1),new THREE.MeshBasicMaterial({map:texture,toneMapped:false}),roomParts.group,[0,.35,-1.1])})
   const body=add(new THREE.SphereGeometry(1,low?20:32,low?14:22),metal,root,[0,-.55,0],[1.12,1.15,.8]);add(new THREE.SphereGeometry(.82,low?18:28,low?12:18),panel,root,[0,-.55,.68],[1,.9,.18]);const core=add(new THREE.OctahedronGeometry(.3,0),glow,root,[0,-.48,1.02],[.72,1,.5])
   const head=add(new THREE.SphereGeometry(1.15,low?22:36,low?16:24),metal,root,[0,1.05,0],[1.15,.85,.85]);add(new THREE.SphereGeometry(.91,low?20:32,low?12:20),glass,root,[0,1.03,.68],[1.15,.62,.17])
   const eyeShape=mood.includes('love')?new THREE.OctahedronGeometry(.12,0):new THREE.SphereGeometry(.12,low?10:16,8),eyeY=mood.includes('sad')?1.08:mood.includes('angry')?1.16:1.1
   ;[-.38,.38].forEach(x=>add(eyeShape,glow,root,[x,eyeY,.91],[1,mood.includes('sleep')?.18:1,.45]));add(new THREE.CylinderGeometry(.04,.04,.43,10),dark,root,[0,2.02,0]);add(new THREE.OctahedronGeometry(.15,0),glow,root,[0,2.27,0])
   const limb=x=>{const arm=new THREE.Group();arm.position.set(x,-.18,0);root.add(arm);add(new THREE.SphereGeometry(.23,14,10),dark,arm);const lower=add(new THREE.CapsuleGeometry(.18,.72,5,10),metal,arm,[x<0?-.12:.12,-.48,0]);lower.rotation.z=x<0?-.18:.18;return arm}
   const leftArm=limb(-1.12),rightArm=limb(1.12);[-.48,.48].forEach(x=>{add(new THREE.CapsuleGeometry(.25,.48,5,10),metal,root,[x,-1.55,0]);add(new THREE.SphereGeometry(.3,14,10),dark,root,[x,-2,.13],[1.25,.55,1.5])})
   if(stage==='scrap'){add(new THREE.TorusGeometry(.17,.04,8,18),mat(0x8b5036,.2,.7),root,[-.58,1.38,.75]);body.rotation.z=.025}
   if(stage==='elite'||stage==='mythic'){const halo=add(new THREE.TorusGeometry(.72,.045,10,40),glow,root,[0,2.42,0],[1,.35,1]);halo.rotation.x=Math.PI/2}
   addEquipment3D(THREE,{root,appearance,add,mat,dark,glow,cfg});add(new THREE.CylinderGeometry(1.85,2.1,.16,low?28:48),mat(0x101827,.55,.34),scene,[0,-2.28,0]);const floorRing=add(new THREE.TorusGeometry(1.58,.025,10,low?36:64),glow,scene,[0,-2.18,0],[1,.45,1]);floorRing.rotation.x=Math.PI/2
   scene.add(new THREE.HemisphereLight(0xb9e6ff,0x100c24,1.9));const key=new THREE.DirectionalLight(0xffffff,low?2.2:3);key.position.set(-3,5,5);scene.add(key);const rim=new THREE.PointLight(cfg.accent,low?8:13,8);rim.position.set(2,1,-2);scene.add(rim)
   let dragging=false,lastX=0,lastY=0,lastPinch=0,targetY=.18,currentY=.18,targetX=0,currentX=0,targetZoom=7.4;const pointers=new Map()
   const down=e=>{pointers.set(e.pointerId,[e.clientX,e.clientY]);dragging=pointers.size===1;lastX=e.clientX;lastY=e.clientY;renderer.domElement.setPointerCapture?.(e.pointerId)},move=e=>{if(!pointers.has(e.pointerId))return;pointers.set(e.pointerId,[e.clientX,e.clientY]);if(pointers.size===2){const [a,b]=[...pointers.values()],distance=Math.hypot(a[0]-b[0],a[1]-b[1]);if(lastPinch)targetZoom=Math.max(5.6,Math.min(9,targetZoom-(distance-lastPinch)*.018));lastPinch=distance;return}lastPinch=0;if(!dragging)return;targetY+=(e.clientX-lastX)*.012;targetX=Math.max(-.25,Math.min(.25,targetX-(e.clientY-lastY)*.006));lastX=e.clientX;lastY=e.clientY},up=e=>{pointers.delete(e.pointerId);dragging=pointers.size===1;lastPinch=0},wheel=e=>{e.preventDefault();targetZoom=Math.max(5.6,Math.min(9,targetZoom+e.deltaY*.006))}
   renderer.domElement.addEventListener('pointerdown',down);renderer.domElement.addEventListener('pointermove',move);renderer.domElement.addEventListener('pointerup',up);renderer.domElement.addEventListener('pointercancel',up);renderer.domElement.addEventListener('wheel',wheel,{passive:false});cleanupPointers=()=>{renderer.domElement.removeEventListener('pointerdown',down);renderer.domElement.removeEventListener('pointermove',move);renderer.domElement.removeEventListener('pointerup',up);renderer.domElement.removeEventListener('pointercancel',up);renderer.domElement.removeEventListener('wheel',wheel)}
   const contextLost=e=>{e.preventDefault();setFallback(true);onFallback?.()},contextRestored=()=>setRetry(v=>v+1);renderer.domElement.addEventListener('webglcontextlost',contextLost);renderer.domElement.addEventListener('webglcontextrestored',contextRestored);cleanupContext=()=>{renderer.domElement.removeEventListener('webglcontextlost',contextLost);renderer.domElement.removeEventListener('webglcontextrestored',contextRestored)}
   const resize=()=>{const w=el.clientWidth,h=el.clientHeight;if(!w||!h)return;renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix()};observer=new ResizeObserver(resize);observer.observe(el);resize()
   const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;let inView=true,lastFrame=0
   const tick=t=>{if(disposed||!inView||document.hidden)return;if(low&&t-lastFrame<32){frame=requestAnimationFrame(tick);return}lastFrame=t;currentY+=(targetY-currentY)*.1;currentX+=(targetX-currentX)*.1;root.rotation.y=currentY;root.rotation.x=currentX;camera.position.z+=(targetZoom-camera.position.z)*.08;actionPose(actionRef.current,t,{root,leftArm,rightArm,head,core},-.2);if(!actionRef.current&&reduced)root.position.y=-.2;glow.emissiveIntensity=.25+(reduced?0:Math.sin(t/420)*.08);renderer.render(scene,camera);frame=requestAnimationFrame(tick)}
   const resume=()=>{cancelAnimationFrame(frame);if(inView&&!document.hidden&&!disposed)frame=requestAnimationFrame(tick)},visibilityChange=()=>resume();document.addEventListener('visibilitychange',visibilityChange);visibilityObserver=new IntersectionObserver(entries=>{inView=Boolean(entries[0]?.isIntersecting);resume()},{rootMargin:'80px'});visibilityObserver.observe(el);cleanupVisibility=()=>{document.removeEventListener('visibilitychange',visibilityChange);visibilityObserver?.disconnect()}
   controls.current={reset:()=>{targetY=.18;targetX=0;targetZoom=7.4},capture:()=>renderer.domElement.toBlob(async blob=>{if(!blob)return;const file=new File([blob],`sector-${pet?.name||'pet'}.png`,{type:'image/png'});try{if(navigator.share&&navigator.canShare?.({files:[file]}))await navigator.share({files:[file],title:pet?.name||'سکتور کوچولو'});else{const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=file.name;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000)}}catch(_){}})}
   setFallback(false);resume();onReady?.();el._dispose=()=>{cancelAnimationFrame(frame);observer?.disconnect();cleanupPointers();cleanupVisibility();cleanupContext();scene.traverse(o=>{o.geometry?.dispose?.();const materials=Array.isArray(o.material)?o.material:[o.material];materials.filter(Boolean).forEach(m=>{m.map?.dispose?.();m.dispose?.()})});renderer.dispose();renderer.domElement.remove()}
  }).catch(()=>{setFallback(true);onFallback?.()})
  return()=>{disposed=true;cancelAnimationFrame(frame);host.current?._dispose?.();if(host.current)delete host.current._dispose}
 },[stage,mood,appearanceKey,room,effectiveQuality,retry,onReady,onFallback,pet?.name])
 function changeQuality(value){setQuality(value);try{localStorage.setItem('sector-3d-quality',value)}catch(_){}}
 return <div ref={host} className={`sector-3d${compact?' sector-3d--compact':''}${expanded?' sector-3d--expanded':''}`}>
  {fallback?<button className="sector-3d__retry" onClick={()=>{setFallback(false);setRetry(v=>v+1)}}>تلاش دوباره برای 3D</button>:null}<span className="sector-3d__hint">بکش: چرخش · دو انگشت: زوم</span>
  <div className="sector-3d__tools" aria-label="ابزار نمای سه‌بعدی"><button onClick={()=>controls.current.reset?.()} aria-label="بازنشانی دوربین"><SectorIcon name="refresh" size={15}/></button><button onClick={()=>controls.current.capture?.()} aria-label="عکس‌برداری"><SectorIcon name="camera" size={15}/></button><button onClick={()=>setExpanded(v=>!v)} aria-label={expanded?'بستن تمام صفحه':'نمای تمام صفحه'}><SectorIcon name={expanded?'minimize':'maximize'} size={15}/></button><select value={quality} onChange={e=>changeQuality(e.target.value)} aria-label="کیفیت سه‌بعدی"><option value="auto">Auto</option><option value="high">High</option><option value="low">Low</option></select></div>
 </div>
}
