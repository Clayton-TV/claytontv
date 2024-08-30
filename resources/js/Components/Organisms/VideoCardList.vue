<script setup>
defineProps({
    videos: {
        type: Array,
        required: true,
    },
    pagingMetadata: {
        nextPage: {
            type: Number,
        },
        pageNumber: {
            type: Number,
        },
        pageCount: {
            type: Number,
        },
        pageLimit: {
            type: Number,
        },
        totalCount: {
            type: Number,
        },
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
    <div class="mx-4 pb-8">
        <h1 class="my-4 text-4xl font-bold text-gray-800">Latest Videos</h1>
        <p v-if="pagingMetadata" class="p-2 text-sm text-gray-500">
            Page {{ pagingMetadata.pageNumber }} of
            {{ pagingMetadata.pageCount }}. Showing
            {{ pagingMetadata.pageLimit }} out of
            {{ pagingMetadata.totalCount }} videos
        </p>
        <ul
            class="grid grid-cols-1 gap-x-4 gap-y-8 sm:grid-cols-2 sm:gap-x-6 lg:grid-cols-3 xl:gap-x-8"
            role="list">
            <li v-for="video in videos" :key="video.source" class="relative">
                <a :href="video.url" target="_blank">
                    <div
                        class="focus-within:ring-indigo-500 group block aspect-video w-full overflow-hidden rounded-lg bg-gray-100 focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-offset-gray-100">
                        <img
                            :src="videoThumbnail(video.url)"
                            alt=""
                            class="pointer-events-none mx-auto h-full w-auto object-cover group-hover:opacity-75" />
                        <button
                            class="absolute inset-0 focus:outline-none"
                            type="button">
                            <span class="sr-only">
                                View details for {{ video.name }}
                            </span>
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
                </a>
            </li>
        </ul>
    </div>
</template>

<style scoped></style>
