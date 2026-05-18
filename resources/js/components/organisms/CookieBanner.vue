<script setup>
import { X } from 'lucide-vue-next';
import { Link } from '@inertiajs/vue3';
</script>

<template>
    <div class="fixed bottom-0 w-full p-4 bg-gray-700 flex flex-row items-center">
        <div class="pl-4 text-lg">
            This site uses cookies to function correctly. By continuing to use this site you are agreeing to our use of cookies.
            <Link href="/privacy" class="pl-1 underline">More information.</Link>
        </div>
        <button class="ml-auto size-[48px] rounded-md cursor-pointer">
            <X class="m-auto" />
        </button>
    </div>
</template>
