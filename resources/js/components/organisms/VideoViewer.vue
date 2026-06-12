<script setup>
defineProps({
    video: {
        type: Object,
        required: true,
    },
});

const getYoutubeId = (videoUrl) => {
    const youtubeRegex = /^.*(youtu\.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=)([^#\&\?]*).*/;
    const youtubeId = videoUrl.match(youtubeRegex)?.[2];
    return youtubeId;
};

const getVimeoEmbedUrl = (videoUrl) => {
    // Matches vimeo.com/<id> and vimeo.com/<id>/<hash>. The hash is the privacy
    // token for unlisted videos — without it as ?h= the player demands a Vimeo
    // sign-in (~2,400 of our legacy URLs carry one).
    const vimeoRegex = /^(?:http|https):\/\/(?:www\.)?vimeo.com\/(\d+)(?:\/(\w+))?.*/;
    const match = videoUrl.match(vimeoRegex);
    if (!match) {
        return null;
    }
    const [, vimeoId, unlistedHash] = match;
    return `https://player.vimeo.com/video/${vimeoId}${unlistedHash ? `?h=${unlistedHash}` : ''}`;
};

const getEmbedUrl = (videoUrl) => {
    const youtubeId = getYoutubeId(videoUrl);
    const vimeoEmbedUrl = getVimeoEmbedUrl(videoUrl);
    if (youtubeId) {
        return `https://www.youtube-nocookie.com/embed/${youtubeId}?autoplay=0&playsinline=1`;
    } else if (vimeoEmbedUrl) {
        return vimeoEmbedUrl;
    } else {
        return false;
    }
};
</script>

<template>
    <div class="aspect-video w-full overflow-hidden rounded-xl border border-white/10 bg-black">
        <iframe
            v-if="getEmbedUrl(video.url)"
            class="h-full w-full"
            :src="getEmbedUrl(video.url)"
            allow="autoplay; clipboard-write; fullscreen; picture-in-picture"
            referrerpolicy="strict-origin-when-cross-origin"
            allowfullscreen
            :title="video.name"
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
