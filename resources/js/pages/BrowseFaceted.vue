<script setup>
import FilterChips from '@/molecules/FilterChips.vue';
import PaginationNav from '@/molecules/PaginationNav.vue';
import FacetSidebar from '@/organisms/FacetSidebar.vue';
import VideoCardGrid from '@/organisms/VideoCardGrid.vue';
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from '@/ui/sheet';
import { Head } from '@inertiajs/vue3';
import { SlidersHorizontal } from 'lucide-vue-next';
import { ref } from 'vue';
import { useBrowseFilters } from '~/composables/useBrowseFilters';

const props = defineProps({
    title: { type: String, default: 'Browse' },
    videos: { type: Array, default: () => [] },
    facets: { type: Object, required: true },
    active: { type: Object, required: true },
    total: { type: Number, default: 0 },
    has_prev_page: { type: Boolean, default: false },
    has_next_page: { type: Boolean, default: false },
    num_pages: { type: Number },
    page: { type: Number },
});

const { toggleMulti, setSingle, remove, clearAll, isActive, activeCount } = useBrowseFilters(() => props.active);

const filtersOpen = ref(false);
</script>

<template>
    <Head title="Browse teaching" />
    <!-- On desktop the filter-rail divider should meet the footer's top border:
         drop our bottom padding and cancel the footer's mt-16 (the results column
         carries its own bottom padding so content isn't cramped). Other pages keep
         the footer's normal top margin. -->
    <div class="mx-auto max-w-6xl px-4 pt-10 pb-10 lg:-mb-16 lg:px-8 lg:pb-0">
        <div class="flex flex-wrap items-end justify-between gap-3">
            <div>
                <h1 class="font-display text-foreground text-2xl font-bold sm:text-3xl">Browse teaching</h1>
                <p class="text-muted-foreground mt-2 text-sm tabular-nums">{{ total }} {{ total === 1 ? 'video' : 'videos' }}</p>
            </div>
            <!-- Mobile: open the filters in a sheet -->
            <Sheet v-model:open="filtersOpen">
                <SheetTrigger
                    class="focus-visible:ring-ring border-input text-foreground hover:border-ring hover:text-foreground inline-flex min-h-11 items-center gap-2 rounded-lg border px-4 text-sm font-medium outline-none focus-visible:ring-2 lg:hidden"
                >
                    <SlidersHorizontal class="h-4 w-4" aria-hidden="true" />
                    Filters<span v-if="activeCount()" class="bg-primary text-primary-foreground ml-1 rounded-full px-1.5 text-xs">{{
                        activeCount()
                    }}</span>
                </SheetTrigger>
                <SheetContent side="left" class="border-border bg-background text-foreground overflow-y-auto">
                    <SheetHeader><SheetTitle class="font-display text-foreground text-left">Filters</SheetTitle></SheetHeader>
                    <div class="px-4 py-2">
                        <FacetSidebar :facets="facets" :is-active="isActive" @single="setSingle" @toggle="toggleMulti" />
                    </div>
                </SheetContent>
            </Sheet>
        </div>

        <div class="mt-6 lg:grid lg:grid-cols-[16rem_1fr] lg:gap-8">
            <!-- Desktop filter rail: a full-height bordered panel (so the space
                 below the facets reads as an intentional rail, not a void) with
                 the facets in a sticky, viewport-height scroll region inside it. -->
            <aside class="lg:border-border hidden lg:block lg:border-r lg:pr-6" aria-label="Filters">
                <div class="ctv-scroll sticky top-20 max-h-[calc(100dvh-6rem)] overflow-y-auto pb-8">
                    <FacetSidebar :facets="facets" :is-active="isActive" @single="setSingle" @toggle="toggleMulti" />
                </div>
            </aside>

            <div class="mt-6 lg:mt-0 lg:pb-10">
                <div class="mb-5"><FilterChips :facets="facets" :active="active" @remove="remove" @clear="clearAll" /></div>
                <VideoCardGrid
                    :videos="videos"
                    empty-title="No videos match those filters"
                    empty-message="Try removing a filter to widen your search."
                />
                <!-- Own pagination so the filter query is preserved across pages -->
                <div v-if="videos.length" class="mt-6">
                    <PaginationNav :num-pages="num_pages" :current-page="page" :has-prev-page="has_prev_page" :has-next-page="has_next_page" />
                </div>
            </div>
        </div>
    </div>
</template>
