import { defineConfig } from 'vite'
import { resolve } from 'path'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
    plugins: [
        vue({
            template: {
                transformAssetUrls: {
                    base: null,
                    includeAbsolute: false,
                },
            },
        }),
    ],
    server: {
        hmr: {
            host: 'localhost'
        },
        port: 5173,
        cors: {
            origin: ['http://localhost:8000', 'https://claytontv.test'],
        }
    },
    resolve: {
        alias: {
            '@': resolve('./resources/js/Components'),
        },
    },
    base: '/static/',
    build: {
        manifest: "manifest.json",
        outDir: resolve('./resources/dist'),
        rollupOptions: {
            input: {
                main: resolve('./resources/js/app.js'),
            },
        },
    },
    root: resolve('./resources'),
})
