<script setup>
import { Head } from '@inertiajs/vue3';
import VideoViewer from '@/organisms/VideoViewer.vue';
import VideoBrowseByLinks from '@/atoms/VideoBrowseByLinks.vue';

defineProps({
    video: {
        type: Object,
        required: true,
    },
    video_metadata: {
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
            <hr class="mx-4 border-gray-800 mb-2 mt-2 lg:mt-4" />
            <VideoBrowseByLinks :video="video" :video_metadata />
        </main>
    </div>
</template>
