import { useState } from "react"

export default function InputBar({ onSend, isLoading }) {
  const [text, setText] = useState("")

  const handleSend = () => {
    if (!text.trim() || isLoading) return
    onSend(text.trim())
    setText("")
  }

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="input-bar">
      <textarea
        className="input-textarea"
        placeholder="Describe your IT issue..."
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={handleKeyDown}
        rows={1}
        disabled={isLoading}
      />
      <button
        className={`send-button ${isLoading ? "loading" : ""}`}
        onClick={handleSend}
        disabled={isLoading || !text.trim()}
      >
        {isLoading ? "..." : "Send"}
      </button>
    </div>
  )
}