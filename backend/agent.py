import json
import os
from groq import Groq
from dotenv import load_dotenv
from kb import search_kb
from ticket import create_ticket

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

tools = [
    {
        "type": "function",
        "function": {
            "name": "search_kb",
            "description": "Search the IT knowledge base for troubleshooting steps based on the user's problem. Call this when the user describes a technical issue.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The user's problem or issue description"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_ticket",
            "description": "Create an IT support ticket when the issue cannot be resolved through troubleshooting steps. Only call this when the user has tried the steps and the problem persists, or the issue requires human intervention.",
            "parameters": {
                "type": "object",
                "properties": {
                    "issue_summary": {
                        "type": "string",
                        "description": "A short summary of the user's issue"
                    },
                    "category": {
                        "type": "string",
                        "description": "The category of the issue e.g. wifi, vpn, password_reset, laptop_not_booting, printer, email, software_install"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "Priority based on business impact. High if user is completely blocked from working."
                    },
                    "steps_tried": {
                        "type": "string",
                        "description": "Summary of troubleshooting steps already attempted with the user"
                    }
                },
                "required": ["issue_summary", "category", "priority", "steps_tried"]
            }
        }
    }
]

SYSTEM_PROMPT = """
You are Alex, an IT Service Desk Agent for a large enterprise company.
You are professional, calm, friendly, and efficient.

CRITICAL RULES - YOU MUST FOLLOW THESE:
- You MUST call search_kb tool EVERY TIME the user describes a technical issue
- You MUST ONLY use troubleshooting steps returned by the search_kb tool
- You MUST NEVER generate troubleshooting steps from your own knowledge
- If search_kb returns no results, say you'll escalate and call create_ticket immediately
- NEVER skip calling search_kb for any technical problem

Your workflow:
1. Ask clarifying questions if the problem is vague
2. Call search_kb with the user's problem
3. Walk through the steps from search_kb ONE AT A TIME
   - After each step, ask the user if it worked before moving to the next
4. If all KB steps are exhausted and issue persists, call create_ticket
5. If the issue is resolved, confirm and close warmly

Ticket rules:
- Never create a ticket without trying at least 2-3 steps from the KB first
- Always maintain context of what steps have already been tried
- If the user is completely blocked from working, mark priority as high
"""

def run_agent(conversation_history):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history

    while True:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,
            tools=tools,
            tool_choice="auto",
            max_tokens=1024
        )

        response_message = response.choices[0].message

        # No tool call — final response
        if not response_message.tool_calls:
            return {
                "message": response_message.content,
                "ticket": None
            }

        # Append assistant message with tool calls
        messages.append({
    "role": "assistant",
    "content": response_message.content or "",
    "tool_calls": response_message.tool_calls
})

        ticket_data = None

        for tool_call in response_message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            if function_name == "search_kb":
                result = search_kb(function_args["query"])
                tool_result = json.dumps(result)

            elif function_name == "create_ticket":
                result = create_ticket(
                    issue_summary=function_args["issue_summary"],
                    category=function_args["category"],
                    priority=function_args["priority"],
                    steps_tried=function_args["steps_tried"]
                )
                ticket_data = result
                tool_result = json.dumps(result)

            messages.append({
    "role": "assistant",
    "content": response_message.content or "",
    "tool_calls": response_message.tool_calls
})

        # If ticket was created, get final closing message
        if ticket_data:
            final_response = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=messages,
                max_tokens=1024
            )
            return {
                "message": final_response.choices[0].message.content,
                "ticket": ticket_data
            }