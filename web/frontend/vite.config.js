import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// The build emits to dist/, which web/server.py serves at "/" (with hashed
// files under /assets). In dev, `npm run dev` runs a server on :5173 and
// proxies /api to the FastAPI backend on :8000, so you can run both with live
// reload. Change the target if you start uvicorn on a different port.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: "dist",
    emptyOutDir: true,
  },
});
