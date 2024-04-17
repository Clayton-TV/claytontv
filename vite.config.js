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
    },
    resolve: {
        alias: {
            '@': resolve('./resources/js/Components'),
        },
    },
    build: {
        outDir: resolve('./resources/dist'),
        assetsDir: '',
        manifest: true,
        emptyOutDir: true,
        rollupOptions: {
            input: {
                main: resolve('./resources/js/app.js'),
            },
            output: {
                chunkFileNames: 'dist/[name]-[hash].js',
            },
        },
    },
})