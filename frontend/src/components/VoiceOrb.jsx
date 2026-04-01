export default function VoiceOrb({ isSpeaking, isListening }) {
  const getOrbState = () => {
    if (isSpeaking) return "speaking"
    if (isListening) return "listening"
    return "idle"
  }

  return (
    <div className={`orb-container ${getOrbState()}`}>
      <div className="orb-ring orb-ring-3"></div>
      <div className="orb-ring orb-ring-2"></div>
      <div className="orb-ring orb-ring-1"></div>
      <div className="orb-core">
        {isSpeaking && <span className="orb-icon">🔊</span>}
        {isListening && <span className="orb-icon">🎙️</span>}
        {!isSpeaking && !isListening && <span className="orb-icon">⏸️</span>}
      </div>
    </div>
  )
}