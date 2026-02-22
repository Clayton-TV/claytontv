import { computed, ref } from 'vue';

interface CategoryItem {
    name: string;
    category: string | string[];
    url: string;
    videosCount: number;
}

interface UseCategoryFilterOptions {
    items: CategoryItem[];
    singleParentCategory?: boolean;
    retainOrder?: boolean;
}

export function useCategoryFilter(options: UseCategoryFilterOptions) {
    const { items, singleParentCategory = false, retainOrder = false } = options;

    const categories = ref([
        'All',
        ...items
            .map((t) => t.category)
            .flat(Infinity)
            .filter((item, index, array) => array.indexOf(item) === index),
    ] as string[]);

    const selectedCategory = ref('All');
    const isLoading = ref(false);

    const sortedCategories = computed(() => {
        return retainOrder ? categories.value : [...categories.value].sort((a, b) => a.localeCompare(b));
    });

    const filteredItems = computed(() => {
        const sorted = retainOrder ? items : [...items].sort((a, b) => a.name.localeCompare(b.name));
        if (selectedCategory.value === 'All') return sorted;
        if (singleParentCategory) {
            return sorted.filter(({ category }) => category === selectedCategory.value);
        }
        return sorted.filter(({ category }) =>
            Array.isArray(category) ? category.includes(selectedCategory.value) : category === selectedCategory.value,
        );
    });

    function selectCategory(category: string) {
        if (category !== selectedCategory.value) {
            selectedCategory.value = category;
            isLoading.value = false;
        }
    }

    return { sortedCategories, filteredItems, selectedCategory, isLoading, selectCategory };
}
