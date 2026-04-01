import { useState, useRef, useEffect } from "react"
import { useMutation } from "@tanstack/react-query"
import MessageBubble from "./MessageBubble"
import TicketCard from "./TicketCard"
import InputBar from "./InputBar"

const WELCOME_MESSAGE = {
  role: "assistant",
  content: "Hi there! I'm Alex, your IT Support Agent. 👋 How can I help you today?"
}

async function sendMessage({ sessionId, message }) {
  const response = await fetch("http://localhost:5000/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, message })
  })
  if (!response.ok) throw new Error("Failed to reach support agent")
  return response.json()
}

export default function ChatWindow({ sessionId }) {
  const [messages, setMessages] = useState([WELCOME_MESSAGE])
  const [ticket, setTicket] = useState(null)
  const bottomRef = useRef(null)

  const mutation = useMutation({
    mutationFn: sendMessage,
    onSuccess: (data) => {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.message }
      ])
      if (data.ticket) {
        setTicket(data.ticket)
      }
    },
    onError: () => {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Sorry, I'm having trouble connecting right now. Please try again in a moment."
        }
      ])
    }
  })

  const handleSend = (text) => {
    if (!text.trim()) return

    setMessages((prev) => [...prev, { role: "user", content: text }])

    mutation.mutate({ sessionId, message: text })
  }

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, ticket])

  return (
    <div className="chat-window">
      <div className="messages-container">
        {messages.map((msg, idx) => (
          <MessageBubble key={idx} role={msg.role} content={msg.content} />
        ))}
        {mutation.isPending && (
          <div className="typing-indicator">
            <span></span><span></span><span></span>
          </div>
        )}
        {ticket && <TicketCard ticket={ticket} />}
        <div ref={bottomRef} />
      </div>
      <InputBar onSend={handleSend} isLoading={mutation.isPending} />
    </div>
  )
}