from flask import Flask, request, jsonify
import requests
import os
import re

app = Flask(__name__)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
#Clean message function:
def clean_text(text):
    if not text:
        return ""
    text = str(text)
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', ' ', text)
    text = text.replace('"', "'")
    text = text.replace('\\', '')
    return text.strip()
#Talk to Groq function:
def ask_sarah(history, customer_message):
    clean_history = clean_text(history)
    clean_msg = clean_text(customer_message)
    
    system_prompt = """You are Sarah, receptionist at Sparkle Clean USA in Dallas Texas. Talk like a real friendly human texting. SHORT replies only, max 2 sentences. NEVER re-introduce yourself after first message. Use customer name naturally once you know it. SERVICES: Standard Clean $120, Deep Clean $220, Move-Out Clean $300. AREAS: Dallas, Plano, Frisco, McKinney only. HOURS: Mon-Sat 8am-6pm. RULES: 1) First message only - introduce yourself as Sarah and ask their name casually. 2) After that just have natural conversation. 3) Outside cleaning requests - say we only do cleaning. 4) Outside service area - say we only cover Dallas Plano Frisco and McKinney. 5) Discount requests - say prices are set but ask about current offers. 6) Urgent keywords like urgent emergency ASAP broken flooding - mark as URGENT. 7) Booking - collect name address date naturally. 8) Never reveal you are AI. OUTPUT PURE JSON ONLY no markdown no backticks: {"reply": "casual short reply", "urgency": "URGENT or CASUAL", "name": "name or blank", "service": "service or blank", "area": "area or blank", "history": "plain text summary of full conversation"}"""

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Previous conversation: {clean_history} | Customer just said: {clean_msg}"}
            ],
            "max_tokens": 500,
            "temperature": 0.5
        }
    )
    return response.json()
#Main endpoint:
@app.route('/sarah', methods=['POST'])
def sarah_endpoint():
    data = request.json
    
    history = data.get('history', '')
    message = data.get('message', '')
    
    groq_response = ask_sarah(history, message)
    
    content = groq_response['choices'][0]['message']['content']
    
    import json
    try:
        parsed = json.loads(content)
    except:
        parsed = {
            "reply": "Sorry, let me get back to you in a moment.",
            "urgency": "CASUAL",
            "name": "",
            "service": "",
            "area": "",
            "history": history
        }
    
    return jsonify(parsed)

if __name__ == '__main__':
    app.run(debug=True)
