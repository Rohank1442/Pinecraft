# python-services/voice/voice_services.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from gtts import gTTS
import os, uuid

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

VOICE_DIR = "voice_outputs"
os.makedirs(VOICE_DIR, exist_ok=True)

@app.post("/voice/generate")
async def generate_voice(req: Request):
    data = await req.json()
    text = data.get("text")
    if not text:
        raise HTTPException(status_code=400, detail="Missing 'text'")
    filename = f"voice_{uuid.uuid4()}.mp3"
    filepath = os.path.join(VOICE_DIR, filename)
    # mock toggle (optional)
    if os.getenv("USE_MOCK_VOICE", "false").lower() == "true":
        with open(filepath, "wb") as f:
            f.write(b"FAKE_MP3_DATA")
        return {"url": f"http://localhost:8000/voice_outputs/{filename}"}
    # real TTS
    tts = gTTS(text=text, lang="en")
    tts.save(filepath)
    return {"url": f"http://localhost:8000/voice_outputs/{filename}"}

# serve static files
from fastapi.staticfiles import StaticFiles
app.mount("/voice_outputs", StaticFiles(directory=VOICE_DIR), name="voice_outputs")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("voice_services:app", host="0.0.0.0", port=8000, reload=True)
