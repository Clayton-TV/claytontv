<script setup lang="ts">
import LogoMark from '@/atoms/LogoMark.vue';
import { Play } from 'lucide-vue-next';
defineProps({
    video: {
        type: Object,
        required: true,
    },
});

const getVideoThumbnail = (video: Record<string, any>) => {
    if (video.thumbnail?.startsWith('http')) {
        return video.thumbnail;
    } else {
        const youtubeRegex = /^.*(youtu\.be\/|v\/|u\/\w\/|embed\/|watch\?v=|&v=)([^#&?]*).*/;
        const youtubeId = video.url.match(youtubeRegex)?.[2];
        if (youtubeId) {
            // If youtube URL
            // Attempt to split the video ID off the end, then shoehorn it into the thumbnail URL
            return `https://img.youtube.com/vi/${youtubeId}/mqdefault.jpg`;
        }
    }
    return null;
};
</script>

<template>
    <div class="group flex h-full w-full rounded-md bg-gradient-to-br from-gray-700 to-gray-900">
        <LogoMark
            class="fill-primary pointer-events-none absolute inset-0 h-[40%] items-center justify-center place-self-center object-cover opacity-80 group-hover:opacity-55"
        />

        <img
            v-if="getVideoThumbnail(video)"
            :src="getVideoThumbnail(video)"
            alt=""
            class="pointer-events-none absolute inset-0 size-full items-center justify-center place-self-center rounded-md object-cover group-hover:opacity-75"
            onerror="this.style.opacity='0';"
        />

        <div
            class="group absolute inset-0 flex h-min w-min cursor-pointer items-center justify-center place-self-center rounded-full p-2 hover:bg-gray-100/20"
        >
            <Play class="h-14 w-14 stroke-1 text-gray-100" />
        </div>

        <div class="z-10 z-50 flex w-svw flex-col gap-y-1 place-self-end rounded-b-md bg-black/60 px-2.5 py-3.5 sm:px-3.5 sm:py-2">
            <h3
                class="line-clamp-1 text-lg leading-snug font-bold text-white transition transition-all duration-150 group-hover:line-clamp-3 sm:text-2xl"
            >
                {{ video.name }}
            </h3>
            <div class="flex flex-row justify-between">
                <p class="line-clamp-1 h-6 truncate text-sm text-white">
                    {{ video.date_recorded ? 'Recorded: ' + video.date_recorded : 'Added: ' + video.date_created }}
                </p>
                <p
                    class="flex w-min items-center gap-x-1.5 rounded bg-red-400/90 px-1.5 py-0.5 text-xs font-bold tracking-wide uppercase sm:px-2"
                    v-if="video.is_livestream"
                >
                    <span class="relative flex h-2.5 w-2.5">
                        <span class="absolute inline-flex h-full w-full animate-ping rounded-full bg-white opacity-50" />
                        <span class="relative inline-flex h-full w-full rounded-full bg-white" />
                    </span>
                    <span class="pb-[1.5px]">Live</span>
                </p>
            </div>
        </div>
    </div>
</template>

<style scoped></style>
