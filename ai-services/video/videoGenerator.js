import axios from "axios";
import FormData from "form-data";

const PYTHON_VIDEO_API = "http://127.0.0.1:8001/generate";

export async function generateVideo(scriptText, voiceUrl) {
  try {
    console.log("🎬 Sending text + audio to Python video service...");

    // Fetch the audio file
    const audioResponse = await axios.get(voiceUrl, { responseType: "arraybuffer" });

    // Create FormData for upload
    const formData = new FormData();
    formData.append("text", scriptText);
    formData.append("audio_file", Buffer.from(audioResponse.data), {
      filename: "voice.mp3",
      contentType: "audio/mpeg",
    });

    // Send to FastAPI
    const response = await axios.post(PYTHON_VIDEO_API, formData, {
      headers: formData.getHeaders(),
    });

    return { url: response.data.url };
  } catch (error) {
    console.error("❌ Error generating video:", error.response?.data || error.message);
    throw new Error("Video generation failed");
  }
}
