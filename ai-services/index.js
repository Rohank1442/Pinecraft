import { generateScript } from "../ai-services/text/textGenerator.js";
import { generateVoice } from "../ai-services/voice/voiceGenerator.js";
import { generateVideo } from "../ai-services/video/videoGenerator.js"

export async function generateReelPipeline(topic) {
  const script = await generateScript(topic);
  const voice = await generateVoice(script.content);
  const video = await generateVideo(script.content, voice.url)

  return { script, voice, video };
}