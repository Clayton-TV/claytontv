import { globalIgnores } from 'eslint/config'
import { defineConfigWithVueTs, vueTsConfigs } from '@vue/eslint-config-typescript'
import pluginVue from 'eslint-plugin-vue'
import pluginOxlint from 'eslint-plugin-oxlint'
import skipFormatting from '@vue/eslint-config-prettier/skip-formatting'

// To allow more languages other than `ts` in `.vue` files, uncomment the following lines:
// import { configureVueProject } from '@vue/eslint-config-typescript'
// configureVueProject({ scriptLangs: ['ts', 'tsx'] })
// More info at https://github.com/vuejs/eslint-config-typescript/#advanced-setup

export default defineConfigWithVueTs(
    {
        name: 'app/files-to-lint',
        files: ['**/*.{ts,mts,tsx,vue}'],
    },

    // Only lint our own frontend source. Without these, eslint walks the Python
    // venv and Django's vendored admin JS (staticfiles), producing hundreds of
    // bogus errors from minified third-party code.
    globalIgnores([
        '**/dist/**',
        '**/dist-ssr/**',
        '**/coverage/**',
        '**/node_modules/**',
        '**/.venv/**',
        '**/staticfiles_collected/**',
        '**/static/**',
        'public/**',
        'bootstrap/ssr/**',
        '**/vendor/**',
        'tailwind.config.js',
        'resources/js/components/ui/**',
    ]) as any,

    pluginVue.configs['flat/essential'] as any,
    vueTsConfigs.recommended,
    {
        rules: {
            'vue/multi-word-component-names': 'off',
            '@typescript-eslint/no-explicit-any': 'off',
            // The overhaul's components are a mix of <script setup> (JS) and
            // <script setup lang="ts">. Accept both rather than force a TS
            // migration here; a later pass can tighten this to ts-only.
            'vue/block-lang': ['error', { script: { lang: ['ts', 'js'], allowNoLang: true } }],
        },
    },
    ...(pluginOxlint.configs['flat/recommended'] as any[]),
    skipFormatting as any,
);
