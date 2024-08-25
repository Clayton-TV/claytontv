<script setup>
defineProps({
    videos: {
        type: Array,
        required: true,
    },
})

const videoSource = (source) => {
    return source || "https://via.placeholder.com/1080x640"
}
</script>

<template>
    <div class="mx-4 pb-8">
        <h1 class="my-4 text-4xl font-bold text-gray-800">Latest Videos</h1>
        <ul
            role="list"
            class="grid grid-cols-1 gap-x-4 gap-y-8 sm:grid-cols-2 sm:gap-x-6 lg:grid-cols-3 xl:gap-x-8">
            <li v-for="video in videos" :key="video.source" class="relative">
                <div
                    class="aspect-h-7 aspect-w-10 focus-within:ring-indigo-500 group block w-full overflow-hidden rounded-lg bg-gray-100 focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-offset-gray-100">
                    <img
                        :src="videoSource(video.source)"
                        alt=""
                        class="pointer-events-none object-cover group-hover:opacity-75" />
                    <button
                        type="button"
                        class="absolute inset-0 focus:outline-none">
                        <span class="sr-only">
                            View details for {{ video.title }}
                        </span>
                    </button>
                </div>
                <p
                    class="pointer-events-none mt-2 block truncate text-xl font-semibold text-gray-800">
                    {{ video.title }}
                </p>
                <p
                    class="pointer-events-none line-clamp-2 text-sm font-normal text-gray-500">
                    {{ video.description }}
                </p>
                <div class="flex gap-x-2">
                    <span class="pointer-events-none text-xs font-normal text-gray-400">{{
                        'Speaker Name' }}</span>
                    <span
                        class="pointer-events-none text-xs font-normal text-gray-400"
                        >{{ video.date ?? "01/01/01" }}</span
                    >
                    <span
                        class="pointer-events-none text-xs font-normal text-gray-400"
                        >{{ video.duration ?? "00:00" }}</span
                    >
                </div>
            </li>
        </ul>
    </div>
</template>

<style scoped></style>
