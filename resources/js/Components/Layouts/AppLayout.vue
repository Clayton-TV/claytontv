<script setup>
import {
    IconBrandYoutube,
    IconBrandVimeo,
    IconBrandGithub,
} from "@tabler/icons-vue"

function subscribeToNewsletter() {
    //
}
</script>

<template>
    <div class="flex min-h-full flex-col">
        <header class="flex-none">
            <h1>Clayton TV</h1>
        </header>

        <div class="flex-1">
            <slot />
        </div>

        <footer
            class="flex flex-col items-center gap-y-10 bg-gradient-to-b from-gray-800 to-gray-950 px-14 py-10">
            <div class="space-y-3">
                <p class="text-balance text-center text-xl font-bold">
                    Want some occasional updates from us?
                </p>

                <form
                    class="flex flex-col gap-y-2"
                    @submit.prevent="subscribeToNewsletter">
                    <input
                        class="h-11 rounded px-3 text-sm"
                        placeholder="Enter your email"
                        type="email" />
                    <button
                        class="h-11 rounded bg-blue-500 text-sm"
                        type="submit">
                        Subscribe
                    </button>
                </form>
            </div>

            <div class="space-y-3 text-center">
                <div>
                    <h1 class="text-3xl font-bold">Clayton TV</h1>
                    <p class="mt-1 text-sm text-gray-300">
                        Your digital catalogue for Godly content.
                    </p>
                </div>

                <div class="flex justify-center gap-x-3">
                    <div
                        class="flex aspect-square w-12 items-center justify-center rounded bg-gray-800">
                        <p class="sr-only">Youtube</p>
                        <IconBrandYoutube class="h-8 w-8 stroke-1 text-white" />
                    </div>
                    <div
                        class="flex aspect-square w-12 items-center justify-center rounded bg-gray-800">
                        <p class="sr-only">Vimeo</p>
                        <IconBrandVimeo class="h-8 w-8 stroke-1 text-white" />
                    </div>
                    <div
                        class="flex aspect-square w-12 items-center justify-center rounded bg-gray-800">
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
