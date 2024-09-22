<script setup>
defineProps({
    video: {
        type: Object,
        required: true,
    },
})

const videoThumbnail = (videoUrl) => {
    const youtubeRegex =
        /^.*(youtu\.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=)([^#\&\?]*).*/
    const youtubeId = videoUrl.match(youtubeRegex)?.[2]
    if (youtubeId) {
        // If youtube URL
        // Attempt to split the video ID off the end, then shoehorn it into the thumbnail URL
        return `https://img.youtube.com/vi/${youtubeId}/mqdefault.jpg`
    }
    return "https://via.placeholder.com/1080x640"
}
</script>

<template>
    <a :href="video.url" target="_blank" class="text-left">
        <div
            class="group block aspect-video w-full overflow-hidden rounded-lg bg-gray-100 focus-within:ring-2 focus-within:ring-indigo-500 focus-within:ring-offset-2 focus-within:ring-offset-gray-100">
            <img
                :src="videoThumbnail(video.url)"
                alt=""
                class="pointer-events-none mx-auto h-full w-auto object-cover group-hover:opacity-75" />
            <button class="absolute inset-0 focus:outline-none" type="button">
                <span class="sr-only"> View details for {{ video.name }} </span>
            </button>
        </div>
        <p
            class="pointer-events-none mt-2 block truncate text-xl font-semibold text-gray-800">
            {{ video.name }}
        </p>
        <p
            class="pointer-events-none line-clamp-2 text-sm font-normal text-gray-500">
            {{ video.description }}
        </p>
        <div class="grid grid-cols-4 gap-1">
            <span
                class="pointer-events-none col-span-2 text-xs font-normal text-gray-400"
                >{{ video.speaker?.[0]?.name ?? "Speaker Name" }}</span
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
    </a>
</template>
