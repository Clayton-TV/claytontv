<script setup>
import { Head, Link } from "@inertiajs/vue3"
import VideoCardList from "@/Organisms/VideoCardList.vue"
import AZBar from "@/Organisms/AZBar.vue"

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
            <AZBar />
            <VideoCardList :videos="videos" class="p-8"/>
        </main>
    </div>
</template>
