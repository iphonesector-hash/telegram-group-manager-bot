let audioContext

export function haptic(tg,kind='light') {
  try {
    if (kind==='success'||kind==='error') tg?.HapticFeedback?.notificationOccurred(kind)
    else tg?.HapticFeedback?.impactOccurred(kind)
  } catch (_) {}
}

export function playTone(kind='tap',enabled=true) {
  if (!enabled||typeof window==='undefined') return
  try {
    const AudioCtx=window.AudioContext||window.webkitAudioContext
    if (!AudioCtx) return
    audioContext=audioContext||new AudioCtx()
    if(audioContext.state==='suspended')audioContext.resume()
    const now=audioContext.currentTime,patterns={tap:[[420,0,.035,'sine']],success:[[540,0,.09,'sine'],[760,.055,.12,'sine']],buy:[[330,0,.09,'triangle'],[660,.07,.15,'sine']],equip:[[480,0,.06,'triangle'],[820,.045,.13,'sine']],memory:[[520,0,.08,'sine']],level:[[420,0,.12,'triangle'],[650,.09,.16,'sine'],[980,.2,.3,'sine']],evolution:[[380,0,.18,'triangle'],[720,.12,.24,'sine'],[1180,.28,.38,'sine']],error:[[190,0,.13,'sawtooth'],[145,.08,.16,'sawtooth']]}
    ;(patterns[kind]||patterns.tap).forEach(([frequency,delay,duration,type])=>{const osc=audioContext.createOscillator(),gain=audioContext.createGain(),start=now+delay;osc.type=type;osc.frequency.setValueAtTime(frequency,start);gain.gain.setValueAtTime(.0001,start);gain.gain.exponentialRampToValueAtTime(kind==='tap'?.025:.045,start+.008);gain.gain.exponentialRampToValueAtTime(.0001,start+duration);osc.connect(gain);gain.connect(audioContext.destination);osc.start(start);osc.stop(start+duration+.02)})
  } catch (_) {}
}

export function feedback(tg,kind='tap',enabled=true) {
  haptic(tg,kind==='error'?'error':kind==='success'?'success':kind==='evolution'?'heavy':'light')
  playTone(kind,enabled)
}
