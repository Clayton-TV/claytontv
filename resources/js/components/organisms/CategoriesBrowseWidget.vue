<script setup>
import { ref, computed } from 'vue';
import LoadingSpinner from '../atoms/LoadingSpinner.vue';
import CardSkeleton from '../atoms/CardSkeleton.vue';
import { Link } from '@inertiajs/vue3';
const props = defineProps({
    categories_data: {
        type: Array as () => Record<string, any>[],
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
        default: "none",
    },
    subcategories_sort_order: {
        // Should be one of "alphabetical", "count", or "none"
        type: String,
        default: "none",
    },
    hide_subcategories_text: {
        type: Boolean,
    },
    unfold: {
      type: Boolean,
    },
})

const fold_results = ref(!props.unfold)
const num_shown_folded = 12

// List out category from all entries, then filter down to only keep the first instance of each category
const categories = ref([
    props.categories_data
        .map((t: Record<string, any>) => t.category),
].flat(Infinity).filter((item: any, index: number, array: any[]) => array.indexOf(item) == index))

// For each entry, obtain its name, category it belongs to, and number of videos it encompasses
const subCategories = ref(props.categories_data)

const categoryCounts = computed(() => {
    let counts: Record<string, number> = {}
    for (const c of categories.value) {
        if (props.single_parent_category) {
            counts[c as string] = subCategories.value.filter(({ category }: any) => category === c).reduce((a: number, b: any) => a + b.videosCount, 0)
        } else {
            counts[c as string] = subCategories.value.filter(({ category }: any) => category.includes(c)).reduce((a: number, b: any) => a + b.videosCount, 0)
        }
    }
    return counts
})

const sortedCategories = computed(() => {
    if (props.categories_sort_order === "alphabetical") {
        return categories.value.toSorted((a: any, b: any) => a.localeCompare(b))
    } else if (props.categories_sort_order === "count") {
        return categories.value.toSorted((a: any, b: any) => (categoryCounts.value[b as string] - categoryCounts.value[a as string]))
    } else {
        return categories.value
    }
})

const filteredSubCategories = computed(() => {
    let filtered = subCategories.value
    if (selectedCategory.value !== "All") {
        if (props.single_parent_category) {
            filtered = subCategories.value.filter(({ category }: any) => category === selectedCategory.value)
        } else {
            filtered = subCategories.value.filter(({ category }: any) => category.includes(selectedCategory.value))
        }
    }

    if (props.subcategories_sort_order === "alphabetical") {
        filtered.sort((a: any, b: any) => a.name.localeCompare(b.name))
    } else if (props.subcategories_sort_order === "count") {
        filtered.sort((a: any, b: any) => (b.videosCount - a.videosCount))
    }
    return filtered
})

let selectedCategory = ref("All")
let isLoadingSubCategories = ref(false)

function selectCategory(category: string) {
    if (category !== selectedCategory.value) {
        selectedCategory.value = category
        isLoadingSubCategories.value = false
        //setTimeout(() => {
        //    isLoadingSubCategories.value = false
        //}, 800)
    }
}
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
                class="relative isolate mb-3 flex w-auto shrink-0 snap-center flex-col justify-end gap-y-2 rounded-md">
                <button
                    class="me-2 rounded-full px-4 py-2 font-bold text-white hover:bg-red-400"
                    :class="
                        category === selectedCategory
                            ? 'bg-primary'
                            : 'bg-gray-700'
                    "
                    @click="selectCategory(category)">
                    {{ category }}
                </button>
            </li>
        </ul>
    </div>
    <div class="w-full px-4 my-3">
        <h1 class="pb-6 text-lg" v-if="!hide_subcategories_text">
            Subcategories for:
            <span class="text-xl font-bold">{{ selectedCategory }}</span>
            <span v-if="subcategories_sort_order === 'alphabetical'"> (alphabetical order)</span>
            <span v-else-if="subcategories_sort_order === 'count'"> (most programmes first)</span>
        </h1>
        <div
            v-if="isLoadingSubCategories"
            class="grid grid-cols-2 gap-x-4 gap-y-8 sm:grid-cols-2 sm:gap-x-6 lg:grid-cols-3 xl:gap-x-8">
            <CardSkeleton
                v-for="skeletonIndex in 6"
                :key="skeletonIndex"
                :rowCount="1"
                :customClasses="'bg-blue-950'"
                :darkText="false" />
        </div>
        <ul
            v-else
            class="grid grid-cols-2 gap-x-4 gap-y-8 sm:grid-cols-2 sm:gap-x-6 lg:grid-cols-3 xl:gap-x-8">
            <Link
                v-for="(subcategory, index) in (fold_results ? filteredSubCategories.slice(0, num_shown_folded) : filteredSubCategories)"
                :key="index"
                :href="subcategory.url"
                :id="subcategory.name"
                class="rounded-lg bg-blue-950 p-4">
                <h2 class="font-bold">{{ subcategory.name }}</h2>
                <div>
                    {{ subcategory.videosCount }} programme{{
                        subcategory.videosCount == 1 ? "" : "s"
                    }}
                </div>
            </Link>
        </ul>
        <button class="bg-blue-950 mx-auto flex w-auto rounded-md p-3 my-6 cursor-pointer" @click="fold_results=false" v-if="fold_results && filteredSubCategories.length > num_shown_folded">
            Show All
        </button>
    </div>
</template>
