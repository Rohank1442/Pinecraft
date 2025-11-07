import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import authRoutes from "./routes/authRoutes.js";
import reelRoutes from "./routes/reelRoutes.js";

dotenv.config();
const app = express();
app.use(cors());
app.use(express.json());

app.use("/", authRoutes);
app.use("/", reelRoutes);

app.get("/", (req, res) => res.send("Pinecraft API running"));
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
