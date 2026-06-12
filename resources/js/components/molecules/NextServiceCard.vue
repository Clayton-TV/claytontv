<script setup lang="ts">
import { Link } from '@inertiajs/vue3';
import { IconArrowRight } from '@tabler/icons-vue';
</script>

<!-- Honest placeholder until Epic 4 supplies real broadcast state from the
     YouTube API: no fake countdowns, no fake "live now". This card then
     becomes the upcoming-stream slot with a real start time and player. -->
<template>
    <div class="rounded-xl border border-white/10 bg-white/[0.03] p-5 sm:p-6">
        <div class="flex items-center gap-2">
            <span class="bg-primary inline-block h-2 w-2 rounded-full" aria-hidden="true"></span>
            <p class="text-xs font-medium tracking-wider text-gray-400 uppercase">Sunday services</p>
        </div>
        <p class="font-display mt-3 text-lg font-bold text-gray-50">Live streams appear here</p>
        <p class="mt-1.5 text-sm leading-relaxed text-gray-400">
            Morning and evening services stream live most Sundays. Until then, catch up on recent services any time.
        </p>
        <Link
            href="/livestreams"
            class="focus-visible:ring-ring mt-4 inline-flex min-h-11 items-center gap-1.5 rounded-lg bg-white/5 px-4 text-sm font-medium text-gray-100 transition-colors duration-150 outline-none hover:bg-white/10 focus-visible:ring-2"
        >
            Watch past services
            <IconArrowRight class="h-4 w-4" aria-hidden="true" />
        </Link>
    </div>
</template>
