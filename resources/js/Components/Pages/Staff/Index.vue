<script setup>
import { Head, Link } from "@inertiajs/vue3"

const mockVideo = {
    title: "Title",
    description:
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
}
</script>

<template>
    <Head title="Staff - Videos" />

    <div class="main-container p-8">
        <main class="isolate">
            <h1 class="mb-4 text-xl font-bold">Videos</h1>
            <div class="grid grid-cols-3 gap-4">
                <div
                    class="col-span-2 grid gap-4 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
                    <div
                        v-for="item in 9"
                        :key="item"
                        class="col-span-1 h-52 border bg-white text-black">
                        <div>{{ `${mockVideo.title} ${item}` }}</div>
                    </div>
                </div>
                <div class="col-span-1">
                    <Link
                        href="/staff/videos/create"
                        as="button"
                        type="button"
                        class="primary-button w-full"
                        >Add a new video</Link
                    >
                </div>
            </div>
        </main>
    </div>
</template>

<style scoped>
</style>
