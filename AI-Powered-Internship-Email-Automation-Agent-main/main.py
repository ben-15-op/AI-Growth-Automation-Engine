import os
import csv
import time
import random
import base64
from datetime import datetime
from email.message import EmailMessage

import google.generativeai as genai
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

import config
import database

# Ensure DB is setup on import
database.setup_db()

# Initialise Gemini client with the API key from config
genai.configure(api_key=config.GEMINI_API_KEY)

def load_leads():
    """Reads from leads.csv with columns: name, email, company, role, pain_point"""
    leads = []
    if not os.path.exists(config.LEADS_CSV_PATH):
        print(f"File not found: {config.LEADS_CSV_PATH}")
        return leads

    with open(config.LEADS_CSV_PATH, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Basic validation
            if row.get('name') and row.get('email'):
                leads.append(row)
    return leads


def build_prompt(lead):
    """Constructs an LLM prompt injecting lead's name, company, role, pain_point"""
    return f"""
Please write a short, highly personalized B2B outreach email for the following lead.
Make it concise (under 120 words), friendly, and solution-oriented. 
Do not include subject line in the output, just the email body.

Name: {lead.get('name')}
Role: {lead.get('role')}
Company: {lead.get('company')}
Pain Point: {lead.get('pain_point')}

Focus on how our "AI Growth Automation Engine" can solve their specific pain point.
"""


def generate_email_llm(prompt):
    """Calls Gemini API (gemini-2.0-flash) and returns generated email text"""
    try:
        model = genai.GenerativeModel(config.LLM_MODEL)
        response = model.generate_content(config.SYSTEM_PROMPT + "\n\n" + prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error generating LLM email: {e}")
        return None


def get_gmail_service():
    """Authenticates and returns the Gmail API service"""
    creds = None
    if os.path.exists(config.TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(config.TOKEN_PATH, config.GMAIL_SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(config.CREDENTIALS_PATH):
                print(f"Missing {config.CREDENTIALS_PATH}! Please download your OAuth client secret from Google Cloud.")
                return None
            flow = InstalledAppFlow.from_client_secrets_file(config.CREDENTIALS_PATH, config.GMAIL_SCOPES)
            creds = flow.run_local_server(port=0)
        with open(config.TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)


def send_email(to, subject, body):
    """Sends via Gmail API with OAuth2"""
    service = get_gmail_service()
    if not service:
        return False
    
    try:
        message = EmailMessage()
        message.set_content(body)
        message['To'] = to
        message['From'] = 'me'
        message['Subject'] = subject

        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {'raw': encoded_message}

        send_message = service.users().messages().send(userId="me", body=create_message).execute()
        print(f"Message Id: {send_message['id']}")
        return True
    except Exception as e:
        print(f"An error occurred while sending email: {e}")
        return False


def log_to_db(lead, status):
    """Logs to SQLite: name, email, company, sent_at, replied=False, follow_up_sent=False"""
    # Assuming successful save uses timestamp automatically via DB defaults.
    database.insert_lead_log(
        name=lead.get('name', 'Unknown'),
        email=lead.get('email', 'Unknown'),
        company=lead.get('company', 'Unknown'),
        status=status
    )


def send_followups():
    """Queries DB for replied=False AND sent_at > 3 days ago AND follow_up_sent=False, sends follow-up, updates DB"""
    candidates = database.get_follow_up_candidates()
    if not candidates:
        print("No follow-ups needed at this time.")
        return

    for candidate in candidates:
        log_id, name, email, company = candidate
        
        # Simple hardcoded follow-up template or could be LLM generated
        subject = f"Following up: AI Growth Engine for {company}"
        body = f"Hi {name},\n\nJust bubbling this up in your inbox. Are you still experiencing bottlenecks with your current processes at {company}? Let's chat.\n\nBest,\nYour Automated Agent"
        
        print(f"Sending follow-up to {email}...")
        success = send_email(email, subject, body)
        if success:
            database.mark_follow_up_sent(log_id)
            print(f"Follow-up successfully sent and logged for {email}.")
        else:
            print(f"Failed to send follow-up to {email}.")


def main():
    """Orchestrates everything with 18–22 min random delay between sends"""
    print("--- Starting AI Growth Automation Engine ---")
    
    # 1. Process new leads
    leads = load_leads()
    if not leads:
        print("No leads found in leads.csv to process.")
    
    for lead in leads:
        print(f"\nProcessing target: {lead.get('email')}")
        
        # Build prompt and generate email
        prompt = build_prompt(lead)
        email_body = generate_email_llm(prompt)
        
        if not email_body:
            print("Skipping lead due to LLM generation failure.")
            continue
        
        subject = f"Optimizing {lead.get('company')}'s Workflows with AI"
        
        # Send Email
        success = send_email(lead.get('email'), subject, email_body)
        
        # Log to SQLite
        status = "Sent" if success else "Failed"
        log_to_db(lead, status)
        
        if success:
            # Delay based on config constants
            delay = random.randint(config.MIN_DELAY_SECONDS, config.MAX_DELAY_SECONDS)
            print(f"Wait triggered: Sleeping for {delay // 60} minutes and {delay % 60} seconds before next action to respect limits and avoid spam flags...")
            # For demonstration / testing purposes, you can comment this sleep out
            time.sleep(delay)

    # 2. Process Follow-ups
    print("\n--- Checking for required follow-ups ---")
    send_followups()
    
    print("\n--- Campaign Cycle Complete ---")


if __name__ == "__main__":
    main()
