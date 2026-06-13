<script setup>
import PlayerFrame from '@/organisms/PlayerFrame.vue';
import { router } from '@inertiajs/vue3';
import { IconArrowsDiagonal, IconPlayerPause, IconPlayerPlay, IconPlayerTrackNext, IconX } from '@tabler/icons-vue';
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue';
import { usePlayerDock } from '~/composables/usePlayerDock';
import { useWatchHistory } from '~/composables/useWatchHistory';

/**
 * The one player the whole app shares. Lives in AppLayout (persistent
 * across Inertia navigations — see resources/js/app.ts), so an iframe that
 * is playing keeps playing wherever the viewer goes:
 *
 * - "docked": a watch page registered its placeholder; the player absolutely
 *   positions itself over it and scrolls with the page.
 * - "mini": no placeholder (any other page); the player floats bottom-right
 *   with its own control bar. The minimize transition is the information:
 *   it tells the viewer their video kept going.
 */

const dock = usePlayerDock();
const { resumePoint } = useWatchHistory();

// ----- position over the watch-page placeholder (document coordinates) -----
const rect = ref(null);
let resizeObserver = null;

const measure = () => {
    const el = dock.placeholder.value;
    if (!el) {
        rect.value = null;
        return;
    }
    const box = el.getBoundingClientRect();
    rect.value = {
        top: box.top + window.scrollY,
        left: box.left + window.scrollX,
        width: box.width,
        height: box.height,
    };
};

watch(dock.placeholder, (el) => {
    resizeObserver?.disconnect();
    if (el) {
        resizeObserver = new ResizeObserver(measure);
        resizeObserver.observe(el);
        // Body too: images/fonts loading above the fold shift the placeholder
        resizeObserver.observe(document.body);
    }
    measure();
});

onMounted(() => window.addEventListener('resize', measure));
onBeforeUnmount(() => {
    window.removeEventListener('resize', measure);
    resizeObserver?.disconnect();
});

const frameStyle = computed(() => {
    if (dock.mode.value === 'docked' && rect.value) {
        return {
            position: 'absolute',
            top: `${rect.value.top}px`,
            left: `${rect.value.left}px`,
            width: `${rect.value.width}px`,
            height: `${rect.value.height}px`,
        };
    }
    return null; // mini: positioned by classes
});

// ----- next-episode chaining (works from any page, no navigation needed) -----
watch(
    () => dock.current.value?.id,
    async (id) => {
        if (!id) return;
        try {
            const response = await fetch(`/api/video/${id}/next`);
            const data = await response.json();
            // Only apply if the video hasn't changed while we fetched
            if (dock.current.value?.id === id) dock.next.value = data.next;
        } catch {
            dock.next.value = null;
        }
    },
    { immediate: true },
);

const playNext = () => {
    const upcoming = dock.next.value;
    if (!upcoming) return;
    dock.load({ id: upcoming.id, name: upcoming.name, url: upcoming.url }, { autoplay: true, startAt: resumePoint(upcoming.id) });
    // On the watch page, bring the page along with the player
    if (dock.mode.value === 'docked') router.visit(`/video/${upcoming.id}`);
};

const onEnded = () => playNext();

// ----- mini chrome -----
const expand = () => router.visit(`/video/${dock.current.value.id}`);

const onScrub = (event) => dock.controls.value?.seekTo(Number(event.target.value));

const formatTime = (totalSeconds) => {
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = Math.floor(totalSeconds % 60);
    return `${minutes}:${String(seconds).padStart(2, '0')}`;
};

// ----- playback keys, global (work in both modes; never while typing) -----
const onKeydown = (event) => {
    if (event.metaKey || event.ctrlKey || event.altKey) return;
    const target = event.target;
    if (target instanceof HTMLElement && (target.isContentEditable || target.matches('input, textarea, select'))) return;
    const controls = dock.controls.value;
    if (!controls) return;
    if (event.key === ' ' || event.key === 'k') {
        event.preventDefault();
        controls.toggle();
    } else if (event.key === 'ArrowLeft') {
        event.preventDefault();
        controls.seekBy(-10);
    } else if (event.key === 'ArrowRight') {
        event.preventDefault();
        controls.seekBy(10);
    } else if (event.key === 'm') {
        controls.toggleMute();
    }
};

