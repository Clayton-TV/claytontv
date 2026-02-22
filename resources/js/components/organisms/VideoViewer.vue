<script setup lang="ts">
defineProps({
    video: {
        type: Object,
        required: true,
    },
});

const getYoutubeId = (videoUrl: string) => {
    const youtubeRegex = /^.*(youtu\.be\/|v\/|u\/\w\/|embed\/|watch\?v=|&v=)([^#&?]*).*/;
    const youtubeId = videoUrl.match(youtubeRegex)?.[2];
    return youtubeId;
};

const getVimeoId = (videoUrl: string) => {
    // Regex to match strings starting with http://vimeo.com/ or https://vimeo.com/ and from there, match and extract an alphanumeric string until the end or any non-alphanumeric character (eg another forwardslash)
    const vimeoRegex = /^(http|https):\/\/vimeo.com\/([\w]+).*/;
    const vimeoId = videoUrl.match(vimeoRegex)?.[2];
    return vimeoId;
};

const getEmbedUrl = (videoUrl: string): string | undefined => {
    const youtubeId = getYoutubeId(videoUrl);
    const vimeoId = getVimeoId(videoUrl);
    if (youtubeId) {
        return `https://www.youtube-nocookie.com/embed/${youtubeId}?autoplay=0&playsinline=1`;
    } else if (vimeoId) {
        return `https://player.vimeo.com/video/${vimeoId}`;
    } else {
        return undefined;
    }
};
</script>

<template>
    <div class="mx-4 mb-0 mb-2 flex flex-col p-2 lg:p-0">
        <div class="aspect-video max-h-[max(calc(100vh-20rem),85vh)]">
            <iframe
                class="mx-auto aspect-video h-full"
                :src="getEmbedUrl(video.url)"
                allow="autoplay; clipboard-write"
                referrerpolicy="strict-origin-when-cross-origin"
                allowfullscreen
                v-if="getEmbedUrl(video.url)"
            >
            </iframe>
            <div class="h-full bg-gray-900 p-4" v-else>
                <!-- Shown if there was a problem generating the embedded video iframe src -->
                Unable to load embedded video for
                <a :href="video.url" class="underline">
                    {{ video.url }}
                </a>
            </div>
        </div>
        <div class="w-full">
            <h1
                class="divide-grey-900 pointer-events-none my-4 line-clamp-2 border-t border-gray-800 text-2xl font-bold text-gray-100 lg:pb-4 lg:text-3xl"
                v-if="video.name"
            >
                {{ video.name }}
            </h1>
            <p class="pointer-events-none line-clamp-2 text-sm font-normal text-gray-500" v-if="video.description" v-html="video.description"></p>
            <div class="grid grid-cols-4 gap-1">
                <span class="pointer-events-none col-span-2 text-xs font-normal text-gray-400">{{ video.speaker?.[0]?.name ?? 'Speaker Name' }}</span>
                <span class="pointer-events-none col-span-1 text-right text-xs font-normal text-gray-400">{{
                    video.date_created ?? '01/01/01'
                }}</span>
                <span class="pointer-events-none col-span-1 text-right text-xs font-normal text-gray-400">{{ video.duration ?? '00:00' }}</span>
            </div>
        </div>
    </div>
</template>

<style scoped></style>
