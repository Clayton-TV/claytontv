<script setup lang="ts">
import { Link } from '@inertiajs/vue3';
import { ArrowRight } from 'lucide-vue-next';

defineProps({
    title: { type: String, required: true },
    moreHref: { type: String, required: false },
    moreLabel: { type: String, default: 'View all' },
});
</script>

<template>
    <div class="mb-5 flex items-baseline justify-between gap-4">
        <h2 class="font-display text-foreground text-xl font-bold sm:text-2xl">{{ title }}</h2>
        <Link
            v-if="moreHref"
            :href="moreHref"
            class="focus-visible:ring-ring text-muted-foreground hover:text-foreground inline-flex shrink-0 items-center gap-1 rounded text-sm font-medium transition-colors duration-150 outline-none focus-visible:ring-2"
        >
            {{ moreLabel }}
            <ArrowRight class="h-3.5 w-3.5" aria-hidden="true" />
        </Link>
    </div>
</template>
