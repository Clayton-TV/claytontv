<script setup>
import { Head, Link } from "@inertiajs/vue3"
import VideoCard from "@/Atoms/VideoCard.vue"

defineProps({
    video: {
        type: Object,
        required: true,
    },
})

</script>

<template>
    <Head :title="video.name" />
    <div class="main-container">
        <main class="isolate">
            <VideoCard :video="video" />
        </main>
    </div>
</template>
