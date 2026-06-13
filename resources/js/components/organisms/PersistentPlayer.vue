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

// ----- reel-style seek bar -----
// A native <input type=range> only scrubs by grabbing its (invisible) thumb —
// iOS Safari won't even click-to-seek on the track. So we drive a custom
// slider: press or drag anywhere on the bar to seek, plus full keyboard support.
const scrubbing = ref(false);
const dragPercent = ref(null);

// Drives the fill: the finger position while scrubbing, else live playback.
const progressPercent = computed(() => {
    if (dragPercent.value !== null) return dragPercent.value;
    const duration = dock.duration.value;
    if (!duration) return 0;
    return Math.min(100, (dock.position.value / duration) * 100);
});

const fractionFromEvent = (event) => {
    const rect = event.currentTarget.getBoundingClientRect();
    return Math.min(1, Math.max(0, (event.clientX - rect.left) / rect.width));
};

const onScrubDown = (event) => {
    scrubbing.value = true;
    dragPercent.value = fractionFromEvent(event) * 100;
    event.currentTarget.setPointerCapture?.(event.pointerId);
};
const onScrubMove = (event) => {
    if (scrubbing.value) dragPercent.value = fractionFromEvent(event) * 100;
};
const onScrubUp = (event) => {
    if (!scrubbing.value) return;
    const duration = dock.duration.value;
    if (duration) dock.controls.value?.seekTo(fractionFromEvent(event) * duration);
    scrubbing.value = false;
    dragPercent.value = null;
};
const onScrubKey = (event) => {
    if (!dock.duration.value) return;
    if (event.key === 'ArrowLeft') {
        event.preventDefault();
        dock.controls.value?.seekBy(-5);
    } else if (event.key === 'ArrowRight') {
        event.preventDefault();
        dock.controls.value?.seekBy(5);
    } else if (event.key === 'Home') {
        event.preventDefault();
        dock.controls.value?.seekTo(0);
    } else if (event.key === 'End') {
        event.preventDefault();
        dock.controls.value?.seekTo(dock.duration.value);
    }
};

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
                ? 'border-border z-10 overflow-hidden rounded-xl border'
                : 'mini-in bg-card fixed inset-x-0 bottom-0 z-50 flex h-[calc(4.5rem+env(safe-area-inset-bottom))] flex-row items-stretch overflow-hidden border-t border-border pb-[env(safe-area-inset-bottom)] sm:inset-x-auto sm:right-[calc(1rem+env(safe-area-inset-right))] sm:bottom-[calc(1rem+env(safe-area-inset-bottom))] sm:h-auto sm:w-[min(340px,calc(100vw-2rem))] sm:flex-col sm:rounded-xl sm:border sm:border-input sm:pb-0 sm:shadow-2xl'
        "
    >
        <!-- One persistent iframe, reflowed: a compact thumbnail on the mobile
             bar, the full-width video on the desktop card. -->
        <div :class="dock.mode.value === 'docked' ? 'h-full w-full' : 'h-[4.5rem] w-32 shrink-0 sm:aspect-video sm:h-auto sm:w-full'">
            <PlayerFrame
                :key="dock.current.value.id"
                :video="dock.current.value"
                :start="dock.resumedFrom.value"
                :autoplay="dock.autoplay.value"
                @ended="onEnded"
            />
        </div>

        <!-- Reel-style seek bar: a near-invisible 2px track that fills with
             playback and grows on hover/focus. Press or drag anywhere on it to
             seek (custom pointer handling — a native range only scrubs via its
             invisible thumb, which fails on iOS Safari). On mobile it pins to the
             top edge of the full-width bar (like YouTube); on desktop it sits
             flush under the video. -->
        <div
            v-if="dock.mode.value === 'mini'"
            class="group/scrub absolute inset-x-0 top-0 z-10 h-3 cursor-pointer touch-none select-none sm:relative sm:inset-x-auto sm:top-auto"
            role="slider"
            tabindex="0"
            aria-label="Seek"
            :aria-valuemin="0"
            :aria-valuemax="Math.floor(dock.duration.value) || 0"
            :aria-valuenow="Math.floor(dock.position.value) || 0"
            :aria-valuetext="`${formatTime(dock.position.value)} of ${formatTime(dock.duration.value)}`"
            @pointerdown="onScrubDown"
            @pointermove="onScrubMove"
            @pointerup="onScrubUp"
            @pointercancel="onScrubUp"
            @keydown="onScrubKey"
        >
            <div
                class="bg-foreground/15 pointer-events-none absolute inset-x-0 top-0 h-[2px] transition-[height] duration-200 ease-out group-focus-within/scrub:h-1 group-hover/scrub:h-1 motion-reduce:transition-none"
            >
                <div
                    class="bg-primary h-full transition-[width] duration-150 ease-linear motion-reduce:transition-none"
                    :style="{ width: `${progressPercent}%`, transitionDuration: scrubbing ? '0s' : undefined }"
                ></div>
            </div>
        </div>

        <!-- Mini control bar: a horizontal strip beside the thumbnail on mobile,
             a stacked block under the video on desktop. -->
        <div
            v-if="dock.mode.value === 'mini'"
            class="flex min-w-0 flex-1 items-center gap-1 px-2 sm:flex-col sm:items-stretch sm:gap-1 sm:px-3 sm:pt-1.5 sm:pb-2.5"
        >
            <button
                @click="expand"
                class="focus-visible:ring-ring text-foreground line-clamp-2 min-w-0 flex-1 cursor-pointer text-left text-sm font-medium outline-none hover:underline focus-visible:ring-2 sm:flex-none sm:truncate"
                :title="dock.current.value.name"
            >
                {{ dock.current.value.name }}
            </button>
            <div class="flex shrink-0 items-center gap-0.5 sm:w-full sm:gap-1">
                <button
                    @click="dock.controls.value?.toggle()"
                    class="focus-visible:ring-ring text-foreground hover:bg-accent hover:text-foreground inline-flex h-10 w-10 cursor-pointer items-center justify-center rounded-md outline-none focus-visible:ring-2"
                    :aria-label="dock.playing.value ? 'Pause' : 'Play'"
                >
                    <IconPlayerPause v-if="dock.playing.value" class="h-5 w-5" aria-hidden="true" />
                    <IconPlayerPlay v-else class="h-5 w-5" aria-hidden="true" />
                </button>
                <button
                    v-if="dock.next.value"
                    @click="playNext"
                    class="focus-visible:ring-ring text-foreground hover:bg-accent hover:text-foreground inline-flex h-10 w-10 cursor-pointer items-center justify-center rounded-md outline-none focus-visible:ring-2"
                    aria-label="Next episode"
                    :title="`Next: ${dock.next.value.name}`"
                >
                    <IconPlayerTrackNext class="h-5 w-5" aria-hidden="true" />
                </button>
                <span class="text-muted-foreground ml-1 hidden text-xs tabular-nums sm:inline">
                    {{ formatTime(dock.position.value) }}<template v-if="dock.duration.value"> / {{ formatTime(dock.duration.value) }}</template>
                </span>
                <button
                    @click="expand"
                    class="focus-visible:ring-ring text-muted-foreground hover:bg-accent hover:text-foreground ml-auto hidden h-10 w-10 cursor-pointer items-center justify-center rounded-md outline-none focus-visible:ring-2 sm:inline-flex"
                    aria-label="Open watch page"
                >
                    <IconArrowsDiagonal class="h-5 w-5" aria-hidden="true" />
                </button>
                <button
                    @click="dock.close()"
                    class="focus-visible:ring-ring text-muted-foreground hover:bg-accent hover:text-foreground inline-flex h-10 w-10 cursor-pointer items-center justify-center rounded-md outline-none focus-visible:ring-2"
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
