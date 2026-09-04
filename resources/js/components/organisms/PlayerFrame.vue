<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from 'vue';
import { usePlayer } from '~/composables/usePlayer';
import { usePlayerDock } from '~/composables/usePlayerDock';
import { useWatchHistory } from '~/composables/useWatchHistory';
import { EVENTS, track } from '~/lib/analytics';
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

// ----- analytics (video_play / video_progress 25·50·75 / video_complete) -----
// Fired once each per loaded video; metadata rides as properties. Live streams
// and zero-duration (pre-metadata) skip the % milestones — duration is the
// elapsed time for a live stream, so milestone maths would be meaningless.
const PROGRESS_MILESTONES = [25, 50, 75];
const firedMilestones = new Set();
let firedPlay = false;

const videoProps = () => ({
    video_id: props.video.id,
    video_name: props.video.name,
    provider: player.provider,
    is_live: !!props.video.is_live,
    speaker: props.video.meta?.speaker,
    series: props.video.meta?.series,
    topic: props.video.meta?.topic,
    bible_book: props.video.meta?.bible_book,
});

const player = usePlayer(iframe, props.video.url, {
    onProgress: (seconds, duration) => {
        dock.position.value = seconds;
        dock.duration.value = duration;
        saveProgress(props.video.id, seconds, duration, props.video.name);

        if (props.video.is_live || !duration) return;
        const percent = (seconds / duration) * 100;
        for (const milestone of PROGRESS_MILESTONES) {
            if (percent >= milestone && !firedMilestones.has(milestone)) {
                firedMilestones.add(milestone);
                track(EVENTS.videoProgress, { ...videoProps(), percent: milestone });
            }
        }
    },
    onEnded: () => {
        track(EVENTS.videoComplete, videoProps());
        emit('ended');
    },
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
// mini control bar); fire video_play once, the first time this video starts.
watch(player.playing, (value) => {
    dock.playing.value = value;
    if (value && !firedPlay) {
        firedPlay = true;
        track(EVENTS.videoPlay, videoProps());
    }
});
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
