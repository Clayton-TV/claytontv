<script setup>
import { onMounted, ref } from 'vue';
import { usePlayer } from '~/composables/usePlayer';
import { getEmbedUrl } from '~/lib/embeds';

const props = defineProps({
    video: { type: Object, required: true },
    // Resume position in seconds — baked into the embed URL (start=/#t=)
    // so there's no seek-after-load race
    start: { type: Number, default: 0 },
    autoplay: { type: Boolean, default: false },
});

const emit = defineEmits(['progress', 'ended']);

const iframe = ref(null);
const embedUrl = getEmbedUrl(props.video.url, { start: props.start, autoplay: props.autoplay });

const player = usePlayer(iframe, props.video.url, {
    onProgress: (seconds, duration) => emit('progress', seconds, duration),
    onEnded: () => emit('ended'),
});

// Attach on mount AND on iframe load: mount alone can be too early on a slow
// first paint, load alone never fires if the iframe finished before Vue
// hydrated its listener. attach() itself is idempotent.
onMounted(() => player.attach());
const onIframeLoad = () => player.attach();

// Parent components (keyboard shortcuts, mini-player) drive playback through this
defineExpose({ player });
</script>

<template>
    <div class="aspect-video w-full overflow-hidden rounded-xl border border-white/10 bg-black">
        <iframe
            v-if="embedUrl"
            ref="iframe"
            class="h-full w-full"
            :src="embedUrl"
            allow="autoplay; clipboard-write; fullscreen; picture-in-picture"
            referrerpolicy="strict-origin-when-cross-origin"
            allowfullscreen
            :title="video.name"
            @load="onIframeLoad"
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
