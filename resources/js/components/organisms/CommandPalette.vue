<script setup>
import { CommandDialog, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList, CommandSeparator } from '@/ui/command';
import { router } from '@inertiajs/vue3';
import {
    IconArrowRight,
    IconBook,
    IconCategory,
    IconCheck,
    IconClock,
    IconDeviceDesktop,
    IconLayoutGrid,
    IconMicrophone,
    IconMoon,
    IconRestore,
    IconSearch,
    IconSparkles,
    IconSun,
    IconTextDecrease,
    IconTextIncrease,
    IconVideo,
} from '@tabler/icons-vue';
import { computed, ref, watch } from 'vue';
import { useAppearance } from '~/composables/useAppearance';
import { usePalette } from '~/composables/usePalette';
import { useTextScale } from '~/composables/useTextScale';
import { useWatchHistory } from '~/composables/useWatchHistory';

const { paletteOpen } = usePalette();
const { continueWatching } = useWatchHistory();
const { appearance, updateAppearance } = useAppearance();
const { scale, increase, decrease, reset, canIncrease, canDecrease, isDefault } = useTextScale();

// Theme + text-size live inside the palette too — selecting one applies it
// immediately and keeps the palette open so the change is visible and you can
// fine-tune (e.g. tap "Larger text" twice). Searchable by "theme"/"text size".
const themeOptions = [
    { value: 'light', label: 'Light theme', icon: IconSun },
    { value: 'system', label: 'Use system theme', icon: IconDeviceDesktop },
    { value: 'dark', label: 'Dark theme', icon: IconMoon },
];
const scalePercent = computed(() => `${Math.round(scale.value * 100)}%`);

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
                        <span class="text-muted-foreground ml-auto text-xs tabular-nums">{{ formatTime(item.t) }} / {{ formatTime(item.d) }}</span>
                    </CommandItem>
                </CommandGroup>
                <CommandGroup heading="Go to">
                    <CommandItem v-for="nav in navShortcuts" :key="nav.url" :value="nav.name" @select="go(nav.url)">
                        <IconArrowRight class="text-muted-foreground h-4 w-4 shrink-0" aria-hidden="true" />
                        {{ nav.name }}
                    </CommandItem>
                </CommandGroup>
            </template>

            <template v-else>
                <CommandGroup v-if="results.videos.length" heading="Videos">
                    <CommandItem v-for="video in results.videos" :key="video.id" :value="`v-${video.id} ${video.name}`" @select="go(video.url)">
                        <IconVideo class="text-muted-foreground h-4 w-4 shrink-0" aria-hidden="true" />
                        <span class="truncate">{{ video.name }}</span>
                        <span v-if="video.date" class="text-muted-foreground ml-auto text-xs tabular-nums">{{ video.date }}</span>
                    </CommandItem>
                </CommandGroup>
                <CommandGroup v-if="results.categories.length" heading="Browse">
                    <CommandItem
                        v-for="category in results.categories"
                        :key="`${category.kind}-${category.url}`"
                        :value="`c-${category.kind}-${category.name}`"
                        @select="go(category.url)"
                    >
                        <component :is="kindIcons[category.kind] || IconCategory" class="text-muted-foreground h-4 w-4 shrink-0" aria-hidden="true" />
                        <span class="truncate">{{ category.name }}</span>
                        <span class="text-muted-foreground ml-auto flex items-center gap-2 text-xs">
                            <span v-if="category.count" class="tabular-nums">{{ category.count }} videos</span>
                            <span class="bg-muted rounded px-1.5 py-0.5 text-[10px] tracking-wide uppercase">{{ category.kind }}</span>
                        </span>
                    </CommandItem>
                </CommandGroup>
                <CommandSeparator />
                <CommandGroup>
                    <CommandItem :value="`all ${query}`" @select="go(`/search?search=${encodeURIComponent(query.trim())}`)">
                        <IconSearch class="text-muted-foreground h-4 w-4 shrink-0" aria-hidden="true" />
                        See all results for “{{ query.trim() }}”
                    </CommandItem>
                </CommandGroup>
            </template>

            <!-- Always available (and searchable): theme + text size. Applying
                 one keeps the palette open so the change is visible. -->
            <CommandSeparator />
            <CommandGroup heading="Theme">
                <CommandItem
                    v-for="option in themeOptions"
                    :key="option.value"
                    :value="`theme ${option.value} colour appearance`"
                    @select="updateAppearance(option.value)"
                >
                    <component :is="option.icon" class="text-muted-foreground h-4 w-4 shrink-0" aria-hidden="true" />
                    <span>{{ option.label }}</span>
                    <IconCheck v-if="appearance === option.value" class="text-primary ml-auto h-4 w-4 shrink-0" aria-hidden="true" />
                </CommandItem>
            </CommandGroup>
            <CommandGroup heading="Text size">
                <CommandItem value="text size larger bigger increase" :disabled="!canIncrease()" @select="increase()">
                    <IconTextIncrease class="text-muted-foreground h-4 w-4 shrink-0" aria-hidden="true" />
                    <span>Larger text</span>
                    <span class="text-muted-foreground ml-auto text-xs tabular-nums">{{ scalePercent }}</span>
                </CommandItem>
                <CommandItem value="text size smaller decrease" :disabled="!canDecrease()" @select="decrease()">
                    <IconTextDecrease class="text-muted-foreground h-4 w-4 shrink-0" aria-hidden="true" />
                    <span>Smaller text</span>
                    <span class="text-muted-foreground ml-auto text-xs tabular-nums">{{ scalePercent }}</span>
                </CommandItem>
                <CommandItem value="text size reset default" :disabled="isDefault()" @select="reset()">
                    <IconRestore class="text-muted-foreground h-4 w-4 shrink-0" aria-hidden="true" />
                    <span>Reset text size</span>
                </CommandItem>
            </CommandGroup>
        </CommandList>
    </CommandDialog>
</template>
