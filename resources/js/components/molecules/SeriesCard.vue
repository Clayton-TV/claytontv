<script setup lang="ts">
import { Link } from '@inertiajs/vue3';
import { BookOpen } from 'lucide-vue-next';

defineProps({
    series: { type: Object, required: true },
    countNoun: { type: String, default: 'episode' },
});
</script>

<template>
    <Link
        :href="series.url"
        prefetch
        class="group focus-visible:ring-ring border-border bg-card hover:border-ring hover:bg-accent flex gap-4 rounded-xl border p-4 transition-colors duration-150 outline-none focus-visible:ring-2"
    >
        <div class="bg-primary/10 flex h-20 w-20 flex-none items-center justify-center rounded-lg" aria-hidden="true">
            <BookOpen class="text-primary h-8 w-8 stroke-[1.5]" />
        </div>
        <div class="min-w-0">
            <h3 class="text-foreground line-clamp-2 text-[15px] font-semibold">{{ series.name }}</h3>
            <p v-if="series.summary" class="text-muted-foreground mt-1 line-clamp-2 text-[13px] leading-relaxed">{{ series.summary }}</p>
            <p class="bg-muted text-muted-foreground mt-2 inline-block rounded-md px-2 py-0.5 text-xs tabular-nums">
                {{ series.videosCount }} {{ countNoun }}{{ series.videosCount === 1 ? '' : 's' }}
            </p>
        </div>
    </Link>
</template>
