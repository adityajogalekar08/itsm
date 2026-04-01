import { useState, useEffect, useRef } from "react"
import { Link } from "react-router-dom"
import VoiceOrb from "../components/VoiceOrb"

const CUSTOMERS = [
  { phone: "+91-9876543210", name: "Rahul Sharma", vehicle: "2021 Maruti Suzuki Swift" },
  { phone: "+91-9845012345", name: "Priya Patel", vehicle: "2022 Hyundai Creta" },
  { phone: "+91-9901234567", name: "Amit Kumar", vehicle: "2023 Tata Nexon" },
  { phone: "+91-9123456789", name: "Sneha Reddy", vehicle: "2020 Honda City" }
]

export default function VoiceAgent() {
  const [selectedCustomer, setSelectedCustomer] = useState(null)
  const [callStatus, setCallStatus] = useState("idle") // idle, calling, active, ended
  const [sessionId, setSessionId] = useState(null)
  const [transcript, setTranscript] = useState([])
  const [isListening, setIsListening] = useState(false)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [appointment, setAppointment] = useState(null)
  const [callbackTime, setCallbackTime] = useState(null)
  const recognitionRef = useRef(null)
  const synthRef = useRef(window.speechSynthesis)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [transcript])

  const speak = (text, onEnd) => {
    synthRef.current.cancel()
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.rate = 1.0
    utterance.pitch = 1.1
    utterance.volume = 1

    // Pick a female voice if available
    const voices = synthRef.current.getVoices()
    const preferred = voices.find(v =>
      v.name.includes("Female") ||
      v.name.includes("Samantha") ||
      v.name.includes("Google UK English Female") ||
      v.name.includes("Microsoft Zira")
    )
    if (preferred) utterance.voice = preferred

    utterance.onstart = () => setIsSpeaking(true)
    utterance.onend = () => {
      setIsSpeaking(false)
      if (onEnd) onEnd()
    }
    synthRef.current.speak(utterance)
  }

  const startListening = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SpeechRecognition) {
      alert("Speech recognition not supported in this browser. Use Chrome.")
      return
    }

    const recognition = new SpeechRecognition()
    recognition.lang = "en-IN"
    recognition.interimResults = false
    recognition.maxAlternatives = 1
    recognitionRef.current = recognition

    recognition.onstart = () => setIsListening(true)
    recognition.onend = () => setIsListening(false)

    recognition.onresult = async (event) => {
      const userText = event.results[0][0].transcript
      setTranscript(prev => [...prev, { role: "user", content: userText }])
      await sendMessage(userText)
    }

    recognition.onerror = (e) => {
      setIsListening(false)
      console.error("Speech recognition error:", e.error)
    }

    recognition.start()
  }

  const startCall = async (customer) => {
    setSelectedCustomer(customer)
    setCallStatus("calling")
    setTranscript([])
    setAppointment(null)
    setCallbackTime(null)

    try {
      const res = await fetch("http://localhost:5000/voice/start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ customer_phone: customer.phone })
      })
      const data = await res.json()
      setSessionId(data.session_id)
      setCallStatus("active")
      setTranscript([{ role: "assistant", content: data.message }])
      speak(data.message, () => startListening())
    } catch (err) {
      console.error(err)
      setCallStatus("idle")
    }
  }

  const sendMessage = async (text) => {
    try {
      const res = await fetch("http://localhost:5000/voice/respond", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, message: text })
      })
      const data = await res.json()

      setTranscript(prev => [...prev, { role: "assistant", content: data.message }])

      if (data.appointment) setAppointment(data.appointment)
      if (data.callback_time) setCallbackTime(data.callback_time)

      speak(data.message, () => {
        if (data.session_status === "active") {
          startListening()
        }
      })
    } catch (err) {
      console.error(err)
    }
  }

  const endCall = async () => {
    synthRef.current.cancel()
    if (recognitionRef.current) recognitionRef.current.stop()

    await fetch("http://localhost:5000/voice/end", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId })
    })

    setCallStatus("ended")
    setIsListening(false)
    setIsSpeaking(false)
  }

  return (
    <div className="voice-page">
      <div className="voice-header">
        <div className="header-left">
          <div className="agent-avatar" style={{ background: "#e05c2a" }}>P</div>
          <div className="header-info">
            <h1>Priya</h1>
            <span className="status-dot"></span>
            <span className="status-text">AutoCare Voice Agent · Online</span>
          </div>
        </div>
        <Link to="/" className="nav-link">💬 IT Support</Link>
      </div>

      <div className="voice-body">
        {callStatus === "idle" && (
          <div className="customer-select">
            <h2>Select a customer to call</h2>
            <p className="subtitle">Simulating outbound call for service appointment</p>
            <div className="customer-cards">
              {CUSTOMERS.map((c) => (
                <div key={c.phone} className="customer-card" onClick={() => startCall(c)}>
                  <div className="customer-avatar">{c.name[0]}</div>
                  <div className="customer-info">
                    <strong>{c.name}</strong>
                    <span>{c.vehicle}</span>
                    <span>{c.phone}</span>
                  </div>
                  <div className="call-icon">📞</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {(callStatus === "calling" || callStatus === "active" || callStatus === "ended") && (
          <div className="call-screen">
            <div className="call-info">
              <div className="call-avatar">{selectedCustomer?.name[0]}</div>
              <h2>{selectedCustomer?.name}</h2>
              <p>{selectedCustomer?.vehicle}</p>
              <p className="call-status-text">
                {callStatus === "calling" && "Connecting..."}
                {callStatus === "active" && (isSpeaking ? "Priya is speaking..." : isListening ? "Listening..." : "Processing...")}
                {callStatus === "ended" && "Call Ended"}
              </p>
            </div>

            <VoiceOrb isSpeaking={isSpeaking} isListening={isListening} />

            <div className="transcript-box">
              {transcript.map((msg, idx) => (
                <div key={idx} className={`transcript-line ${msg.role}`}>
                  <span className="transcript-name">
                    {msg.role === "assistant" ? "Priya" : selectedCustomer?.name}
                  </span>
                  <span className="transcript-text">{msg.content}</span>
                </div>
              ))}
              <div ref={bottomRef} />
            </div>

            {appointment && (
              <div className="voice-badge green">
                ✅ Appointment Booked: {appointment}
              </div>
            )}
            {callbackTime && (
              <div className="voice-badge yellow">
                🕐 Callback Requested: {callbackTime}
              </div>
            )}

            <div className="call-controls">
              {callStatus === "active" && !isSpeaking && !isListening && (
                <button className="mic-button" onClick={startListening}>
                  🎙️ Speak
                </button>
              )}
              {callStatus !== "ended" && (
                <button className="end-button" onClick={endCall}>
                  📵 End Call
                </button>
              )}
              {callStatus === "ended" && (
                <button className="restart-button" onClick={() => setCallStatus("idle")}>
                  🔄 New Call
                </button>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}