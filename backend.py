from fastapi import FastAPI, Request, Response
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import csv
import os
from datetime import datetime

app = FastAPI()

# CORS for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory logs
opens = []
clicks = []
unsubscribes = []

@app.get("/")
def home():
    return {"message": "Email Tracker Backend is Live!"}

@app.get("/pixel.png")
def pixel(email: str):
    timestamp = datetime.utcnow().isoformat()
    opens.append({"email": email, "timestamp": timestamp})
    return FileResponse("pixel.png", media_type="image/png")

@app.get("/click")
def click(email: str, url: str):
    timestamp = datetime.utcnow().isoformat()
    clicks.append({"email": email, "url": url, "timestamp": timestamp})
    return RedirectResponse(url)

@app.get("/unsubscribe")
def unsubscribe(email: str):
    timestamp = datetime.utcnow().isoformat()
    unsubscribes.append({"email": email, "timestamp": timestamp})
    return Response(
        content=f"<h2>You have been unsubscribed, {email}</h2>",
        media_type="text/html"
    )

@app.get("/status")
def status():
    return {
        "opens": opens,
        "clicks": clicks,
        "unsubscribes": unsubscribes
    }
