# app.py
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from dotenv import load_dotenv
from datetime import datetime
from twilio.rest import Client


load_dotenv()


app = Flask(__name__)
CORS(app)


# ========== Config (from .env) ==========
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "accident_db")


TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM")  # e.g. "whatsapp:+14155238886"
EMERGENCY_TO_WHATSAPP = os.getenv("EMERGENCY_TO_WHATSAPP") # e.g. "whatsapp:+91XXXXXXXXXX"


twilio_client = None
if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Dipali@123",
        database="db_accident"
    )


# ========== ADD THESE NEW ROUTES HERE ==========
@app.route("/")
def home():
    return jsonify({
        "message": "Accident Alert System API is running!",
        "endpoints": [
            "/register - POST",
            "/login - POST", 
            "/send-alert - POST"
        ]
    })

@app.route("/test")
def test():
    return jsonify({"status": "success", "message": "API is working!"})


# ========== Register ==========
@app.route("/register", methods=["POST"])
def register():
    try:
        data = request.json or {}
        email = data.get("email")
        password = data.get("password")
        if not email or not password:
            return jsonify({"status":"error","message":"email and password required"}), 400


        hashed = generate_password_hash(password)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
        if cursor.fetchone():
            cursor.close(); conn.close()
            return jsonify({"status":"error","message":"User already exists"}), 400


        cursor.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, hashed))
        conn.commit()
        cursor.close(); conn.close()
        return jsonify({"status":"success","message":"Registered"}), 201
    except Exception as e:
        return jsonify({"status":"error","message": str(e)}), 500


# ========== Login ==========
@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.json or {}
        email = data.get("email"); password = data.get("password")
        if not email or not password:
            return jsonify({"status":"error","message":"email and password required"}), 400


        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, email, password FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()
        cursor.close(); conn.close()


        if user and check_password_hash(user["password"], password):
            return jsonify({"status":"success","message":"Login successful", "user_id": user["id"]})
        else:
            return jsonify({"status":"error","message":"Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"status":"error","message": str(e)}), 500


# ========== Send Alert endpoint (called by device) ==========
# Expects JSON: {"name":"...", "blood_group":"A+", "lat":12.34, "lon":78.90, "user_phone":"+91..." }
@app.route("/send-alert", methods=["POST"])
def send_alert():
    try:
        data = request.json or {}
        name = data.get("name", "Unknown")
        blood_group = data.get("blood_group", "N/A")
        lat = data.get("lat")
        lon = data.get("lon")
        user_phone = data.get("user_phone", "N/A")
        timestamp = datetime.utcnow()


        # Save to DB
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO accident_alerts (name, blood_group, latitude, longitude, user_phone, created_at) VALUES (%s, %s, %s, %s, %s, %s)",
            (name, blood_group, lat, lon, user_phone, timestamp)
        )
        conn.commit()
        cursor.close(); conn.close()


        # Prepare WhatsApp message (Twilio)
        map_link = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}" if lat and lon else "Location not available"
        text = f"🚨 ACCIDENT ALERT 🚨\nPerson: {name}\nBlood Group: {blood_group}\nPhone: {user_phone}\nLocation: {map_link}\nTime (UTC): {timestamp.strftime('%Y-%m-%d %H:%M:%S')}\nPlease respond immediately."


        api_response = None
        if twilio_client and TWILIO_WHATSAPP_FROM and EMERGENCY_TO_WHATSAPP:
            message = twilio_client.messages.create(
                body=text,
                from_=TWILIO_WHATSAPP_FROM,
                to=EMERGENCY_TO_WHATSAPP
            )
            api_response = {"sid": message.sid, "status": message.status}


        return jsonify({"status":"success","message":"Alert stored and sent","twilio": api_response}), 200


    except Exception as e:
        return jsonify({"status":"error","message": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
