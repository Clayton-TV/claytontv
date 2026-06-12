<script setup lang="ts">
import { Link } from '@inertiajs/vue3';
import { IconArrowRight } from '@tabler/icons-vue';

defineProps({
    title: { type: String, required: true },
    moreHref: { type: String, required: false },
    moreLabel: { type: String, default: 'View all' },
});
</script>

<template>
    <div class="mb-5 flex items-baseline justify-between gap-4">
        <h2 class="font-display text-xl font-bold text-gray-50 sm:text-2xl">{{ title }}</h2>
        <Link
            v-if="moreHref"
            :href="moreHref"
            class="focus-visible:ring-ring inline-flex shrink-0 items-center gap-1 rounded text-sm font-medium text-gray-400 transition-colors duration-150 outline-none hover:text-white focus-visible:ring-2"
        >
            {{ moreLabel }}
            <IconArrowRight class="h-3.5 w-3.5" aria-hidden="true" />
        </Link>
    </div>
</template>
