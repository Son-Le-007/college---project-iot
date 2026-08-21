from fastapi import HTTPException
import requests

RESEND_API_KEY = ""

def send_alert_email(user_email: str, current_data: float):
    url = "https://api.resend.com/emails"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {RESEND_API_KEY}"
    }
    
    payload = {
        "from": "onboarding@resend.dev", 
        "to": user_email,             
        "subject": "Hey! Low moisture detected",
        "html": f"""
            <h3>Warning TVS</h3>
        """
    }
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200 or response.status_code == 201:
        print("Successfully send mail:", response.json())
        return response.json()
    else:
        print(f"Failed to send MAIL: [{response.status_code}]:", response.text)
        raise HTTPException(status_code=400, detail=f"Lỗi Resend API: {response.text}")

def trigger_alert(user_email: str, current_moisture: float):
    THRESHOLD = 40.0
    if current_moisture < THRESHOLD:
        print(f"Độ ẩm {current_moisture}% < {THRESHOLD}%. Sending mail...")
        send_alert_email(user_email, current_moisture)
     