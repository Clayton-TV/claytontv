<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from 'vue';
import { usePlayer } from '~/composables/usePlayer';
import { usePlayerDock } from '~/composables/usePlayerDock';
import { useWatchHistory } from '~/composables/useWatchHistory';
import { getEmbedUrl } from '~/lib/embeds';

/**
 * The actual iframe + provider API wiring for the persistent player. One
 * instance per video (PersistentPlayer keys it by video id); it feeds the
 * dock store with live state and registers the control surface.
 */

const props = defineProps({
    video: { type: Object, required: true }, // DockVideo
    start: { type: Number, default: 0 },
    autoplay: { type: Boolean, default: false },
});

const emit = defineEmits(['ended']);

const dock = usePlayerDock();
const { saveProgress } = useWatchHistory();

const iframe = ref(null);
const embedUrl = getEmbedUrl(props.video.url, { start: props.start, autoplay: props.autoplay });

const player = usePlayer(iframe, props.video.url, {
    onProgress: (seconds, duration) => {
        dock.position.value = seconds;
        dock.duration.value = duration;
        saveProgress(props.video.id, seconds, duration, props.video.name);
    },
    onEnded: () => emit('ended'),
});

onMounted(() => {
    player.attach();
    dock.controls.value = {
        toggle: player.toggle,
        play: player.play,
        pause: player.pause,
        seekTo: player.seekTo,
        seekBy: player.seekBy,
        toggleMute: player.toggleMute,
    };
});

// Mirror playing state into the dock (drives persist-on-navigate and the
// mini control bar)
watch(player.playing, (value) => (dock.playing.value = value));
onBeforeUnmount(() => {
    dock.playing.value = false;
});
</script>

<template>
    <div class="h-full w-full overflow-hidden bg-black">
        <iframe
            v-if="embedUrl"
            ref="iframe"
            class="h-full w-full"
            :src="embedUrl"
            allow="autoplay; clipboard-write; fullscreen; picture-in-picture"
            referrerpolicy="strict-origin-when-cross-origin"
            allowfullscreen
            :title="video.name"
            @load="player.attach()"
        >
        </iframe>
        <div v-else class="flex h-full items-center justify-center p-6 text-sm text-gray-400">
            <p>
                We couldn't embed this video.
                <a :href="video.url" class="text-primary underline underline-offset-4" rel="noopener" target="_blank">Watch it at the source</a>
            </p>
        </div>
    </div>
</template>
