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

for (const name of ['brand-hero.svg', 'mascot-emotions.svg', 'rank-badges.svg']) {
  const rel = `public/assets/sector/${name}`
  const body = read(rel)
  expect(body.includes('<svg'), `invalid svg: ${rel}`)
}

const splash = read('src/components/ui/SectorBootSplash.jsx')
const home = read('src/pages/HomePage.jsx')
const gate = read('src/App.jsx')
const celebration = read('src/components/ui/SectorCelebration.jsx')
const manifestRaw = read('release/current.json')
const stickers = read('bot/modules/stickers.py')

expect(splash.includes('/assets/sector/brand-hero.svg'), 'splash must use brand-hero.svg')
expect(home.includes('/assets/sector/brand-hero.svg'), 'home hero must use brand-hero.svg')
expect(home.includes('/assets/sector/mascot-emotions.svg'), 'home mascot must use mascot-emotions.svg')
expect(home.includes('/assets/sector/rank-badges.svg'), 'home ranks must use rank-badges.svg')
expect(gate.includes('/assets/sector/brand-hero.svg'), 'membership gate must use brand-hero.svg')
expect(celebration.includes('/assets/sector/mascot-emotions.svg'), 'celebration must use mascot-emotions.svg')
expect(!stickers.includes('mascot-emotions.webp'), 'sticker generator must not depend on corrupted webp sheet')

try {
  const manifest = JSON.parse(manifestRaw)
  expect(String(manifest.image || '').endsWith('.svg'), 'release manifest image must use stable SVG artwork')
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
