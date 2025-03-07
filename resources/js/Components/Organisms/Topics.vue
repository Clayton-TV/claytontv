<script setup>
import { ref, computed } from "vue"
import LoadingSpinner from "../Atoms/LoadingSpinner.vue"
import CardSkeleton from "../Atoms/CardSkeleton.vue"
import { Link } from "@inertiajs/vue3"
const props = defineProps({
    topics_data: {
        type: Object,
        required: true,
    },
})

// List out category from all topics, then filter down to only keep the first instance of each category
const categories = ref([
    "All",
    ...props.topics_data
        .map((t) => t.category)
        .filter((item, index, array) => array.indexOf(item) == index),
])

// For each topic entry, obtain its name, category it belongs to, and number of videos it encompasses
const subCategories = ref(props.topics_data)

const sortedCategories = computed(() => {
    return categories.value.sort((a, b) => a.localeCompare(b))
})
const filteredSubCategories = computed(() => {
    const sortedSubCategories = subCategories.value.sort((a, b) =>
        a.name.localeCompare(b.name)
    )
    if (selectedCategory.value === "All") {
        return sortedSubCategories
    }
    return sortedSubCategories.filter(
        ({ category }) => category === selectedCategory.value
    )
})

let selectedCategory = ref("All")
let isLoadingSubCategories = ref(false)

function selectCategory(category) {
    if (category !== selectedCategory.value) {
        selectedCategory.value = category
        isLoadingSubCategories.value = true
        setTimeout(() => {
            isLoadingSubCategories.value = false
        }, 800)
    }
}
</script>

<template>
    <div class="mb-4 justify-items-center space-y-2">
        <h2 class="text-center text-3xl font-bold text-gray-100">
            Explore Topics
        </h2>
        <p class="text-center text-gray-400">
            There are a variety of topics for you to discover
        </p>
    </div>
    <div class="w-full items-center justify-center overflow-x-hidden pt-4">
        <ul class="flex snap-x snap-mandatory gap-x-0 overflow-x-auto px-2">
            <li
                v-for="(category, index) in sortedCategories"
                :key="index"
                class="relative isolate mb-3 flex w-auto shrink-0 snap-center flex-col justify-end gap-y-2 rounded-md">
                <button
                    class="me-2 rounded-full px-4 py-2 font-bold text-white hover:bg-red-400"
                    :class="
                        category === selectedCategory
                            ? 'bg-claytonRed'
                            : 'bg-gray-700'
                    "
                    @click="selectCategory(category)">
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
            <li
                v-for="(subcategory, index) in filteredSubCategories"
                :key="index"
                class="contents">
                <Link :href="`/topic/`+subcategory.name" :id="subcategory.name" class="rounded-lg bg-blue-950 p-4">
                    <h2 class="font-bold">{{ subcategory.name }}</h2>
                    <div>
                        {{ subcategory.videosCount }} programme{{
                            subcategory.videosCount == 1 ? "" : "s"
                        }}
                    </div>
                </Link>
            </li>
        </ul>
    </div>
</template>