onMounted(() => window.addEventListener('keydown', onKeydown));
onBeforeUnmount(() => window.removeEventListener('keydown', onKeydown));
</script>

<template>
    <div
        v-if="dock.current.value"
        :style="frameStyle"
        :class="
            dock.mode.value === 'docked'
                ? 'z-10 overflow-hidden rounded-xl border border-white/10'
                : 'mini-in fixed right-[calc(1rem+env(safe-area-inset-right))] bottom-[calc(1rem+env(safe-area-inset-bottom))] z-50 w-[min(340px,calc(100vw-2rem))] overflow-hidden rounded-xl border border-white/15 bg-gray-900 shadow-2xl'
        "
    >
        <div :class="dock.mode.value === 'docked' ? 'h-full w-full' : 'aspect-video w-full'">
            <PlayerFrame
                :key="dock.current.value.id"
                :video="dock.current.value"
                :start="dock.resumedFrom.value"
                :autoplay="dock.autoplay.value"
                @ended="onEnded"
            />
        </div>

        <!-- Mini control bar -->
        <div v-if="dock.mode.value === 'mini'" class="flex flex-col gap-1 px-3 pt-2 pb-2.5">
            <button
                @click="expand"
                class="focus-visible:ring-ring cursor-pointer truncate text-left text-sm font-medium text-gray-100 outline-none hover:underline focus-visible:ring-2"
                :title="dock.current.value.name"
            >
                {{ dock.current.value.name }}
            </button>
            <input
                type="range"
                min="0"
                :max="Math.max(1, Math.floor(dock.duration.value))"
                :value="Math.floor(dock.position.value)"
                @input="onScrub"
                class="accent-primary h-1.5 w-full cursor-pointer"
                aria-label="Seek"
            />
            <div class="flex items-center gap-1">
                <button
                    @click="dock.controls.value?.toggle()"
                    class="focus-visible:ring-ring inline-flex h-10 w-10 cursor-pointer items-center justify-center rounded-md text-gray-200 outline-none hover:bg-white/10 hover:text-white focus-visible:ring-2"
                    :aria-label="dock.playing.value ? 'Pause' : 'Play'"
                >
                    <IconPlayerPause v-if="dock.playing.value" class="h-5 w-5" aria-hidden="true" />
                    <IconPlayerPlay v-else class="h-5 w-5" aria-hidden="true" />
                </button>
                <button
                    v-if="dock.next.value"
                    @click="playNext"
                    class="focus-visible:ring-ring inline-flex h-10 w-10 cursor-pointer items-center justify-center rounded-md text-gray-200 outline-none hover:bg-white/10 hover:text-white focus-visible:ring-2"
                    aria-label="Next episode"
                    :title="`Next: ${dock.next.value.name}`"
                >
                    <IconPlayerTrackNext class="h-5 w-5" aria-hidden="true" />
                </button>
                <span class="ml-1 text-xs text-gray-500 tabular-nums">
                    {{ formatTime(dock.position.value) }}<template v-if="dock.duration.value"> / {{ formatTime(dock.duration.value) }}</template>
                </span>
                <button
                    @click="expand"
                    class="focus-visible:ring-ring ml-auto inline-flex h-10 w-10 cursor-pointer items-center justify-center rounded-md text-gray-300 outline-none hover:bg-white/10 hover:text-white focus-visible:ring-2"
                    aria-label="Open watch page"
                >
                    <IconArrowsDiagonal class="h-5 w-5" aria-hidden="true" />
                </button>
                <button
                    @click="dock.close()"
                    class="focus-visible:ring-ring inline-flex h-10 w-10 cursor-pointer items-center justify-center rounded-md text-gray-300 outline-none hover:bg-white/10 hover:text-white focus-visible:ring-2"
                    aria-label="Close player"
                >
                    <IconX class="h-5 w-5" aria-hidden="true" />
                </button>
            </div>
        </div>
    </div>
</template>

<style scoped>
@keyframes mini-in {
    from {
        transform: translateY(12px) scale(0.96);
        opacity: 0.6;
    }
    to {
        transform: translateY(0) scale(1);
        opacity: 1;
    }
}
.mini-in {
    animation: mini-in 250ms ease-out;
}
@media (prefers-reduced-motion: reduce) {
    .mini-in {
        animation: none;
    }
}
</style>
