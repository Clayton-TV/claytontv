import vue from '@vitejs/plugin-vue';
import path from 'node:path';
import { defineConfig } from 'vitest/config';

// Vitest config kept separate from vite.config.ts so the test run doesn't pull
// in Tailwind / devtools / SSR build concerns. Mirrors the same `@` and `~`
// aliases the app uses so component imports resolve identically.
export default defineConfig({
    plugins: [vue()],
    resolve: {
        alias: {
            '@': path.resolve(__dirname, './resources/js/components'),
            '~': path.resolve(__dirname, './resources/js'),
        },
    },
    test: {
        environment: 'jsdom',
        globals: true,
        include: ['resources/js/**/*.{test,spec}.{ts,js}'],
    },
});
