import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Разрешаем твоему сайту делать запросы к этому серверу

# Берем токен из настроек Render (Environment)
BOT_TOKEN = os.environ.get("BOT_TOKEN")
# Твой личный ID в Telegram (куда бот будет слать сообщения)
ADMIN_ID = "6023363388"  

@app.route('/')
def home():
    return "Bot server is running!"

# Эндпоинт, куда сайт отправляет сообщения пользователей
@app.route('/send_to_tg',彻 methods=['POST'])
def send_to_tg():
    data = request.get_json()
    if not data or 'message' not in data or 'client_id' not in data:
        return jsonify({"error": "Bad Request"}), 400
    
    client_id = data['client_id']
    user_message = data['message']
    
    # Формируем текст для тебя
    text_to_admin = f"📩 *Новое сообщение!*\n\n*ID:* `{client_id}`\n*Текст:* {user_message}"
    
    # Отправляем тебе в Telegram
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": ADMIN_ID,
        "text": text_to_admin,
        "parse_mode": "Markdown"
    }
    
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return jsonify({"status": "success"}), 200
    else:
        return jsonify({"error": "Failed to send message to Telegram"}), 500

# Эндпоинт Вебхука, куда Telegram присылает твои ОТВЕТЫ
@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.get_json()
    
    # Проверяем, что это текстовый ответ (Reply) от тебя
    if "message" in update and "reply_to_message" in update["message"]:
        message = update["message"]
        chat_id = message["chat"]["id"]
        
        # Проверяем, что отвечаешь именно ты (админ)
        if str(chat_id) == ADMIN_ID:
            reply_text = message.get("text")
            original_text = message["reply_to_message"].get("text", "")
            
            # Пытаемся вытащить ID клиента из оригинального сообщения
            # Ищем строчку "ID: User_XXXXX"
            try:
                for line in original_text.split("\n"):
                    if line.startswith("ID:"):
                        client_id = line.replace("ID:", "").strip()
                        print(f"Ответ для клиента {client_id}: {reply_text}")
                        # Здесь в будущем можно отправлять ответ обратно на сайт
                        break
            except Exception as e:
                print(f"Ошибка при обработке ID клиента: {e}")
                
    return "ok", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
