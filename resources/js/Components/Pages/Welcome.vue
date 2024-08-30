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
    <div class="main-container p-8">
        <main class="isolate">
            <VideoCardList :videos="videos" />
        </main>
    </div>
</template>
