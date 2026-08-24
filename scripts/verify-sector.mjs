import fs from 'node:fs'
import path from 'node:path'

const root = process.cwd()
const failures = []

function read(rel) {
  const full = path.join(root, rel)
  if (!fs.existsSync(full)) {
    failures.push(`missing: ${rel}`)
    return ''
  }
  return fs.readFileSync(full, 'utf8')
}

function expect(condition, message) {
  if (!condition) failures.push(message)
}

for (const name of ['koochooloo-hero-v2.webp', 'koochooloo-moods-v2.webp', 'rank-badges.webp', 'companion-room-v3.webp']) {
  const rel = `public/assets/sector/${name}`
  const full = path.join(root, rel)
  if (!fs.existsSync(full)) {
    failures.push(`missing: ${rel}`)
    continue
  }
  const body = fs.readFileSync(full)
  expect(body.length > 1024, `image too small: ${rel}`)
  expect(body.subarray(0, 4).toString('ascii') === 'RIFF', `invalid webp header: ${rel}`)
  expect(body.subarray(8, 12).toString('ascii') === 'WEBP', `invalid webp signature: ${rel}`)
}

for (const [dir, minimum] of [['stages-v3', 6], ['actions-v3', 8], ['equipment-v3', 28], ['rooms-v3', 4], ['missions-v3', 8], ['story-v3', 8], ['social-v3', 8], ['emotions-v3', 12]]) {
  const full = path.join(root, 'public/assets/sector', dir)
  if (!fs.existsSync(full)) {
    failures.push(`missing art pack: ${dir}`)
    continue
  }
  const files = fs.readdirSync(full).filter(name => name.endsWith('.webp'))
  expect(files.length >= minimum, `incomplete art pack: ${dir} (${files.length}/${minimum})`)
  for (const name of files) {
    const body = fs.readFileSync(path.join(full, name))
    expect(body.length > 4096, `art asset too small: ${dir}/${name}`)
    expect(body.subarray(0, 4).toString('ascii') === 'RIFF', `invalid art asset: ${dir}/${name}`)
  }
}

const splash = read('src/components/ui/SectorBootSplash.jsx')
const home = read('src/pages/HomePage.jsx')
const gate = read('src/App.jsx')
const celebration = read('src/components/ui/SectorCelebration.jsx')
const petPage = read('src/pages/SectorPetPage.jsx')
const bottomNav = read('src/components/ui/BottomNav.jsx')
const icons = read('src/components/ui/SectorIcon.jsx')
const skeleton = read('src/components/sector/SectorPetSkeleton.jsx')
const shareCard = read('src/components/sector/SectorShareCard.jsx')
const commandCenter = read('src/components/sector/SectorCommandCenter.jsx')
const workshop = read('src/components/sector/SectorRobotWorkshop.jsx')
const expansion = read('bot/services/sector_expansion.py')
const feedback = read('src/utils/feedback.js')
const styles = read('src/styles/global.css')
const manifestRaw = read('release/current.json')
const stickers = read('bot/modules/stickers.py')

