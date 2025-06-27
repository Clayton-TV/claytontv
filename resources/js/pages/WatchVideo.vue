<script setup>
import { Head } from '@inertiajs/vue3';
import VideoViewer from '@/organisms/VideoViewer.vue';

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
