// ===== BACKEND API CONFIGURATION =====
const API_BASE = "http://127.0.0.1:5000";

console.log("🚀 API_BASE set to:", API_BASE);

// ===== Drawer =====
function toggleDrawer() {
    document.getElementById('drawer').classList.toggle('open');
}

// ===== User Storage =====
const LS_USER_KEY = "jr_user";

function saveUser(u) {
    localStorage.setItem(LS_USER_KEY, JSON.stringify(u));
}

function getUser() {
    try {
        return JSON.parse(localStorage.getItem(LS_USER_KEY) || "null");
    } catch (e) {
        return null;
    }
}

function logout() {
    localStorage.removeItem(LS_USER_KEY);
    alert("Logged out successfully!");
    location.href = "index.html";
}

// ===== Register Step 2 =====
function goStep2() {
    const e = document.getElementById('stepEmailAddr').value.trim();
    const p = document.getElementById('stepEmailPass').value.trim();
    if (!e || !p) {
        alert("Enter email + email password");
        return;
    }
    
    document.getElementById('regEmail').value = e;
    document.getElementById('stepEmail').style.display = "none";
    document.getElementById('stepForm').style.display = "block";
}

// ===== UPDATED REGISTER FUNCTION =====
async function doRegister() {
    console.log("🔥 Registration started!");
    console.log("Using API_BASE:", API_BASE);
    
    // Get form values
    const name = document.getElementById('regName').value.trim();
    const email = document.getElementById('regEmail').value.trim();
    const phone = document.getElementById('regPhone').value.trim();
    const pass1 = document.getElementById('regPass').value;
    const pass2 = document.getElementById('regPass2').value;
    
    console.log("Form data:", { name, email, phone });
    
    // Basic validation
    if (!name || !email || !phone || !pass1 || !pass2) {
        alert("❌ Please fill all fields!");
        return;
    }
    
    if (pass1 !== pass2) {
        alert("❌ Passwords do not match!");
        return;
    }
    
    // Test backend connection first
    try {
        console.log("Testing backend connection...");
        const testUrl = `${API_BASE}/`;
        console.log("Test URL:", testUrl);
        
        const testResponse = await fetch(testUrl);
        console.log("Test response status:", testResponse.status);
        
        if (!testResponse.ok) {
            throw new Error(`Backend responded with status: ${testResponse.status}`);
        }
        
        console.log("✅ Backend connection successful!");
        
    } catch (backendError) {
        console.error("❌ Backend connection failed:", backendError);
        
        alert(`🚨 Backend Server Connection Failed!

Backend URL: ${API_BASE}
Error: ${backendError.message}

SOLUTIONS:
1. Open Terminal in backend folder
2. Run: python app.py
3. Wait for: "Running on http://127.0.0.1:5000"
4. Make sure no other app is using port 5000
5. Try again

Current Status: Backend is NOT running or not accessible`);
        return;
    }
    
    // Proceed with registration
    try {
        console.log("Sending registration request...");
        const registerUrl = `${API_BASE}/register`;
        console.log("Register URL:", registerUrl);
        
        const response = await fetch(registerUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            body: JSON.stringify({
                email: email,
                password: pass1
            })
        });
        
        console.log("Registration response status:", response.status);
        console.log("Registration response headers:", response.headers);
        
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP ${response.status}: ${errorText}`);
        }
        
        const data = await response.json();
        console.log("Registration response data:", data);
        
        if (data.status === "success") {
            // Save user data locally
            const userData = { name, email, phone };
            localStorage.setItem("jr_user", JSON.stringify(userData));
            
            alert("✅ Account Created Successfully!");
            console.log("✅ Registration successful, redirecting to login...");
            window.location.href = "login.html";
            
        } else {
            alert("❌ Registration Failed: " + (data.message || "Unknown error"));
            console.error("Registration failed with data:", data);
        }
        
    } catch (registrationError) {
        console.error("❌ Registration error:", registrationError);
        alert(`❌ Registration Error!

Error: ${registrationError.message}
API URL: ${API_BASE}/register

Possible Causes:
1. Flask backend not running
2. Database connection issues
3. CORS configuration problems
4. Network connectivity issues

Check browser console (F12) for detailed logs.`);
    }
}

// ===== LOGIN FUNCTION =====
async function doLogin() {
    const email = document.getElementById('loginEmail').value.trim();
    const password = document.getElementById('loginPass').value;
    
    if (!email || !password) {
        alert("Please fill all fields");
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/login`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (data.status === "success") {
            saveUser({ email, user_id: data.user_id });
            alert("✅ Login successful!");
            location.href = "home.html";
        } else {
            alert("❌ Login failed: " + data.message);
        }
    } catch (error) {
        alert(`❌ Login Error: ${error.message}`);
    }
}

// ===== Profile Hydration =====
(function hydrateProfile() {
    const box = document.getElementById('profileBox');
    if (!box) return;
    
    const u = getUser();
    if (!u) {
        box.innerHTML = "<p>Please login.</p>";
        return;
    }
    
    box.innerHTML = `
        <h3>User Profile</h3>
        <p><strong>Email:</strong> ${u.email}</p>
        <p><strong>Name:</strong> ${u.name || 'Not provided'}</p>
        <p><strong>Phone:</strong> ${u.phone || 'Not provided'}</p>
    `;
})();

// ===== Initialize =====
console.log("🚀 Script loaded successfully!");
console.log("API_BASE configuration:", API_BASE);
