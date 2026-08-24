const PATHS = {
  home: '<path d="M3 11.5 12 4l9 7.5"/><path d="M5.5 10.5V20h13v-9.5M9 20v-6h6v6"/>',
  shop: '<path d="M4 9h16l-1 11H5L4 9Z"/><path d="M8 9V7a4 4 0 0 1 8 0v2"/>',
  wallet: '<path d="M3 6.5h15a2 2 0 0 1 2 2V19H5a2 2 0 0 1-2-2V6.5Z"/><path d="M3.5 7 16 3v3.5M15 12h5v4h-5a2 2 0 0 1 0-4Z"/>',
  games: '<path d="M8 9h8a5 5 0 0 1 4.7 6.7l-.7 2a2 2 0 0 1-3.3.8L14.5 16h-5l-2.2 2.5a2 2 0 0 1-3.3-.8l-.7-2A5 5 0 0 1 8 9Z"/><path d="M7 12v4M5 14h4M16.5 13.5h.01M18.5 15.5h.01"/>',
  profile: '<circle cx="12" cy="8" r="4"/><path d="M4.5 21a7.5 7.5 0 0 1 15 0"/>',
  whatsnew: '<path d="m12 3 1.5 5.5L19 10l-5.5 1.5L12 17l-1.5-5.5L5 10l5.5-1.5L12 3Z"/><path d="m19 16 .7 2.3L22 19l-2.3.7L19 22l-.7-2.3L16 19l2.3-.7L19 16Z"/>',
  admin: '<path d="m4 7 4 4 4-7 4 7 4-4-1.5 12h-13L4 7Z"/><path d="M6 15h12"/>',
  sectorpet: '<rect x="4" y="6" width="16" height="14" rx="5"/><path d="M9 6V3m6 3V3M8 12h.01M16 12h.01M9 16h6"/>',
  care: '<path d="M12 21s-8-4.5-8-11a4 4 0 0 1 7-2.7L12 8.5l1-1.2A4 4 0 0 1 20 10c0 6.5-8 11-8 11Z"/>',
  growth: '<path d="M12 21V10M12 15c-5 0-7-3-7-7 4 0 7 2 7 6M12 12c4 0 7-2 7-6-4 0-7 2-7 6Z"/>',
  season: '<circle cx="12" cy="12" r="8"/><path d="M12 2v3m0 14v3M2 12h3m14 0h3M5 5l2 2m10 10 2 2m0-14-2 2M7 17l-2 2"/>',
  social: '<circle cx="9" cy="9" r="3"/><circle cx="17" cy="8" r="2.5"/><path d="M3 20a6 6 0 0 1 12 0M14 14a5 5 0 0 1 7 4.5"/>',
  memories: '<path d="M6 4h11a2 2 0 0 1 2 2v14H8a3 3 0 0 1-3-3V5a1 1 0 0 1 1-1Z"/><path d="M8 4v16M11 9h5m-5 4h5"/>',
  talk: '<path d="M4 5h16v12H9l-5 4V5Z"/><path d="M8 10h8m-8 3h5"/>',
  energy: '<path d="m13 2-8 12h7l-1 8 8-12h-7l1-8Z"/>', happiness:'<circle cx="12" cy="12" r="9"/><path d="M8 10h.01M16 10h.01M8 14c1 3 7 3 8 0"/>',
  hunger: '<path d="M7 3v7a3 3 0 0 1-3 3V3m3 4H4m3 6v8M16 3v18m0-18c5 3 5 9 0 11"/>',
  cleanliness: '<path d="M12 3S6 10 6 15a6 6 0 0 0 12 0c0-5-6-12-6-12Z"/><path d="M9 16c.5 1.5 1.5 2 3 2"/>',
  health: '<path d="M4 12h4l2-5 4 10 2-5h4"/>', knowledge:'<path d="M4 5h7a3 3 0 0 1 3 3v12a3 3 0 0 0-3-3H4V5Zm16 0h-3a3 3 0 0 0-3 3v12a3 3 0 0 1 3-3h3V5Z"/>',
  charge:'<path d="M8 2h8v3h2v16H6V5h2V2Z"/><path d="m13 8-3 5h3l-2 4 4-6h-3l1-3Z"/>', play:'<path d="M8 5v14l11-7L8 5Z"/>', train:'<path d="M4 9v6m16-6v6M7 7v10m10-10v10M4 12h16"/>', learn:'<path d="M3 6.5 12 3l9 3.5-9 3.5-9-3.5Z"/><path d="M6 9v6c3 3 9 3 12 0V9M21 7v7"/>', repair:'<path d="M14 6a5 5 0 0 0-6 6L3 17l4 4 5-5a5 5 0 0 0 6-6l-3 3-4-4 3-3Z"/>', feed:'<path d="M5 4h14l-1 17H6L5 4Z"/><path d="M8 8h8m-6 4h4"/>', clean:'<path d="m14 4 6 6M5 20l9-9-3-3-9 9 3 3Zm7-2h8"/>', sleep:'<path d="M5 16h7M7 12h6l-6 7h6M15 7h5l-5 5h5"/>',
  coin:'<circle cx="12" cy="12" r="9"/><path d="M14.5 8.5c-4-2-6 1-3 2.5s1 4.5-3 2.5M12 6v12"/>', lock:'<rect x="5" y="10" width="14" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/>', buy:'<path d="M3 5h2l2 11h10l2-8H6M9 20h.01M17 20h.01"/>', equip:'<path d="m5 12 4 4L19 6"/>', share:'<circle cx="18" cy="5" r="2"/><circle cx="6" cy="12" r="2"/><circle cx="18" cy="19" r="2"/><path d="m8 11 8-5m-8 7 8 5"/>', gift:'<path d="M4 10h16v11H4V10Zm-1-4h18v4H3V6Z"/><path d="M12 6v15M12 6c-1-4-6-4-5 0m5 0c1-4 6-4 5 0"/>', visit:'<path d="m3 11 9-8 9 8M5 10v11h14V10M9 21v-7h6v7"/>', battle:'<path d="m5 4 15 15M19 4 4 19M14 4l6 6M4 14l6 6"/>', send:'<path d="m3 11 18-8-7 18-3-7-8-3Zm8 3 4-5"/>', refresh:'<path d="M20 11a8 8 0 1 0-2 5.5M20 5v6h-6"/>', camera:'<path d="M4 7h4l1.5-2h5L16 7h4v12H4V7Z"/><circle cx="12" cy="13" r="3.5"/>', maximize:'<path d="M8 3H3v5m13-5h5v5M8 21H3v-5m13 5h5v-5"/>', minimize:'<path d="M3 8h5V3m13 5h-5V3M3 16h5v5m13-5h-5v5"/>', sound:'<path d="M4 10v4h4l5 4V6l-5 4H4Zm13-2a6 6 0 0 1 0 8m2-11a10 10 0 0 1 0 14"/>', mute:'<path d="M4 10v4h4l5 4V6l-5 4H4Zm12 0 5 5m0-5-5 5"/>'
}

export default function SectorIcon({name,size=20,label,className=''}) {
  const body=PATHS[name]||PATHS.sectorpet
  return <svg className={'sector-icon '+className} width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" role={label?'img':'presentation'} aria-label={label} aria-hidden={label?undefined:true} dangerouslySetInnerHTML={{__html:body}}/>
}
