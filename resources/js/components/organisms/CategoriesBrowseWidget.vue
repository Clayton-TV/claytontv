<script setup lang="ts">
import { Link } from '@inertiajs/vue3';
import { computed, ref } from 'vue';
import CardSkeleton from '@/atoms/CardSkeleton.vue';
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
    retain_order: {
        type: Boolean,
    },
});

// List out category from all entries, then filter down to only keep the first instance of each category
const categories = ref(
    ['All', props.categories_data.map((t) => t.category)].flat(Infinity).filter((item, index, array) => array.indexOf(item) == index),
);

// For each entry, obtain its name, category it belongs to, and number of videos it encompasses
const subCategories = ref(props.categories_data);

const sortedCategories = computed(() => {
    if (props.retain_order) {
        return categories.value;
    } else {
        return [...categories.value].sort((a, b) => a.localeCompare(b));
    }
});
const filteredSubCategories = computed(() => {
    const sortedSubCategories = props.retain_order ? subCategories.value : [...subCategories.value].sort((a, b) => a.name.localeCompare(b.name));
    if (selectedCategory.value === 'All') {
        return sortedSubCategories;
    }
    if (props.single_parent_category) {
        return sortedSubCategories.filter(({ category }) => category === selectedCategory.value);
    } else {
        return sortedSubCategories.filter(({ category }) => category.includes(selectedCategory.value));
    }
});

const selectedCategory = ref('All');
const isLoadingSubCategories = ref(false);

function selectCategory(category) {
    if (category !== selectedCategory.value) {
        selectedCategory.value = category;
        isLoadingSubCategories.value = false;
        //setTimeout(() => {
        //    isLoadingSubCategories.value = false
        //}, 800)
    }
}
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
