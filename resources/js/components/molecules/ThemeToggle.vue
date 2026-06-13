<script setup lang="ts">
import { Monitor, Moon, Sun } from 'lucide-vue-next';
import { useAppearance } from '~/composables/useAppearance';

// Light / System / Dark segmented control. Default is "system" (follows the
// OS preference); the choice persists via useAppearance (localStorage + cookie).
const { appearance, updateAppearance } = useAppearance();

const options = [
    { value: 'light', label: 'Light', icon: Sun },
    { value: 'system', label: 'System', icon: Monitor },
    { value: 'dark', label: 'Dark', icon: Moon },
] as const;
</script>

<template>
    <div class="border-border inline-flex items-center gap-0.5 rounded-md border p-0.5" role="group" aria-label="Colour theme">
        <button
            v-for="option in options"
            :key="option.value"
            @click="updateAppearance(option.value)"
            :aria-label="option.label + ' theme'"
            :aria-pressed="appearance === option.value"
            :class="appearance === option.value ? 'bg-accent text-accent-foreground' : 'text-muted-foreground hover:text-foreground'"
            class="focus-visible:ring-ring inline-flex min-h-8 min-w-8 cursor-pointer items-center justify-center rounded outline-none focus-visible:ring-2"
        >
            <component :is="option.icon" class="h-4 w-4" aria-hidden="true" />
        </button>
    </div>
</template>
