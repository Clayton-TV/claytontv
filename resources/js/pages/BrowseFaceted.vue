<script setup>
import FilterChips from '@/molecules/FilterChips.vue';
import PaginationNav from '@/molecules/PaginationNav.vue';
import FacetSidebar from '@/organisms/FacetSidebar.vue';
import VideoCardGrid from '@/organisms/VideoCardGrid.vue';
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from '@/ui/sheet';
import { Head } from '@inertiajs/vue3';
import { IconAdjustmentsHorizontal } from '@tabler/icons-vue';
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
});

const { toggleMulti, setSingle, remove, clearAll, isActive, activeCount } = useBrowseFilters(() => props.active);

const filtersOpen = ref(false);
</script>

<template>
    <Head title="Browse teaching" />
    <div class="mx-auto max-w-6xl px-4 py-10 lg:px-8">
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
                    <IconAdjustmentsHorizontal class="h-4 w-4" aria-hidden="true" />
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
            <!-- Desktop sidebar: sticky under the header, one scroll region that
                 fills the viewport so it's clearly a scrollable container. -->
            <aside
                class="ctv-scroll hidden self-start lg:sticky lg:top-20 lg:block lg:max-h-[calc(100dvh-6rem)] lg:overflow-y-auto lg:pr-2 lg:pb-8"
                aria-label="Filters"
            >
                <FacetSidebar :facets="facets" :is-active="isActive" @single="setSingle" @toggle="toggleMulti" />
            </aside>

            <div class="mt-6 lg:mt-0">
                <div class="mb-5"><FilterChips :facets="facets" :active="active" @remove="remove" @clear="clearAll" /></div>
                <VideoCardGrid
                    :videos="videos"
                    empty-title="No videos match those filters"
                    empty-message="Try removing a filter to widen your search."
                />
                <!-- Own pagination so the filter query is preserved across pages -->
                <div v-if="videos.length" class="mt-6">
                    <PaginationNav :has-prev-page="has_prev_page" :has-next-page="has_next_page" />
                </div>
            </div>
        </div>
    </div>
</template>
