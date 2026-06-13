import tailwindcss from '@tailwindcss/vite';
import vue from '@vitejs/plugin-vue';
import path from 'node:path';
import { defineConfig, loadEnv } from 'vite';
import vueDevTools from 'vite-plugin-vue-devtools';

export default defineConfig(({ mode }) => {
    const env = loadEnv(mode, process.cwd());

    return {
        // Runtime-imported chunks (lazy pages, dynamic icons) resolve against
        // `base`. In production collectstatic serves the Vite output under
        // /static/build/ (django-vite static_url_prefix="build"), so the base
        // must match or those chunks 404. Dev serves from the Vite dev server.
        base: mode === 'production' ? '/static/build/' : '/static/',
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
                '@': path.resolve(__dirname, './resources/js/components'),
                '~': path.resolve(__dirname, './resources/js'),
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
