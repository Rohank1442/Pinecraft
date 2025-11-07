import { supabase } from "../lib/supabaseClient.js";
import { generateReelPipeline } from "../../ai-services/index.js";

export const generateReel = async (req, res) => {
    console.log("Generating reel...");
  try {
    console.log("Request body:", req.body);
    const { topic, userId } = req.body;

    if (!topic || !userId)
      return res.status(400).json({ message: "Missing topic or userId" });

    const { script, voice, video } = await generateReelPipeline(topic);

    const { data, error } = await supabase
      .from("reels")
      .insert([
        {
          user_id: userId,
          topic,
          script,
          voiceover_url: voice.url,
          video_url: video.url,
          duration: 30,
          status: "completed",
        },
      ])
      .select();

    if (error) throw error;

    res.json({ message: "Reel generated successfully!", reel: data[0] });
  } catch (err) {
    console.error("Error generating reel:", err);
    res.status(500).json({ message: err.message });
  }
};