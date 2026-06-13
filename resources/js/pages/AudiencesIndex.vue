<script setup>
import { Head, Link } from '@inertiajs/vue3';
import { IconMoodKid } from '@tabler/icons-vue';
import { useEntrance } from '~/composables/useEntrance';

// Image-led Kids/Youth/Adults tiles for the parent/kids persona — one tap to
// a friendly, clearly-labelled page. Thumbnail with a warm colour fallback so
// a tile is never broken when the (often-empty) thumbnail is missing.
defineProps({
    audiences: { type: Array, default: () => [] },
});

const { entrance } = useEntrance();

const thumb = (audience) => (audience.thumbnail?.startsWith('http') ? audience.thumbnail : null);
</script>

<template>
    <Head title="For every age" />
    <div class="mx-auto max-w-6xl px-4 py-10 lg:px-8">
        <h1 class="font-display text-2xl font-bold text-gray-50 sm:text-3xl">For every age</h1>
        <p class="mt-2 text-sm text-gray-500">Teaching chosen for children, young people and adults.</p>

        <div v-bind="entrance(80)" class="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            <Link
                v-for="audience in audiences"
                :key="audience.url"
                :href="audience.url"
                prefetch
                class="group focus-visible:ring-ring block overflow-hidden rounded-2xl border border-white/10 bg-white/[0.03] transition-colors duration-150 outline-none hover:border-white/25 focus-visible:ring-2"
            >
                <div class="from-primary/30 relative flex aspect-[16/9] items-center justify-center bg-gradient-to-br to-gray-900">
                    <img
                        v-if="thumb(audience)"
                        :src="thumb(audience)"
                        alt=""
                        loading="lazy"
                        decoding="async"
                        class="absolute inset-0 h-full w-full object-cover transition-transform duration-300 ease-out group-hover:scale-[1.03] motion-reduce:transition-none motion-reduce:group-hover:scale-100"
                        onerror="this.style.opacity='0'"
                    />
                    <IconMoodKid class="h-12 w-12 text-white/80" aria-hidden="true" />
                </div>
                <div class="p-5">
                    <p class="font-display text-xl font-bold text-gray-50">{{ audience.name }}</p>
                    <p v-if="audience.summary" class="mt-1 line-clamp-2 text-sm leading-relaxed text-gray-400">{{ audience.summary }}</p>
                    <p class="mt-3 text-sm text-gray-500 tabular-nums">
                        {{ audience.videosCount }} {{ audience.videosCount === 1 ? 'video' : 'videos' }}
                    </p>
                </div>
            </Link>
        </div>
    </div>
</template>
