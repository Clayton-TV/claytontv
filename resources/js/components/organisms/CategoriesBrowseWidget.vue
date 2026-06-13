<script setup>
import { Link } from '@inertiajs/vue3';
import { computed, ref } from 'vue';
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
    unfold: {
        type: Boolean,
    },
});

const fold_results = ref(!props.unfold);
const num_shown_folded = 12;

// List out category from all entries, then filter down to only keep the first instance of each category
const categories = ref([props.categories_data.map((t) => t.category)].flat(Infinity).filter((item, index, array) => array.indexOf(item) == index));

// For each entry, obtain its name, category it belongs to, and number of videos it encompasses
const subCategories = ref(props.categories_data);

const categoryCounts = computed(() => {
    let counts = {};
    for (const c of categories.value) {
        if (props.single_parent_category) {
            counts[c] = subCategories.value.filter(({ category }) => category === c).reduce((a, b) => a + b.videosCount, 0);
        } else {
            counts[c] = subCategories.value.filter(({ category }) => category.includes(c)).reduce((a, b) => a + b.videosCount, 0);
        }
    }
    return counts;
});

const sortedCategories = computed(() => {
    if (props.categories_sort_order === 'alphabetical') {
        return categories.value.toSorted((a, b) => a.localeCompare(b));
    } else if (props.categories_sort_order === 'count') {
        return categories.value.toSorted((a, b) => categoryCounts.value[b] - categoryCounts.value[a]);
    } else {
        return categories.value;
    }
});

const filteredSubCategories = computed(() => {
    let filtered = subCategories.value;
    if (selectedCategory.value !== 'All') {
        if (props.single_parent_category) {
            filtered = subCategories.value.filter(({ category }) => category === selectedCategory.value);
        } else {
            filtered = subCategories.value.filter(({ category }) => category.includes(selectedCategory.value));
        }
    }

    if (props.subcategories_sort_order === 'alphabetical') {
        filtered.sort((a, b) => a.name.localeCompare(b.name));
    } else if (props.subcategories_sort_order === 'count') {
        filtered.sort((a, b) => b.videosCount - a.videosCount);
    }
    return filtered;
});

let selectedCategory = ref('All');
let isLoadingSubCategories = ref(false);

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
    <div class="justify-items-center space-y-2">
        <h2 class="text-foreground mt-8 text-center text-3xl font-bold" v-if="title">
            {{ title }}
        </h2>
        <p class="text-muted-foreground mt-2 text-center" v-if="description">
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
                    class="me-2 rounded-full px-4 py-2 font-bold hover:bg-red-400"
                    :class="category === selectedCategory ? 'bg-primary text-primary-foreground' : 'bg-muted text-foreground'"
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
            <CardSkeleton v-for="skeletonIndex in 6" :key="skeletonIndex" :rowCount="1" :customClasses="'bg-muted'" />
        </div>
        <ul v-else class="grid grid-cols-2 gap-x-4 gap-y-8 sm:grid-cols-2 sm:gap-x-6 lg:grid-cols-3 xl:gap-x-8">
            <Link
                v-for="(subcategory, index) in fold_results ? filteredSubCategories.slice(0, num_shown_folded) : filteredSubCategories"
                :key="index"
                :href="subcategory.url"
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
            v-if="fold_results && filteredSubCategories.length > num_shown_folded"
        >
            Show All
        </button>
    </div>
</template>
