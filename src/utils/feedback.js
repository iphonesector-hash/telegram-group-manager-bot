let audioContext
let lastToneAt=0

export function haptic(tg,kind='light') {
  try {
    const settings=JSON.parse(localStorage.getItem('sector-ui-settings')||'{}')
    if(settings.haptics===false)return
    if (kind==='success'||kind==='error') tg?.HapticFeedback?.notificationOccurred(kind)
    else tg?.HapticFeedback?.impactOccurred(kind)
  } catch (_) {}
}

export function playTone(kind='tap',enabled=true) {
  if (!enabled||typeof window==='undefined') return
  try {
    const settings=JSON.parse(localStorage.getItem('sector-ui-settings')||'{}')
    if(settings.sound===false)return
    const mode=settings.soundMode||'full',volume=Math.max(.2,Math.min(1,Number(settings.soundVolume??.8)))
    if(mode==='calm'&&['tap','memory'].includes(kind)&&Date.now()-lastToneAt<180)return
    lastToneAt=Date.now()
    const AudioCtx=window.AudioContext||window.webkitAudioContext
    if (!AudioCtx) return
    audioContext=audioContext||new AudioCtx()
    if(audioContext.state==='suspended')audioContext.resume()
    const now=audioContext.currentTime,patterns={tap:[[420,0,.035,'sine']],success:[[540,0,.09,'sine'],[760,.055,.12,'sine']],story:[[310,0,.13,'triangle'],[520,.1,.16,'sine'],[830,.24,.28,'sine']],alert:[[220,0,.09,'sawtooth'],[180,.13,.1,'sawtooth'],[260,.27,.14,'triangle']],buy:[[330,0,.09,'triangle'],[660,.07,.15,'sine']],equip:[[480,0,.06,'triangle'],[820,.045,.13,'sine']],charge:[[180,0,.08,'sawtooth'],[360,.07,.12,'triangle'],[720,.16,.16,'sine']],repair:[[220,0,.045,'square'],[280,.07,.045,'square'],[620,.14,.12,'sine']],feed:[[310,0,.07,'sine'],[430,.06,.1,'triangle']],clean:[[660,0,.06,'sine'],[880,.05,.1,'sine']],sleep:[[420,0,.12,'sine'],[300,.09,.2,'sine']],play:[[520,0,.07,'triangle'],[740,.06,.11,'sine']],train:[[260,0,.06,'square'],[390,.06,.09,'triangle']],learn:[[500,0,.08,'sine'],[620,.08,.12,'sine']],memory:[[520,0,.08,'sine']],level:[[420,0,.12,'triangle'],[650,.09,.16,'sine'],[980,.2,.3,'sine']],evolution:[[380,0,.18,'triangle'],[720,.12,.24,'sine'],[1180,.28,.38,'sine']],error:[[190,0,.13,'sawtooth'],[145,.08,.16,'sawtooth']]}
    const extras={mission:[[360,0,.08,'triangle'],[610,.07,.13,'sine']],reward:[[520,0,.08,'sine'],[780,.06,.13,'sine'],[1040,.15,.18,'triangle']],unlock:[[330,0,.1,'triangle'],[660,.08,.18,'sine'],[990,.2,.22,'sine']],message:[[640,0,.06,'sine'],[820,.05,.09,'sine']],battle:[[150,0,.07,'sawtooth'],[260,.06,.1,'triangle'],[520,.13,.14,'square']],timer:[[880,0,.04,'sine']]}
    const notes=extras[kind]||patterns[kind]||patterns.tap,selected=mode==='calm'&&notes.length>1?[notes[notes.length-1]]:notes
    ;selected.forEach(([frequency,delay,duration,type])=>{const osc=audioContext.createOscillator(),gain=audioContext.createGain(),start=now+delay;osc.type=type;osc.frequency.setValueAtTime(frequency,start);gain.gain.setValueAtTime(.0001,start);gain.gain.exponentialRampToValueAtTime((kind==='tap'?.025:.045)*volume,start+.008);gain.gain.exponentialRampToValueAtTime(.0001,start+duration);osc.connect(gain);gain.connect(audioContext.destination);osc.start(start);osc.stop(start+duration+.02)})
  } catch (_) {}
}

export function feedback(tg,kind='tap',enabled=true) {
  haptic(tg,kind==='error'||kind==='alert'?'error':kind==='success'?'success':kind==='evolution'||kind==='story'?'heavy':'light')
  playTone(kind,enabled)
}
