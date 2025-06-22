
<script setup>
import { computed } from "vue"
import { IconPlayerPlay } from "@tabler/icons-vue"
import { Head, Link } from "@inertiajs/vue3"
import VideoCardGrid from "@/organisms/VideoCardGrid.vue"

const props = defineProps({
    results: {
        type: Array,
    },
    searchquery: {
        type: String,
    },
})
</script>

<template>
    <Head :title="`Search: ` + searchquery" />
    <VideoCardGrid :videos="results" :title="`Search for '` + searchquery + `'`" :description="`Found ` + results.length + (results.length == 1 ? ' result' : ' results')" />
</template>