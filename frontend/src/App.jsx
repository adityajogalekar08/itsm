import { useState } from "react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { BrowserRouter, Routes, Route, Link } from "react-router-dom"
import ChatWindow from "./components/ChatWindow"
import VoiceAgent from "./pages/VoiceAgent"
import "./App.css"

const queryClient = new QueryClient()

function ITSMPage() {
  const [sessionId] = useState(() => "session-" + Math.random().toString(36).substr(2, 9))

  return (
    <div className="app-container">
      <div className="app-header">
        <div className="header-left">
          <div className="agent-avatar">A</div>
          <div className="header-info">
            <h1>Alex</h1>
            <span className="status-dot"></span>
            <span className="status-text">IT Support Agent · Online</span>
          </div>
        </div>
        <Link to="/voice" className="nav-link">🎙️ Voice Agent</Link>
      </div>
      <ChatWindow sessionId={sessionId} />
    </div>
  )
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<ITSMPage />} />
          <Route path="/voice" element={<VoiceAgent />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}