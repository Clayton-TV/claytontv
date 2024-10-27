<script setup>
defineProps({
    video: {
        type: Object,
        required: true,
    }
})

const getYoutubeId = (videoUrl) => {
    const youtubeRegex = /^.*(youtu\.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=)([^#\&\?]*).*/;
    const youtubeId = videoUrl.match(youtubeRegex)?.[2];
    return youtubeId
}

const getEmbedUrl = (videoUrl) => {
    const youtubeId = getYoutubeId(videoUrl)
    if (youtubeId) {
        return `https://www.youtube-nocookie.com/embed/${youtubeId}`
    } else {
        return false
    }
}

const videoThumbnail = (videoUrl) => {
    const youtubeId = getYoutubeId(videoUrl);
    if (youtubeId) {
        // If youtube URL
        // Attempt to split the video ID off the end, then shoehorn it into the thumbnail URL
        return `https://img.youtube.com/vi/${youtubeId}/mqdefault.jpg`
    } else {
        return "https://via.placeholder.com/1080x640"
    }
}
</script>

<template>
    <div class="mx-4 p-2 mb-0 lg:p-0">
        <h1 class="my-4 text-2xl lg:text-3xl lg:pb-4 font-bold text-gray-100 line-clamp-2" v-if="video.name">{{ video.name }}</h1>
        <div class="aspect-video w-auto mx-auto max-h-[80dvh] bg-gray-900">
            <iframe class="aspect-video w-full" :src="getEmbedUrl(video.url) + `?autoplay=1`" allow="autoplay; clipboard-write" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen v-if="getEmbedUrl(video.url)">
            </iframe>
            <div class="p-4" v-else> <!-- Shown if there was an error generating the embedded video iframe -->
                Error loading embedded video for
                <a :href="video.url" class="underline">
                    {{ video.url }}
                </a>
            </div>
        </div>
        <p
            class="pointer-events-none line-clamp-2 text-sm font-normal text-gray-500" v-if="video.description">
            {{ video.description }}
        </p>
        <div class="grid grid-cols-4 gap-1">
            <span
                class="pointer-events-none col-span-2 text-xs font-normal text-gray-400"
                >{{
                    video.speaker?.[0]?.name ?? "Speaker Name"
                }}</span
            >
            <span
                class="pointer-events-none col-span-1 text-right text-xs font-normal text-gray-400"
                >{{ video.date_created ?? "01/01/01" }}</span
            >
            <span
                class="pointer-events-none col-span-1 text-right text-xs font-normal text-gray-400"
                >{{ video.duration ?? "00:00" }}</span
            >
        </div>
    </div>
</template>

<style scoped></style>
