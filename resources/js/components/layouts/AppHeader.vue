<script setup lang="ts">
import LogoMark from '@/atoms/LogoMark.vue';
import ShortcutsHelp from '@/molecules/ShortcutsHelp.vue';
import TextSizeControl from '@/molecules/TextSizeControl.vue';
import ThemeToggle from '@/molecules/ThemeToggle.vue';
import CommandPalette from '@/organisms/CommandPalette.vue';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/ui/dropdown-menu';
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from '@/ui/sheet';
import { Link, usePage } from '@inertiajs/vue3';
import { IconChevronDown, IconMenu2, IconSearch } from '@tabler/icons-vue';
import { computed, onBeforeUnmount, onMounted, ref } from 'vue';
import { usePalette } from '~/composables/usePalette';

// Calm primary bar for the elderly-first audience: Home · Browse · Latest ·
// Live. Everything directory-shaped folds under "Browse" so the top stays
// scannable; the command palette (⌘K) is the power-user fast path.
const browseLinks = [
    { name: 'All teaching', href: '/browse', hint: 'Filter by speaker, book, length…' },
    { name: 'Series', href: '/series', hint: 'Courses & sermon series' },
    { name: 'Topics', href: '/topic', hint: 'Browse by subject' },
    { name: 'Speakers', href: '/speaker', hint: 'Find a preacher' },
    { name: 'Bible books', href: '/book', hint: 'Teaching by passage' },
    { name: 'For every age', href: '/audience', hint: 'Kids, youth & adults' },
];
const BROWSE_PREFIXES = ['/browse', '/series', '/topic', '/speaker', '/book', '/audience', '/ministry'];

const page = usePage();
const mobileNavOpen = ref(false);

const isCurrent = (href: string) => (href === '/' ? page.url === '/' : page.url.startsWith(href));
const isBrowseSection = () => BROWSE_PREFIXES.some((p) => page.url.startsWith(p));
// Global "a service is on air" flag (shared from the Inertia middleware)
const liveNow = computed(() => page.props.live_now === true);

const { paletteOpen, helpOpen } = usePalette();

const openPalette = () => {
    mobileNavOpen.value = false;
    paletteOpen.value = true;
};

// Global shortcuts — never while typing (the palette's own input included)
const onKeydown = (event: KeyboardEvent) => {
    const target = event.target as HTMLElement;
    const typing = target instanceof HTMLElement && (target.isContentEditable || target.matches('input, textarea, select'));
    if ((event.metaKey || event.ctrlKey) && event.key === 'k') {
        event.preventDefault();
        paletteOpen.value = !paletteOpen.value;
        return;
    }
    if (typing || event.metaKey || event.ctrlKey || event.altKey) return;
    if (event.key === '/') {
        event.preventDefault();
        paletteOpen.value = true;
    } else if (event.key === '?') {
        event.preventDefault();
        helpOpen.value = true;
    }
};

onMounted(() => window.addEventListener('keydown', onKeydown));
onBeforeUnmount(() => window.removeEventListener('keydown', onKeydown));

// Roughly: Mac keyboards show ⌘, everything else Ctrl
const isMac = typeof navigator !== 'undefined' && /Mac|iPhone|iPad/.test(navigator.platform);

const navLink = (active: boolean) =>
    `${active ? 'bg-accent text-accent-foreground' : 'text-muted-foreground'} focus-visible:ring-ring inline-flex items-center gap-1.5 rounded-md px-3 py-2 text-sm font-medium transition-colors duration-150 outline-none hover:text-foreground focus-visible:ring-2`;
</script>

