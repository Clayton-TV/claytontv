<script lang="ts" setup>
import { Link } from '@inertiajs/vue3';

defineProps<{
    video: {
        id: number;
        title: string;
        thumbnailUrl: string;
        datetime: string;
    };
}>();
</script>

<template>
    <div class="hover:bg-secondary transform rounded-xl px-2 py-2 transition duration-200 ease-in-out">
        <div class="bg-card aspect-video w-full rounded-lg">
            <img :alt="video.title" :src="video.thumbnailUrl" class="text-muted-foreground h-full w-full rounded-md object-cover text-sm" />
        </div>

        <Link class="" href="#">
            <h3 class="text-foreground text-lg/6 font-semibold">{{ video.title }}</h3>
            <p class="text-muted-foreground text-sm">{{ video.datetime }}</p>
        </Link>
    </div>
</template>

<style scoped></style>
