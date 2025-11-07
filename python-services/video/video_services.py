import os
import time
import requests
from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from uuid import uuid4
from dotenv import load_dotenv
from google.oauth2 import service_account
from google.auth.transport.requests import Request

# -------------------------------------------------------
# Load environment variables
# -------------------------------------------------------
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# ⚠️ Use double backslashes OR forward slashes for Windows paths
GOOGLE_CREDENTIALS_PATH = r"C:\Users\rohan\Downloads\pinecraft-ai-af5d1a4cb868.json"

# Load service account credentials if available
credentials = None
if os.path.exists(GOOGLE_CREDENTIALS_PATH):
    credentials = service_account.Credentials.from_service_account_file(GOOGLE_CREDENTIALS_PATH)
    print("✅ Loaded Google service account credentials.")
else:
    print("⚠️ Using only API key auth (no service account found).")

# -------------------------------------------------------
# FastAPI App Setup
# -------------------------------------------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------
# Generate Video Endpoint
# -------------------------------------------------------
@app.post("/generate")
async def generate_video(text: str = Form(...), audio_file: UploadFile = None):
    """
    Generates a 30-second AI video using Google Veo 3 with uploaded audio + script text.
    """
    if not audio_file:
        raise HTTPException(status_code=400, detail="Audio file missing")

    # Save uploaded audio locally
    local_audio_path = f"temp_{uuid4()}_{audio_file.filename}"
    with open(local_audio_path, "wb") as f:
        f.write(await audio_file.read())

    print(f"🎧 Received audio file: {local_audio_path}")
    print(f"📝 Prompt: {text}")

    # Prepare auth headers
    headers = {}
    if credentials:
        credentials.refresh(Request())
        headers["Authorization"] = f"Bearer {credentials.token}"
    elif GOOGLE_API_KEY:
        headers["x-goog-api-key"] = GOOGLE_API_KEY
    else:
        raise HTTPException(status_code=500, detail="Missing Google credentials")

    # Prepare Veo-3 API payload
    veo_api_url = "https://generativelanguage.googleapis.com/v1beta/models/veo-3:generateVideo"
    payload = {
        "model": "veo-3",
        "prompt": text,
        "duration": 30,
        "aspect_ratio": "9:16",
    }

    files = {
        "audio": (os.path.basename(local_audio_path), open(local_audio_path, "rb"), "audio/mpeg")
    }

    # Call the Veo-3 API
    response = requests.post(veo_api_url, headers=headers, data=payload, files=files)

    if response.status_code != 200:
        print("❌ Veo-3 Error:", response.text)
        os.remove(local_audio_path)
        raise HTTPException(status_code=500, detail=f"Veo 3 API error: {response.text}")

    data = response.json()
    operation_id = data.get("name")
    print(f"🎬 Video generation started (operation ID: {operation_id})")

    # Poll for completion
    video_url = None
    for attempt in range(20):
        poll = requests.get(
            f"https://generativelanguage.googleapis.com/v1beta/{operation_id}",
            headers=headers,
        )
        poll_data = poll.json()

        if "response" in poll_data and "videoUri" in poll_data["response"]:
            video_url = poll_data["response"]["videoUri"]
            break

        print(f"⏳ Waiting for video… ({attempt + 1}/20)")
        time.sleep(5)

    os.remove(local_audio_path)

    if not video_url:
        raise HTTPException(status_code=504, detail="Video generation timed out")

    print(f"✅ Video ready: {video_url}")
    return {"message": "Video generated successfully", "url": video_url}

# -------------------------------------------------------
# Run Locally
# -------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("video_services:app", host="0.0.0.0", port=8001, reload=True)
