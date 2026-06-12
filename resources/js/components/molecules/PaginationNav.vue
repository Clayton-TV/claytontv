<script setup lang="ts">
import { router } from '@inertiajs/vue3';

const props = defineProps({
    hasPrevPage: { type: Boolean, default: false },
    hasNextPage: { type: Boolean, default: false },
});

const currentPage = () => {
    const match = window.location.search.match(/[?&]page=([0-9]+)/);
    const page = parseInt(match?.[1] ?? '1');
    return isNaN(page) ? 1 : page;
};

const goTo = (page: number) => {
    const params = new URLSearchParams(window.location.search);
    params.set('page', String(Math.max(1, page)));
    router.get(`${window.location.pathname}?${params}`, {}, { preserveScroll: false });
};
</script>

<template>
    <nav v-if="hasPrevPage || hasNextPage" class="flex justify-center gap-x-3" aria-label="Pagination">
        <button
            class="focus-visible:ring-ring min-h-11 cursor-pointer rounded-lg border border-white/15 px-5 text-sm font-medium text-gray-200 transition-colors duration-150 outline-none hover:border-white/30 hover:text-white focus-visible:ring-2 disabled:cursor-default disabled:opacity-35 disabled:hover:border-white/15"
            :disabled="!hasPrevPage"
            @click="goTo(currentPage() - 1)"
        >
            Previous
        </button>
        <button
            class="focus-visible:ring-ring min-h-11 cursor-pointer rounded-lg border border-white/15 px-5 text-sm font-medium text-gray-200 transition-colors duration-150 outline-none hover:border-white/30 hover:text-white focus-visible:ring-2 disabled:cursor-default disabled:opacity-35 disabled:hover:border-white/15"
            :disabled="!hasNextPage"
            @click="goTo(currentPage() + 1)"
        >
            Next
        </button>
    </nav>
</template>
