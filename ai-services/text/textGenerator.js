// ai-services/text/textGenerator.js
import OpenAI from "openai";
import dotenv from "dotenv";
import path from "path";

dotenv.config({ path: path.resolve(process.cwd(), "../.env") });

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

const USE_MOCK = process.env.USE_MOCK_AI === "true";

export async function generateScript(topic) {
  if (USE_MOCK) {
    console.log("⚙️ [MOCK MODE] Generating fake script for topic:", topic);
    return {
      topic,
      content: `🎬 Here's a fun, engaging explanation about ${topic}!`,
    };
  }

  try {
    console.log("🧠 [REAL MODE] Calling OpenAI API for:", topic);
    const prompt = `
    You are a creative scriptwriter for educational short videos.
    Write a concise, engaging 30-second script on: "${topic}".
    Include:
    - Hook (1 line)
    - Explanation (3-4 lines)
    - Takeaway (1 line)
    `;

    const completion = await openai.chat.completions.create({
      model: "gpt-4o-mini",
      messages: [{ role: "user", content: prompt }],
      temperature: 0.8,
    });

    return {
      topic,
      content: completion.choices[0].message.content.trim(),
    };
  } catch (err) {
    console.error("❌ Error generating script:", err);
    throw new Error("Failed to generate script");
  }
}
