import { useState } from "react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import ChatWindow from "./components/ChatWindow"
import "./App.css"

const queryClient = new QueryClient()

export default function App() {
  const [sessionId] = useState(() => "session-" + Math.random().toString(36).substr(2, 9))

  return (
    <QueryClientProvider client={queryClient}>
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
        </div>
        <ChatWindow sessionId={sessionId} />
      </div>
    </QueryClientProvider>
  )
}