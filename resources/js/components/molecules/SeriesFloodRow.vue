<script setup>
import { Link } from '@inertiajs/vue3';
import { IconChevronRight, IconStack2 } from '@tabler/icons-vue';

defineProps({
    // {name, url, count, thumbnails: [...]} from the latest feed
    item: { type: Object, required: true },
});
</script>

<template>
    <Link
        :href="item.url"
        prefetch
        class="group focus-visible:ring-ring border-border bg-card hover:border-ring hover:bg-accent col-span-full flex items-center gap-4 rounded-xl border p-3 transition-colors duration-150 outline-none focus-visible:ring-2 sm:gap-5 sm:p-4"
    >
        <!-- Fanned thumbnails signal "a stack of episodes" at a glance -->
        <span class="relative h-16 w-32 shrink-0 sm:h-20 sm:w-40" aria-hidden="true">
            <span
                v-for="(thumb, n) in item.thumbnails.slice(0, 3)"
                :key="n"
                class="absolute inset-y-0 overflow-hidden rounded-md border border-white/10 bg-gray-800"
                :class="['', '-z-10 translate-x-2 scale-[0.94]', '-z-20 translate-x-4 scale-[0.88]'][n]"
                :style="{ width: '85%' }"
            >
                <img :src="thumb" alt="" loading="lazy" decoding="async" class="h-full w-full object-cover" onerror="this.style.opacity='0'" />
            </span>
            <span v-if="!item.thumbnails.length" class="absolute inset-0 flex items-center justify-center rounded-md bg-gray-800">
                <IconStack2 class="h-7 w-7 text-gray-500" />
            </span>
        </span>

        <span class="min-w-0 flex-1">
            <span class="text-primary block text-xs font-semibold tracking-wider uppercase">Series</span>
            <span class="text-foreground mt-0.5 block truncate text-base font-bold sm:text-lg">{{ item.name }}</span>
            <span class="text-muted-foreground mt-0.5 block text-sm"> {{ item.count }} new {{ item.count === 1 ? 'episode' : 'episodes' }} </span>
        </span>

        <span
            class="text-muted-foreground group-hover:text-foreground flex shrink-0 items-center gap-1 text-sm font-medium transition-colors duration-150"
        >
            <span class="hidden sm:inline">View series</span>
            <IconChevronRight class="h-5 w-5" aria-hidden="true" />
        </span>
    </Link>
</template>
