# 🤖 AI-Powered Internship Email Automation Agent

An intelligent Python-based tool that automates cold-email outreach for internships using personalized content, Google Sheets, and Gmail APIs.

## 🚀 Features

- 🔄 Fetches recipient data (Name, Email, Organization) from Google Sheets
- 📩 Sends personalized emails using Gmail API
- 📎 Attaches resume automatically (PDF)
- 💬 Rotates between 4 message templates
- 🕓 Adds random delay between emails (to avoid spam filters)
- 🧠 Email validation using regex
- 📊 Logging system to track sent status and time
- 🔁 Handles Broken Pipe and API retry logic

## 🛠️ Tech Stack

- Python, Pandas, Regex  
- Gmail API, Google Sheets API, OAuth2  
- EmailMessage, base64  
- Google Cloud Console
## 📁 Folder Structure

project-folder/
├── script.py # Main email automation script
├── credentials.json # Google API credentials (downloaded from Google Cloud Console)
├── token.json # OAuth access token (auto-generated on first run)
├── resume.pdf # Resume to attach with emails
├── sent_log.csv # Logs each sent email's status and timestamp
├── README.md # Project documentation
└── .venv/ # Python virtual environment (optional but recommended)


## 📌 How It Works

1. Authorizes with Gmail & Sheets using OAuth2  
2. Pulls recipient info from Google Sheet  
3. Randomly selects and personalizes a message template  
4. Sends email with resume attachment  
5. Waits 20±1 minutes and repeats

## 🔐 Setup Instructions

1. Clone the repo  
2. Add `credentials.json` from your Google Cloud Console  
3. Place your `resume.pdf` in the root directory  
4. Run `script.py` using Python 3.9+  
5. Authorize via browser on first run

## 🧠 Inspiration

Built to streamline internship outreach while maintaining personalization and avoiding Gmail spam traps — a perfect mix of automation and human touch.

## 🙋‍♂️ About Me

**Aayush Singh**  
Final-year B.Tech Electronics Engineering  
💡 Passionate about Data Science, ML, Full Stack, and Automation  
📫 [LinkedIn](https://www.linkedin.com/in/aayush-singh-49a949271/) | ✉️ code.aayush.19@gmail.com

---

Feel free to ⭐ the repo if you found it interesting!
