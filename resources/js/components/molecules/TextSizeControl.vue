<script setup lang="ts">
import { ALargeSmall } from 'lucide-vue-next';
import { useTextScale } from '~/composables/useTextScale';

// A−/A+ text resizing for the elderly-first audience. Adds to (never replaces)
// browser pinch-zoom. Persists via useTextScale.
const { increase, decrease, reset, canIncrease, canDecrease, isDefault } = useTextScale();
</script>

<template>
    <div class="flex items-center gap-1" role="group" aria-label="Text size">
        <button
            @click="decrease()"
            :disabled="!canDecrease()"
            aria-label="Decrease text size"
            class="focus-visible:ring-ring text-muted-foreground hover:bg-accent hover:text-foreground inline-flex min-h-9 min-w-9 cursor-pointer items-center justify-center rounded-md outline-none focus-visible:ring-2 disabled:cursor-default disabled:opacity-40 disabled:hover:bg-transparent"
        >
            <ALargeSmall class="h-3.5 w-3.5" aria-hidden="true" />
        </button>
        <button
            @click="reset()"
            :disabled="isDefault()"
            aria-label="Reset text size"
            class="focus-visible:ring-ring text-muted-foreground hover:bg-accent hover:text-foreground inline-flex min-h-9 min-w-9 cursor-pointer items-center justify-center rounded-md outline-none focus-visible:ring-2 disabled:cursor-default disabled:opacity-40 disabled:hover:bg-transparent"
        >
            <ALargeSmall class="h-5 w-5" aria-hidden="true" />
        </button>
        <button
            @click="increase()"
            :disabled="!canIncrease()"
            aria-label="Increase text size"
            class="focus-visible:ring-ring text-muted-foreground hover:bg-accent hover:text-foreground inline-flex min-h-9 min-w-9 cursor-pointer items-center justify-center rounded-md outline-none focus-visible:ring-2 disabled:cursor-default disabled:opacity-40 disabled:hover:bg-transparent"
        >
            <ALargeSmall class="h-6 w-6" aria-hidden="true" />
        </button>
    </div>
</template>
