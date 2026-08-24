import {useEffect,useRef,useState} from 'react'
import SectorIcon from '../ui/SectorIcon'
import {addEquipment3D} from './sector3dKit'

const PALETTE={scrap:{panel:0x27333e,accent:0xd9824b},patched:{panel:0x20384b,accent:0x3ccbe8},core:{panel:0x17334b,accent:0x38bde8},advanced:{panel:0x292a4d,accent:0x7775ff},elite:{panel:0x382747,accent:0xac72ff},mythic:{panel:0x43371f,accent:0xe8c75b}}
function webglAvailable(){try{const c=document.createElement('canvas');return Boolean(c.getContext('webgl2')||c.getContext('webgl'))}catch(_){return false}}
function autoQuality(){return navigator.connection?.saveData||(navigator.deviceMemory||4)<=2||(navigator.hardwareConcurrency||4)<=2?'low':'high'}
function initialQuality(){try{return localStorage.getItem('sector-3d-quality')||'auto'}catch(_){return'auto'}}

export default function SectorAvatar3D({pet,previewItem,compact=false,onReady,onFallback}){
 const host=useRef(null),controls=useRef({}),[fallback,setFallback]=useState(false),[retry,setRetry]=useState(0),[quality,setQuality]=useState(initialQuality),[expanded,setExpanded]=useState(false)
 const stage=pet?.visual_stage?.id||'scrap',appearance={...(pet?.appearance||{})}
 if(previewItem?.slot)appearance[previewItem.slot]=previewItem.id
 const appearanceKey=JSON.stringify(appearance),room=appearance.background||'command_room_bg',effectiveQuality=quality==='auto'?autoQuality():quality
 useEffect(()=>{
  if(!host.current||!webglAvailable()){setFallback(true);onFallback?.();return}
  let disposed=false,frame=0,observer,visibilityObserver,mixer
  const cleanups=[]
  Promise.all([import('three'),import('three/addons/loaders/GLTFLoader.js')]).then(([THREE,{GLTFLoader}])=>{
   if(disposed||!host.current)return
   const el=host.current,scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(31,1,.1,100);camera.position.set(0,.1,8)
   const low=effectiveQuality==='low',renderer=new THREE.WebGLRenderer({alpha:true,antialias:!low,powerPreference:low?'low-power':'high-performance'})
   renderer.setPixelRatio(Math.min(devicePixelRatio||1,low?1:1.5));renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.18;renderer.shadowMap.enabled=!low
   renderer.domElement.className='sector-3d__canvas';renderer.domElement.setAttribute('aria-label',`${pet?.name||'سکتور کوچولو'} سه‌بعدی؛ برای چرخاندن لمس کنید`);renderer.domElement.setAttribute('role','img');el.appendChild(renderer.domElement)
   const cfg=PALETTE[stage]||PALETTE.scrap,world=new THREE.Group(),avatar=new THREE.Group();world.add(avatar);scene.add(world)
   const mat=(color,metal=.72,rough=.28,emissive=0)=>new THREE.MeshStandardMaterial({color,metalness:metal,roughness:rough,emissive,emissiveIntensity:emissive?.28:0})
   const dark=mat(0x111925,.82,.3),glow=mat(cfg.accent,.28,.2,cfg.accent)
   const add=(geometry,material,parent=avatar,pos=[0,0,0],scale=[1,1,1])=>{const mesh=new THREE.Mesh(geometry,material);mesh.position.set(...pos);mesh.scale.set(...scale);mesh.castShadow=!low;mesh.receiveShadow=!low;parent.add(mesh);return mesh}
   // The room artwork belongs to the CSS layer behind the transparent canvas.
   // Duplicating it inside WebGL created the opaque black halo seen on mobile.
   scene.add(new THREE.HemisphereLight(0xd9edff,0x10131b,2.5));const key=new THREE.DirectionalLight(0xffffff,4.8);key.position.set(-3,5,5);key.castShadow=!low;scene.add(key);const fill=new THREE.DirectionalLight(0x7199ff,2);fill.position.set(4,1,4);scene.add(fill);const rim=new THREE.PointLight(cfg.accent,11,9);rim.position.set(2,1,-2);scene.add(rim)
   new GLTFLoader().load('/assets/sector/sector-unit.glb',gltf=>{
    if(disposed)return
    const model=gltf.scene,box=new THREE.Box3().setFromObject(model),size=box.getSize(new THREE.Vector3()),center=box.getCenter(new THREE.Vector3()),scale=3.75/Math.max(size.y,.001)
    model.scale.setScalar(scale);model.position.set(-center.x*scale,-2.13-box.min.y*scale,-center.z*scale)
    model.traverse(node=>{if(!node.isMesh)return;node.castShadow=!low;node.receiveShadow=!low;const materials=Array.isArray(node.material)?node.material:[node.material];materials.forEach(material=>{material.metalness=Math.max(.35,material.metalness||0);material.roughness=.3;if(material.color&&material.color.r+material.color.g+material.color.b<.55)material.color.setHex(cfg.panel);material.needsUpdate=true})})
    avatar.add(model);addEquipment3D(THREE,{root:avatar,appearance,add,mat,dark,glow,cfg})
    mixer=new THREE.AnimationMixer(model);const idle=gltf.animations.find(clip=>/idle/i.test(clip.name))||gltf.animations[0];if(idle)mixer.clipAction(idle).play()
    setFallback(false);onReady?.()
   },undefined,()=>{setFallback(true);onFallback?.()})
   let dragging=false,lastX=0,lastY=0,lastPinch=0,targetY=.12,currentY=.12,targetX=0,currentX=0,targetZoom=8;const pointers=new Map()
   const down=e=>{pointers.set(e.pointerId,[e.clientX,e.clientY]);dragging=pointers.size===1;lastX=e.clientX;lastY=e.clientY;renderer.domElement.setPointerCapture?.(e.pointerId)},move=e=>{if(!pointers.has(e.pointerId))return;pointers.set(e.pointerId,[e.clientX,e.clientY]);if(pointers.size===2){const [a,b]=[...pointers.values()],d=Math.hypot(a[0]-b[0],a[1]-b[1]);if(lastPinch)targetZoom=Math.max(6,Math.min(9,targetZoom-(d-lastPinch)*.018));lastPinch=d;return}if(!dragging)return;targetY+=(e.clientX-lastX)*.012;targetX=Math.max(-.2,Math.min(.2,targetX-(e.clientY-lastY)*.006));lastX=e.clientX;lastY=e.clientY},up=e=>{pointers.delete(e.pointerId);dragging=pointers.size===1;lastPinch=0},wheel=e=>{e.preventDefault();targetZoom=Math.max(6,Math.min(9,targetZoom+e.deltaY*.006))}
   renderer.domElement.addEventListener('pointerdown',down);renderer.domElement.addEventListener('pointermove',move);renderer.domElement.addEventListener('pointerup',up);renderer.domElement.addEventListener('pointercancel',up);renderer.domElement.addEventListener('wheel',wheel,{passive:false});cleanups.push(()=>{renderer.domElement.removeEventListener('pointerdown',down);renderer.domElement.removeEventListener('pointermove',move);renderer.domElement.removeEventListener('pointerup',up);renderer.domElement.removeEventListener('pointercancel',up);renderer.domElement.removeEventListener('wheel',wheel)})
   const contextLost=e=>{e.preventDefault();setFallback(true);onFallback?.()},contextRestored=()=>setRetry(v=>v+1);renderer.domElement.addEventListener('webglcontextlost',contextLost);renderer.domElement.addEventListener('webglcontextrestored',contextRestored);cleanups.push(()=>{renderer.domElement.removeEventListener('webglcontextlost',contextLost);renderer.domElement.removeEventListener('webglcontextrestored',contextRestored)})
   const resize=()=>{const w=el.clientWidth,h=el.clientHeight;if(!w||!h)return;renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix()};observer=new ResizeObserver(resize);observer.observe(el);resize()
   const clock=new THREE.Clock(),reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;let inView=true,lastFrame=0
   const tick=t=>{if(disposed||!inView||document.hidden)return;if(low&&t-lastFrame<32){frame=requestAnimationFrame(tick);return}lastFrame=t;const dt=Math.min(clock.getDelta(),.05);if(!reduced)mixer?.update(dt);currentY+=(targetY-currentY)*.1;currentX+=(targetX-currentX)*.1;avatar.rotation.y=currentY;avatar.rotation.x=currentX;camera.position.z+=(targetZoom-camera.position.z)*.08;if(!reduced)world.position.y=Math.sin(t/850)*.025;glow.emissiveIntensity=.28+(reduced?0:Math.sin(t/420)*.07);renderer.render(scene,camera);frame=requestAnimationFrame(tick)}
   const resume=()=>{cancelAnimationFrame(frame);clock.getDelta();if(inView&&!document.hidden&&!disposed)frame=requestAnimationFrame(tick)},visibilityChange=()=>resume();document.addEventListener('visibilitychange',visibilityChange);visibilityObserver=new IntersectionObserver(entries=>{inView=Boolean(entries[0]?.isIntersecting);resume()},{rootMargin:'80px'});visibilityObserver.observe(el);cleanups.push(()=>{document.removeEventListener('visibilitychange',visibilityChange);visibilityObserver?.disconnect()})
   controls.current={reset:()=>{targetY=.12;targetX=0;targetZoom=8},capture:()=>{renderer.render(scene,camera);renderer.domElement.toBlob(async blob=>{if(!blob)return;const file=new File([blob],`sector-${pet?.name||'pet'}.png`,{type:'image/png'});try{if(navigator.share&&navigator.canShare?.({files:[file]}))await navigator.share({files:[file],title:pet?.name||'سکتور کوچولو'});else{const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=file.name;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000)}}catch(_){}})}}
   resume();el._dispose=()=>{cancelAnimationFrame(frame);observer?.disconnect();cleanups.forEach(fn=>fn());scene.traverse(o=>{o.geometry?.dispose?.();const ms=Array.isArray(o.material)?o.material:[o.material];ms.filter(Boolean).forEach(m=>{m.map?.dispose?.();m.dispose?.()})});renderer.dispose();renderer.domElement.remove()}
  }).catch(()=>{setFallback(true);onFallback?.()})
  return()=>{disposed=true;cancelAnimationFrame(frame);host.current?._dispose?.();if(host.current)delete host.current._dispose}
 },[stage,appearanceKey,room,effectiveQuality,retry,onReady,onFallback,pet?.name])
 function changeQuality(value){setQuality(value);try{localStorage.setItem('sector-3d-quality',value)}catch(_){}}
 return <div ref={host} className={`sector-3d${compact?' sector-3d--compact':''}${expanded?' sector-3d--expanded':''}`}>
  {fallback?<button className="sector-3d__retry" onClick={()=>{setFallback(false);setRetry(v=>v+1)}}>تلاش دوباره برای 3D</button>:null}<span className="sector-3d__hint">بکش: چرخش · دو انگشت: زوم</span>
  <div className="sector-3d__tools" aria-label="ابزار نمای سه‌بعدی"><button onClick={()=>controls.current.reset?.()} aria-label="بازنشانی دوربین"><SectorIcon name="refresh" size={15}/></button><button onClick={()=>controls.current.capture?.()} aria-label="عکس‌برداری"><SectorIcon name="camera" size={15}/></button><button onClick={()=>setExpanded(v=>!v)} aria-label={expanded?'بستن تمام صفحه':'نمای تمام صفحه'}><SectorIcon name={expanded?'minimize':'maximize'} size={15}/></button><select value={quality} onChange={e=>changeQuality(e.target.value)} aria-label="کیفیت سه‌بعدی"><option value="auto">Auto</option><option value="high">High</option><option value="low">Low</option></select></div>
 </div>
}
