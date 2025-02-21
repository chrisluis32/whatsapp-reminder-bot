import os
import time
from dotenv import load_dotenv
from twilio.rest import Client
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Twilio credentials from .env file
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

# Initialize Twilio client
client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

# Function to send WhatsApp message
def send_whatsapp_message(to, message):
    try:
        client.messages.create(
            from_=f"whatsapp:{TWILIO_WHATSAPP_NUMBER}",
            body=message,
            to=f"whatsapp:{to}",
        )
        print(f"✅ Reminder sent to {to} at {datetime.now().strftime('%I:%M %p')}")
    except Exception as e:
        print(f"❌ Failed to send message: {e}")

# Get user inputs
message = input("Enter reminder message: ")
recipient = input("Enter recipient's WhatsApp number (with country code): ")
frequency = input("Enter frequency (daily/weekly/monthly): ").strip().lower()
custom_time = input("Enter time to send the message (HH:MM AM/PM): ").strip()

# Convert user time input to 24-hour format
try:
    reminder_time = datetime.strptime(custom_time, "%I:%M %p").time()
except ValueError:
    print("❌ Invalid time format! Use HH:MM AM/PM (e.g., 10:30 AM)")
    exit()

# Initialize scheduler
scheduler = BackgroundScheduler()

if frequency == "daily":
    scheduler.add_job(
        send_whatsapp_message, 
        "cron", 
        hour=reminder_time.hour, 
        minute=reminder_time.minute, 
        args=[recipient, message]
    )
elif frequency == "weekly":
    scheduler.add_job(
        send_whatsapp_message, 
        "cron", 
        day_of_week="mon",  # Sends every Monday
        hour=reminder_time.hour, 
        minute=reminder_time.minute, 
        args=[recipient, message]
    )
elif frequency == "monthly":
    scheduler.add_job(
        send_whatsapp_message, 
        "cron", 
        day=1,  # Sends on the 1st of every month
        hour=reminder_time.hour, 
        minute=reminder_time.minute, 
        args=[recipient, message]
    )
else:
    print("❌ Invalid frequency! Please enter daily, weekly, or monthly.")
    exit()

# Start scheduler
scheduler.start()

print(f"⏳ Reminder bot is running... The message will be sent at {custom_time} ({frequency}) (Press Ctrl + C to stop)")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n🛑 Bot stopped.")
    scheduler.shutdown()
