# AI Growth Automation Engine

## Project Overview

**AI Growth Automation Engine** is an intelligent, automated system for generating and sending personalized B2B outreach emails. This project solves the problem of high manual effort in sales outreach by leveraging Large Language Models (LLMs) to craft highly specific, context-aware emails based on structured lead data.

**Key Technical Achievements:**
- **Developed an automated system for generating personalized outreach emails using LLM APIs.**
- **Integrated Gmail API and structured prompts to create context-aware email content.**
- **Implemented workflow logic for sending emails and managing follow-ups.**
- **Focused on building a practical automation tool to reduce manual outreach effort.**

## Architecture & Data Flow

```text
 +-----------+       +----------------+       +--------------+
 | leads.csv | ----> | Prompt Builder | ----> |   LLM API    |
 | (Inputs)  |       |  (Structured)  |       | (Google Gem) |
 +-----------+       +----------------+       +--------------+
                                                     |
                                                     v
 +--------------+                             +--------------+
 |  SQLite DB   |                             |  Gmail API   |
 | (Lead State) | <-------------------------- |  (OAuth2)    |
 +--------------+                             +--------------+
        |                                            ^
        |            +--------------------+          |
        +----------> | Follow-up Checker  | ---------+
                     | (sent_at > 3 days) |
                     +--------------------+
```

## Setup Instructions

### 1. Prerequisites
- Python 3.8+
- A Google Desktop Application OAuth Credentials JSON.
- A Google AI Studio (Gemini) API Key.

### 2. Environment Setup
Install the necessary python dependencies (you will need google-api-python-client, google-auth-oauthlib, and google-generativeai):
```bash
pip install -r requirements.txt
```

### 3. API Keys and Credentials

**Google Gemini API Key**
Create a free API key at [Google AI Studio](https://aistudio.google.com/app/apikey) and set it as an environment variable:
```bash
# On Mac/Linux:
export GEMINI_API_KEY="your-api-key"

# On Windows:
set GEMINI_API_KEY="your-api-key"
```

**Gmail API OAuth2**
1. Go to the [Google Cloud Console](https://console.cloud.google.com).
2. Create a new project and enable the **Gmail API**.
3. Configure the OAuth Consent Screen.
4. Create **OAuth Client ID** credentials (Desktop Application).
5. Download the JSON file and rename it to `credentials.json`.
6. Place `credentials.json` in the root directory of this project.

### 4. Running the Engine
Simply run the script to process leads and check for queued follow-ups:
```bash
python main.py
```
On the first run, a browser window will open to authorize your Gmail account. Once authorized, a `token.json` file is generated for future headless operations.

## n8n Workflow

While this engine functions perfectly as a standalone Python script, it is designed to be easily integrated into broader business automation workflows using tools like **n8n**. 

**Recommended n8n Setup for Follow-up Management:**
1. **Cron Trigger Node**: Set to run daily at 9:00 AM.
2. **Execute Command Node**: Executes the python logic or triggers an HTTP endpoint wrapping `main.py`.
3. **Database Read/Write Node (SQLite/Postgres)**: By exposing the database, n8n can query the `leads_log` table directly to monitor daily campaign volumes and calculate reply rates.
4. **Webhook Node (Optional)**: Can be used to receive incoming email webhooks (via Gmail push notifications or parsed email services), directly triggering `mark_replied()` in the database so the script intuitively halts follow-ups the moment a prospect responds.

*This logical orchestration ensures no hot leads are missed while keeping your codebase completely decoupled from complex cron job setups.*
