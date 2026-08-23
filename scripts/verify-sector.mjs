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

for (const name of ['koochooloo-hero-v2.webp', 'koochooloo-moods-v2.webp', 'rank-badges.webp']) {
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

const splash = read('src/components/ui/SectorBootSplash.jsx')
const home = read('src/pages/HomePage.jsx')
const gate = read('src/App.jsx')
const celebration = read('src/components/ui/SectorCelebration.jsx')
const manifestRaw = read('release/current.json')
const stickers = read('bot/modules/stickers.py')

expect(splash.includes('/assets/sector/koochooloo-hero-v2.webp'), 'splash must use production hero artwork')
expect(home.includes('/assets/sector/koochooloo-hero-v2.webp'), 'home must use production hero artwork')
expect(home.includes('/assets/sector/koochooloo-moods-v2.webp'), 'home must use production mood artwork')
expect(home.includes('/assets/sector/rank-badges.webp'), 'home must use production rank artwork')
expect(gate.includes('/assets/sector/koochooloo-hero-v2.webp'), 'membership gate must use production hero artwork')
expect(celebration.includes('/assets/sector/koochooloo-moods-v2.webp'), 'celebration must use production mood artwork')
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
