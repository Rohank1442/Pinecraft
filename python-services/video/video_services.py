import os
import math
import json
import subprocess
import requests
from io import BytesIO
from typing import List
from PIL import Image
from fastapi import FastAPI, File, Form, UploadFile
from dotenv import load_dotenv
from diffusers import StableDiffusionPipeline
import torch

# ────────────────────────────────────────────────
# ⚙️ Load environment + setup
# ────────────────────────────────────────────────
load_dotenv()
app = FastAPI()

TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)

STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")

# ────────────────────────────────────────────────
# 🎨 Load Stable Diffusion (local fallback)
# ────────────────────────────────────────────────
print("Loading full Stable Diffusion 2 model...")
pipe = StableDiffusionPipeline.from_pretrained(
    "stabilityai/stable-diffusion-2-1-base",
    torch_dtype=torch.float32  # use float16 if GPU available
)
pipe.to("cuda" if torch.cuda.is_available() else "cpu")
print("✅ Full model loaded successfully!")


# ────────────────────────────────────────────────
# 🧠 Helper: Get audio duration (seconds)
# ────────────────────────────────────────────────
def get_audio_duration(audio_path: str) -> float:
    """Return audio duration in seconds using ffprobe."""
    result = subprocess.run(
        [
            "ffprobe", "-v", "error", "-show_entries",
            "format=duration", "-of", "json", audio_path
        ],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    duration = float(json.loads(result.stdout)["format"]["duration"])
    return duration


# ────────────────────────────────────────────────
# 🖼️ Image Generation (API → Local Fallback)
# ────────────────────────────────────────────────
def generate_image(prompt: str, index: int):
    """
    Generate image using Stability AI first,
    then fall back to local Diffusers if needed.
    """
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

        # Save image
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
def create_video_from_images(images: List[str], audio_path: str, output_path: str, duration: float):
    """
    Create a video slideshow from images, synced to full audio length.
    Each image is displayed for 3 seconds.
    """
    segment_duration = 3
    total_duration = len(images) * segment_duration

    file_list_path = os.path.join(TEMP_DIR, "file_list.txt")

    # Write ffmpeg file list
    with open(file_list_path, "w") as f:
        for img in images:
            f.write(f"file '{os.path.abspath(img)}'\n")
            f.write(f"duration {segment_duration}\n")
        f.write(f"file '{os.path.abspath(images[-1])}'\n")

    # Create slideshow
    video_no_audio = os.path.join(TEMP_DIR, "slideshow.mp4")
    subprocess.run(
        [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", file_list_path,
            "-vf", "scale=720:1280,format=yuv420p",
            video_no_audio
        ],
        check=True
    )

    # Merge with audio (trim to shortest)
    subprocess.run(
        [
            "ffmpeg", "-y", "-i", video_no_audio, "-i", audio_path,
            "-c:v", "copy", "-c:a", "aac", "-shortest",
            output_path
        ],
        check=True
    )

    print(f"🎬 Final video created: {output_path}")
    return output_path


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

    # Save audio locally
    audio_path = os.path.join(TEMP_DIR, audio_file.filename)
    with open(audio_path, "wb") as f:
        f.write(await audio_file.read())

    # Get audio duration
    duration = get_audio_duration(audio_path)
    print(f"🎵 Audio duration: {duration:.2f} seconds")

    # Determine number of images needed (3s per image)
    image_count = math.ceil(duration / 3)
    print(f"🖼️ Need {image_count} images (3s each)")

    # Split or repeat text prompts
    segments = [s.strip() for s in text.split(". ") if s.strip()]
    if not segments:
        segments = ["Abstract galaxy background"]

    # Repeat prompts if fewer than needed
    if len(segments) < image_count:
        segments = (segments * math.ceil(image_count / len(segments)))[:image_count]
    else:
        segments = segments[:image_count]

    # Generate all images
    images = []
    for idx, segment in enumerate(segments):
        img_path = generate_image(segment, idx)
        images.append(img_path)

    # Create video
    output_video_path = os.path.join(TEMP_DIR, "final_video.mp4")
    create_video_from_images(images, audio_path, output_video_path, duration)

    return {"video_path": output_video_path}
