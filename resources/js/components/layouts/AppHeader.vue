<script setup lang="ts">
import LogoMark from '@/atoms/LogoMark.vue';
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from '@/ui/sheet';
import { Link, router, usePage } from '@inertiajs/vue3';
import { IconMenu2, IconSearch } from '@tabler/icons-vue';
import { reactive, ref } from 'vue';

const navOptions = [
    { name: 'Home', href: '/' },
    { name: 'Series', href: '/series' },
    { name: 'Topics', href: '/topic' },
    { name: 'Speakers', href: '/speaker' },
    { name: 'Latest', href: '/latest' },
];

const page = usePage();
const mobileNavOpen = ref(false);

const isCurrent = (href: string) => (href === '/' ? page.url === '/' : page.url.startsWith(href));

const searchForm = reactive({ search: '' });

const submitSearch = () => {
    if (searchForm.search) {
        mobileNavOpen.value = false;
        router.get('/search', { search: searchForm.search });
    }
};
</script>

<template>
    <header class="sticky top-0 z-40 border-b border-white/5 bg-gray-950/90 backdrop-blur-md">
        <div class="mx-auto flex h-16 max-w-6xl items-center gap-6 px-4 lg:px-8">
            <Link
                href="/"
                class="focus-visible:ring-ring flex shrink-0 items-center gap-2.5 rounded-md outline-none focus-visible:ring-2"
                aria-label="Clayton TV home"
            >
                <LogoMark class="fill-primary h-7 w-auto" />
                <span class="font-display hidden text-[15px] font-bold tracking-wide text-gray-50 sm:block">Clayton&nbsp;TV</span>
            </Link>

            <nav class="hidden items-center gap-1 lg:flex" aria-label="Primary">
                <Link
                    v-for="option in navOptions"
                    :key="option.name"
                    :href="option.href"
                    prefetch
                    :class="isCurrent(option.href) ? 'bg-white/10 text-white' : 'text-gray-400'"
                    class="focus-visible:ring-ring rounded-md px-3 py-2 text-sm font-medium transition-colors duration-150 outline-none hover:text-white focus-visible:ring-2"
                    :aria-current="isCurrent(option.href) ? 'page' : undefined"
                >
                    {{ option.name }}
                </Link>
            </nav>

            <form @submit.prevent="submitSearch" class="ml-auto hidden w-full max-w-xs sm:block">
                <label class="sr-only" for="header-search">Search</label>
                <div class="relative">
                    <IconSearch class="pointer-events-none absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2 text-gray-500" aria-hidden="true" />
                    <!-- text-base (16px) prevents iOS Safari zooming the page on focus -->
                    <input
                        id="header-search"
                        v-model="searchForm.search"
                        type="search"
                        name="search"
                        placeholder="Search teaching…"
                        class="focus:ring-ring h-10 w-full rounded-lg border border-white/10 bg-white/5 pr-3 pl-9 text-base text-gray-100 transition-colors duration-150 placeholder:text-gray-500 focus:bg-white/10 focus:ring-2 focus:outline-none"
                    />
                </div>
            </form>

            <Sheet v-model:open="mobileNavOpen">
                <SheetTrigger
                    class="focus-visible:ring-ring ml-auto inline-flex min-h-11 min-w-11 items-center justify-center rounded-md text-gray-300 outline-none hover:text-white focus-visible:ring-2 sm:ml-0 lg:hidden"
                    aria-label="Open menu"
                >
                    <IconMenu2 class="h-6 w-6" aria-hidden="true" />
                </SheetTrigger>
                <SheetContent side="right" class="border-white/10 bg-gray-950 text-gray-100">
                    <SheetHeader>
                        <SheetTitle class="font-display text-left text-gray-50">Clayton TV</SheetTitle>
                    </SheetHeader>
                    <form @submit.prevent="submitSearch" class="px-4 pb-2 sm:hidden">
                        <label class="sr-only" for="mobile-search">Search</label>
                        <input
                            id="mobile-search"
                            v-model="searchForm.search"
                            type="search"
                            name="search"
                            placeholder="Search teaching…"
                            class="focus:ring-ring h-11 w-full rounded-lg border border-white/10 bg-white/5 px-4 text-base text-gray-100 placeholder:text-gray-500 focus:ring-2 focus:outline-none"
                        />
                    </form>
                    <nav class="flex flex-col gap-1 px-2" aria-label="Mobile">
                        <Link
                            v-for="option in navOptions"
                            :key="option.name"
                            :href="option.href"
                            @click="mobileNavOpen = false"
                            :class="isCurrent(option.href) ? 'bg-white/10 text-white' : 'text-gray-300'"
                            class="focus-visible:ring-ring rounded-md px-4 py-3 text-base font-medium outline-none hover:bg-white/5 hover:text-white focus-visible:ring-2"
                            :aria-current="isCurrent(option.href) ? 'page' : undefined"
                        >
                            {{ option.name }}
                        </Link>
                    </nav>
                </SheetContent>
            </Sheet>
        </div>
    </header>
</template>
