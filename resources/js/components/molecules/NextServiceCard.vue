<script setup lang="ts">
import { Link } from '@inertiajs/vue3';
import { IconArrowRight, IconBroadcast } from '@tabler/icons-vue';
import { computed, ref } from 'vue';
import { getEmbedUrl } from '~/lib/embeds';

// Real broadcast state from the LiveStream sync (Epic 4). Three honest
// states: live right now (embedded player), a scheduled next service
// (real date/time), or the quiet evergreen fallback.
const props = defineProps({
    livestreams: { type: Array, default: () => [] },
    nextService: { type: Object, default: null },
});

const live = computed(() => props.livestreams[0] ?? null);
const watching = ref(false);

const liveEmbedUrl = computed(() => (live.value ? getEmbedUrl(live.value.url, { autoplay: true }) : false));

const formatSchedule = (iso: string) => {
    const date = new Date(iso);
    const day = date.toLocaleDateString('en-GB', { weekday: 'long', day: 'numeric', month: 'long' });
    const time = date.toLocaleTimeString('en-GB', { hour: 'numeric', minute: '2-digit' });
    return `${day}, ${time}`;
};
</script>

<template>
    <!-- LIVE now: one tap from the homepage into the service -->
    <div v-if="live" class="border-primary/40 overflow-hidden rounded-xl border bg-white/[0.03]">
        <div v-if="watching && liveEmbedUrl" class="aspect-video w-full bg-black">
            <iframe
                class="h-full w-full"
                :src="liveEmbedUrl"
                allow="autoplay; clipboard-write; fullscreen; picture-in-picture"
                referrerpolicy="strict-origin-when-cross-origin"
                allowfullscreen
                :title="live.title"
            ></iframe>
        </div>
        <button v-else @click="watching = true" class="group relative block aspect-video w-full cursor-pointer bg-black" aria-label="Watch live">
            <img v-if="live.thumbnail" :src="live.thumbnail" alt="" class="absolute inset-0 h-full w-full object-cover opacity-80" />
            <span class="absolute inset-0 flex items-center justify-center">
                <span
                    class="bg-primary text-primary-foreground inline-flex items-center gap-2 rounded-full px-5 py-2.5 text-sm font-bold transition-transform duration-150 ease-out group-hover:scale-105 motion-reduce:transition-none"
                >
                    <IconBroadcast class="h-5 w-5" aria-hidden="true" />
                    Watch live
                </span>
            </span>
        </button>
        <div class="p-4">
            <div class="flex items-center gap-2">
                <span class="relative flex h-2.5 w-2.5" aria-hidden="true">
                    <span
                        class="bg-primary absolute inline-flex h-full w-full animate-ping rounded-full opacity-75 motion-reduce:animate-none"
                    ></span>
                    <span class="bg-primary relative inline-flex h-2.5 w-2.5 rounded-full"></span>
                </span>
                <p class="text-primary text-xs font-bold tracking-wider uppercase">Live now</p>
            </div>
            <p class="font-display mt-2 text-lg leading-snug font-bold text-gray-50">{{ live.title }}</p>
            <p v-if="live.channel" class="mt-1 text-sm text-gray-400">{{ live.channel }}</p>
        </div>
    </div>

    <!-- A real scheduled service: honest date and time, no countdown theatre -->
    <div v-else-if="nextService" class="rounded-xl border border-white/10 bg-white/[0.03] p-5 sm:p-6">
        <div class="flex items-center gap-2">
            <span class="bg-primary inline-block h-2 w-2 rounded-full" aria-hidden="true"></span>
            <p class="text-xs font-medium tracking-wider text-gray-400 uppercase">Next service</p>
        </div>
        <p class="font-display mt-3 text-lg leading-snug font-bold text-gray-50">{{ nextService.title }}</p>
        <p class="mt-1.5 text-sm leading-relaxed text-gray-300 tabular-nums">{{ formatSchedule(nextService.scheduled_start) }}</p>
        <p class="mt-1 text-sm text-gray-400">The stream will appear here when it starts.</p>
        <Link
            href="/livestreams"
            class="focus-visible:ring-ring mt-4 inline-flex min-h-11 items-center gap-1.5 rounded-lg bg-white/5 px-4 text-sm font-medium text-gray-100 transition-colors duration-150 outline-none hover:bg-white/10 focus-visible:ring-2"
        >
            Watch past services
            <IconArrowRight class="h-4 w-4" aria-hidden="true" />
        </Link>
    </div>

    <!-- Nothing live or scheduled: the quiet evergreen card -->
    <div v-else class="rounded-xl border border-white/10 bg-white/[0.03] p-5 sm:p-6">
        <div class="flex items-center gap-2">
            <span class="bg-primary inline-block h-2 w-2 rounded-full" aria-hidden="true"></span>
            <p class="text-xs font-medium tracking-wider text-gray-400 uppercase">Sunday services</p>
        </div>
        <p class="font-display mt-3 text-lg font-bold text-gray-50">Live streams appear here</p>
        <p class="mt-1.5 text-sm leading-relaxed text-gray-400">
            Morning and evening services stream live most Sundays. Until then, catch up on recent services any time.
        </p>
        <Link
            href="/livestreams"
            class="focus-visible:ring-ring mt-4 inline-flex min-h-11 items-center gap-1.5 rounded-lg bg-white/5 px-4 text-sm font-medium text-gray-100 transition-colors duration-150 outline-none hover:bg-white/10 focus-visible:ring-2"
        >
            Watch past services
            <IconArrowRight class="h-4 w-4" aria-hidden="true" />
        </Link>
    </div>
</template>
