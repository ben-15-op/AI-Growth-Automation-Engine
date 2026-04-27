import sqlite3
from urllib.request import DataHandler
import config

def get_connection():
    """Returns a connection to the SQLite database."""
    return sqlite3.connect(config.DB_PATH)

def setup_db():
    """Initializes the database schema if it doesn't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    # Create the leads_log table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leads_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            company TEXT NOT NULL,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            replied BOOLEAN DEFAULT FALSE,
            follow_up_sent BOOLEAN DEFAULT FALSE,
            status TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def insert_lead_log(name, email, company, status, sent_at=None):
    """Inserts a new log entry when an email is sent."""
    conn = get_connection()
    cursor = conn.cursor()
    if sent_at:
        cursor.execute('''
            INSERT INTO leads_log (name, email, company, status, sent_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, email, company, status, sent_at))
    else:
        cursor.execute('''
            INSERT INTO leads_log (name, email, company, status)
            VALUES (?, ?, ?, ?)
        ''', (name, email, company, status))
    conn.commit()
    conn.close()

def get_follow_up_candidates():
    """
    Selects leads that:
    1. Have not replied (replied=FALSE)
    2. Have not received a follow-up yet (follow_up_sent=FALSE)
    3. The original email was sent > 3 days ago
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, name, email, company 
        FROM leads_log 
        WHERE replied = 0 
          AND follow_up_sent = 0 
          AND status = 'Sent'
          AND sent_at < datetime('now', '-3 days')
    ''')
    results = cursor.fetchall()
    conn.close()
    return results

def mark_follow_up_sent(log_id):
    """Marks a lead as having received a follow-up."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE leads_log 
        SET follow_up_sent = 1 
        WHERE id = ?
    ''', (log_id,))
    conn.commit()
    conn.close()

def mark_replied(email):
    """Marks a lead as having replied (typically driven by a webhook or external check)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE leads_log 
        SET replied = 1 
        WHERE email = ?
    ''', (email,))
    conn.commit()
    conn.close()
