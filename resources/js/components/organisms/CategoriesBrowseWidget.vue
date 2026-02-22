<script setup lang="ts">
import CardSkeleton from '@/atoms/CardSkeleton.vue';
import { Link } from '@inertiajs/vue3';
import { useCategoryFilter } from '~/composables/useCategoryFilter';
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
        type: Boolean,
    },
    retain_order: {
        type: Boolean,
    },
});

const {
    sortedCategories,
    filteredItems: filteredSubCategories,
    selectedCategory,
    isLoading: isLoadingSubCategories,
    selectCategory,
} = useCategoryFilter({
    items: props.categories_data,
    singleParentCategory: props.single_parent_category,
    retainOrder: props.retain_order,
});
</script>

<template>
    <div class="mt-10 mb-4 justify-items-center space-y-2">
        <h2 class="text-center text-3xl font-bold text-gray-100">
            {{ title }}
        </h2>
        <p class="text-center text-gray-400">
            {{ description }}
        </p>
    </div>
    <div class="w-full items-center justify-center overflow-x-hidden pt-4">
        <ul class="flex snap-x snap-mandatory gap-x-0 overflow-x-auto px-2">
            <li
                v-for="(category, index) in sortedCategories"
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
    <div class="w-full px-4 pb-4">
        <h1 class="my-4 text-lg">
            Subcategories for:
            <span class="text-xl font-bold">{{ selectedCategory }}</span>
        </h1>
        <div v-if="isLoadingSubCategories" class="grid grid-cols-2 gap-x-4 gap-y-8 sm:grid-cols-2 sm:gap-x-6 lg:grid-cols-3 xl:gap-x-8">
            <CardSkeleton v-for="skeletonIndex in 6" :key="skeletonIndex" :rowCount="1" :customClasses="'bg-blue-950'" :darkText="false" />
        </div>
        <ul v-else class="grid grid-cols-2 gap-x-4 gap-y-8 sm:grid-cols-2 sm:gap-x-6 lg:grid-cols-3 xl:gap-x-8">
            <Link
                v-for="(subcategory, index) in filteredSubCategories"
                :key="index"
                :href="subcategory.url"
                :id="subcategory.name"
                class="rounded-lg bg-blue-950 p-4"
            >
                <h2 class="font-bold">{{ subcategory.name }}</h2>
                <div>{{ subcategory.videosCount }} programme{{ subcategory.videosCount == 1 ? '' : 's' }}</div>
            </Link>
        </ul>
    </div>
</template>
