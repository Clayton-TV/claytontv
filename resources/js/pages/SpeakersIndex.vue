<script setup>
import SectionHeading from '@/molecules/SectionHeading.vue';
import { Skeleton } from '@/ui/skeleton';
import { Head, Link, WhenVisible, router } from '@inertiajs/vue3';
import { IconSearch, IconX } from '@tabler/icons-vue';
import { ref } from 'vue';

const props = defineProps({
    query: { type: String, default: '' },
    total: { type: Number, default: 0 },
    results: { type: Array, default: () => [] },
    featured: { type: Array, default: () => [] },
    all_speakers: { type: Array, default: null },
});

const filter = ref(props.query);

const submit = () => {
    router.get('/speaker/', filter.value ? { q: filter.value } : {}, { preserveState: true });
};

const clear = () => {
    filter.value = '';
    router.get('/speaker/');
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
        <!-- Lookup-first: the search IS the hero. Nobody scans 662 names. -->
        <div class="mx-auto max-w-xl text-center">
            <h1 class="font-display text-2xl font-bold text-gray-50 sm:text-3xl">Speakers</h1>
            <p class="mt-2 text-sm text-gray-500 tabular-nums">Find any of the {{ total }} speakers on Clayton TV</p>
            <form @submit.prevent="submit" class="mt-5">
                <label class="sr-only" for="speaker-search">Search speakers</label>
                <div class="relative">
                    <IconSearch class="pointer-events-none absolute top-1/2 left-4 h-5 w-5 -translate-y-1/2 text-gray-500" aria-hidden="true" />
                    <input
                        id="speaker-search"
                        v-model="filter"
                        type="search"
                        placeholder="Search by name…"
                        class="focus:ring-ring h-13 w-full rounded-xl border border-white/10 bg-white/5 pr-4 pl-12 text-base text-gray-100 transition-colors duration-150 placeholder:text-gray-500 focus:bg-white/10 focus:ring-2 focus:outline-none"
                    />
                </div>
            </form>
        </div>

        <!-- Lookup results -->
        <section v-if="query" class="mt-10" aria-label="Results">
            <div class="flex items-baseline justify-between">
                <h2 class="text-xs font-semibold tracking-wider text-gray-500 uppercase">
                    {{ results.length }} {{ results.length === 1 ? 'match' : 'matches' }} for “{{ query }}”
                </h2>
                <button
                    @click="clear"
                    class="focus-visible:ring-ring inline-flex items-center gap-1 rounded text-xs font-medium text-gray-400 outline-none hover:text-white focus-visible:ring-2"
                >
                    <IconX class="h-3.5 w-3.5" aria-hidden="true" /> Clear
                </button>
            </div>
            <ul class="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
                <li v-for="speaker in results" :key="speaker.url">
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
            <p v-if="!results.length" class="mt-10 text-center text-sm text-gray-500">No speakers match “{{ query }}”.</p>
        </section>

        <template v-else>
            <!-- Curated tier: the voices with the deepest catalogues -->
            <section class="mt-12" aria-label="Featured voices">
                <SectionHeading title="Featured voices" />
                <div class="grid gap-4 sm:grid-cols-2">
                    <Link
                        v-for="speaker in featured"
                        :key="speaker.url"
                        :href="speaker.url"
                        prefetch
                        class="focus-visible:ring-ring flex items-center gap-4 rounded-xl border border-white/10 bg-white/[0.03] p-4 transition-colors duration-150 outline-none hover:border-white/20 hover:bg-white/[0.06] focus-visible:ring-2"
                    >
                        <span
                            class="bg-primary/10 text-primary flex h-14 w-14 flex-none items-center justify-center rounded-full text-lg font-semibold"
                            aria-hidden="true"
                        >
                            {{ initials(speaker.name) }}
                        </span>
                        <span class="min-w-0">
                            <span class="block truncate text-[15px] font-semibold text-gray-50">{{ speaker.name }}</span>
                            <span class="block text-xs text-gray-500 tabular-nums">
                                {{ speaker.videosCount }} talks<template v-if="speaker.knownFor"> · known for {{ speaker.knownFor }}</template>
                            </span>
                        </span>
                    </Link>
                </div>
            </section>

            <!-- The long tail: present, honest, compact — and only loaded on scroll -->
            <WhenVisible data="all_speakers" :buffer="300">
                <template #fallback>
                    <section class="mt-14" aria-label="All speakers">
                        <Skeleton class="h-7 w-48 bg-white/5" />
                        <div class="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
                            <Skeleton v-for="n in 12" :key="n" class="h-5 w-36 bg-white/5" />
                        </div>
                    </section>
                </template>
                <section class="mt-14" aria-label="All speakers">
                    <SectionHeading title="All speakers A–Z" />
                    <div v-for="group in all_speakers || []" :key="group.letter" class="mt-6">
                        <h3 class="text-xs font-semibold tracking-wider text-gray-500 uppercase">{{ group.letter }}</h3>
                        <ul class="mt-2 grid grid-cols-1 gap-x-6 gap-y-1.5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                            <li v-for="speaker in group.speakers" :key="speaker.url" class="min-w-0">
                                <Link
                                    :href="speaker.url"
                                    class="focus-visible:ring-ring inline-flex max-w-full items-baseline gap-1.5 rounded text-sm text-gray-300 outline-none hover:text-white hover:underline focus-visible:ring-2"
                                >
                                    <span class="truncate">{{ speaker.name }}</span>
                                    <span class="shrink-0 text-xs text-gray-600 tabular-nums">{{ speaker.videosCount }}</span>
                                </Link>
                            </li>
                        </ul>
                    </div>
                </section>
            </WhenVisible>
        </template>
    </div>
</template>
