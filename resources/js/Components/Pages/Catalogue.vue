<script setup>
import { Head, Link } from "@inertiajs/vue3"
import VideoCardList from "../Organisms/VideoCardList.vue"

defineProps({
    videos: {
        type: Array,
    },
})
</script>

<template>
    <Head title="Video Catalogue" />
    <div class="main-container">
        <main class="isolate p-8">
            <VideoCardList :videos="videos" heading="Video Catalogue" />
        </main>
    </div>
</template>
