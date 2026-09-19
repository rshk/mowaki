import { defineConfig, loadEnv } from "vite";
import { devtools } from "@tanstack/devtools-vite";

import { tanstackStart } from "@tanstack/react-start/plugin/vite";

import viteReact from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import { nitro } from "nitro/vite";

const config = defineConfig(({ mode }) => {
    const env = loadEnv(mode, process.cwd(), "");
    return {
        resolve: { tsconfigPaths: true },
        plugins: [
            devtools(),
            nitro({ rollupConfig: { external: [/^@sentry\//] } }),
            tailwindcss(),
            tanstackStart(),
            viteReact(),
        ],
        server: {
            host: true,  // expose on 0.0.0.0
            port: env.APP_PORT ? Number(env.APP_PORT) : 8000,
        },
    };
});

export default config;
