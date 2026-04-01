from flask import Blueprint, request, jsonify
from voice_agent import run_voice_agent, get_customer_by_phone, get_customer_by_name, get_service_locations
import uuid

voice_bp = Blueprint("voice", __name__)

call_sessions = {}

@voice_bp.route("/voice/start", methods=["POST"])
def start_call():
    data = request.json
    customer_phone = data.get("customer_phone")
    session_id = str(uuid.uuid4())

    customer = get_customer_by_phone(customer_phone)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    call_sessions[session_id] = {
        "customer_phone": customer_phone,
        "history": [],
        "status": "active",
        "appointment": None,
        "feedback": None,
        "callback_time": None
    }

    # Generate opening line
    opening = run_voice_agent([], customer_phone=customer_phone)

    call_sessions[session_id]["history"].append({
        "role": "assistant",
        "content": opening
    })

    return jsonify({
        "session_id": session_id,
        "message": opening,
        "customer": {
            "name": customer["name"],
            "vehicle": f"{customer['vehicles'][0]['year']} {customer['vehicles'][0]['make']} {customer['vehicles'][0]['model']}",
            "pending_services": customer["vehicles"][0]["pending_services"]
        }
    })

@voice_bp.route("/voice/respond", methods=["POST"])
def respond():
    data = request.json
    session_id = data.get("session_id")
    user_message = data.get("message", "")

    if session_id not in call_sessions:
        return jsonify({"error": "Session not found"}), 404

    session = call_sessions[session_id]

    session["history"].append({
        "role": "user",
        "content": user_message
    })

    # Detect appointment booking
    if any(word in user_message.lower() for word in ["confirm", "book", "yes", "sure", "okay", "ok"]):
        if any(word in user_message.lower() for word in ["am", "pm", "morning", "afternoon", "slot", "time"]):
            session["appointment"] = user_message

    # Detect callback request
    if any(word in user_message.lower() for word in ["later", "call back", "busy", "not now"]):
        session["callback_time"] = user_message
        session["status"] = "callback_requested"

    # Detect negative feedback
    if any(word in user_message.lower() for word in ["complaint", "unhappy", "problem", "issue", "bad", "terrible", "worst"]):
        session["feedback"] = user_message
        session["status"] = "feedback_captured"

    response = run_voice_agent(
        session["history"],
        customer_phone=session["customer_phone"]
    )

    session["history"].append({
        "role": "assistant",
        "content": response
    })

    return jsonify({
        "message": response,
        "session_status": session["status"],
        "appointment": session["appointment"],
        "callback_time": session["callback_time"]
    })

@voice_bp.route("/voice/end", methods=["POST"])
def end_call():
    data = request.json
    session_id = data.get("session_id")

    if session_id not in call_sessions:
        return jsonify({"error": "Session not found"}), 404

    session = call_sessions[session_id]
    session["status"] = "completed"

    return jsonify({
        "status": "completed",
        "appointment": session["appointment"],
        "callback_time": session["callback_time"],
        "feedback": session["feedback"],
        "total_turns": len(session["history"])
    })

@voice_bp.route("/voice/customers", methods=["GET"])
def get_customers():
    from voice_agent import load_customers
    data = load_customers()
    return jsonify([
        {
            "phone": c["phone"],
            "name": c["name"],
            "vehicle": f"{c['vehicles'][0]['year']} {c['vehicles'][0]['make']} {c['vehicles'][0]['model']}"
        }
        for c in data["customers"]
    ])