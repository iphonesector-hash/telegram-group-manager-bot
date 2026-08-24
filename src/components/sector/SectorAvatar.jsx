import React from 'react'

const STAGE={
 scrap:{metal:'#756a62',panel:'#403833',accent:'#c1784c',rust:true},patched:{metal:'#b8c1ca',panel:'#354250',accent:'#55d8ff'},core:{metal:'#cbd5e1',panel:'#243850',accent:'#4fc7ff'},advanced:{metal:'#c9d0e8',panel:'#303457',accent:'#7c7bff'},elite:{metal:'#ded2ee',panel:'#432e5b',accent:'#b779ff'},mythic:{metal:'#fff0c5',panel:'#4a3b22',accent:'#ffe16b'}
}
const BODY={blue_shell:'#2f6fb5',gold_shell:'#cda63d',patched_vest:'#72533f',utility_jacket:'#41566d',officer_coat:'#243e6e',neon_armor:'#413671',royal_chassis:'#65426f',singularity_core:'#282433'}
const HEAD={scrap_cap:'#69523e',engineer_cap:'#d0a53d',commander_cap:'#2c477b',captain_hat:'#2d497e',elite_crown:'#e5ba45',halo_core:'#ffe16b'}

function Wearable({slot,id,accent}){
 if(!id)return null
 if(slot==='aura')return <><circle cx="180" cy="178" r="131" fill="none" stroke={id==='star_aura'?'#ffe16b':id==='quantum_aura'?'#b06fff':'#55d8ff'} strokeWidth="5" opacity=".22"/><circle cx="180" cy="178" r="112" fill="none" stroke={accent} strokeWidth="2" opacity=".18"/></>
 if(slot==='background')return <g opacity=".55">{id==='workshop_bg'?<><path d="M20 290H340M45 55V290M315 55V290" stroke="#7c4f32" strokeWidth="8"/><path d="M55 86H305M55 118H305" stroke="#6d7382" strokeWidth="4"/></>:id==='neon_city_bg'?<><path d="M28 285V145h48v140M91 285V92h52v193M157 285V126h55v159M229 285V72h72v213" fill="none" stroke="#4554a8" strokeWidth="8"/><path d="M102 120h25M244 101h35M173 155h22" stroke="#58e1ff" strokeWidth="5"/></>:id==='orbit_bg'?<><circle cx="281" cy="82" r="27" fill="#335bc4" opacity=".6"/><ellipse cx="281" cy="82" rx="47" ry="11" fill="none" stroke="#8f9fff" strokeWidth="4"/><circle cx="70" cy="83" r="5" fill="#fff"/><circle cx="315" cy="155" r="4" fill="#fff"/></>:<><path d="M40 62H320V290H40Z" fill="none" stroke="#38516d" strokeWidth="5"/><circle cx="180" cy="105" r="40" fill="none" stroke="#55d8ff" strokeWidth="4" opacity=".35"/></>}</g>
 if(slot==='back'){
  if(id==='tool_pack')return <g><rect x="91" y="206" width="43" height="79" rx="13" fill="#514536" stroke="#9b7a55" strokeWidth="4"/><rect x="226" y="206" width="43" height="79" rx="13" fill="#514536" stroke="#9b7a55" strokeWidth="4"/><path d="M107 224h12M241 224h12" stroke="#d4b176" strokeWidth="5"/></g>
  if(id==='mini_cape')return <path d="M116 207Q70 232 82 317L180 284L278 317Q290 232 244 207Q180 245 116 207Z" fill="#632f68" opacity=".88"/>
  if(id==='jetpack')return <><rect x="88" y="205" width="35" height="87" rx="12" fill="#30384c" stroke="#7b7fff" strokeWidth="4"/><rect x="237" y="205" width="35" height="87" rx="12" fill="#30384c" stroke="#7b7fff" strokeWidth="4"/><path d="M99 292l12 40 12-40M248 292l12 40 12-40" fill="#55d8ff" opacity=".65"/></>
  return <><path d="M123 213Q61 168 55 241Q89 238 137 276Z" fill={id==='ion_wings'?'#8c6cff':'#45c7ff'} opacity=".68"/><path d="M237 213q62-45 68 28-34-3-82 35z" fill={id==='ion_wings'?'#8c6cff':'#45c7ff'} opacity=".68"/></>
 }
 if(slot==='body'){const c=BODY[id]||'#33435d';return <><path d="M118 205H242L231 293Q180 314 129 293Z" fill={c} stroke={id.includes('gold')?'#ffe16b':id.includes('neon')?'#9b7dff':'#6f82a5'} strokeWidth="5"/><path d="M149 221H211L202 266H158Z" fill="#101722" opacity=".58"/>{id==='singularity_core'&&<><circle cx="180" cy="250" r="24" fill="#0b0c11" stroke="#ffe16b" strokeWidth="5"/><circle cx="180" cy="250" r="8" fill="#ffe16b"/></>}</>}
 if(slot==='face'){
  if(id==='welder_mask')return <><rect x="126" y="132" width="108" height="62" rx="14" fill="#342d29" stroke="#9d7655" strokeWidth="5"/><rect x="145" y="148" width="70" height="25" rx="7" fill="#07121a" stroke="#ffad45" strokeWidth="3"/></>
  if(id==='mono_visor')return <path d="M131 151Q180 132 229 151L220 174Q180 184 140 174Z" fill="#101522" stroke="#6bdcff" strokeWidth="5"/>
  return id==='round_goggles'?<><circle cx="154" cy="154" r="20" fill="none" stroke="#88ddff" strokeWidth="7"/><circle cx="206" cy="154" r="20" fill="none" stroke="#88ddff" strokeWidth="7"/></>:<rect x="129" y="139" width="102" height="37" rx="16" fill="#07111d" stroke={id==='combat_visor'?'#d16cff':'#55d8ff'} strokeWidth="5" opacity=".88"/>
 }
 if(slot==='head'){
  if(id==='halo_core')return <ellipse cx="180" cy="84" rx="61" ry="16" fill="none" stroke="#ffe16b" strokeWidth="7"/>
  if(id==='elite_crown')return <path d="M126 116l13-40 28 25 15-37 19 37 26-25 9 40z" fill="#ffd455" stroke="#ffab32" strokeWidth="4"/>
  return <><path d="M119 116Q180 75 241 116L230 133H130Z" fill={HEAD[id]||'#39547a'} stroke="#9eabba" strokeWidth="4"/>{id==='engineer_cap'&&<rect x="162" y="82" width="36" height="14" rx="5" fill="#222a33"/>}</>
 }
 if(slot==='hand'){
  if(id==='data_pad')return <g transform="translate(248 224) rotate(7)"><rect width="55" height="70" rx="10" fill="#182436" stroke="#59dfff" strokeWidth="4"/><path d="M10 18h35M10 29h27M10 40h31" stroke="#8a9fb5" strokeWidth="3"/></g>
  if(id==='wrench')return <g transform="translate(264 216) rotate(14)"><path d="M6 0l11 11-8 8 18 52-12 5-18-52-11-1 3-14z" fill="#aeb6c1" stroke="#5f6873" strokeWidth="3"/></g>
  return id==='game_pad'?<g transform="translate(247 225)"><rect width="61" height="37" rx="16" fill="#242b49" stroke="#917bff" strokeWidth="4"/><circle cx="18" cy="18" r="6" fill="#5fe6ff"/><path d="M39 13v11M34 18h11" stroke="#ff8fd8" strokeWidth="4"/></g>:<g transform="translate(265 214) rotate(12)"><rect width="13" height="79" rx="6" fill="#9aa4ae"/><circle cx="6" cy="0" r="12" fill={id==='plasma_tool'?'#b270ff':'#5fe5ff'}/></g>
 }
 return null
}

