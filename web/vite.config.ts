import react from "@vitejs/plugin-react";
import { defineConfig, loadEnv } from "vite";

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
    const env = loadEnv(mode, process.cwd(), "");
    return {
        plugins: [react()],
        server: {
            host: true, // Expose on 0.0.0.0
            port: env.APP_PORT ? Number(env.APP_PORT) : 5173,
        },
        resolve: {
            alias: {},
        },
    };
});
