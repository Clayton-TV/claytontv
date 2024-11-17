<script setup>
import { Head, Link } from "@inertiajs/vue3"
import VideoViewer from "@/Organisms/VideoViewer.vue"

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
            <VideoViewer :video="video" />
        </main>
    </div>
</template>
