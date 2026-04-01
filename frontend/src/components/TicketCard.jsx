export default function TicketCard({ ticket }) {
  const priorityColors = {
    high: { bg: "#fff0f0", border: "#ff4d4f", text: "#cf1322" },
    medium: { bg: "#fffbe6", border: "#faad14", text: "#d46b08" },
    low: { bg: "#f6ffed", border: "#52c41a", text: "#389e0d" }
  }

  const colors = priorityColors[ticket.priority] || priorityColors.medium

  return (
    <div className="ticket-card" style={{ borderColor: colors.border, background: colors.bg }}>
      <div className="ticket-header">
        <div className="ticket-icon">🎫</div>
        <div className="ticket-title">
          <span className="ticket-label">Support Ticket Created</span>
          <span className="ticket-id">{ticket.ticket_id}</span>
        </div>
        <span
          className="ticket-priority"
          style={{ background: colors.border, color: "white" }}
        >
          {ticket.priority.toUpperCase()}
        </span>
      </div>

      <div className="ticket-body">
        <div className="ticket-row">
          <span className="ticket-field">Issue</span>
          <span className="ticket-value">{ticket.issue_summary}</span>
        </div>
        <div className="ticket-row">
          <span className="ticket-field">Category</span>
          <span className="ticket-value">{ticket.category}</span>
        </div>
        <div className="ticket-row">
          <span className="ticket-field">Status</span>
          <span className="ticket-value ticket-status">● {ticket.status.toUpperCase()}</span>
        </div>
        <div className="ticket-row">
          <span className="ticket-field">Assigned To</span>
          <span className="ticket-value">{ticket.assigned_to}</span>
        </div>
        <div className="ticket-row">
          <span className="ticket-field">Expected Response</span>
          <span className="ticket-value">{ticket.estimated_response}</span>
        </div>
        <div className="ticket-row">
          <span className="ticket-field">Created At</span>
          <span className="ticket-value">{ticket.created_at}</span>
        </div>
      </div>
    </div>
  )
}