<script setup>
import PaginationNav from '@/molecules/PaginationNav.vue';
import { Head, Link, router } from '@inertiajs/vue3';
import { IconSearch } from '@tabler/icons-vue';
import { ref } from 'vue';

const props = defineProps({
    speakers: { type: Array, default: () => [] },
    query: { type: String, default: '' },
    total: { type: Number, default: 0 },
    has_prev_page: { type: Boolean },
    has_next_page: { type: Boolean },
});

const filter = ref(props.query);

const submitFilter = () => {
    router.get('/speaker/', filter.value ? { q: filter.value } : {}, { preserveState: true });
};

// "Surname, First" → initials for the avatar tile
const initials = (name) =>
    name
        .split(/[,\s]+/)
        .filter(Boolean)
        .slice(0, 2)
        .map((part) => part[0]?.toUpperCase())
        .join('');
</script>

<template>
    <Head title="Speakers" />
    <div class="mx-auto max-w-6xl px-4 py-10 lg:px-8">
        <div class="flex flex-wrap items-end justify-between gap-4">
            <div>
                <h1 class="font-display text-2xl font-bold text-gray-50 sm:text-3xl">Speakers</h1>
                <p class="mt-2 text-sm text-gray-500 tabular-nums">{{ total }} speakers{{ query ? ` matching “${query}”` : '' }}</p>
            </div>
            <form @submit.prevent="submitFilter" class="w-full sm:w-72">
                <label class="sr-only" for="speaker-filter">Filter speakers</label>
                <div class="relative">
                    <IconSearch class="pointer-events-none absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2 text-gray-500" aria-hidden="true" />
                    <input
                        id="speaker-filter"
                        v-model="filter"
                        type="search"
                        placeholder="Filter speakers…"
                        class="focus:ring-ring h-11 w-full rounded-lg border border-white/10 bg-white/5 pr-3 pl-9 text-base text-gray-100 transition-colors duration-150 placeholder:text-gray-500 focus:bg-white/10 focus:ring-2 focus:outline-none"
                    />
                </div>
            </form>
        </div>

        <ul class="mt-8 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
            <li v-for="speaker in speakers" :key="speaker.url">
                <Link
                    :href="speaker.url"
                    prefetch
                    class="focus-visible:ring-ring flex items-center gap-3.5 rounded-xl border border-white/10 bg-white/[0.03] p-3.5 transition-colors duration-150 outline-none hover:border-white/20 hover:bg-white/[0.06] focus-visible:ring-2"
                >
                    <span
                        class="bg-primary/10 text-primary flex h-11 w-11 flex-none items-center justify-center rounded-full text-sm font-semibold"
                        aria-hidden="true"
                    >
                        {{ initials(speaker.name) }}
                    </span>
                    <span class="min-w-0">
                        <span class="block truncate text-[15px] font-medium text-gray-100">{{ speaker.name }}</span>
                        <span class="block text-xs text-gray-500 tabular-nums">
                            {{ speaker.videosCount }} {{ speaker.videosCount === 1 ? 'talk' : 'talks' }}
                        </span>
                    </span>
                </Link>
            </li>
        </ul>
        <p v-if="!speakers.length" class="mt-12 text-center text-sm text-gray-500">No speakers match “{{ query }}”.</p>

        <div class="mt-10">
            <PaginationNav :has-prev-page="has_prev_page" :has-next-page="has_next_page" />
        </div>
    </div>
</template>
