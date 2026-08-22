from fastapi import HTTPException
import os
from dotenv import load_dotenv
import requests
import time
from app.services import cache

RESEND_API_KEY = os.getenv("RESEND_API_KEY")

def send_alert_email(user_email: str, current_data: float):
    url = "https://api.resend.com/emails"
    print("USER : ++++++++++++++++++++++ ")
    print(user_email)
    print("USER : ++++++++++++++++++++++ \n")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {RESEND_API_KEY}"
    }
    
    payload = {
        "from": "onboarding@resend.dev", 
        "to": user_email,             
        "subject": "Hey! Low Soil Moisture Detected!",
        "text": (
        f"CRITICAL ALERT - TVS SOIL MOISTURE SYSTEM\n\n"
        f"Current Soil Moisture Level: {current_data}%\n"
        f"Status: Below threshold limit (40.0%)\n\n"
        f"Action Required: Please inspect the irrigation system and turn on the pump immediately.\n\n"
        f"Time Recorded: {time.strftime('%Y-%m-%d %H:%M:%S')}"
        )
    }
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200 or response.status_code == 201:
        print("Successfully send mail:", response.json())
        return response.json()
    else:
        print(f"Failed to send MAIL: [{response.status_code}]:", response.text)
        raise HTTPException(status_code=400, detail=f"Error Resend API: {response.text}")

def trigger_alert(user_email: str, current_moisture: float):
    THRESHOLD = 40.0
    COOLDOWN_SECONDS = 15 * 60
    if current_moisture < THRESHOLD:
        current_time = time.time()
        last_sent = cache.get_last_email_sent_time()
        time_passed = current_time - last_sent
        
        if time_passed >= COOLDOWN_SECONDS:
            print(f"Moisture {current_moisture}% < {THRESHOLD}%. Sending mail...")
            send_alert_email(user_email, current_moisture)
            cache.update_last_email_sent_time()

        
     
def trigger_alert_moisture():
    target_email = cache.get_latest_user_gmail()
    current_moisture = cache.get_cache_soil_moisture()
    
    if not target_email:
        target_email = "admin@gmail.com"

    trigger_alert(target_email, current_moisture)