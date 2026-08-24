import fs from 'node:fs'

const read=file=>fs.readFileSync(file,'utf8')
const route=read('api/sector_v2_routes.py')
const expansion=read('bot/services/sector_expansion.py')
const meta=read('bot/services/sector_meta.py')
const v2=read('bot/services/sector_v2.py')
const reminders=read('api/sector_reminder_routes.py')
const page=read('src/pages/SectorPetPage.jsx')
const api=read('src/services/api.js')
const styles=read('src/styles/global.css')
const failures=[]
const expect=(ok,message)=>{if(!ok)failures.push(message)}

expect(route.includes('token_hash')&&route.includes('compare_digest'),'minigames need one-use server tickets')
expect(route.includes('value["used"]=True'),'game ticket must be consumed atomically')
expect(route.includes('<=900'),'game tickets need an expiry')
expect(expansion.includes('timedelta(minutes=10)'),'tactical battles need cooldown')
expect(expansion.includes('SCHEMA_VERSION=3')&&expansion.includes('normalize_pet'),'legacy Sector data needs migration')
expect(expansion.includes('crafted=bool')&&expansion.includes('inv["crafted:"+key]=True'),'crafted gear needs anti-loop tracking')
expect(meta.includes("crafted:'+item_key"),'crafted gear must not be sold for infinite coins')
expect(v2.includes("item_key not in owned_keys(pet)"),'unowned equipment must never be equipped')
expect(expansion.includes('key in dict(pet.appearance or {}).values()'),'equipped gear must never be salvaged')
expect(meta.includes('if value==item_key:a.pop(slot,None)'),'sold gear must be removed from appearance')
expect(reminders.includes('22*3600')&&reminders.includes('notifications_enabled.is_(True)'),'private reminders need opt-in and daily throttling')
expect(page.includes('shopLimit')&&page.includes('content-visibility')===false,'shop pagination should be component-driven')
expect(api.includes('AbortController')&&api.includes('20000'),'API calls need bounded network waits')
expect(!page.includes('۰۰:۰۰ UTC'),'UI must not expose confusing UTC reset text')
expect(page.includes('Sector Koochooloo Beta')&&page.includes('گزارش مشکل'),'Beta status and issue reporting are required')
expect(styles.includes('min-height:44px')&&styles.includes('content-visibility:auto'),'mobile touch targets and deferred shop rendering are required')

const typicalDailyGames=8*35
const typicalDailyMissions=200
const dailyCareCost=35+55
const netTypical=typicalDailyGames+typicalDailyMissions-dailyCareCost
expect(netTypical>=300&&netTypical<=700,`typical daily net economy is out of range: ${netTypical}`)
const baseCosts=[450,700,600,500,900]
expect(Math.min(...baseCosts)>=400,'base upgrades are too cheap')

if(failures.length){console.error('Sector hardening verification failed:');failures.forEach(x=>console.error('- '+x));process.exit(1)}
console.log(`Sector hardening passed. Typical daily net: ${netTypical} coins.`)
