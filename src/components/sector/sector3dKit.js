const ITEM_ALIAS={halo_core:'star_aura',officer_coat:'utility_jacket'}
const SLOT_LAYOUT={head:{position:[0,1.48,.68],size:[1.55,1.55]},face:{position:[0,.92,.76],size:[1.42,1.42]},body:{position:[0,-.08,.68],size:[1.72,1.72]},back:{position:[0,-.02,-.52],size:[2.15,2.15]},hand:{position:[1.02,-.72,.68],size:[.94,.94]}}

function cutoutTexture(THREE,url,onLoad){
 new THREE.ImageLoader().load(url,image=>{
  const canvas=document.createElement('canvas'),size=512;canvas.width=size;canvas.height=size
  const ctx=canvas.getContext('2d',{willReadFrequently:true}),crop=Math.round(image.width*.035);ctx.drawImage(image,crop,crop,image.width-crop*2,image.height-crop*2,0,0,size,size)
  const data=ctx.getImageData(0,0,size,size),p=data.data,corners=[[6,6],[size-7,6],[6,size-7],[size-7,size-7]],bg=[0,0,0]
  corners.forEach(([x,y])=>{const i=(y*size+x)*4;bg[0]+=p[i]/4;bg[1]+=p[i+1]/4;bg[2]+=p[i+2]/4})
  for(let i=0;i<p.length;i+=4){const d=Math.hypot(p[i]-bg[0],p[i+1]-bg[1],p[i+2]-bg[2]),lum=Math.max(p[i],p[i+1],p[i+2]);p[i+3]=Math.max(0,Math.min(255,(d-12)*8,(lum-5)*9))}
  ctx.putImageData(data,0,0);const texture=new THREE.CanvasTexture(canvas);texture.colorSpace=THREE.SRGBColorSpace;texture.anisotropy=4;onLoad(texture)
 })
}

export function addEquipment3D(THREE,{root,appearance,add,mat}){
 Object.entries(SLOT_LAYOUT).forEach(([slot,layout])=>{const id=appearance[slot];if(!id)return;const asset=ITEM_ALIAS[id]||id
  cutoutTexture(THREE,`/assets/sector/equipment-v3/${asset}.webp`,texture=>{const material=new THREE.MeshBasicMaterial({map:texture,transparent:true,alphaTest:.08,side:THREE.DoubleSide,depthWrite:false,toneMapped:false}),plane=add(new THREE.PlaneGeometry(...layout.size),material,root,layout.position);plane.renderOrder=slot==='back'?0:4;plane.userData.equipmentSlot=slot})
 })
 const aura=appearance.aura
 if(aura){const color=aura==='star_aura'?0xffd45c:aura==='quantum_aura'?0xa971ff:0x50dfff,material=mat(color,.2,.18,color),ring=add(new THREE.TorusGeometry(1.38,.025,10,56),material,root,[0,-.15,.05]);ring.rotation.x=Math.PI/2;ring.scale.y=.58;if(aura!=='pulse_aura'){const top=add(new THREE.TorusGeometry(1.12,.018,10,56),material,root,[0,.75,.05]);top.rotation.x=Math.PI/2;top.scale.y=.42}}
}
