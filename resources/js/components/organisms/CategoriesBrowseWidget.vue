<script setup lang="ts">
import { Link } from '@inertiajs/vue3';
import { ref } from 'vue';
import { useCategoryFilter } from '../../composables/useCategoryFilter';
import CardSkeleton from '../atoms/CardSkeleton.vue';

const props = defineProps({
    categories_data: {
        type: Object,
        required: true,
    },
    title: {
        type: String,
    },
    description: {
        type: String,
    },
    single_parent_category: {
        // True: subcategory only has a single parent category (meaning entry.category is a string)
        // False: may be part of multiple categories (meaning entry.category is an array)
        type: Boolean,
    },
    categories_sort_order: {
        // Should be one of "alphabetical", "count", or "none"
        type: String,
        default: 'none',
    },
    subcategories_sort_order: {
        // Should be one of "alphabetical", "count", or "none"
        type: String,
        default: 'none',
    },
    hide_subcategories_text: {
        type: Boolean,
    },
    retain_order: {
        type: Boolean,
    },
    unfold: {
        type: Boolean,
    },
});

const fold_results = ref(!props.unfold);
const num_shown_folded = 12;

const { sortedCategories, filteredItems, selectedCategory, selectCategory } = useCategoryFilter(props.categories_data as any[], {
    singleParentCategory: props.single_parent_category,
    retainOrder: props.retain_order,
});

const isLoadingSubCategories = ref(false);
</script>

<template>
    <div class="justify-items-center space-y-2">
        <h2 class="mt-8 text-center text-3xl font-bold text-gray-100" v-if="title">
            {{ title }}
        </h2>
        <p class="mt-2 text-center text-gray-400" v-if="description">
            {{ description }}
        </p>
    </div>
    <div class="w-full items-center justify-center overflow-x-hidden pt-4">
        <ul class="flex snap-x snap-mandatory gap-x-0 overflow-x-auto px-2">
            <li
                v-for="(category, index) in ['All'].concat(sortedCategories)"
                :key="index"
                class="relative isolate mb-3 flex w-auto shrink-0 snap-center flex-col justify-end gap-y-2 rounded-md"
            >
                <button
                    class="me-2 rounded-full px-4 py-2 font-bold text-white hover:bg-red-400"
                    :class="category === selectedCategory ? 'bg-primary' : 'bg-gray-700'"
                    @click="selectCategory(category)"
                >
                    {{ category }}
                </button>
            </li>
        </ul>
    </div>
    <div class="my-3 w-full px-4">
        <h1 class="pb-6 text-lg" v-if="!hide_subcategories_text">
            Subcategories for:
            <span class="text-xl font-bold">{{ selectedCategory }}</span>
            <span v-if="subcategories_sort_order === 'alphabetical'"> (alphabetical order)</span>
            <span v-else-if="subcategories_sort_order === 'count'"> (most programmes first)</span>
        </h1>
        <div v-if="isLoadingSubCategories" class="grid grid-cols-2 gap-x-4 gap-y-8 sm:grid-cols-2 sm:gap-x-6 lg:grid-cols-3 xl:gap-x-8">
            <CardSkeleton v-for="skeletonIndex in 6" :key="skeletonIndex" :rowCount="1" :customClasses="'bg-blue-950'" :darkText="false" />
        </div>
        <ul v-else class="grid grid-cols-2 gap-x-4 gap-y-8 sm:grid-cols-2 sm:gap-x-6 lg:grid-cols-3 xl:gap-x-8">
            <Link
                v-for="(subcategory, index) in fold_results ? filteredItems.slice(0, num_shown_folded) : filteredItems"
                :key="index"
                :href="(subcategory as any).url"
                :id="subcategory.name"
                class="rounded-lg bg-blue-950 p-4"
            >
                <h2 class="font-bold">{{ subcategory.name }}</h2>
                <div>{{ subcategory.videosCount }} programme{{ subcategory.videosCount == 1 ? '' : 's' }}</div>
            </Link>
        </ul>
        <button
            class="mx-auto my-6 flex w-auto cursor-pointer rounded-md bg-blue-950 p-3"
            @click="fold_results = false"
            v-if="fold_results && filteredItems.length > num_shown_folded"
        >
            Show All
        </button>
    </div>
</template>
