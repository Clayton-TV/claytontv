<script setup>
import { computed } from "vue"
import { IconPlayerPlay } from "@tabler/icons-vue"
import { Head, Link } from "@inertiajs/vue3"
import VideoCardList from "@/Organisms/VideoCardList.vue"

const props = defineProps({
    results: {
        type: Array,
    },
    num_results: {
        type: Number,
    },
    searchquery: {
        type: String,
    },
    pagenum_results: {
        type: Number,
    },
    num_pages: {
        type: Number,
    },
})
</script>

<template>
    <Head :title="`Search: ` + searchquery" />
    <VideoCardList :videos="results" :title="`Search for '` + searchquery + `'`" :description="`Found ` + num_results + (num_results == 1 ? ' result' : ' results')" :id="`search_` + searchquery" :page="pagenum_results" :num_pages="num_pages" />
</template>
