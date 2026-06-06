import os
import sqlite3
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

DB = "chat.db"


# ---------------- DB ----------------
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id TEXT,
            sender TEXT,
            message TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()


def save_message(client_id, sender, message):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO messages (client_id, sender, message) VALUES (?, ?, ?)",
              (client_id, sender, message))
    conn.commit()
    conn.close()


def get_messages(client_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT sender, message FROM messages WHERE client_id=? ORDER BY id", (client_id,))
    rows = c.fetchall()
    conn.close()

    return [{"sender": r[0], "message": r[1]} for r in rows]


# ---------------- SEND TO TG ----------------
@app.route("/send", methods=["POST"])
def send():
    data = request.json
    client_id = data["client_id"]
    message = data["message"]

    save_message(client_id, "user", message)

    text = f"📩 NEW MESSAGE\nID: {client_id}\n\n{message}"

    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={
            "chat_id": ADMIN_ID,
            "text": text
        }
    )

    return jsonify({"ok": True})


# ---------------- GET CHAT ----------------
@app.route("/chat/<client_id>")
def chat(client_id):
    return jsonify(get_messages(client_id))


# ---------------- TELEGRAM WEBHOOK ----------------
@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.json

    if "message" in update:
        msg = update["message"]
        chat_id = msg["chat"]["id"]

        if str(chat_id) != str(ADMIN_ID):
            return "ok"

        if "reply_to_message" in msg:
            text = msg["text"]
            original = msg["reply_to_message"]["text"]

            # ищем ID
            client_id = None
            for line in original.split("\n"):
                if "ID:" in line:
                    client_id = line.replace("ID:", "").strip()

            if client_id:
                save_message(client_id, "admin", text)

    return "ok"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
