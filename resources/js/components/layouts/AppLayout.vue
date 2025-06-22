<script setup>
import {
    IconBrandYoutube,
    IconBrandVimeo,
    IconBrandGithub,
} from "@tabler/icons-vue"
import {
    Disclosure,
    DisclosureButton,
    DisclosurePanel,
    Menu,
    MenuButton,
    MenuItem,
    MenuItems,
} from "@headlessui/vue"
import { MagnifyingGlassIcon } from "@heroicons/vue/20/solid"
import { Bars3Icon, BellIcon, XMarkIcon } from "@heroicons/vue/24/outline"
import LogoMark from "@/atoms/LogoMark.vue"
import { Link, router } from "@inertiajs/vue3"
import { reactive } from "vue"

const navOptions = [
    { name: "Livestreams", href: "#livestreams" },
    { name: "Series", href: "#series" },
    { name: "Topics", href: "#topics" },
]

const isCurrent = (href) => {
    return window.location.href.includes(href)
}

function subscribeToNewsletter() {
    //
}

const searchForm = reactive({
    search: null,
})

const submitSearch = () => {
    if (searchForm.search) {
        router.get("/search", searchForm)
    }
}
</script>

<template>
    <div class="flex min-h-full flex-col">
        <div class="sticky top-2 isolate z-10 mx-2 my-2 h-16">
            <Disclosure
                v-slot="{ open }"
                as="nav"
                class="mx-auto w-full max-w-6xl flex-none rounded-md bg-gray-900 shadow-2xl">
                <div class="mx-auto max-w-7xl px-2 sm:px-4 lg:px-8">
                    <div
                        class="relative flex h-16 items-center justify-between">
                        <div class="flex items-center px-2 lg:px-0">
                            <Link href="/" class="flex items-center">
                                <LogoMark class="size-8 fill-claytonRed" />
                                <!--<h1 class="mx-3 mb-1 hidden lg:block text-2xl font-bold">Clayton&nbsp;TV</h1>-->
                            </Link>
                            <div class="hidden lg:ml-6 lg:block">
                                <div class="flex space-x-4">
                                    <!-- Current: "", Default: "" -->
                                    <Link
                                        v-for="option in navOptions"
                                        :key="option.name"
                                        :class="
                                            isCurrent(option.href) ? 'bg-gray-900 text-white' : ''
                                        "
                                        class="rounded-md bg-gray-900 px-3 py-2 text-sm font-medium text-gray-300 hover:bg-gray-700 hover:text-white"
                                        href="#">
                                        {{ option.name }}
                                    </Link>
                                </div>
                            </div>
                        </div>
                        <div
                            class="flex flex-1 justify-center px-2 lg:ml-6 lg:justify-end">
                            <form @submit.prevent="submitSearch" class="w-full max-w-lg lg:max-w-xs">
                                <label class="sr-only" for="search"
                                    >Search</label
                                >
                                <div class="relative">
                                    <div
                                        class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                                        <MagnifyingGlassIcon
                                            aria-hidden="true"
                                            class="h-5 w-5 text-gray-400" />
                                    </div>
                                    <input
                                        id="search"
                                        class="block h-9 w-full rounded-md border-0 bg-gray-700 py-1.5 pl-10 pr-3 text-gray-300 placeholder:text-gray-400 focus:bg-white focus:text-gray-900 focus:ring-0 sm:text-sm sm:leading-6"
                                        name="search" v-model="searchForm.search"
                                        placeholder="Search"
                                        type="search" />
                                </div>
                            </form>
                        </div>
                        <div class="flex lg:hidden">
                            <!-- Mobile menu button -->
                            <DisclosureButton
                                class="relative inline-flex items-center justify-center rounded-md p-2 text-gray-400 hover:bg-gray-700 hover:text-white focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white">
                                <span class="absolute -inset-0.5" />
                                <span class="sr-only"> Open main menu </span>
                                <Bars3Icon
                                    v-if="!open"
                                    aria-hidden="true"
                                    class="block h-6 w-6" />
                                <XMarkIcon
                                    v-else
                                    aria-hidden="true"
                                    class="block h-6 w-6" />
                            </DisclosureButton>
                        </div>
                        <div v-if="false" class="hidden lg:ml-4 lg:block">
                            <div class="flex items-center">
                                <button
                                    class="relative flex-shrink-0 rounded-full bg-gray-800 p-1 text-gray-400 hover:text-white focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-gray-800"
                                    type="button">
                                    <span class="absolute -inset-1.5" />
                                    <span class="sr-only">
                                        View notifications
                                    </span>
                                    <BellIcon
                                        aria-hidden="true"
                                        class="h-6 w-6" />
                                </button>

                                <!-- Profile dropdown -->
                                <Menu
                                    as="div"
                                    class="relative ml-4 flex-shrink-0">
                                    <div>
                                        <MenuButton
                                            class="relative flex rounded-full bg-gray-800 text-sm text-white focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-gray-800">
                                            <span class="absolute -inset-1.5" />
                                            <span class="sr-only">
                                                Open user menu
                                            </span>
                                            <img
                                                alt=""
                                                class="h-8 w-8 rounded-full"
                                                src="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80" />
                                        </MenuButton>
                                    </div>
                                    <transition
                                        enter-active-class="transition ease-out duration-100"
                                        enter-from-class="transform opacity-0 scale-95"
                                        enter-to-class="transform opacity-100 scale-100"
                                        leave-active-class="transition ease-in duration-75"
                                        leave-from-class="transform opacity-100 scale-100"
                                        leave-to-class="transform opacity-0 scale-95">
                                        <MenuItems
                                            class="absolute right-0 z-10 mt-2 w-48 origin-top-right rounded-md bg-white py-1 shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
                                            <MenuItem v-slot="{ active }">
                                                <a
                                                    :class="[
                                                        active
                                                            ? 'bg-gray-100'
                                                            : '',
                                                        'block px-4 py-2 text-sm text-gray-700',
                                                    ]"
                                                    href="#">
                                                    Your Profile
                                                </a>
                                            </MenuItem>
                                            <MenuItem v-slot="{ active }">
                                                <a
                                                    :class="[
                                                        active
                                                            ? 'bg-gray-100'
                                                            : '',
                                                        'block px-4 py-2 text-sm text-gray-700',
                                                    ]"
                                                    href="#">
                                                    Settings
                                                </a>
                                            </MenuItem>
                                            <MenuItem v-slot="{ active }">
                                                <a
                                                    :class="[
                                                        active
                                                            ? 'bg-gray-100'
                                                            : '',
                                                        'block px-4 py-2 text-sm text-gray-700',
                                                    ]"
                                                    href="#">
                                                    Sign out
                                                </a>
                                            </MenuItem>
                                        </MenuItems>
                                    </transition>
                                </Menu>
                            </div>
                        </div>
                    </div>
                </div>

                <DisclosurePanel class="lg:hidden">
                    <div class="space-y-1 px-2 pb-3 pt-2">
                        <DisclosureButton
                            v-for="option in navOptions"
                            :key="option.name"
                            :class="
                                isCurrent(option.href)
                                    ? 'bg-gray-800 text-white'
                                    : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                            "
                            :href="option.href"
                            as="a"
                            class="block rounded-md px-3 py-2 text-base font-medium text-white">
                            {{ option.name }}
                        </DisclosureButton>
                    </div>
                    <div
                        v-if="false"
                        class="border-t border-gray-700 pb-3 pt-4">
                        <div class="flex items-center px-5">
                            <div class="flex-shrink-0">
                                <img
                                    alt=""
                                    class="h-10 w-10 rounded-full"
                                    src="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80" />
                            </div>
                            <div class="ml-3">
                                <div class="text-base font-medium text-white">
                                    Tom Cook
                                </div>
                                <div class="text-sm font-medium text-gray-400">
                                    tom@example.com
                                </div>
                            </div>
                            <button
                                class="relative ml-auto flex-shrink-0 rounded-full bg-gray-800 p-1 text-gray-400 hover:text-white focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-gray-800"
                                type="button">
                                <span class="absolute -inset-1.5" />
                                <span class="sr-only">View notifications</span>
                                <BellIcon aria-hidden="true" class="h-6 w-6" />
                            </button>
                        </div>
                        <div class="mt-3 space-y-1 px-2">
                            <DisclosureButton
                                as="a"
                                class="block rounded-md px-3 py-2 text-base font-medium text-gray-400 hover:bg-gray-700 hover:text-white"
                                href="#">
                                Your Profile
                            </DisclosureButton>
                            <DisclosureButton
                                as="a"
                                class="block rounded-md px-3 py-2 text-base font-medium text-gray-400 hover:bg-gray-700 hover:text-white"
                                href="#">
                                Settings
                            </DisclosureButton>
                            <DisclosureButton
                                as="a"
                                class="block rounded-md px-3 py-2 text-base font-medium text-gray-400 hover:bg-gray-700 hover:text-white"
                                href="#">
                                Sign out
                            </DisclosureButton>
                        </div>
                    </div>
                </DisclosurePanel>
            </Disclosure>
        </div>

        <div class="flex-1">
            <slot />
        </div>

        <footer
            class="flex flex-col items-center gap-y-10 rounded-t-lg bg-gradient-to-b from-gray-800 to-gray-950 px-5 py-10">
            <div class="space-y-3">
                <p class="text-balance text-center text-xl font-bold">
                    Want some occasional updates from us?
                </p>

                <form
                    class="flex flex-col gap-y-2"
                    @submit.prevent="subscribeToNewsletter">
                    <input
                        class="block h-11 w-full rounded-md border-0 bg-gray-700 px-3 py-1.5 text-gray-300 placeholder:text-gray-400 focus:bg-white focus:text-gray-900 focus:ring-0 sm:text-sm sm:leading-6"
                        placeholder="Enter your email"
                        type="email" />
                    <button class="h-11 rounded bg-blue-500" type="submit">
                        Subscribe
                    </button>
                </form>
            </div>

            <div class="space-y-3 text-center">
                <div class="flex flex-col items-center">
                    <div class="flex items-center gap-x-2.5">
                        <LogoMark class="size-10 fill-claytonRed" />
                        <h1 class="text-3xl font-bold">Clayton TV</h1>
                    </div>
                    <p class="mt-1 text-sm text-gray-300">
                        Your digital catalogue for Godly content.
                    </p>
                </div>

                <div class="flex justify-center gap-x-3">
                    <div
                        class="flex aspect-square w-12 items-center justify-center rounded-md bg-gray-800">
                        <p class="sr-only">Youtube</p>
                        <IconBrandYoutube class="h-8 w-8 stroke-1 text-white" />
                    </div>
                    <div
                        class="flex aspect-square w-12 items-center justify-center rounded-md bg-gray-800">
                        <p class="sr-only">Vimeo</p>
                        <IconBrandVimeo class="h-8 w-8 stroke-1 text-white" />
                    </div>
                    <div
                        class="flex aspect-square w-12 items-center justify-center rounded-md bg-gray-800">
                        <p class="sr-only">Github</p>
                        <IconBrandGithub class="h-8 w-8 stroke-1 text-white" />
                    </div>
                </div>
            </div>

            <div>
                <p class="text-xs text-gray-400">
                    &copy; {{ new Date().getFullYear() }} The Jesmond Trust. All
                    rights reserved.
                </p>
            </div>
        </footer>
    </div>
</template>
