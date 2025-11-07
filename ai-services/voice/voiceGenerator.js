import axios from "axios";

const PYTHON_VOICE_API = "http://127.0.0.1:8000/voice/generate";

export async function generateVoice(scriptText) {
  try {
    console.log("🎤 Sending text to Python TTS service...");
    const response = await axios.post(PYTHON_VOICE_API, { text: scriptText });

    if (response.data && response.data.url) {
      console.log("Voice generated:", response.data.url);
      return { url: response.data.url };
    } else {
      throw new Error("Invalid response from Python service");
    }
  } catch (error) {
    console.error("❌ Error generating voice:", error.message);
    throw new Error("Voice generation failed");
  }
}
