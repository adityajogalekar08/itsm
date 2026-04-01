import json
import os

KB_PATH = os.path.join(os.path.dirname(__file__), "data", "kb.json")

def load_kb():
    with open(KB_PATH, "r") as f:
        return json.load(f)

def search_kb(query: str):
    kb = load_kb()
    query_lower = query.lower()

    matched = []

    for category in kb["categories"]:
        score = 0

        for keyword in category["keywords"]:
            if keyword in query_lower:
                score += 1

        if score > 0:
            matched.append({
                "score": score,
                "category": category
            })

    matched.sort(key=lambda x: x["score"], reverse=True)

    if not matched:
        return {
            "found": False,
            "message": "No matching knowledge base article found for this issue.",
            "categories": []
        }

    top_matches = matched[:2]

    return {
        "found": True,
        "message": f"Found {len(top_matches)} relevant KB article(s).",
        "categories": [
            {
                "id": m["category"]["id"],
                "title": m["category"]["title"],
                "steps": m["category"]["steps"],
                "escalate_after_steps": m["category"]["escalate_after_steps"],
                "ticket_reason": m["category"]["ticket_reason"]
            }
            for m in top_matches
        ]
    }