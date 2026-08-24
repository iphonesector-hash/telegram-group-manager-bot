import SectorIcon from '../ui/SectorIcon'

export default function SectorShareCard({pet,onShare}){
 const equipped=Object.values(pet.equipped||{}).filter(Boolean).slice(0,3)
 return <section className="sector-share-card"><div className="sector-share-card__copy"><small>SECTOR IDENTITY // ACTIVE</small><h3>{pet.name||'سکتور کوچولو'}</h3><p>سطح {pet.level||1} · {pet.visual_stage?.title||'Scrap Unit'}</p><div className="sector-share-card__chips">{equipped.length?equipped.map((x,i)=><span key={x.id||i}>{x.title||x.name||'تجهیزات'}</span>):<span>هسته‌ی استاندارد</span>}</div></div><button className="btn btn-primary sector-share-card__button" onClick={onShare}><SectorIcon name="share" size={17}/> اشتراک‌گذاری</button></section>
}
