<script setup>
import PaginationNav from '@/molecules/PaginationNav.vue';
import SeriesCard from '@/molecules/SeriesCard.vue';
import { Head, router } from '@inertiajs/vue3';
import { IconSearch } from '@tabler/icons-vue';
import { ref } from 'vue';

const props = defineProps({
    series: { type: Array, default: () => [] },
    query: { type: String, default: '' },
    total: { type: Number, default: 0 },
    has_prev_page: { type: Boolean },
    has_next_page: { type: Boolean },
});

const filter = ref(props.query);

const submitFilter = () => {
    router.get('/series/', filter.value ? { q: filter.value } : {}, { preserveState: true });
};
</script>

<template>
    <Head title="Series" />
    <div class="mx-auto max-w-6xl px-4 py-10 lg:px-8">
        <div class="flex flex-wrap items-end justify-between gap-4">
            <div>
                <h1 class="font-display text-foreground text-2xl font-bold sm:text-3xl">Series</h1>
                <p class="text-muted-foreground mt-2 text-sm tabular-nums">
                    {{ total }} series{{ query ? ` matching “${query}”` : '' }}, most episodes first
                </p>
            </div>
            <form @submit.prevent="submitFilter" class="w-full sm:w-72">
                <label class="sr-only" for="series-filter">Filter series</label>
                <div class="relative">
                    <IconSearch
                        class="text-muted-foreground pointer-events-none absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2"
                        aria-hidden="true"
                    />
                    <input
                        id="series-filter"
                        v-model="filter"
                        type="search"
                        placeholder="Filter series…"
                        class="focus:ring-ring border-border bg-muted text-foreground placeholder:text-muted-foreground focus:bg-accent h-11 w-full rounded-lg border pr-3 pl-9 text-base transition-colors duration-150 focus:ring-2 focus:outline-none"
                    />
                </div>
            </form>
        </div>

        <div class="mt-8 grid gap-5 sm:grid-cols-2">
            <SeriesCard v-for="entry in series" :key="entry.url" :series="entry" />
        </div>
        <p v-if="!series.length" class="text-muted-foreground mt-12 text-center text-sm">No series match “{{ query }}”.</p>

        <div class="mt-10">
            <PaginationNav :has-prev-page="has_prev_page" :has-next-page="has_next_page" />
        </div>
    </div>
</template>
