from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os
import csv

app = FastAPI()

# CORS for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# CSV Path
CSV_FILE_PATH = 'email_status.csv'

# In-memory logs
opens = []
clicks = []
unsubscribes = []

# Ensure CSV file exists, if not create it
if not os.path.exists(CSV_FILE_PATH):
    with open(CSV_FILE_PATH, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Email', 'Status', 'Opened', 'Clicked', 'Unsubscribed', 'Timestamp'])

def update_email_status(email: str, status: str, opened=False, clicked=False, unsubscribed=False):
    # Read the current CSV contents
    rows = []
    email_found = False
    with open(CSV_FILE_PATH, mode='r') as file:
        reader = csv.reader(file)
        rows = list(reader)

    # Check if the email already exists, if so update it
    for i, row in enumerate(rows):
        if row[0] == email:
            rows[i] = [email, status, opened, clicked, unsubscribed, datetime.utcnow().isoformat()]
            email_found = True
            break
    
    # If email not found, add new row
    if not email_found:
        rows.append([email, status, opened, clicked, unsubscribed, datetime.utcnow().isoformat()])

    # Write the updated rows back to the CSV
    with open(CSV_FILE_PATH, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(rows)

@app.get("/")
def home():
    return {"message": "Email Tracker Backend is Live!"}

@app.get("/pixel.png")
def pixel(email: str):
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")

    timestamp = datetime.utcnow().isoformat()
    opens.append({"email": email, "timestamp": timestamp})
    
    # Update email status in CSV to 'Opened'
    update_email_status(email, 'Opened', opened=True)
    
    return FileResponse("pixel.png", media_type="image/png")

@app.get("/click")
def click(email: str, url: str):
    if not email or not url:
        raise HTTPException(status_code=400, detail="Email and URL are required")

    timestamp = datetime.utcnow().isoformat()
    clicks.append({"email": email, "url": url, "timestamp": timestamp})
    
    # Update email status in CSV to 'Clicked'
    update_email_status(email, 'Clicked', clicked=True)
    
    return RedirectResponse(url)

@app.get("/unsubscribe")
def unsubscribe(email: str):
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")

    timestamp = datetime.utcnow().isoformat()
    unsubscribes.append({"email": email, "timestamp": timestamp})
    
    # Update email status in CSV to 'Unsubscribed'
    update_email_status(email, 'Unsubscribed', unsubscribed=True)
    
    return Response(
        content=f"<h2>You have been unsubscribed, {email}</h2>",
        media_type="text/html"
    )

@app.get("/status")
def status():
    # Return all logs as a JSON response
    return {
        "opens": opens,
        "clicks": clicks,
        "unsubscribes": unsubscribes
    }
