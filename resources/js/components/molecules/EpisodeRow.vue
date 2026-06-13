<script setup>
import { Link } from '@inertiajs/vue3';
import { IconCheck, IconPlayerPlayFilled } from '@tabler/icons-vue';
import { useWatchHistory } from '~/composables/useWatchHistory';
import { formatDuration } from '~/lib/duration';

defineProps({
    episode: { type: Object, required: true },
    // Display position: episode number where the data has one, else row index
    position: { type: Number, required: true },
});

const { hasWatched } = useWatchHistory();

const thumb = (episode) => {
    if (episode.thumbnail?.startsWith('http')) return episode.thumbnail;
    return null;
};
</script>

<template>
    <Link
        :href="episode.url"
        prefetch
        class="group focus-visible:ring-ring border-border bg-card hover:border-ring hover:bg-accent flex items-center gap-4 rounded-xl border p-3 transition-colors duration-150 outline-none focus-visible:ring-2"
    >
        <span class="text-muted-foreground w-6 shrink-0 text-center text-sm font-medium tabular-nums">{{ position }}</span>
        <span class="relative aspect-video w-28 shrink-0 overflow-hidden rounded-md bg-gray-800 sm:w-32">
            <img
                v-if="thumb(episode)"
                :src="thumb(episode)"
                alt=""
                loading="lazy"
                decoding="async"
                class="h-full w-full object-cover"
                onerror="this.style.opacity='0'"
            />
            <span
                class="absolute inset-0 flex items-center justify-center opacity-0 transition-opacity duration-150 group-hover:opacity-100"
                aria-hidden="true"
            >
                <IconPlayerPlayFilled class="h-7 w-7 text-white drop-shadow" />
            </span>
            <span
                v-if="formatDuration(episode.duration_seconds)"
                class="absolute right-1 bottom-1 rounded bg-black/75 px-1 py-0.5 text-[10px] font-semibold text-white tabular-nums"
            >
                {{ formatDuration(episode.duration_seconds) }}
            </span>
        </span>
        <span class="min-w-0 flex-1">
            <span class="text-foreground block truncate text-[15px] font-medium">{{ episode.name }}</span>
            <span v-if="episode.date" class="text-muted-foreground mt-0.5 block text-xs tabular-nums">{{ episode.date }}</span>
        </span>
        <span
            v-if="hasWatched(episode.id)"
            class="text-primary mr-1 inline-flex shrink-0 items-center gap-1 text-xs font-medium"
            title="You've watched this"
        >
            <IconCheck class="h-3.5 w-3.5" aria-hidden="true" /> Watched
        </span>
    </Link>
</template>
