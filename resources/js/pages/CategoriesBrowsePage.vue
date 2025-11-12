<script setup>
import CategoriesBrowseWidget from "@/organisms/CategoriesBrowseWidget.vue"

const props = defineProps({
    title: {
        type: String,
    },
    description: {
        type: String,
    },
    categories_data: {
        type: Object,
        required: true,
    },
    single_parent_category: {
        type: Boolean,
    },
    sort_order: {
        type: String,
    }
})
</script>

<template>
    <CategoriesBrowseWidget :categories_data :title :description :single_parent_category :sort_order />
</template>
