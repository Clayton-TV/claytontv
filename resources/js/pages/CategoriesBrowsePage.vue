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
    retain_order: {
        type: Boolean,
    },
});
</script>

<template>
    <CategoriesBrowseWidget :categories_data :title :description :single_parent_category :retain_order />
</template>
