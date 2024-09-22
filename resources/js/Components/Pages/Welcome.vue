<script setup>
import { Head, Link } from "@inertiajs/vue3"
import VideoCardList from "@/Organisms/VideoCardList.vue"

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
            <VideoCardList :videos="videos" class="p-8" />
        </main>
    </div>
</template>
