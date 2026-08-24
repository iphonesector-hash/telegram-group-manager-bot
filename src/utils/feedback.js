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
    const now=audioContext.currentTime,osc=audioContext.createOscillator(),gain=audioContext.createGain()
    const notes={tap:[360,.035],success:[620,.09],buy:[440,.12],equip:[520,.08],evolution:[760,.24],error:[180,.1]}
    const [frequency,duration]=notes[kind]||notes.tap
    osc.type=kind==='error'?'sawtooth':'sine';osc.frequency.setValueAtTime(frequency,now)
    if(kind==='evolution')osc.frequency.exponentialRampToValueAtTime(1180,now+duration)
    gain.gain.setValueAtTime(.0001,now);gain.gain.exponentialRampToValueAtTime(.045,now+.008);gain.gain.exponentialRampToValueAtTime(.0001,now+duration)
    osc.connect(gain);gain.connect(audioContext.destination);osc.start(now);osc.stop(now+duration+.02)
  } catch (_) {}
}

export function feedback(tg,kind='tap',enabled=true) {
  haptic(tg,kind==='error'?'error':kind==='success'?'success':kind==='evolution'?'heavy':'light')
  playTone(kind,enabled)
}
