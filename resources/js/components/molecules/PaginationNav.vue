<script setup lang="ts">
import { router } from '@inertiajs/vue3';
import { ChevronLeft, ChevronRight, Ellipsis } from 'lucide-vue-next';
import { onMounted } from 'vue';

const props = defineProps({
    hasPrevPage: { type: Boolean, default: false },
    hasNextPage: { type: Boolean, default: false },
    numPages: { type: Number, default: 1 },
    // The page the server actually served. It can differ from the ?page= in the
    // URL, because an out-of-range page is clamped to the last real one — and
    // then a URL-derived Prev walks back through pages that all clamp to the
    // same content. Pages that don't send it fall back to the URL.
    currentPage: { type: Number, default: 0 },
});

const pageFromUrl = () => {
    const match = window.location.search.match(/[?&]page=([0-9]+)/);
    const page = parseInt(match?.[1] ?? '1');
    return isNaN(page) ? 1 : page;
};

const activePage = () => props.currentPage || pageFromUrl();

const goTo = (page: number) => {
    const params = new URLSearchParams(window.location.search);
    params.set('page', String(Math.max(1, page)));
    router.get(`${window.location.pathname}?${params}`, {}, { preserveScroll: false });
};

onMounted(() => {
    document.getElementById(`pagebutton-${activePage()}`)?.scrollIntoView();
});
</script>

<template>
    <!-- Version rendering on small screens (below md: breakpoint) -->
    <nav v-if="hasPrevPage || hasNextPage" class="flex w-full justify-center text-sm font-medium tabular-nums md:hidden" aria-label="Pagination">
        <button
            class="focus-visible:ring-ring border-input text-foreground hover:border-ring hover:text-foreground disabled:hover:border-input min-h-11 cursor-pointer rounded-lg border px-3 transition-colors duration-150 outline-none focus-visible:ring-2 disabled:cursor-default disabled:opacity-35"
            :disabled="!hasPrevPage"
            @click="goTo(activePage() - 1)"
        >
            <ChevronLeft />
        </button>

        <div class="flex snap-x items-center gap-x-1 overflow-x-scroll mask-x-from-[90%] px-8">
            <template v-for="pn in numPages" :key="pn">
                <button
                    class="focus-visible:ring-ring border-input text-foreground hover:border-ring hover:text-foreground disabled:hover:border-input disabled:bg-accent min-h-11 max-w-[50px] min-w-[44px] flex-1 cursor-pointer snap-center rounded-lg border transition-colors duration-150 outline-none focus-visible:ring-2 disabled:cursor-default"
                    :disabled="pn == activePage()"
                    :id="`pagebutton-${pn}`"
                    @click="goTo(pn)"
                >
                    {{ pn }}
                </button>
            </template>
        </div>

        <button
            class="focus-visible:ring-ring border-input text-foreground hover:border-ring hover:text-foreground disabled:hover:border-input min-h-11 cursor-pointer rounded-lg border px-3 transition-colors duration-150 outline-none focus-visible:ring-2 disabled:cursor-default disabled:opacity-35"
            :disabled="!hasNextPage"
            @click="goTo(activePage() + 1)"
        >
            <ChevronRight />
        </button>
    </nav>
    <!-- Version rendering on large screens (md: and above) -->
    <nav
        v-if="hasPrevPage || hasNextPage"
        class="hidden w-full justify-center gap-x-1 gap-x-2 text-sm font-medium tabular-nums md:flex lg:gap-x-3"
        aria-label="Pagination"
    >
        <button
            class="focus-visible:ring-ring border-input text-foreground hover:border-ring hover:text-foreground disabled:hover:border-input min-h-11 cursor-pointer rounded-lg border px-3 transition-colors duration-150 outline-none focus-visible:ring-2 disabled:cursor-default disabled:opacity-35 lg:px-5"
            :disabled="!hasPrevPage"
            @click="goTo(activePage() - 1)"
        >
            <ChevronLeft />
        </button>

        <template v-for="pn in numPages" :key="pn">
            <button
                class="focus-visible:ring-ring border-input text-foreground hover:border-ring hover:text-foreground disabled:hover:border-input disabled:bg-accent min-h-11 max-w-[50px] min-w-[32px] flex-1 cursor-pointer rounded-lg border transition-colors duration-150 outline-none focus-visible:ring-2 disabled:cursor-default"
                :disabled="pn == activePage()"
                @click="goTo(pn)"
                v-if="pn <= 2 || pn > numPages - 2"
            >
                {{ pn }}
            </button>
            <button
                class="focus-visible:ring-ring border-input text-foreground hover:border-ring hover:text-foreground disabled:hover:border-input disabled:bg-accent min-h-11 max-w-[50px] min-w-[32px] flex-1 cursor-pointer rounded-lg border transition-colors duration-150 outline-none focus-visible:ring-2 disabled:cursor-default"
                :disabled="pn == activePage()"
                @click="goTo(pn)"
                v-else-if="pn <= activePage() + 3 && pn >= activePage() - 3"
            >
                {{ pn }}
            </button>
            <Ellipsis class="w-[32px] self-center" v-else-if="pn == 3 || pn == numPages - 2" />
        </template>

        <button
            class="focus-visible:ring-ring border-input text-foreground hover:border-ring hover:text-foreground disabled:hover:border-input min-h-11 cursor-pointer rounded-lg border px-3 transition-colors duration-150 outline-none focus-visible:ring-2 disabled:cursor-default disabled:opacity-35 lg:px-5"
            :disabled="!hasNextPage"
            @click="goTo(activePage() + 1)"
        >
            <ChevronRight />
        </button>
    </nav>
</template>