expect(splash.includes('/assets/sector/koochooloo-hero-v2.webp'), 'splash must use production hero artwork')
expect(home.includes('/assets/sector/koochooloo-hero-v2.webp'), 'home must use production hero artwork')
expect(home.includes('/assets/sector/koochooloo-moods-v2.webp'), 'home must use production mood artwork')
expect(home.includes('/assets/sector/rank-badges.webp'), 'home must use production rank artwork')
expect(gate.includes('/assets/sector/koochooloo-hero-v2.webp'), 'membership gate must use production hero artwork')
expect(celebration.includes('/assets/sector/koochooloo-moods-v2.webp'), 'celebration must use production mood artwork')
expect(petPage.includes('sector-assets'), 'Sector Pet must expose the owned-assets collection')
expect(petPage.includes('دارایی‌های سکتور'), 'Sector asset collection title is missing')
for (const game of ['circuit','pulse','cipher','balance']) expect(petPage.includes(`'${game}'`), `missing Sector minigame: ${game}`)
expect(petPage.includes('قانون جایزه بازی‌ها'), 'Sector game rewards must be explained in the UI')
expect(petPage.includes('sector-social-target'), 'Sector social username input must use the mobile-sized control')
expect(petPage.includes('Countdown'), 'Sector timed progression must expose live countdowns')
expect(petPage.includes('story_daily_used'), 'Sector story must expose the daily move quota')
expect(styles.includes('.sector-workshop'), 'personal Sector workshop styling is missing')
expect(styles.includes('.wheel-win__star'), 'wheel prize star reveal is missing')
for(const marker of ['sector-onboarding','sector-mission-hq','sector-base','sector-forge','sector-live-event','sector-story-branches'])expect(commandCenter.includes(marker),`missing Sector expansion UI: ${marker}`)
for(const feature of ['upgrade_base','salvage','forge','claim_event','story_branch','tactical_battle'])expect(expansion.includes(feature),`missing Sector expansion logic: ${feature}`)
for(const feature of ['upgrade_gear','repair_gear','save_loadout','apply_loadout'])expect(expansion.includes(feature),`missing equipment progression logic: ${feature}`)
for(const marker of ['sector-id-card','sector-parts','power_score','onEquip','loadout'])expect(workshop.includes(marker),`missing component workshop UI: ${marker}`)
expect(!workshop.includes('sector-layerbot'), 'legacy CSS robot must be removed from the workshop')
expect(styles.includes('object-fit:contain'), 'shop and equipment artwork must stay inside its frame')
for (const item of ['scrap_cap','engineer_cap','commander_cap','captain_hat','elite_crown','welder_mask','round_goggles','mono_visor','combat_visor','patched_vest','utility_jacket','neon_armor','royal_chassis','singularity_core','blue_shell','gold_shell','tool_pack','jetpack','mini_cape','neon_wings','ion_wings','wrench','data_pad','game_pad','plasma_tool','pulse_aura','quantum_aura','star_aura']) expect(fs.existsSync(path.join(root,'public/assets/sector/equipment-v3',`${item}.webp`)), `missing equipment artwork: ${item}`)
for (const room of ['workshop_bg','neon_city_bg','orbit_bg','command_room_bg']) expect(fs.existsSync(path.join(root,'public/assets/sector/rooms-v3',`${room}.webp`)), `missing room artwork: ${room}`)
expect(styles.includes('.sector-assets__rail'), 'Sector assets gallery styling is missing')
expect(bottomNav.includes('SectorIcon'), 'bottom navigation must use the unified icon pack')
expect(icons.includes('const PATHS'), 'unified SVG icon pack is missing')
expect(petPage.includes('SectorPetSkeleton'), 'Sector Pet must use its graphical skeleton')
expect(petPage.includes('SectorShareCard'), 'Sector Pet must expose its share card')
expect(skeleton.includes('aria-busy="true"'), 'Sector skeleton must expose its loading state')
expect(shareCard.includes('اشتراک‌گذاری'), 'Sector share card is incomplete')
expect(feedback.includes('HapticFeedback'), 'Sector feedback must support Telegram haptics')
expect(!stickers.includes('mascot-emotions.webp'), 'sticker generator must not depend on corrupted webp sheet')

try {
  const manifest = JSON.parse(manifestRaw)
  expect(manifest.image === '/assets/sector/koochooloo-hero-v2.webp', 'release manifest must use production hero artwork')
  expect(Boolean(manifest.release_id), 'release manifest needs release_id')
  expect(Boolean(manifest.channel), 'release manifest needs channel')
} catch (error) {
  failures.push(`invalid release/current.json: ${error.message}`)
}

if (failures.length) {
  console.error('Sector verification failed:')
  for (const failure of failures) console.error(`- ${failure}`)
  process.exit(1)
}

console.log('Sector verification passed.')
