<script setup lang="ts">
import CategoriesBrowseWidget from '@/organisms/CategoriesBrowseWidget.vue';

defineProps({
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
    categories_sort_order: {
        type: String,
    },
    subcategories_sort_order: {
        type: String,
    },
});
</script>

<template>
    <CategoriesBrowseWidget :categories_data :title :description :single_parent_category :categories_sort_order :subcategories_sort_order />
</template>
