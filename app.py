import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
MY_TELEGRAM_ID = "7586627550" 

@app.route("/")
def home():
    return "Bot server is running!"

@app.route('/send_to_tg', methods=['POST'])
def send_to_tg():
    data = request.json
    if not data:
        return jsonify({"status": "error", "message": "No data received"}), 400
        
    client_id = data.get("client_id", "Неизвестный")
    user_message = data.get("message", "")
    
    text_to_tg = f"📩 Новое сообщение!\nID: {client_id}\nТекст: {user_message}"
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": MY_TELEGRAM_ID, "text": text_to_tg})
    
    return jsonify({"status": "success"}), 200

@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    data = request.json
    
    if "message" in data and "reply_to_message" in data["message"]:
        reply_text = data["message"]["text"]
        original_text = data["message"]["reply_to_message"]["text"]
        
        try:
            client_id = original_text.split("ID: ")[1].split("\n")[0].strip()
            print(f"Ответ для клиента {client_id}: {reply_text}")
            
        except Exception as e:
            print("Не удалось найти ID клиента:", e)
            
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
