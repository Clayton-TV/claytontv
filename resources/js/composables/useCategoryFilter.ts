import { computed, ref, type ComputedRef, type Ref } from 'vue';

/**
 * Category-filtering state for the CategoriesBrowseWidget.
 *
 * Each item belongs to one category (`single_parent_category`, so `category` is
 * a string) or several (so `category` is an array). The composable derives the
 * distinct category list, per-category video counts, the active selection, and
 * the filtered + sorted item list.
 *
 * Sort orders match the widget's props — `'alphabetical'`, `'count'`, or
 * `'none'` (retain source order) — applied independently to the category chips
 * and the filtered items.
 */

export type SortOrder = 'alphabetical' | 'count' | 'none';

export interface CategoryItem {
    name: string;
    url: string;
    category: string | string[];
    videosCount: number;
    [key: string]: unknown;
}

export interface UseCategoryFilterOptions {
    singleParentCategory?: boolean;
    categoriesSortOrder?: SortOrder;
    subcategoriesSortOrder?: SortOrder;
}

export interface UseCategoryFilterReturn {
    categories: ComputedRef<string[]>;
    categoryCounts: ComputedRef<Record<string, number>>;
    sortedCategories: ComputedRef<string[]>;
    filteredItems: ComputedRef<CategoryItem[]>;
    selectedCategory: Ref<string>;
    selectCategory: (category: string) => void;
}

export function useCategoryFilter(
    items: Ref<CategoryItem[]> | ComputedRef<CategoryItem[]> | CategoryItem[],
    options: UseCategoryFilterOptions = {},
): UseCategoryFilterReturn {
    const { singleParentCategory = false, categoriesSortOrder = 'none', subcategoriesSortOrder = 'none' } = options;

    const rawItems = computed(() => (Array.isArray(items) ? items : items.value));

    const belongsTo = (item: CategoryItem, category: string) =>
        singleParentCategory ? item.category === category : (item.category as string[]).includes(category);

    // Distinct category list, keeping the first instance of each category.
    const categories = computed(() => {
        const all = [rawItems.value.map((item) => item.category)].flat(Infinity) as string[];
        return all.filter((item, index, array) => array.indexOf(item) === index);
    });

    const categoryCounts = computed(() => {
        const counts: Record<string, number> = {};
        for (const category of categories.value) {
            counts[category] = rawItems.value.filter((item) => belongsTo(item, category)).reduce((sum, item) => sum + item.videosCount, 0);
        }
        return counts;
    });

    const sortedCategories = computed(() => {
        if (categoriesSortOrder === 'alphabetical') {
            return [...categories.value].sort((a, b) => a.localeCompare(b));
        } else if (categoriesSortOrder === 'count') {
            return [...categories.value].sort((a, b) => categoryCounts.value[b] - categoryCounts.value[a]);
        }
        return categories.value;
    });

    const selectedCategory = ref('All');

    const filteredItems = computed(() => {
        let filtered = rawItems.value;
        if (selectedCategory.value !== 'All') {
            filtered = rawItems.value.filter((item) => belongsTo(item, selectedCategory.value));
        }

        if (subcategoriesSortOrder === 'alphabetical') {
            return [...filtered].sort((a, b) => a.name.localeCompare(b.name));
        } else if (subcategoriesSortOrder === 'count') {
            return [...filtered].sort((a, b) => b.videosCount - a.videosCount);
        }
        return filtered;
    });

    function selectCategory(category: string): void {
        if (category !== selectedCategory.value) {
            selectedCategory.value = category;
        }
    }

    return {
        categories,
        categoryCounts,
        sortedCategories,
        filteredItems,
        selectedCategory,
        selectCategory,
    };
}
