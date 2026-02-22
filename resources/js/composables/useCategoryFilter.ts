import { computed, ref, type ComputedRef, type Ref } from 'vue';

interface CategoryItem {
    name: string;
    category: string | string[];
    [key: string]: unknown;
}

interface UseCategoryFilterOptions {
    singleParentCategory?: boolean;
    retainOrder?: boolean;
}

interface UseCategoryFilterReturn {
    sortedCategories: ComputedRef<string[]>;
    filteredItems: ComputedRef<CategoryItem[]>;
    selectedCategory: Ref<string>;
    selectCategory: (category: string) => void;
}

export function useCategoryFilter(
    items: Ref<CategoryItem[]> | ComputedRef<CategoryItem[]> | CategoryItem[],
    options: UseCategoryFilterOptions = {},
): UseCategoryFilterReturn {
    const { singleParentCategory = false, retainOrder = false } = options;

    const rawItems = computed(() => (Array.isArray(items) ? items : items.value));

    const categories = computed(() => {
        const allCategories = rawItems.value.map((item) => item.category);
        const flattened = ['All', ...allCategories].flat(Infinity) as string[];
        return flattened.filter((item, index, array) => array.indexOf(item) === index);
    });

    const sortedCategories = computed(() => {
        if (retainOrder) {
            return categories.value;
        }
        return [...categories.value].sort((a, b) => a.localeCompare(b));
    });

    const selectedCategory = ref('All');

    const filteredItems = computed(() => {
        const sorted = retainOrder ? rawItems.value : [...rawItems.value].sort((a, b) => a.name.localeCompare(b.name));

        if (selectedCategory.value === 'All') {
            return sorted;
        }

        if (singleParentCategory) {
            return sorted.filter(({ category }) => category === selectedCategory.value);
        }

        return sorted.filter(({ category }) => category.includes(selectedCategory.value));
    });

    function selectCategory(category: string): void {
        if (category !== selectedCategory.value) {
            selectedCategory.value = category;
        }
    }

    return {
        sortedCategories,
        filteredItems,
        selectedCategory,
        selectCategory,
    };
}
