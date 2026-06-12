<script setup lang="ts">
import { Link } from '@inertiajs/vue3';
import { IconBook2 } from '@tabler/icons-vue';

defineProps({
    series: { type: Object, required: true },
    countNoun: { type: String, default: 'episode' },
});
</script>

<template>
    <Link
        :href="series.url"
        prefetch
        class="group focus-visible:ring-ring flex gap-4 rounded-xl border border-white/10 bg-white/[0.03] p-4 transition-colors duration-150 outline-none hover:border-white/20 hover:bg-white/[0.06] focus-visible:ring-2"
    >
        <div class="bg-primary/10 flex h-20 w-20 flex-none items-center justify-center rounded-lg" aria-hidden="true">
            <IconBook2 class="text-primary h-8 w-8 stroke-[1.5]" />
        </div>
        <div class="min-w-0">
            <h3 class="truncate text-[15px] font-semibold text-gray-50">{{ series.name }}</h3>
            <p v-if="series.summary" class="mt-1 line-clamp-2 text-[13px] leading-relaxed text-gray-400">{{ series.summary }}</p>
            <p class="mt-2 inline-block rounded-md bg-white/5 px-2 py-0.5 text-xs text-gray-300 tabular-nums">
                {{ series.videosCount }} {{ countNoun }}{{ series.videosCount === 1 ? '' : 's' }}
            </p>
        </div>
    </Link>
</template>
