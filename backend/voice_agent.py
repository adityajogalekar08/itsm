import json
import os
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

CUSTOMERS_PATH = os.path.join(os.path.dirname(__file__), "data", "customers.json")

def load_customers():
    with open(CUSTOMERS_PATH, "r") as f:
        return json.load(f)

def get_customer_by_phone(phone):
    data = load_customers()
    for customer in data["customers"]:
        if customer["phone"] == phone:
            return customer
    return None

def get_customer_by_name(name):
    data = load_customers()
    name_lower = name.lower()
    for customer in data["customers"]:
        if name_lower in customer["name"].lower():
            return customer
    return None

def get_service_locations():
    data = load_customers()
    return data["service_center"]["locations"]

SYSTEM_PROMPT = """
You are Priya, a friendly and professional outbound voice agent for AutoCare Service Center in Bengaluru.
You are calling customers to remind them about pending vehicle service and book appointments.

You have access to customer and vehicle data that will be provided to you.

YOUR CALLING SCRIPT FLOW:
1. Greet the customer warmly and introduce yourself
2. Verify you are speaking with the right person by asking their name
3. Verify vehicle ownership by asking about their vehicle registration or model
4. Inform them about pending service and why it's important
5. Suggest the closest service center and available slots
6. Book the appointment or handle objections
7. Confirm the appointment details and close warmly

SCENARIO HANDLING:
- "Call me later" → Ask for a preferred time and note it down, be gracious
- Complaints/negative feedback → Apologize sincerely, note the feedback, offer to escalate
- Wrong person → Apologize and end the call politely
- Not interested → Acknowledge, mention importance of service for safety, don't be pushy
- Already serviced → Congratulate them, update records, close warmly

PERSONALITY:
- Warm, friendly, and conversational — NOT robotic
- Speak naturally like a real person would on a phone call
- Keep responses SHORT — this is a voice call, not a chat
- Never use bullet points or lists in responses
- Use natural filler words occasionally like "Sure", "Of course", "Absolutely"
- Be empathetic and never pushy

IMPORTANT:
- Keep each response to 1-3 sentences maximum
- This is a voice conversation — be natural and concise
- Never repeat the same information twice
"""

def run_voice_agent(conversation_history, customer_phone=None):
    data = load_customers()
    
    # Find customer context
    customer_context = ""
    if customer_phone:
        customer = get_customer_by_phone(customer_phone)
        if customer:
            vehicle = customer["vehicles"][0]
            locations = get_service_locations()
            customer_context = f"""
CUSTOMER DATA:
- Name: {customer["name"]}
- Phone: {customer["phone"]}
- Vehicle: {vehicle["year"]} {vehicle["make"]} {vehicle["model"]}
- Registration: {vehicle["registration"]}
- Last Service: {vehicle["last_service_date"]}
- Next Service Due: {vehicle["next_service_due"]}
- Pending Services: {", ".join(vehicle["pending_services"])}

NEAREST SERVICE CENTERS:
{json.dumps(locations, indent=2)}
"""

    system_with_context = SYSTEM_PROMPT
    if customer_context:
        system_with_context = SYSTEM_PROMPT + "\n\n" + customer_context

    messages = [{"role": "system", "content": system_with_context}] + conversation_history

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        max_tokens=256
    )

    return response.choices[0].message.content or ""