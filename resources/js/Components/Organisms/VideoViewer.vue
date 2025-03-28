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

const getVimeoId = (videoUrl) => {
    // Regex to match strings starting with http://vimeo.com/ or https://vimeo.com/ and from there, match and extract an alphanumeric string until the end or any non-alphanumeric character (eg another forwardslash)
    const vimeoRegex = /^(http|https):\/\/vimeo.com\/([\w]+).*/;
    const vimeoId = videoUrl.match(vimeoRegex)?.[2];
    return vimeoId
}

const getEmbedUrl = (videoUrl) => {
    const youtubeId = getYoutubeId(videoUrl)
    const vimeoId = getVimeoId(videoUrl)
    if (youtubeId) {
        return `https://www.youtube-nocookie.com/embed/${youtubeId}?autoplay=0&playsinline=1`
    } else if (vimeoId) {
        return `https://player.vimeo.com/video/${vimeoId}`
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
    <div class="mx-4 p-2 mb-0 lg:p-0 flex flex-col mb-2">
        <div class="aspect-video max-h-[max(calc(100vh-20rem),85vh)]">
            <iframe class="aspect-video mx-auto h-full" :src="getEmbedUrl(video.url)" allow="autoplay; clipboard-write" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen v-if="getEmbedUrl(video.url)">
            </iframe>
            <div class="p-4 bg-gray-900 h-full" v-else> <!-- Shown if there was a problem generating the embedded video iframe src -->
                Unable to load embedded video for
                <a :href="video.url" class="underline">
                    {{ video.url }}
                </a>
            </div>
        </div>
        <div class="w-full">
            <h1 class="border-t border-gray-800 divide-grey-900 pointer-events-none my-4 text-2xl lg:text-3xl lg:pb-4 font-bold text-gray-100 line-clamp-2" v-if="video.name">{{ video.name }}</h1>
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
    </div>
</template>

<style scoped></style>
