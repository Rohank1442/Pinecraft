import os
import math
import json
import subprocess
import requests
from io import BytesIO
from typing import List
from PIL import Image
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from diffusers import StableDiffusionPipeline
from supabase import create_client, Client
import torch

# ────────────────────────────────────────────────
# ⚙️ Load environment + setup
# ────────────────────────────────────────────────
load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change this to your frontend domain later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)

# Supabase setup
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "reels-videos")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Stability AI key
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")

# ────────────────────────────────────────────────
# 🎨 Load Stable Diffusion
# ────────────────────────────────────────────────
print("Loading full Stable Diffusion 2 model...")
pipe = StableDiffusionPipeline.from_pretrained(
    "stabilityai/stable-diffusion-2-1-base",
    torch_dtype=torch.float32
)
pipe.to("cuda" if torch.cuda.is_available() else "cpu")
print("✅ Full model loaded successfully!")


# ────────────────────────────────────────────────
# 🧠 Helper: Get audio duration
# ────────────────────────────────────────────────
def get_audio_duration(audio_path: str) -> float:
    """Return audio duration in seconds using ffprobe."""
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", audio_path],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    duration = float(json.loads(result.stdout)["format"]["duration"])
    return duration


# ────────────────────────────────────────────────
# 🖼️ Image Generation (API → Local Fallback)
# ────────────────────────────────────────────────
def generate_image(prompt: str, index: int):
    try:
        print(f"🎨 Generating image {index + 1} via Stability API...")
        response = requests.post(
            "https://api.stability.ai/v2beta/stable-image/generate/core",
            headers={
                "Authorization": f"Bearer {STABILITY_API_KEY}",
                "Accept": "application/json"
            },
            files={"none": ""},
            data={"prompt": prompt, "output_format": "png"}
        )

        if response.status_code == 402 or "insufficient credits" in response.text.lower():
            raise Exception("No credits left for Stability API")

        if response.status_code != 200:
            raise Exception(f"Stability API failed: {response.text}")

        img = Image.open(BytesIO(response.content))
        path = f"{TEMP_DIR}/image_{index}.png"
        img.save(path)
        print(f"✅ Stability image saved: {path}")
        return path

    except Exception as e:
        print(f"⚠️ Falling back to local Diffusers: {e}")
        print("🧠 Generating image locally...")
        image = pipe(prompt).images[0]
        path = f"{TEMP_DIR}/image_{index}.png"
        image.save(path)
        print(f"✅ Local Diffusers image saved: {path}")
        return path


# ────────────────────────────────────────────────
# 🎞️ Create video from images + audio
# ────────────────────────────────────────────────
def create_video_from_images(images: List[str], audio_path: str, output_path: str):
    segment_duration = 3
    file_list_path = os.path.join(TEMP_DIR, "file_list.txt")

    with open(file_list_path, "w") as f:
        for img in images:
            f.write(f"file '{os.path.abspath(img)}'\n")
            f.write(f"duration {segment_duration}\n")
        f.write(f"file '{os.path.abspath(images[-1])}'\n")

    video_no_audio = os.path.join(TEMP_DIR, "slideshow.mp4")
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", file_list_path,
         "-vf", "scale=720:1280,format=yuv420p", video_no_audio],
        check=True
    )

    subprocess.run(
        ["ffmpeg", "-y", "-i", video_no_audio, "-i", audio_path,
         "-c:v", "copy", "-c:a", "aac", "-shortest", output_path],
        check=True
    )

    print(f"🎬 Final video created: {output_path}")
    return output_path


# ────────────────────────────────────────────────
# ☁️ Upload to Supabase
# ────────────────────────────────────────────────
def upload_to_supabase(local_path: str, filename: str):
    print("☁️ Uploading video to Supabase...")
    with open(local_path, "rb") as f:
        res = supabase.storage.from_(SUPABASE_BUCKET).upload(filename, f, {"content-type": "video/mp4", "upsert": True})

    if res.get("error"):
        raise Exception(f"Supabase upload error: {res['error']}")

    public_url = supabase.storage.from_(SUPABASE_BUCKET).get_public_url(filename)
    print(f"✅ Uploaded to Supabase: {public_url}")
    return public_url


# ────────────────────────────────────────────────
# 🚀 API Endpoint
# ────────────────────────────────────────────────
@app.post("/generate")
async def generate_video(
    text: str = Form(...),
    audio_file: UploadFile = File(...),
):
    print(f"📝 Text prompt received:\n{text}")
    print(f"🎧 Audio file: {audio_file.filename}")

    audio_path = os.path.join(TEMP_DIR, audio_file.filename)
    with open(audio_path, "wb") as f:
        f.write(await audio_file.read())

    duration = get_audio_duration(audio_path)
    print(f"🎵 Audio duration: {duration:.2f} seconds")

    image_count = math.ceil(duration / 3)
    print(f"🖼️ Need {image_count} images (3s each)")

    segments = [s.strip() for s in text.split(". ") if s.strip()]
    if not segments:
        segments = ["Abstract galaxy background"]

    if len(segments) < image_count:
        segments = (segments * math.ceil(image_count / len(segments)))[:image_count]
    else:
        segments = segments[:image_count]

    images = []
    for idx, segment in enumerate(segments):
        img_path = generate_image(segment, idx)
        images.append(img_path)

    output_video_filename = f"final_{os.path.splitext(audio_file.filename)[0]}.mp4"
    output_video_path = os.path.join(TEMP_DIR, output_video_filename)
    create_video_from_images(images, audio_path, output_video_path)

    # ☁️ Upload to Supabase
    video_url = upload_to_supabase(output_video_path, output_video_filename)

    return {
        "video_url": video_url,
        "duration": duration,
        "image_count": image_count,
    }
