import os
import json
import requests
from fastapi import FastAPI, File, Form, UploadFile
from google.oauth2 import service_account
from google.auth.transport.requests import Request

app = FastAPI()

# ────────────────────────────────────────────────
# 🔐 Google Cloud Setup
# ────────────────────────────────────────────────
SERVICE_ACCOUNT_PATH = r"C:\Users\rohan\Downloads\pinecraft-ai-6a82b64d0911.json"  # ✅ Use your actual JSON file path
PROJECT_ID = "pinecraft-ai"
LOCATION = "us-central1"
MODEL_ID = "veo-3.0-generate-001"

# Load service account credentials
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_PATH,
    scopes=["https://www.googleapis.com/auth/cloud-platform"],
)

# ────────────────────────────────────────────────
# 🔁 Helper: Get Access Token
# ────────────────────────────────────────────────
def get_access_token():
    credentials.refresh(Request())
    return credentials.token


# ────────────────────────────────────────────────
# 🎥 Video Generation Endpoint
# ────────────────────────────────────────────────
@app.post("/generate")
async def generate_video(
    audio_file: UploadFile = File(...),
    text: str = Form(...)
):
    print(f"🎧 Received audio file: {audio_file.filename}")
    print(f"📝 Text prompt: {text}")

    # Save audio temporarily (optional)
    audio_path = f"temp_{audio_file.filename}"
    with open(audio_path, "wb") as f:
        f.write(await audio_file.read())

    try:
        # ────────────────────────────────────────────────
        # 🚀 Call Veo model directly with predict
        # ────────────────────────────────────────────────
        access_token = get_access_token()
        endpoint = (
            f"https://{LOCATION}-aiplatform.googleapis.com/v1/"
            f"projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/{MODEL_ID}:predict"
        )

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        # Build the payload for Veo 3.0 video generation
        payload = {
            "instances": [
                {
                    "prompt": text,
                    "aspectRatio": "9:16",
                    "resolution": "720p",
                }
            ],
            "parameters": {"responseCount": 1},
        }

        response = requests.post(endpoint, headers=headers, data=json.dumps(payload))

        if response.status_code != 200:
            print(f"❌ Request Error: {response.text}")
            return {"error": response.text}

        result = response.json()

        # ────────────────────────────────────────────────
        # 🎥 Extract and return the video URI
        # ────────────────────────────────────────────────
        try:
            predictions = result.get("predictions", [])
            if not predictions:
                print("⚠️ No predictions in response")
                print("Raw response:", result)
                return {"error": "No predictions found"}

            output = predictions[0]
            video_uri = (
                output.get("videoUri")
                or output.get("uri")
                or "No video URI found in response"
            )

            print(f"📽️ Final video URI: {video_uri}")
            return {"video_uri": video_uri}

        except Exception as parse_error:
            print(f"❌ Error parsing video response: {parse_error}")
            print("Raw response:", result)
            return {"error": str(parse_error)}

    except Exception as e:
        print(f"❌ Exception: {e}")
        return {"error": str(e)}

    finally:
        if os.path.exists(audio_path):
            os.remove(audio_path)
