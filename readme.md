---

```markdown
# 🎥 PineReel Backend

PineReel is an **AI-powered backend service** that generates dynamic background videos and music suggestions for reels.  
It integrates **Stable Diffusion 2** (via `diffusers`) for local frame generation, uses **FFmpeg** for video composition, and supports **Node.js** clients for end-to-end automation.

---

## 🚀 Features

* 🎨 **Stable Diffusion 2 Integration** – Generate stunning visuals using Hugging Face’s `diffusers` library.  
* ⚡ **FastAPI Backend** – High-performance async backend with Python + Uvicorn.  
* 🧠 **Offline AI Model Option** – Use locally downloaded Stable Diffusion models to avoid API costs.  
* ☁️ **Stability AI API Option** – Optionally integrate with Stability AI cloud API for faster inference.  
* 🎞️ **FFmpeg Video Composer** – Combines AI-generated frames and voiceovers into full-length videos.  
* 🗄️ **Supabase Integration** – Stores generated video metadata and URLs in a managed database.  
* 🌐 **Node.js API Bridge** – Seamless connection to frontend or workflow orchestrators.  
* 📁 **Organized Project Structure** – Modular folder structure for clarity and scalability.

---

````

---

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Rohank1442/Pinecraft.git
cd pinecraft/python-services/video
````

---

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate    # (Mac/Linux)
venv\Scripts\activate       # (Windows)
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

If you don’t have a `requirements.txt`, here’s what it should include:

```txt
diffusers
transformers
torch
accelerate
safetensors
pillow
fastapi
uvicorn
python-dotenv
requests
ffmpeg-python
```

---

### 4. Install FFmpeg (Required)

PineReel uses **FFmpeg** for merging images and audio into video files.

#### 🧩 Install on Windows:

Download the latest FFmpeg from [ffmpeg.org/download](https://ffmpeg.org/download.html)
Then add the `bin` folder to your **system PATH**.

#### 🧩 Install on macOS (Homebrew):

```bash
brew install ffmpeg
```

#### 🧩 Install on Linux:

```bash
sudo apt update && sudo apt install ffmpeg
```

Check installation:

```bash
ffmpeg -version
```

---

### 5. (Optional) Download Stable Diffusion Model Locally

To avoid API calls and run fully offline:

```bash
huggingface-cli download stabilityai/stable-diffusion-2-1-base
```

Or you can rely on `from_pretrained("stabilityai/stable-diffusion-2-1-base")` (it will auto-download).

---

---

### 7. Run the FastAPI Server

```bash
uvicorn video_services:app --reload --port 8001
```

---

## 💻 How It Works

1. User provides a **script text** and **audio file** (voiceover).
2. The backend:

   * Calculates the audio duration.
   * Splits or repeats the text into segments.
   * Generates 1 image per 3 seconds of audio using Stable Diffusion.
   * Uses **FFmpeg** to assemble these into a video slideshow.
   * Merges the final audio with the video.
3. The completed video is returned or uploaded to **Supabase Storage**.

---

---

## 🧰 Tech Stack

| Component         | Technology                                                   |
| ----------------- | ------------------------------------------------------------ |
| Backend Framework | FastAPI                                                      |
| AI Model          | Stable Diffusion 2 (`diffusers`)                             |
| Model Hosting     | Local / Hugging Face / Stability AI API                      |
| Language          | Python                                                       |
| Video Engine      | FFmpeg                                                       |
| Database/Storage  | Supabase                                                     |
| Node Bridge       | Axios + Express                                              |
| Dependencies      | `torch`, `diffusers`, `requests`, `fastapi`, `ffmpeg-python` |

---

```

---

## 🧑‍💻 Author

**Rohan Kumar**
🌍 [LinkedIn](https://www.linkedin.com/in/rohan-kumar-1656b923b/)

```

---
