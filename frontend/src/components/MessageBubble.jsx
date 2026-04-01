export default function MessageBubble({ role, content }) {
  const isUser = role === "user"

  return (
    <div className={`message-row ${isUser ? "user-row" : "agent-row"}`}>
      {!isUser && (
        <div className="bubble-avatar">A</div>
      )}
      <div className={`message-bubble ${isUser ? "user-bubble" : "agent-bubble"}`}>
        {formatContent(content)}
      </div>
    </div>
  )
}

function formatContent(content) {
  const lines = content.split("\n")

  return lines.map((line, idx) => {
    // Numbered steps like "1. Do this"
    if (/^\d+\.\s/.test(line)) {
      return (
        <p key={idx} className="step-line">
          {line}
        </p>
      )
    }

    // Bold text wrapped in **
    if (line.includes("**")) {
      const parts = line.split(/\*\*(.*?)\*\*/g)
      return (
        <p key={idx}>
          {parts.map((part, i) =>
            i % 2 === 1 ? <strong key={i}>{part}</strong> : part
          )}
        </p>
      )
    }

    // Empty line = spacer
    if (line.trim() === "") {
      return <br key={idx} />
    }

    return <p key={idx}>{line}</p>
  })
}