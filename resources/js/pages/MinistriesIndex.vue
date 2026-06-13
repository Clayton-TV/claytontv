<script setup>
import SeriesCard from '@/molecules/SeriesCard.vue';
import { Head } from '@inertiajs/vue3';

defineProps({
    ministries: { type: Array, default: () => [] },
    total: { type: Number, default: 0 },
});
</script>

<template>
    <Head title="Ministries" />
    <div class="mx-auto max-w-6xl px-4 py-10 lg:px-8">
        <h1 class="font-display text-foreground text-2xl font-bold sm:text-3xl">Ministries</h1>
        <p class="text-muted-foreground mt-2 text-sm tabular-nums">{{ total }} churches and ministries with teaching on Clayton TV</p>

        <div class="mt-8 grid gap-5 sm:grid-cols-2">
            <SeriesCard v-for="ministry in ministries" :key="ministry.url" :series="ministry" count-noun="video" />
        </div>
    </div>
</template>
