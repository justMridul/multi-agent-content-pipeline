import type { NextConfig } from "next";
import { config } from "dotenv";
import { resolve } from "path";

// Load environment variables from root .env file (shared with Python)
// This allows sharing the same .env file between Python and Next.js
// Priority: nextjs-app/.env.local > root .env.local > root .env
config({ path: resolve(__dirname, "../.env") });
config({ path: resolve(__dirname, "../.env.local"), override: true });
config({ path: resolve(__dirname, ".env.local"), override: true });

const nextConfig: NextConfig = {
  /* config options here */
};

export default nextConfig;
