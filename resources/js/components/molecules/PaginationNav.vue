<script setup lang="ts">
import { router } from '@inertiajs/vue3';
import { ChevronLeft, ChevronRight, Ellipsis } from 'lucide-vue-next';

defineProps({
    hasPrevPage: { type: Boolean, default: false },
    hasNextPage: { type: Boolean, default: false },
    pageRange: { type: Array },
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
    <nav
        v-if="hasPrevPage || hasNextPage"
        class="flex w-full justify-center gap-x-1 text-sm font-medium tabular-nums md:gap-x-2 lg:gap-x-3"
        aria-label="Pagination"
    >
        <button
            class="focus-visible:ring-ring border-input text-foreground hover:border-ring hover:text-foreground disabled:hover:border-input min-h-11 cursor-pointer rounded-lg border px-2 transition-colors duration-150 outline-none focus-visible:ring-2 disabled:cursor-default disabled:opacity-35 md:px-3 lg:px-5"
            :disabled="!hasPrevPage"
            @click="goTo(currentPage() - 1)"
        >
            <ChevronLeft />
        </button>

        <template v-for="pn in pageRange" :key="pn">
            <button
                class="focus-visible:ring-ring border-input text-foreground hover:border-ring hover:text-foreground disabled:hover:border-input disabled:bg-accent min-h-11 max-w-[50px] min-w-[32px] flex-1 cursor-pointer rounded-lg border transition-colors duration-150 outline-none focus-visible:ring-2 disabled:cursor-default"
                :disabled="pn == currentPage()"
                @click="goTo(pn)"
                v-if="pn != '…'"
            >
                {{ pn }}
            </button>
            <Ellipsis class="self-center sm:w-[32px] md:w-[44px]" v-else />
        </template>

        <button
            class="focus-visible:ring-ring border-input text-foreground hover:border-ring hover:text-foreground disabled:hover:border-input min-h-11 cursor-pointer rounded-lg border px-2 transition-colors duration-150 outline-none focus-visible:ring-2 disabled:cursor-default disabled:opacity-35 md:px-3 lg:px-5"
            :disabled="!hasNextPage"
            @click="goTo(currentPage() + 1)"
        >
            <ChevronRight />
        </button>
    </nav>
</template>
