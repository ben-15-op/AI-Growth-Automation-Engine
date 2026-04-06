import base64
import os
import time
import random
import re
import socket
import pandas as pd
from datetime import datetime, timedelta
from email.message import EmailMessage
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# --- CONFIG ---
SPREADSHEET_ID = '1ADgXCjAxPQA_U-2R45hwMY9xVLlSHZ9IepY2hTVKwGc'
RANGE_NAME = 'Sheet1!A:C'
RESUME_PATH = 'resume.pdf'
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets.readonly',
    'https://www.googleapis.com/auth/gmail.send'
]

# --- AUTH ---
creds = None
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
else:
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

# --- GOOGLE API CLIENTS ---
def get_gmail_service():
    return build('gmail', 'v1', credentials=creds)

sheets_service = build('sheets', 'v4', credentials=creds)
gmail_service = get_gmail_service()

# --- LOAD EMAIL DATA FROM SHEET ---
result = sheets_service.spreadsheets().values().get(
    spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
values = result.get('values', [])
if not values:
    print("No data found.")
    exit()
df = pd.DataFrame(values[1:], columns=values[0])

# --- EMAIL TEMPLATES ---
TEMPLATES = [
    """Hello {name},\n\nI’m Aayush Singh, currently pursuing a B.Tech in Electronics Engineering at Harcourt Butler Technical University, Kanpur.\n\nI recently interned at the National Internet Exchange of India (NIXI), where I developed a secure internal portal using Django, integrated MySQL databases, and collaborated on frontend components.\n\nI’m particularly interested in contributing to {organisation} and have attached my resume for your kind consideration.\n\nBest regards,\nAayush Singh\n📧 code.aayush.19@gmail.com | 📱 +91-7451854550\n""",
    """Hello {name},\n\nMy name is Aayush Singh, a B.Tech student at HBTU Kanpur, with a strong passion for data science and machine learning.\n\nI’ve built a stock market prediction app and an IoT soil analysis system. At NIXI, I contributed to Django-based portals and collaborated on secure backend integration.\n\nI’d be excited to apply my skills at {organisation}. My resume is attached.\n\nSincerely,\nAayush Singh\n📧 code.aayush.19@gmail.com | 📱 +91-7451854550\n""",
    """Dear {organisation} team,\n\nI’m Aayush Singh, a third-year Electronics Engineering student at HBTU Kanpur, exploring internship roles in web development or data analysis.\n\nDuring my NIXI internship, I developed Django web apps, managed MySQL databases, and led UI integration. I also lead the design team for our Electronics Association.\n\nI admire the work at {organisation} and would love to contribute to your initiatives.\n\nWarm regards,\nAayush Singh\n📧 code.aayush.19@gmail.com | 📱 +91-7451854550\n""",
    """Hello {name},\n\nI’m Aayush Singh, currently studying Electronics Engineering at HBTU.\n\nAt NIXI, I helped build a Django-based admin system with secure login and MySQL integration. I’ve also developed a stock analytics app and an IoT-based soil monitoring device.\n\nI’m very interested in the work at {organisation}, and I’ve attached my resume for your review.\n\nThank you,\nAayush Singh\n📧 code.aayush.19@gmail.com | 📱 +91-7451854550\n"""
]

# --- LOGGING SETUP ---
log_file = 'sent_log.csv'
if not os.path.exists(log_file):
    with open(log_file, 'w') as f:
        f.write('email,name,status,timestamp\n')

# --- EMAIL VALIDATION ---
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

# --- EMAIL SENDING FUNCTION ---
def send_email(to_email, name, body):
    try:
        message = EmailMessage()
        message['To'] = to_email
        message['From'] = 'me'
        message['Subject'] = "Internship Application – Aayush Singh (Data Science, Analysis & Web Projects)"
        message.set_content(body)

        with open(RESUME_PATH, 'rb') as f:
            message.add_attachment(
                f.read(),
                maintype='application',
                subtype='pdf',
                filename=os.path.basename(RESUME_PATH)
            )

        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        # Ensure fresh Gmail connection if needed
        global gmail_service
        gmail_service = get_gmail_service()

        gmail_service.users().messages().send(userId="me", body={'raw': encoded_message}).execute()
        return True

    except (socket.error, BrokenPipeError, HttpError) as e:
        print(f"⚠️ Retrying after connection error: {e}")
        time.sleep(30)
        try:
            gmail_service = get_gmail_service()
            gmail_service.users().messages().send(userId="me", body={'raw': encoded_message}).execute()
            return True
        except Exception as e2:
            print(f"❌ Retry failed: {e2}")
            return False
    except Exception as e:
        print(f"❌ Unhandled error: {e}")
        return False

# --- MAIN LOOP ---
for i, row in df.iterrows():
    name = row['name']
    email = row['email']
    organisation = row['organisation'] if 'organisation' in row else "your organization"

    if not is_valid_email(email):
        print(f"⚠️ Skipping invalid email: {email}")
        continue

    current_time = datetime.now()
    timestamp = current_time.strftime('%Y-%m-%d %H:%M:%S')
    template = TEMPLATES[i % len(TEMPLATES)]
    personalized_body = template.format(name=name, organisation=organisation)

    success = send_email(email, name, personalized_body)
    log_status = "Sent" if success else "Failed"

    with open(log_file, 'a') as f:
        f.write(f"{email},{name},{log_status},{timestamp}\n")

    if success:
        print(f"✅ Sent to {email} at {timestamp}")
    else:
        print(f"❌ Could not send to {email}")

    delay = random.randint(1150, 1250)  # around 19–21 minutes
    next_time = current_time + timedelta(seconds=delay)
    print(f"⏳ Waiting {delay // 60} minutes. Next email at {next_time.strftime('%Y-%m-%d %H:%M:%S')}...")
    time.sleep(delay)
