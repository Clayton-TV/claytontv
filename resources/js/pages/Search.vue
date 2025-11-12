<script setup>
import { computed } from "vue"
import { IconPlayerPlay } from "@tabler/icons-vue"
import { Link } from "@inertiajs/vue3"
import VideoCardGrid from "@/organisms/VideoCardGrid.vue"
import CategoriesBrowseWidget from '@/organisms/CategoriesBrowseWidget.vue';

const props = defineProps({
    categories: {
        type: Array,
    },
    videos: {
        type: Array,
    },
    title: {
        type: String,
    },
    description: {
        type: String,
    },
    has_prev_page: {
        type: Boolean,
    },
    has_next_page: {
        type: Boolean,
    },
})
</script>

<template>
    <!-- TODO might be worth paginating categories separately from video results, and making backend only redo search for one or other when switching pages -->
    <div class="mt-8 justify-items-center space-y-2">
        <h2 class="text-center text-3xl font-bold text-gray-100">
            {{ title }}
        </h2>
    </div>

    <CategoriesBrowseWidget
        v-if="categories.length"
        :categories_data="categories"
        :description="`Found ` + categories.length + ` categories`"
        single_parent_category
        sort_order="count"
        hide_subcategories_text />

    <br/>

    <VideoCardGrid
        :videos
        :description
        :has_prev_page
        :has_next_page />
</template>
