import uuid
from datetime import datetime

ticket_store = []

def create_ticket(issue_summary: str, category: str, priority: str, steps_tried: str):
    ticket_id = "TKT-" + str(uuid.uuid4())[:8].upper()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    ticket = {
        "ticket_id": ticket_id,
        "issue_summary": issue_summary,
        "category": category,
        "priority": priority,
        "steps_tried": steps_tried,
        "status": "open",
        "created_at": timestamp,
        "assigned_to": "IT Support Team",
        "estimated_response": get_estimated_response(priority)
    }

    ticket_store.append(ticket)

    return ticket

def get_estimated_response(priority: str):
    if priority == "high":
        return "Within 1 hour"
    elif priority == "medium":
        return "Within 4 hours"
    else:
        return "Within 24 hours"

def get_all_tickets():
    return ticket_store