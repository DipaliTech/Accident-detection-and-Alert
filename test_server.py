from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["*"])

@app.route("/")
def home():
    return jsonify({
        "message": "🚀 Test Server is running!",
        "status": "success",
        "endpoints": ["/register", "/login", "/test"]
    })

@app.route("/test")
def test():
    return jsonify({
        "message": "✅ Test endpoint working!",
        "status": "success"
    })

@app.route("/register", methods=["POST"])
def register():
    data = request.json or {}
    email = data.get("email")
    
    print(f"🎯 Registration request: {email}")
    
    return jsonify({
        "status": "success",
        "message": "Account created successfully!",
        "email": email
    })

@app.route("/login", methods=["POST"])  # ← NEW LOGIN ENDPOINT
def login():
    data = request.json or {}
    email = data.get("email")
    password = data.get("password")
    
    print(f"🔐 Login attempt: {email}")
    
    # Accept any email/password for testing
    if email and password:
        return jsonify({
            "status": "success",
            "message": "Login successful!",
            "user_id": 123
        })
    else:
        return jsonify({
            "status": "error", 
            "message": "Invalid credentials"
        })

if __name__ == "__main__":
    print("🚀 Starting test server with login support...")
    app.run(host="0.0.0.0", port=5000, debug=True)
