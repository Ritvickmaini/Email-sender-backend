from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os

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

# Make sure the pixel.png file exists
PIXEL_PATH = "pixel.png"
if not os.path.exists(PIXEL_PATH):
    with open(PIXEL_PATH, 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n...')  # Placeholder PNG binary data

@app.get("/")
def home():
    return {"message": "Email Tracker Backend is Live!"}

@app.get("/pixel.png")
def pixel(email: str):
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")

    timestamp = datetime.utcnow().isoformat()
    opens.append({"email": email, "timestamp": timestamp})
    return FileResponse(PIXEL_PATH, media_type="image/png")

@app.get("/click")
def click(email: str, url: str):
    if not email or not url:
        raise HTTPException(status_code=400, detail="Email and URL are required")

    timestamp = datetime.utcnow().isoformat()
    clicks.append({"email": email, "url": url, "timestamp": timestamp})
    return RedirectResponse(url)

@app.get("/unsubscribe")
def unsubscribe(email: str):
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")

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
