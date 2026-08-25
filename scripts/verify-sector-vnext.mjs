import fs from 'node:fs'

const read = file => fs.readFileSync(file, 'utf8')
const failures = []
const expect = (ok, message) => { if (!ok) failures.push(message) }

const story = read('bot/services/sector_story.py')
const actions = read('api/sector_action_intent_routes.py')
const api = read('src/services/api.js')
const narrative = read('src/components/sector/SectorNarrativeHub.jsx')
const command = read('src/components/sector/SectorCommandCenter.jsx')
const emoji = read('bot/utils/animated_emoji.py')
const emojiLib = read('bot/modules/sector_emoji_library.py')
const main = read('bot/main.py')
const diagnostics = read('api/sector_diagnostics_routes.py')

const chapters = ['بیداری در مه آهنی','پایگاه خاموش','معادن کریستالی','شهر ربات‌های خاموش','مهاجمان نِبولا','اتحاد سکتورها','حافظه گمشده','هسته تاریک']
for (const chapter of chapters) expect(story.includes(chapter), `missing story chapter: ${chapter}`)

const storyActions = [...story.matchAll(/scene\([^\n]*?,\s*"([a-z_]+)"(?:,|\))/g)].map(m => m[1])
const routeBlock = (story.match(/ACTION_ROUTES=\{([^\n]+)\}/) || [,''])[1]
const routeActions = [...routeBlock.matchAll(/"([a-z_]+)"\s*:/g)].map(m => m[1])
for (const action of [...new Set(storyActions)]) expect(routeActions.includes(action), `story action has no route: ${action}`)

for (const action of ['train_ready','defense_ready','core_ready','boss_ready']) {
  expect(story.includes(`if action=="${action}"`) || story.includes(`elif action=="${action}"`), `smart composite guidance missing: ${action}`)
}
expect(story.includes('trained=any(x.action=="train" for x in actions)'), 'training must be based on a persisted train action')
expect(story.includes('created_at>=start'), 'story progress must be scoped to the current scene start')
expect(story.includes('"mission_complete"') && story.includes('story:scene_mission_baseline'), 'mission story objective needs a scene baseline')

for (const action of ['train','charge','repair','feed','clean','sleep','learn','play']) expect(actions.includes(`("${action}"`), `natural-language intent missing: ${action}`)
expect(actions.includes('story_advanced') && actions.includes('narrative'), 'smart actions must return fresh narrative state')
expect(actions.includes('session.commit()') && actions.includes('session.rollback()'), 'smart actions must be transactional')

expect(api.includes('/action-smart/') && api.includes('/talk-smart'), 'Mini App must use coherent smart action/chat routes')
expect(api.includes('sectorSnapshotCache.delete(key)'), 'mutations without narrative must invalidate Sector cache')
expect(api.includes('SECTOR_FAST_TTL = 700'), 'Sector cache must remain short-lived')
expect(api.includes('AbortController'), 'API calls must have bounded waits')

expect(narrative.includes("scene.ready?'بازکردن بخش بعدی'"), 'story CTA must advance when ready')
expect(narrative.includes('تمرین رزمی'), 'training story CTA must be explicit')
expect(narrative.includes('requirements.map'), 'story requirements must be visible individually')
expect(command.includes('همه سامانه‌ها') && command.includes('مرکز مأموریت'), 'command center user-facing labels must be Persian')

expect(emoji.includes('SECTOR_KOOCHOOLOO_EMOJI_KEY'), 'dedicated Koochooloo emoji key missing')
expect(emoji.includes('LEGACY_SECTOR_EMOJI_KEY'), 'legacy emoji fallback must be preserved')
expect(emoji.includes('dedicated or _read_ids'), 'dedicated emojis must override, not mix with legacy')
expect(!emojiLib.includes('reset_sector_emojis'), 'Koochooloo library must never require clearing old emojis')
expect(!emojiLib.includes('resetsectoremoji'), 'destructive emoji reset command must not exist')
expect(emojiLib.includes('_append_ids'), 'Koochooloo emojis must be append-only')

expect(main.includes('get_antispam_handlers'), 'antispam handlers must use their actual exported name')
expect(!main.includes('from bot.modules.antispam import get_handlers as get_antispam_handlers'), 'broken antispam import regression')
expect(diagnostics.includes('stack') && diagnostics.includes('message'), 'client diagnostics must preserve crash message and stack')

if (failures.length) {
  console.error('Sector vNext verification failed:')
  failures.forEach(x => console.error('- ' + x))
  process.exit(1)
}
console.log(`Sector vNext verification passed: ${chapters.length} chapters, ${new Set(storyActions).size} story actions checked.`)
