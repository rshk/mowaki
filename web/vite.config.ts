import { devtools } from "@tanstack/devtools-vite";
import { tanstackStart } from "@tanstack/react-start/plugin/vite";
import viteReact from "@vitejs/plugin-react";
import { nitro } from "nitro/vite";
import { defineConfig, loadEnv } from "vite";

const config = defineConfig(({ mode }) => {
    const env = loadEnv(mode, process.cwd(), "");
    return {
        resolve: { tsconfigPaths: true },
        plugins: [
            devtools(),
            nitro({ rollupConfig: { external: [/^@sentry\//] } }),
            tanstackStart(),
            viteReact(),
        ],
        server: {
            host: true, // expose on 0.0.0.0
            port: env.APP_PORT ? Number(env.APP_PORT) : 8000,
        },
    };
});

export default config;
