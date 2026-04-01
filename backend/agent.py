import json
import os
from openai import OpenAI
from dotenv import load_dotenv
from kb import search_kb
from ticket import create_ticket

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

Your job is to:
1. Understand the user's IT problem clearly — ask clarifying questions if the problem is vague
2. Search the knowledge base and walk the user through troubleshooting steps ONE AT A TIME
   - Do not dump all steps at once
   - After each step, ask the user if it worked before moving to the next
3. If the issue is resolved, confirm and close warmly
4. If all steps are exhausted and the issue persists, create a support ticket
5. Handle multiple issues in one message — address each one clearly

Important rules:
- Never give generic advice — always use the knowledge base
- Never create a ticket without trying at least 2-3 troubleshooting steps first
- Always maintain context of what steps have already been tried
- Be empathetic — users are often frustrated when things don't work
- Keep responses concise and structured
- If the user is completely blocked from working, mark priority as high
"""

def run_agent(conversation_history):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history

    while True:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        response_message = response.choices[0].message

        # No tool call — final response
        if not response_message.tool_calls:
            return {
                "message": response_message.content,
                "ticket": None
            }

        # Handle tool calls
        messages.append(response_message)
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
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": tool_result
            })

        # If ticket was created, get final message then return with ticket
        if ticket_data:
            final_response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                tools=tools,
                tool_choice="none"
            )
            return {
                "message": final_response.choices[0].message.content,
                "ticket": ticket_data
            }