export default function SectorAvatar({pet,previewItem,compact=false}){
 const stage=pet?.visual_stage?.id||'scrap',cfg=STAGE[stage]||STAGE.scrap,appearance={...(pet?.appearance||{})}
 if(previewItem?.slot)appearance[previewItem.slot]=previewItem.id
 const mood=pet?.mood?.id||pet?.mood?.key||'happy', eye=mood.includes('sad')?'sad':mood.includes('angry')?'angry':mood.includes('sleep')?'sleep':mood.includes('love')?'love':'happy'
 const eyePath=eye==='sad'?['M148 160q10-7 20 0','M192 160q10-7 20 0']:eye==='angry'?['M147 164l21-8','M192 156l21 8']:eye==='sleep'?['M148 161h20','M192 161h20']:eye==='love'?['M147 160l8-8 8 8-8 8z','M192 160l8-8 8 8-8 8z']:['M148 157q10 10 20 0','M192 157q10 10 20 0']
 const room=appearance.background||'crystal_room'
 return <div className={`sector-room sector-room--${room} sector-stage--${stage}${compact?' sector-room--compact':''}`}>
  <div className="sector-room__light"/>
  <svg className="sector-avatar" viewBox="0 0 360 360" role="img" aria-label={`${pet?.name||'سکتور کوچولو'}، مرحله ${stage}`}>
   <defs>
    <linearGradient id="sa-metal" x1="0" y1="0" x2="1" y2="1"><stop stopColor="#ffffff"/><stop offset=".22" stopColor="#cbd3df"/><stop offset=".55" stopColor={cfg.metal}/><stop offset=".78" stopColor="#f5f7fb"/><stop offset="1" stopColor="#7d8796"/></linearGradient>
    <linearGradient id="sa-dark-metal" x1="0" x2="1"><stop stopColor="#111722"/><stop offset=".55" stopColor="#313b4a"/><stop offset="1" stopColor="#080b11"/></linearGradient>
    <radialGradient id="sa-glow"><stop stopColor="#fff"/><stop offset=".18" stopColor={cfg.accent}/><stop offset="1" stopColor={cfg.accent} stopOpacity="0"/></radialGradient>
    <filter id="sa-shadow"><feDropShadow dx="0" dy="8" stdDeviation="8" floodOpacity=".65"/></filter>
    <filter id="sa-bloom"><feGaussianBlur stdDeviation="4"/></filter>
   </defs>
   <Wearable slot="aura" id={appearance.aura} accent={cfg.accent}/>
   <circle cx="180" cy="180" r="122" fill="url(#sa-glow)" opacity={stage==='mythic'?'.3':'.15'} filter="url(#sa-bloom)"/>
   <ellipse cx="180" cy="325" rx="82" ry="16" fill="#000" opacity=".58"/>
   <g className="sector-avatar__float" filter="url(#sa-shadow)">
    <Wearable slot="back" id={appearance.back} accent={cfg.accent}/>
    <g>{/* articulated legs */}
     <rect x="132" y="274" width="37" height="43" rx="14" fill="url(#sa-metal)" stroke="#303846" strokeWidth="5"/><rect x="191" y="274" width="37" height="43" rx="14" fill="url(#sa-metal)" stroke="#303846" strokeWidth="5"/>
     <path d="M125 313h48l-5 22h-53q-8-13 10-22zM235 313h-48l5 22h53q8-13-10-22z" fill="url(#sa-dark-metal)" stroke="#707c8d" strokeWidth="4"/>
    </g>
    <g>{/* rounded core body */}
     <path d="M121 205Q180 180 239 205L247 271Q235 297 180 304Q125 297 113 271Z" fill="url(#sa-metal)" stroke="#242b35" strokeWidth="7"/>
     <path d="M132 215Q180 198 228 215L222 271Q180 289 138 271Z" fill={cfg.panel} stroke="#4a5565" strokeWidth="4"/>
     <circle cx="180" cy="250" r="29" fill="#121726" stroke="#7b56d9" strokeWidth="6"/>
     <path d="M180 225l17 19-17 29-17-29z" fill={cfg.accent} stroke="#e7fbff" strokeWidth="3"/>
     <circle cx="180" cy="250" r="37" fill="none" stroke={cfg.accent} strokeWidth="3" opacity=".42"/>
     <path d="M138 218l-12 53M222 218l12 53" stroke="#fff" strokeWidth="3" opacity=".35"/>
    </g>
    <g>{/* segmented arms */}
     <circle cx="112" cy="222" r="17" fill="url(#sa-dark-metal)" stroke="#6e7887" strokeWidth="4"/><rect x="88" y="225" width="31" height="62" rx="15" transform="rotate(10 88 225)" fill="url(#sa-metal)" stroke="#303846" strokeWidth="5"/>
     <circle cx="248" cy="222" r="17" fill="url(#sa-dark-metal)" stroke="#6e7887" strokeWidth="4"/><rect x="241" y="225" width="31" height="62" rx="15" transform="rotate(-10 241 225)" fill="url(#sa-metal)" stroke="#303846" strokeWidth="5"/>
     <circle cx="94" cy="286" r="13" fill="url(#sa-dark-metal)"/><circle cx="266" cy="286" r="13" fill="url(#sa-dark-metal)"/>
    </g>
    <g>{/* helmet and glass face */}
     <circle cx="102" cy="158" r="28" fill="url(#sa-dark-metal)" stroke="#697484" strokeWidth="5"/><circle cx="258" cy="158" r="28" fill="url(#sa-dark-metal)" stroke="#697484" strokeWidth="5"/>
     <rect x="91" y="92" width="178" height="124" rx="59" fill="url(#sa-metal)" stroke="#222a35" strokeWidth="8"/>
     <path d="M111 134Q180 104 249 134L244 184Q180 212 116 184Z" fill="#050913" stroke={cfg.accent} strokeWidth="4"/>
     <path d="M121 134Q180 115 239 134" fill="none" stroke="#fff" strokeWidth="5" opacity=".22"/>
     <path d={eyePath[0]} fill="none" stroke={eye==='love'?'#ff6dbd':cfg.accent} strokeWidth="10" strokeLinecap="round"/>
     <path d={eyePath[1]} fill="none" stroke={eye==='love'?'#ff6dbd':cfg.accent} strokeWidth="10" strokeLinecap="round"/>
     <path d="M129 103q51-28 102 0" fill="none" stroke="#fff" strokeWidth="4" opacity=".55"/>
     <path d="M180 91V65" stroke="#737e8d" strokeWidth="7"/><path d="M180 48l12 15-12 18-12-18z" fill={cfg.accent} stroke="#e8ffff" strokeWidth="3"/>
    </g>
    {cfg.rust&&<><circle cx="126" cy="116" r="8" fill="#8b5036" opacity=".72"/><path d="M115 245l18 7" stroke="#8b5036" strokeWidth="6"/></>}
    {stage==='advanced'&&<path d="M104 213L73 188M256 213l31-25" stroke="#7c7bff" strokeWidth="6" opacity=".7"/>}
    {stage==='elite'&&<path d="M102 216L63 181M258 216l39-35" stroke="#b779ff" strokeWidth="7" opacity=".75"/>}
    {stage==='mythic'&&<ellipse cx="180" cy="55" rx="49" ry="13" fill="none" stroke="#ffe16b" strokeWidth="6"/>}
    <Wearable slot="body" id={appearance.body} accent={cfg.accent}/><Wearable slot="face" id={appearance.face} accent={cfg.accent}/><Wearable slot="head" id={appearance.head} accent={cfg.accent}/><Wearable slot="hand" id={appearance.hand} accent={cfg.accent}/>
   </g>
  </svg>
  <div className="sector-room__stage"><span>{pet?.visual_stage?.title||'Sector Unit'}</span><i style={{background:cfg.accent}}/></div>
 </div>
}
