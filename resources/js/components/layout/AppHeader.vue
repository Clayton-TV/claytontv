<script setup lang="ts">
import { Link, usePage } from '@inertiajs/vue3'
import { computed, ref } from 'vue'
import { Menu, Search } from 'lucide-vue-next'
import AppLogoIcon from '@/AppLogoIcon.vue'
import { Button } from '@/ui/button'
import { Input } from '@/ui/input'
import { Separator } from '@/ui/separator'
import {
    NavigationMenu,
    NavigationMenuItem,
    NavigationMenuLink,
    NavigationMenuList,
    navigationMenuTriggerStyle,
} from '@/ui/navigation-menu'
import {
    Sheet,
    SheetContent,
    SheetDescription,
    SheetHeader,
    SheetTitle,
    SheetTrigger,
} from '@/ui/sheet'

const navItems = [
    { name: 'Livestreams', href: '/livestreams' },
    { name: 'Latest', href: '/latest' },
    { name: 'Series', href: '/series' },
    { name: 'Topics', href: '/topic' },
]

const currentUrl = computed(() => usePage().url)
const searchQuery = ref('')
const mobileOpen = ref(false)

function isActive(href: string): boolean {
    return currentUrl.value.startsWith(href)
}
</script>

<template>
    <header class="sticky top-0 z-50 w-full border-b bg-gray-900 shadow-sm">
        <div class="mx-auto flex h-14 max-w-7xl items-center gap-4 px-4 sm:px-6 lg:px-8">
            <!-- Logo -->
            <Link href="/" class="flex shrink-0 items-center gap-2">
                <div class="flex size-8 items-center justify-center rounded-md bg-white/10">
                    <AppLogoIcon class="size-5 fill-current text-white" />
                </div>
                <span class="text-sm font-semibold text-white">Clayton TV</span>
            </Link>

            <!-- Desktop nav -->
            <NavigationMenu class="hidden md:flex" :viewport="false">
                <NavigationMenuList>
                    <NavigationMenuItem v-for="item in navItems" :key="item.name">
                        <NavigationMenuLink as-child>
                            <Link
                                :href="item.href"
                                :class="[
                                    navigationMenuTriggerStyle(),
                                    'bg-transparent text-gray-300 hover:bg-white/10 hover:text-white focus:bg-white/10 focus:text-white',
                                    isActive(item.href) && 'bg-white/10 text-white',
                                ]"
                            >
                                {{ item.name }}
                            </Link>
                        </NavigationMenuLink>
                    </NavigationMenuItem>
                </NavigationMenuList>
            </NavigationMenu>

            <div class="flex-1" />

            <!-- Desktop search -->
            <form action="/search" method="get" class="hidden items-center gap-2 md:flex">
                <div class="relative">
                    <Search class="absolute top-1/2 left-2.5 size-4 -translate-y-1/2 text-gray-400" />
                    <Input
                        v-model="searchQuery"
                        type="search"
                        name="q"
                        placeholder="Search..."
                        class="h-9 w-48 border-white/20 bg-white/10 pl-8 text-sm text-white placeholder:text-gray-400 focus:border-white/40 focus:bg-white/15 lg:w-64"
                    />
                </div>
            </form>

            <!-- Mobile hamburger -->
            <Sheet v-model:open="mobileOpen">
                <SheetTrigger as-child>
                    <Button variant="ghost" size="icon" class="md:hidden text-gray-300 hover:bg-white/10 hover:text-white">
                        <Menu class="size-5" />
                        <span class="sr-only">Open menu</span>
                    </Button>
                </SheetTrigger>
                <SheetContent side="right" class="w-72 bg-gray-900 text-white border-gray-800">
                    <SheetHeader>
                        <SheetTitle class="flex items-center gap-2 text-white">
                            <AppLogoIcon class="size-5 fill-current text-white" />
                            Clayton TV
                        </SheetTitle>
                        <SheetDescription class="sr-only">Navigation menu</SheetDescription>
                    </SheetHeader>

                    <!-- Mobile search -->
                    <form action="/search" method="get" class="px-1 pb-4">
                        <div class="relative">
                            <Search class="absolute top-1/2 left-2.5 size-4 -translate-y-1/2 text-gray-400" />
                            <Input
                                type="search"
                                name="q"
                                placeholder="Search..."
                                class="h-9 w-full border-white/20 bg-white/10 pl-8 text-sm text-white placeholder:text-gray-400"
                            />
                        </div>
                    </form>

                    <Separator class="bg-gray-700" />

                    <!-- Mobile nav links -->
                    <nav class="flex flex-col gap-1 pt-4">
                        <Link
                            v-for="item in navItems"
                            :key="item.name"
                            :href="item.href"
                            :class="[
                                'rounded-md px-3 py-2 text-sm font-medium text-gray-300 transition-colors hover:bg-white/10 hover:text-white',
                                isActive(item.href) && 'bg-white/10 text-white',
                            ]"
                            @click="mobileOpen = false"
                        >
                            {{ item.name }}
                        </Link>
                    </nav>
                </SheetContent>
            </Sheet>
        </div>
    </header>
</template>
