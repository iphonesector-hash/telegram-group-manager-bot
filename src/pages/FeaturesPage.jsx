import { useAppContext } from '../App'
import SectorIcon from '../components/ui/SectorIcon'

var FEATURES = [
  {icon:'sectorpet',tone:'cyan',title:'دستیار هوشمند',desc:'پرسش و پاسخ فارسی با Sector AI',action:'tools'},
  {icon:'shield',tone:'red',title:'مدیریت گروه',desc:'اخطار، بن، میوت و مدیریت اعضا',action:'group'},
  {icon:'lock',tone:'violet',title:'قفل‌های گروه',desc:'لینک، رسانه، فوروارد، منشن و ضداسپم',action:'group'},
  {icon:'group',tone:'green',title:'خوش‌آمد و قوانین',desc:'تنظیم پیام ورود و قوانین هر گروه',action:'group'},
  {icon:'weather',tone:'cyan',title:'آب‌وهوا و ابزارها',desc:'هواشناسی، ترجمه، ماشین‌حساب و تبدیل واحد',action:'tools'},
  {icon:'games',tone:'violet',title:'سرگرمی و مسابقه',desc:'چیستان، حدس پرچم، جوایز و بازی‌ها',action:'games'},
  {icon:'wallet',tone:'gold',title:'بانک SectorLand',desc:'واریز، برداشت، وام و تراکنش‌ها',action:'wallet'},
  {icon:'support',tone:'green',title:'پشتیبانی و جوایز',desc:'دریافت جایزه‌های کانفیگ و پروکسی',action:'support'},
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
    if (item.action === 'games') return ctx.navigate('games')
    if (item.action === 'tools') return ctx.navigate('tools')
    if (item.action === 'group') return openTelegram('https://t.me/iSectorlandbot?startgroup=true')
  }
  return (
    <div className="page fade-up">
      <section className="glass visual-hero"><div className="visual-hero__core"><SectorIcon name="features" size={34}/></div><div><small>SECTOR SYSTEMS</small><h2>مرکز امکانات</h2><p>ابزارهای شخصی همین‌جا اجرا می‌شوند؛ فرمان‌های مدیریتی با دسترسی امن داخل گروه باز می‌شوند.</p></div></section>
      <div className="visual-grid">
        {FEATURES.map(function(item){return <button key={item.title} onClick={function(){run(item)}} className={'glass visual-card visual-card--'+item.tone}><span className="visual-card__icon"><SectorIcon name={item.icon} size={29}/><i/></span><b>{item.title}</b><small>{item.desc}</small><em>ورود به سامانه ‹</em></button>})}
      </div>
    </div>
  )
}
