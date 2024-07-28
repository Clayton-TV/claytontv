<script setup>
defineProps({
    videos: {
        type: Array,
        required: true,
    },
})
</script>

<template>
    <div class="pb-8 mx-4">
        <h1 class="text-4xl my-4 font-bold text-gray-700">
            Latest Videos
        </h1>
        <ul role="list" class="grid grid-cols-1 gap-x-4 gap-y-8 sm:grid-cols-2 sm:gap-x-6 lg:grid-cols-4 xl:gap-x-8">
            <li v-for="video in videos" :key="video.source" class="relative">
                <div
                    class="group aspect-h-7 aspect-w-10 block w-full overflow-hidden rounded-lg bg-gray-100 focus-within:ring-2 focus-within:ring-indigo-500 focus-within:ring-offset-2 focus-within:ring-offset-gray-100">
                    <img
                        :src="[
                            video.source || 'https://via.placeholder.com/600x400',
                        ]"
                        alt="" class="pointer-events-none object-cover group-hover:opacity-75" />
                    <button type="button" class="absolute inset-0 focus:outline-none">
                        <span class="sr-only">View details for {{ video.title }}</span>
                    </button>
                </div>
                <p class="pointer-events-none mt-2 block truncate text-sm font-medium text-gray-900">
                    {{ video.title }}
                </p>
                <p class="pointer-events-none block text-sm font-medium text-gray-500">{{ video.description }}</p>
            </li>
        </ul>
    </div>
</template>

<style scoped>

</style>