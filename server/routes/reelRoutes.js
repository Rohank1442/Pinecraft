import express from 'express';
import { generateReel } from "../controllers/reelController.js";
const router = express.Router();

router.post('/generate-reel', generateReel);

export default router;