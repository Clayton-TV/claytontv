// Fallback declaration for plain-JS `<script setup>` single-file components.
// vue-tsc / Volar generates precise types for `.vue` files that use
// `<script setup lang="ts">`; this shim only covers the remaining untyped
// legacy components so importing them from TypeScript doesn't error.
declare module '*.vue' {
    import type { DefineComponent } from 'vue';
    const component: DefineComponent<Record<string, any>, Record<string, any>, any>;
    export default component;
}
