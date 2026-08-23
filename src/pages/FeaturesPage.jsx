import { useAppContext } from '../App'

var FEATURES = [
  {icon:'🤖',title:'دستیار هوشمند',desc:'پرسش و پاسخ فارسی با Sector AI',action:'bot'},
  {icon:'🛡️',title:'مدیریت گروه',desc:'اخطار، بن، میوت و مدیریت اعضا',action:'group'},
  {icon:'🔒',title:'قفل‌های گروه',desc:'لینک، رسانه، فوروارد، منشن و ضداسپم',action:'group'},
  {icon:'👋',title:'خوش‌آمد و قوانین',desc:'تنظیم پیام ورود و قوانین هر گروه',action:'group'},
  {icon:'🌤️',title:'آب‌وهوا و ابزارها',desc:'هواشناسی، ترجمه، ماشین‌حساب و تبدیل واحد',action:'bot'},
  {icon:'🎭',title:'سرگرمی ربات',desc:'فال حافظ، جوک، چیستان، تاس و دوئل',action:'bot'},
  {icon:'🏦',title:'بانک SectorLand',desc:'واریز، برداشت، وام و تراکنش‌ها',action:'wallet'},
  {icon:'🎫',title:'پشتیبانی و جوایز',desc:'دریافت جایزه‌های کانفیگ و پروکسی',action:'support'},
]

export default function FeaturesPage() {
  var ctx = useAppContext()
  function openTelegram(url) {
    if (ctx.tg && ctx.tg.openTelegramLink) ctx.tg.openTelegramLink(url)
    else window.location.assign(url)
  }
  function run(item) {
    if (item.action === 'wallet') return ctx.navigate('wallet')
    if (item.action === 'support') return ctx.navigate('support')
    if (item.action === 'group') return openTelegram('https://t.me/iSectorlandbot?startgroup=true')
    openTelegram('https://t.me/iSectorlandbot?start=features')
  }
  return (
    <div className="page fade-up">
      <div className="glass" style={{padding:16,marginBottom:16,lineHeight:1.8,fontSize:12,color:'var(--muted)'}}>امکانات شخصی داخل Mini App اجرا می‌شوند؛ ابزارهای مدیریتی با حفظ دسترسی ادمین مستقیماً در گروه باز می‌شوند.</div>
      <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:10}}>
        {FEATURES.map(function(item){return <button key={item.title} onClick={function(){run(item)}} className="glass" style={{padding:15,minHeight:145,border:'1px solid var(--border)',color:'inherit',textAlign:'right',cursor:'pointer'}}><div style={{fontSize:30}}>{item.icon}</div><div style={{fontWeight:800,fontSize:14,marginTop:8}}>{item.title}</div><div style={{fontSize:10,color:'var(--muted)',lineHeight:1.7,marginTop:4}}>{item.desc}</div></button>})}
      </div>
    </div>
  )
}
