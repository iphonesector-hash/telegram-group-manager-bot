const RANKS=[
 {level:1,title:'Bronze Newbie',icon:'◆',color:'#a96d45'},
 {level:6,title:'Silver Explorer',icon:'✦',color:'#b9c6d8'},
 {level:12,title:'Gold Champion',icon:'★',color:'#ffd05b'},
 {level:18,title:'Diamond Master',icon:'◇',color:'#65dcff'},
 {level:24,title:'Galaxy Elite',icon:'✧',color:'#9b78ff'},
 {level:30,title:'Legend Sector',icon:'♛',color:'#ffb85c'},
]

export function rankFor(level){return [...RANKS].reverse().find(x=>Number(level||1)>=x.level)||RANKS[0]}

export default function SectorRankTrack({level=1}){
 const current=rankFor(level),index=RANKS.findIndex(x=>x.title===current.title),next=RANKS[index+1]
 const start=current.level,end=next?.level||current.level,progress=next?Math.max(0,Math.min(100,(Number(level)-start)/(end-start)*100)):100
 return <section className="sector-rank-track glass"><header><div><small>SECTOR RANKS</small><h3>مسیر رتبه تو</h3></div><b style={{color:current.color}}>{current.title}</b></header><div className="sector-rank-track__line"><i/><i style={{width:`${(index/(RANKS.length-1))*100+progress/(RANKS.length-1)}%`}}/>{RANKS.map((rank,i)=><div key={rank.title} className={`${i<index?'done ':''}${i===index?'current':''}`} style={{'--rank-color':rank.color}}><span>{rank.icon}</span><b>{rank.title}</b><small>Lv.{rank.level}</small></div>)}</div><footer>{next?<><span>مرحله بعد: <b>{next.title}</b></span><strong>{Math.max(0,next.level-Number(level))} سطح باقی مانده</strong></>:<strong>بالاترین رتبه فعال است</strong>}</footer></section>
}
