import tailwindcss from '@tailwindcss/vite';
import vue from '@vitejs/plugin-vue';
import path from 'node:path';
import { defineConfig, loadEnv } from 'vite';
import vueDevTools from 'vite-plugin-vue-devtools';

export default defineConfig(({ mode }) => {
    const env = loadEnv(mode, process.cwd());

    return {
        base: '/static/',
        publicDir: false,
        build: {
            manifest: 'manifest.json',
            outDir: path.resolve(__dirname, 'public/build'),
            emptyOutDir: true,
            rollupOptions: {
                input: {
                    app: path.resolve(__dirname, 'resources/js/app.ts'),
                },
            }
        },
        plugins: [
            tailwindcss(),
            vue({
                template: {
                    transformAssetUrls: {
                        base: null,
                        includeAbsolute: false,
                    },
                },
            }),
            vueDevTools(),
        ],
        resolve: {
            alias: {
                '@': path.resolve(__dirname, './resources/js'),
            },
        },
        server: {
            cors: {
                origin: [
                    /^https?:\/\/(?:(?:[^:]+\.)?localhost|127\.0\.0\.1|\[::1\])(?::\d+)?$/, // Copied from Vite itself.
                    ...(env.APP_URL ? [env.APP_URL] : []),
                    /^https?:\/\/.*\.test(:\d+)?$/,
                ]
            }
        },
    };
});
