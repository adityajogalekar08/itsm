# AI Agent Suite — ITSM & Voice

Two AI-powered agent demos built with React + Flask + Groq.

---

## Case 1 — ITSM Troubleshooting Agent

A chat-based IT helpdesk agent named **Alex** that helps employees resolve IT issues.

### What it does
- Greets the user and asks clarifying questions before troubleshooting
- Searches a structured knowledge base to find relevant steps
- Walks the user through troubleshooting **one step at a time**
- Asks for confirmation after each step before moving to the next
- If all steps are exhausted and issue persists — automatically creates a support ticket
- Handles multi-intent queries (e.g. "my VPN is down and I can't print")

### Supported issue categories
- WiFi / Network Issues
- VPN Not Connecting
- Password Reset / Account Locked
- Laptop Not Starting / Black Screen
- Printer Not Working
- Email / Outlook Issues
- Software Installation / Access Request

### How to use
1. Open `http://localhost:5173`
2. Type your IT issue in the chat box
3. Follow Alex's troubleshooting steps
4. If unresolved, a ticket card will appear with ticket ID, priority, and SLA

---

## Case 2 — Outbound Voice Agent

A voice-based outbound calling agent named **Priya** for AutoCare Service Center, Bengaluru.

### What it does
- Simulates an outbound call to a customer for vehicle service reminder
- Verifies the customer's identity and vehicle ownership
- Informs about pending services and explains why they matter
- Suggests the nearest service center with available time slots
- Books the appointment and confirms details

### How to use
1. Open `http://localhost:5173/voice`
2. Select a customer from the list to simulate an outbound call
3. Priya will start speaking automatically
4. Click **Speak** to respond after Priya finishes
5. Speak naturally — your voice is transcribed and sent to the agent
6. Appointment confirmation or callback badge appears based on the conversation
7. Click **End Call** to end the session

### Mock customers available
| Name | Vehicle |
|---|---|
| Rahul Sharma | 2021 Maruti Suzuki Swift |
| Priya Patel | 2022 Hyundai Creta |
| Amit Kumar | 2023 Tata Nexon |
| Sneha Reddy | 2020 Honda City |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React + Vite + TanStack Query |
| Backend | Python Flask |
| LLM | Groq (LLaMA 3.1 8B Instant) |
| STT | Groq Whisper / Browser Speech API |
| TTS | Browser Speech Synthesis API |
| Routing | React Router |

---

## Running Locally

**Backend**
```bash
cd backend
pip install -r requirements.txt
python app.py
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
```

Add a `.env` file in `backend/` with:

```
GROQ_API_KEY=your_key_here
```

Open `http://localhost:5173` in Chrome.