"""Central configuration for AI Growth Automation Engine."""

import os

# --- API KEYS & SECRETS ---
# Keep secrets in environment variables. Never hardcode real secrets in source.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyCS1pBSdGtM9T0I1gCwgOLssmwry9k5Fn0")

# --- GMAIL CONFIGURATION ---
GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

# --- FILE PATHS ---
DB_PATH = "leads_tracking.db"
LEADS_CSV_PATH = "leads.csv"
CREDENTIALS_PATH = "credentials.json"
TOKEN_PATH = "token.json"

# --- APP CONSTANTS ---
OUTREACH_SUBJECT_TEMPLATE = "Quick idea for {company}'s {role} priorities"
FOLLOW_UP_SUBJECT_TEMPLATE = "Following up: improving workflows at {company}"

# Delay between outreach sends (18-22 minutes in seconds)
MIN_DELAY_SECONDS = 2
MAX_DELAY_SECONDS = 5

# LLM model requirement from spec
LLM_MODEL = "gemini-2.0-flash"

SYSTEM_PROMPT = """You are an expert B2B sales development representative helping to pitch an AI Growth Automation Engine. 
Your goal is to write a highly personalized, compelling, and professional outreach email. 
Keep the tone helpful and solution-oriented."""
