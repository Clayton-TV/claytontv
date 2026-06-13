<script setup>
import { CommandDialog, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList, CommandSeparator } from '@/ui/command';
import { router } from '@inertiajs/vue3';
import {
    IconArrowRight,
    IconBook,
    IconCategory,
    IconClock,
    IconLayoutGrid,
    IconMicrophone,
    IconSearch,
    IconSparkles,
    IconVideo,
} from '@tabler/icons-vue';
import { ref, watch } from 'vue';
import { usePalette } from '~/composables/usePalette';
import { useWatchHistory } from '~/composables/useWatchHistory';

const { paletteOpen } = usePalette();
const { continueWatching } = useWatchHistory();

const query = ref('');
const results = ref({ videos: [], categories: [] });
let debounceTimer = null;
let inFlight = null;

const kindIcons = {
    Series: IconLayoutGrid,
    Speaker: IconMicrophone,
    Topic: IconCategory,
    Ministry: IconSparkles,
    Book: IconBook,
};

const onQuery = (value) => {
    query.value = value;
    clearTimeout(debounceTimer);
    if (!value.trim()) {
        results.value = { videos: [], categories: [] };
        return;
    }
    debounceTimer = setTimeout(async () => {
        inFlight?.abort();
        inFlight = new AbortController();
        try {
            const response = await fetch(`/api/palette?q=${encodeURIComponent(value.trim())}`, { signal: inFlight.signal });
            results.value = await response.json();
        } catch {
            // aborted or offline — keep showing the previous results
        }
    }, 180);
};

const go = (url) => {
    paletteOpen.value = false;
    router.visit(url);
};

const formatTime = (totalSeconds) => {
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = Math.floor(totalSeconds % 60);
    return `${minutes}:${String(seconds).padStart(2, '0')}`;
};

// Fresh slate each open
watch(paletteOpen, (open) => {
    if (open) {
        query.value = '';
        results.value = { videos: [], categories: [] };
    }
});

const navShortcuts = [
    { name: 'Browse & filter all teaching', url: '/browse/' },
    { name: 'Latest teaching', url: '/latest/' },
    { name: 'Live & services', url: '/livestreams/' },
    { name: 'Series', url: '/series/' },
    { name: 'Topics', url: '/topic/' },
    { name: 'Speakers', url: '/speaker/' },
    { name: 'Bible books', url: '/book/' },
    { name: 'For every age (Kids, Youth, Adults)', url: '/audience/' },
];
</script>

<template>
    <CommandDialog v-model:open="paletteOpen" title="Search" description="Search teaching, series, speakers and more">
        <CommandInput aria-label="Search teaching, series, speakers" placeholder="Search teaching, series, speakers…" @update:model-value="onQuery" />
        <CommandList>
            <CommandEmpty v-if="query.trim()">No matches for “{{ query }}”</CommandEmpty>

            <template v-if="!query.trim()">
                <CommandGroup v-if="continueWatching().length" heading="Continue watching">
                    <CommandItem v-for="item in continueWatching()" :key="item.id" :value="`resume-${item.id}`" @select="go(`/video/${item.id}`)">
                        <IconClock class="text-primary h-4 w-4 shrink-0" aria-hidden="true" />
                        <span class="truncate">{{ item.name }}</span>
                        <span class="ml-auto text-xs text-gray-500 tabular-nums">{{ formatTime(item.t) }} / {{ formatTime(item.d) }}</span>
                    </CommandItem>
                </CommandGroup>
                <CommandGroup heading="Go to">
                    <CommandItem v-for="nav in navShortcuts" :key="nav.url" :value="nav.name" @select="go(nav.url)">
                        <IconArrowRight class="h-4 w-4 shrink-0 text-gray-500" aria-hidden="true" />
                        {{ nav.name }}
                    </CommandItem>
                </CommandGroup>
            </template>

            <template v-else>
                <CommandGroup v-if="results.videos.length" heading="Videos">
                    <CommandItem v-for="video in results.videos" :key="video.id" :value="`v-${video.id} ${video.name}`" @select="go(video.url)">
                        <IconVideo class="h-4 w-4 shrink-0 text-gray-500" aria-hidden="true" />
                        <span class="truncate">{{ video.name }}</span>
                        <span v-if="video.date" class="ml-auto text-xs text-gray-500 tabular-nums">{{ video.date }}</span>
                    </CommandItem>
                </CommandGroup>
                <CommandGroup v-if="results.categories.length" heading="Browse">
                    <CommandItem
                        v-for="category in results.categories"
                        :key="`${category.kind}-${category.url}`"
                        :value="`c-${category.kind}-${category.name}`"
                        @select="go(category.url)"
                    >
                        <component :is="kindIcons[category.kind] || IconCategory" class="h-4 w-4 shrink-0 text-gray-500" aria-hidden="true" />
                        <span class="truncate">{{ category.name }}</span>
                        <span class="ml-auto flex items-center gap-2 text-xs text-gray-500">
                            <span v-if="category.count" class="tabular-nums">{{ category.count }} videos</span>
                            <span class="rounded bg-white/10 px-1.5 py-0.5 text-[10px] tracking-wide uppercase">{{ category.kind }}</span>
                        </span>
                    </CommandItem>
                </CommandGroup>
                <CommandSeparator />
                <CommandGroup>
                    <CommandItem :value="`all ${query}`" @select="go(`/search?search=${encodeURIComponent(query.trim())}`)">
                        <IconSearch class="h-4 w-4 shrink-0 text-gray-500" aria-hidden="true" />
                        See all results for “{{ query.trim() }}”
                    </CommandItem>
                </CommandGroup>
            </template>
        </CommandList>
    </CommandDialog>
</template>
