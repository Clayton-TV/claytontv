<script setup>
import LogoMark from '@/atoms/LogoMark.vue';
import { IconCheck, IconPlayerPlay } from '@tabler/icons-vue';
import { useWatchHistory } from '~/composables/useWatchHistory';
import { formatDuration } from '~/lib/duration';

defineProps({
    video: {
        type: Object,
        required: true,
    },
});

const { hasWatched } = useWatchHistory();

const getVideoThumbnail = (video) => {
    if (video.thumbnail?.startsWith('http')) {
        return video.thumbnail;
    } else {
        const youtubeRegex = /^.*(youtu\.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=)([^#\&\?]*).*/;
        const youtubeId = video.url.match(youtubeRegex)?.[2];
        if (youtubeId) {
            // Derive the thumbnail from the YouTube video ID when none is stored
            return `https://img.youtube.com/vi/${youtubeId}/mqdefault.jpg`;
        }
    }
    return null;
};
</script>

<template>
    <div class="group relative flex h-full w-full overflow-hidden rounded-lg bg-gradient-to-br from-gray-700 to-gray-900">
        <LogoMark class="fill-primary pointer-events-none absolute inset-0 h-[40%] place-self-center object-cover opacity-80" />

        <img
            v-if="getVideoThumbnail(video)"
            :src="getVideoThumbnail(video)"
            alt=""
            loading="lazy"
            decoding="async"
            class="pointer-events-none absolute inset-0 size-full place-self-center object-cover transition-transform duration-300 ease-out group-hover:scale-[1.03] motion-reduce:transition-none motion-reduce:group-hover:scale-100"
            onerror="this.style.opacity='0';"
        />

        <!-- Bottom scrim keeps the play glyph and title legible over any thumbnail -->
        <div class="pointer-events-none absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" aria-hidden="true"></div>

        <!-- Courtesy "watched" tick from localStorage history -->
        <span
            v-if="hasWatched(video.id)"
            class="bg-primary text-primary-foreground absolute top-2 right-2 z-10 inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-semibold"
        >
            <IconCheck class="h-3 w-3" aria-hidden="true" /> Watched
        </span>

        <div
            class="absolute inset-0 flex h-min w-min items-center justify-center place-self-center rounded-full bg-black/30 p-2 opacity-90 backdrop-blur-[2px] transition-opacity duration-200 ease-out group-hover:opacity-100"
            aria-hidden="true"
        >
            <IconPlayerPlay class="h-14 w-14 stroke-1 text-gray-100" />
        </div>

        <div class="z-10 flex w-full flex-col gap-y-1 place-self-end bg-black/60 px-2.5 py-3.5 backdrop-blur-sm sm:px-3.5 sm:py-2">
            <h3 class="line-clamp-1 text-lg leading-snug font-bold text-white group-hover:line-clamp-3 sm:text-2xl">
                {{ video.name }}
            </h3>
            <div class="flex flex-row justify-between">
                <p class="line-clamp-1 h-6 truncate text-sm text-white tabular-nums">
                    {{ video.date_recorded ? 'Recorded: ' + video.date_recorded : 'Added: ' + video.date_created }}
                </p>
                <!-- A pulsing LIVE badge on a years-old recording is a lie; it returns
                     in Epic 4 driven by real broadcast state from the YouTube API. -->
                <p
                    class="flex w-min items-center rounded bg-white/15 px-1.5 py-0.5 text-xs font-bold tracking-wide uppercase sm:px-2"
                    v-if="video.is_livestream"
                >
                    <span class="pb-[1.5px] whitespace-nowrap">Streamed</span>
                </p>
                <p
                    v-else-if="formatDuration(video.duration_seconds)"
                    class="flex w-min items-center rounded bg-white/15 px-1.5 py-0.5 text-xs font-semibold text-white tabular-nums sm:px-2"
                >
                    <span class="whitespace-nowrap">{{ formatDuration(video.duration_seconds) }}</span>
                </p>
            </div>
        </div>
    </div>
</template>

<style scoped></style>
