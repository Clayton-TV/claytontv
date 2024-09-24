<script setup>
import { Head, Link } from "@inertiajs/vue3"
import VideoCarousel from "@/Organisms/VideoCarousel.vue"

defineProps({
    videos: {
        type: Array,
    },
})
</script>

<template>
    <Head title="Welcome" />
    <div class="main-container">
        <main class="isolate">
            <!-- <VideoCardList :videos="videos" :heading="`Latest Videos`" class="p-8" /> -->
            <VideoCarousel :videos="videos" class="my-2" />
        </main>
    </div>
</template>
