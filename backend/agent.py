import json
import os
import re
from groq import Groq
from dotenv import load_dotenv
from kb import search_kb
from ticket import create_ticket

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """
You are Alex, an IT Service Desk Agent for a large enterprise company.
You are professional, calm, friendly, and efficient.

You have access to two actions you can take by responding with JSON inside <action> tags:

1. Search the knowledge base:
<action>{"type": "search_kb", "query": "user's problem here"}</action>

2. Create a support ticket:
<action>{"type": "create_ticket", "issue_summary": "...", "category": "vpn", "priority": "high", "steps_tried": "..."}</action>

Valid categories: wifi, vpn, password_reset, laptop_not_booting, printer, email, software_install
Valid priorities: low, medium, high

RULES:
- When a user describes a technical issue, ALWAYS use <action> to search_kb first
- ONLY use troubleshooting steps returned from the knowledge base search
- Give steps ONE AT A TIME — one step per message, then ask if it worked
- After all KB steps are exhausted and issue persists, use <action> to create_ticket
- Never create a ticket without trying at least 2-3 steps first
- Ask clarifying questions if the problem is vague
- Be empathetic and professional
- When you use an <action> tag, do NOT write anything else in your response
"""

def extract_action(text):
    match = re.search(r'<action>(.*?)</action>', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            return None
    return None

def run_agent(conversation_history):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history

    for _ in range(10):
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            max_tokens=1024
        )

        content = response.choices[0].message.content or ""
        action = extract_action(content)

        # No action — return as final response
        if not action:
            return {
                "message": content,
                "ticket": None
            }

        action_type = action.get("type")

        if action_type == "search_kb":
            query = action.get("query", "")
            result = search_kb(query)

            messages.append({"role": "assistant", "content": content})
            messages.append({
                "role": "user",
                "content": f"[KB Search Result]: {json.dumps(result)}"
            })

        elif action_type == "create_ticket":
            result = create_ticket(
                issue_summary=action.get("issue_summary", ""),
                category=action.get("category", "general"),
                priority=action.get("priority", "medium"),
                steps_tried=action.get("steps_tried", "")
            )

            messages.append({"role": "assistant", "content": content})
            messages.append({
                "role": "user",
                "content": f"[Ticket Created]: {json.dumps(result)}"
            })

            # Get final closing message
            final_response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages,
                max_tokens=1024
            )
            return {
                "message": final_response.choices[0].message.content,
                "ticket": result
            }

        else:
            return {
                "message": content,
                "ticket": None
            }

    return {
        "message": "I'm sorry, I encountered an issue. Please try again.",
        "ticket": None
    }