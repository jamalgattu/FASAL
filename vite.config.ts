import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  // Relative base so the built assets resolve correctly whether this is
  // served from https://<user>.github.io/<repo>/ or any other subpath.
  base: "./",
  server: {
    port: 5173,
  },
});
