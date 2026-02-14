import http.server
import socketserver
import json
import random
import os

PORT = int(os.environ.get("PORT", 8081))
OTP_STORE = {}

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'X-Requested-With, Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.end_headers()

    def do_POST(self):
        content_length_str = self.headers.get('Content-Length')
        if content_length_str:
            content_length = int(content_length_str)
            post_data = self.rfile.read(content_length)
        else:
            post_data = b''
        
        data = {}
        try:
            if content_length_str and int(content_length_str) > 0:
                data = json.loads(post_data.decode('utf-8'))
        except Exception as e:
            print(f"Error parsing body: {e}")
            pass
        
        response = {}
        
        if self.path == '/api/send-otp':
            phone = data.get('phone_number')
            # Mock OTP logic
            otp = str(random.randint(1000, 9999))
            if phone:
                OTP_STORE[str(phone)] = otp
                print(f"Generated OTP for {phone}: {otp}")
                response = {"status": "success", "message": "OTP sent successfully", "otp": otp}
            else:
                 self.send_response(400)
                 self.end_headers()
                 return
            
        elif self.path == '/api/verify-otp':
            phone = str(data.get('phone_number'))
            user_otp = str(data.get('otp'))
            
            # Simple verification for demo
            valid_otp = OTP_STORE.get(phone)
            print(f"Verifying {phone}: User sent {user_otp}, Stored {valid_otp}")

            if valid_otp and valid_otp == user_otp:
                response = {"status": "success", "message": "OTP verified", "token": "mock-jwt-token"}
            else:
                # For demo purposes, allow entering the OTP directly if user missed it
                if user_otp == "1234":
                     response = {"status": "success", "message": "OTP verified (dev)", "token": "mock-jwt-token"}
                else:
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "error", "message": "Invalid OTP"}).encode('utf-8'))
                    return

        elif self.path == '/api/predict-price':
            # Mock price prediction
            qty = data.get('quantity', 0)
            waste_type = data.get('waste_type', 'unknown')
            base_price = 2000 if 'rice' in str(waste_type) else 3000
            total = base_price * float(qty) if qty else 0
            response = {"estimated_price": base_price, "total_value": total, "currency": "INR"}

        elif self.path == '/api/classify-waste':
            # Mock classification - return static data for any image
            response = {
                "predicted_class": "rice_straw",
                "display_name": "Rice Straw",
                "confidence": 0.98,
                "price_range": {"min_per_ton": 2200, "max_per_ton": 2800, "currency": "INR"},
                "environmental_benefits": {
                    "co2_reduction_per_ton": 1500,
                    "soil_nitrogen_retained_kg": 12,
                    "water_savings_liters": 5000
                },
                "industrial_uses": [
                    {"industry": "Bio-Energy", "application": "Ethanol Production", "processing": "Fermentation", "market_demand": "Very High"},
                    {"industry": "Paper & Pulp", "application": "Paper Manufacturing", "processing": "Pulping", "market_demand": "High"}
                ]
            }
            
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode('utf-8'))

    def do_GET(self):
        if self.path == '/api/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "healthy"}).encode('utf-8'))
        else:
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"StubbleX Backend Running")

print(f"Starting simple server on port {PORT}")

# Allow address reuse to prevent "Address already in use" errors during restarts
socketserver.TCPServer.allow_reuse_address = True

with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print("serving at port", PORT)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
