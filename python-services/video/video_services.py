import os
import json
import time
import requests
from fastapi import FastAPI, File, Form, UploadFile
from google.oauth2 import service_account
from google.auth.transport.requests import Request

app = FastAPI()

# ────────────────────────────────────────────────
# 🔐 Load Google credentials
# ────────────────────────────────────────────────
SERVICE_ACCOUNT_PATH = r"C:\Users\rohan\Downloads\pinecraft-ai-af5d1a4cb868.json"
PROJECT_ID = "pinecraft-ai"
LOCATION = "us-central1"
MODEL_ID = "veo-3.0-generate-001"

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_PATH,
    scopes=["https://www.googleapis.com/auth/cloud-platform"],
)

# ────────────────────────────────────────────────
# 🔁 Helper: Get access token
# ────────────────────────────────────────────────
def get_access_token():
    credentials.refresh(Request())
    return credentials.token

# ────────────────────────────────────────────────
# 🧩 Video Generation Endpoint
# ────────────────────────────────────────────────
@app.post("/generate")
async def generate_video(
    audio_file: UploadFile = File(...),  # 👈 match Node.js field name
    text: str = Form(...)                # 👈 match Node.js field name
):
    print(f"🎧 Received audio file: {audio_file.filename}")
    print(f"📝 Text prompt: {text}")

    # Save the audio file temporarily
    audio_path = f"temp_{audio_file.filename}"
    with open(audio_path, "wb") as f:
        f.write(await audio_file.read())

    try:
        access_token = get_access_token()
        endpoint = (
            f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/"
            f"locations/{LOCATION}/publishers/google/models/{MODEL_ID}:predictLongRunning"
        )

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        # Build the Vertex AI request payload
        payload = {
            "instances": [
                {
                    "prompt": text,          # 👈 use the text field
                    "aspectRatio": "9:16",
                    "resolution": "720p",
                }
            ],
            "parameters": {
                "responseCount": 1
            }
        }

        # ────────────────────────────────────────────────
        # 🚀 Send the video generation request
        # ────────────────────────────────────────────────
        response = requests.post(endpoint, headers=headers, data=json.dumps(payload))
        if response.status_code != 200:
            print(f"❌ Request Error: {response.text}")
            return {"error": response.text}

        operation = response.json()
        operation_name = operation.get("name")
        print(f"🎬 Operation started: {operation_name}")

        # ────────────────────────────────────────────────
        # ⏳ Poll until video is ready
        # ────────────────────────────────────────────────
        op_url = f"https://{LOCATION}-aiplatform.googleapis.com/v1/{operation_name}"
        while True:
            op_res = requests.get(op_url, headers=headers)
            result = op_res.json()
            if result.get("done"):
                print("✅ Video generation complete!")
                break
            print("⏳ Waiting for video to be ready...")
            time.sleep(10)

        # ────────────────────────────────────────────────
        # 🎥 Return video URI
        # ────────────────────────────────────────────────
        output = result.get("response", {}).get("predictions", [{}])[0]
        video_uri = output.get("videoUri")
        return {"url": video_uri or "No URI found"}

    except Exception as e:
        print(f"❌ Exception: {e}")
        return {"error": str(e)}