<template>
    <header class="pt-safe px-safe border-border bg-background/90 sticky top-0 z-40 border-b backdrop-blur-md">
        <div class="mx-auto flex h-16 max-w-6xl items-center gap-6 px-4 lg:px-8">
            <Link
                href="/"
                class="focus-visible:ring-ring flex shrink-0 items-center gap-2.5 rounded-md outline-none focus-visible:ring-2"
                aria-label="Clayton TV home"
            >
                <LogoMark class="fill-primary h-7 w-auto" />
                <span class="font-display text-foreground hidden text-[15px] font-bold tracking-wide sm:block">Clayton&nbsp;TV</span>
            </Link>

            <nav class="hidden items-center gap-1 lg:flex" aria-label="Primary">
                <Link href="/" prefetch :class="navLink(isCurrent('/'))" :aria-current="isCurrent('/') ? 'page' : undefined">Home</Link>

                <!-- Browse: click-triggered panel of the directories (not a hover mega-menu) -->
                <DropdownMenu>
                    <DropdownMenuTrigger :class="navLink(isBrowseSection())" :aria-current="isBrowseSection() ? 'page' : undefined">
                        Browse
                        <IconChevronDown class="h-4 w-4 opacity-70" aria-hidden="true" />
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="start" class="w-64">
                        <DropdownMenuItem v-for="link in browseLinks" :key="link.href" as-child>
                            <Link :href="link.href" prefetch class="flex cursor-pointer flex-col items-start gap-0.5 py-2">
                                <span class="text-sm font-medium">{{ link.name }}</span>
                                <span class="text-muted-foreground text-xs">{{ link.hint }}</span>
                            </Link>
                        </DropdownMenuItem>
                    </DropdownMenuContent>
                </DropdownMenu>

                <Link href="/latest" prefetch :class="navLink(isCurrent('/latest'))" :aria-current="isCurrent('/latest') ? 'page' : undefined"
                    >Latest</Link
                >

                <Link
                    href="/livestreams"
                    prefetch
                    :class="navLink(isCurrent('/livestreams'))"
                    :aria-current="isCurrent('/livestreams') ? 'page' : undefined"
                >
                    Live
                    <span v-if="liveNow" class="relative flex h-2 w-2" title="A service is live now">
                        <span
                            class="bg-primary absolute inline-flex h-full w-full animate-ping rounded-full opacity-75 motion-reduce:animate-none"
                        ></span>
                        <span class="bg-primary relative inline-flex h-2 w-2 rounded-full"></span>
                        <span class="sr-only">live now</span>
                    </span>
                </Link>
            </nav>

            <!-- Looks like the old search field; opens the command palette -->
            <button
                @click="openPalette"
                class="focus-visible:ring-ring border-border bg-muted text-muted-foreground hover:bg-accent hover:text-foreground ml-auto hidden h-10 w-full max-w-xs cursor-pointer items-center gap-2 rounded-lg border px-3 transition-colors duration-150 outline-none focus-visible:ring-2 sm:flex"
            >
                <IconSearch class="h-4 w-4 shrink-0" aria-hidden="true" />
                <span class="text-base">Search teaching…</span>
                <kbd class="border-border bg-muted ml-auto rounded border px-1.5 py-0.5 font-sans text-xs">{{ isMac ? '⌘K' : 'Ctrl K' }}</kbd>
            </button>

            <Sheet v-model:open="mobileNavOpen">
                <SheetTrigger
                    class="focus-visible:ring-ring text-muted-foreground hover:text-foreground ml-auto inline-flex min-h-11 min-w-11 items-center justify-center rounded-md outline-none focus-visible:ring-2 sm:ml-0 lg:hidden"
                    aria-label="Open menu"
                >
                    <IconMenu2 class="h-6 w-6" aria-hidden="true" />
                </SheetTrigger>
                <SheetContent side="right" class="border-border bg-background text-foreground overflow-y-auto">
                    <SheetHeader>
                        <SheetTitle class="font-display text-foreground text-left">Clayton TV</SheetTitle>
                    </SheetHeader>
                    <div class="px-4 pb-2">
                        <button
                            @click="openPalette"
                            class="focus-visible:ring-ring border-border bg-muted text-muted-foreground flex h-11 w-full cursor-pointer items-center gap-2 rounded-lg border px-4 text-base outline-none focus-visible:ring-2"
                        >
                            <IconSearch class="h-4 w-4 shrink-0" aria-hidden="true" />
                            Search teaching…
                        </button>
                    </div>
                    <nav class="flex flex-col gap-1 px-2" aria-label="Mobile">
                        <Link
                            href="/"
                            @click="mobileNavOpen = false"
                            :class="isCurrent('/') ? 'bg-accent text-accent-foreground' : 'text-muted-foreground'"
                            class="focus-visible:ring-ring hover:bg-accent hover:text-foreground rounded-md px-4 py-3 text-base font-medium outline-none focus-visible:ring-2"
                        >
                            Home
                        </Link>

                        <p class="text-muted-foreground px-4 pt-3 pb-1 text-xs font-semibold tracking-wider uppercase">Browse</p>
                        <Link
                            v-for="link in browseLinks"
                            :key="link.href"
                            :href="link.href"
                            @click="mobileNavOpen = false"
                            :class="isCurrent(link.href) ? 'bg-accent text-accent-foreground' : 'text-muted-foreground'"
                            class="focus-visible:ring-ring hover:bg-accent hover:text-foreground rounded-md px-4 py-3 text-base font-medium outline-none focus-visible:ring-2"
                        >
                            {{ link.name }}
                        </Link>

                        <p class="text-muted-foreground px-4 pt-3 pb-1 text-xs font-semibold tracking-wider uppercase">Watch</p>
                        <Link
                            href="/latest"
                            @click="mobileNavOpen = false"
                            :class="isCurrent('/latest') ? 'bg-accent text-accent-foreground' : 'text-muted-foreground'"
                            class="focus-visible:ring-ring hover:bg-accent hover:text-foreground rounded-md px-4 py-3 text-base font-medium outline-none focus-visible:ring-2"
                        >
                            Latest
                        </Link>
                        <Link
                            href="/livestreams"
                            @click="mobileNavOpen = false"
                            :class="isCurrent('/livestreams') ? 'bg-accent text-accent-foreground' : 'text-muted-foreground'"
                            class="focus-visible:ring-ring hover:bg-accent hover:text-foreground inline-flex items-center gap-2 rounded-md px-4 py-3 text-base font-medium outline-none focus-visible:ring-2"
                        >
                            Live
                            <span v-if="liveNow" class="relative flex h-2 w-2">
                                <span
                                    class="bg-primary absolute inline-flex h-full w-full animate-ping rounded-full opacity-75 motion-reduce:animate-none"
                                ></span>
                                <span class="bg-primary relative inline-flex h-2 w-2 rounded-full"></span>
                                <span class="sr-only">live now</span>
                            </span>
                        </Link>
                    </nav>
                    <div class="border-border mt-4 flex items-center justify-between border-t px-4 pt-4">
                        <span class="text-muted-foreground text-sm">Theme</span>
                        <ThemeToggle />
                    </div>
                    <div class="flex items-center justify-between px-4 pt-3">
                        <span class="text-muted-foreground text-sm">Text size</span>
                        <TextSizeControl />
                    </div>
                </SheetContent>
            </Sheet>
        </div>

        <CommandPalette />
        <ShortcutsHelp />
    </header>
</template>
