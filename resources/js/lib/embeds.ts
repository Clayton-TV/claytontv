/** Embed-URL building for the two providers the catalogue holds. */

export type Provider = 'youtube' | 'vimeo' | null;

export const getYoutubeId = (videoUrl: string): string | undefined => {
    const youtubeRegex = /^.*(youtu\.be\/|v\/|u\/\w\/|embed\/|watch\?v=|&v=)([^#&?]*).*/;
    return videoUrl.match(youtubeRegex)?.[2];
};

// Matches vimeo.com/<id> and vimeo.com/<id>/<hash>. The hash is the privacy
// token for unlisted videos — without it as ?h= the player demands a Vimeo
// sign-in (~2,400 of our legacy URLs carry one).
const vimeoRegex = /^(?:http|https):\/\/(?:www\.)?vimeo.com\/(\d+)(?:\/(\w+))?.*/;

export const detectProvider = (videoUrl: string): Provider => {
    if (getYoutubeId(videoUrl)) return 'youtube';
    if (videoUrl.match(vimeoRegex)) return 'vimeo';
    return null;
};

export interface EmbedOptions {
    start?: number; // resume position, whole seconds
    autoplay?: boolean;
}

export const getEmbedUrl = (videoUrl: string, { start, autoplay }: EmbedOptions = {}): string | false => {
    const youtubeId = getYoutubeId(videoUrl);
    if (youtubeId) {
        const params = new URLSearchParams({
            autoplay: autoplay ? '1' : '0',
            playsinline: '1',
            // Lets the YouTube iframe API attach for progress/ended events
            enablejsapi: '1',
            origin: typeof window !== 'undefined' ? window.location.origin : '',
        });
        if (start) params.set('start', String(Math.floor(start)));
        return `https://www.youtube-nocookie.com/embed/${youtubeId}?${params}`;
    }

    const vimeoMatch = videoUrl.match(vimeoRegex);
    if (vimeoMatch) {
        const [, vimeoId, unlistedHash] = vimeoMatch;
        const params = new URLSearchParams();
        if (unlistedHash) params.set('h', unlistedHash);
        if (autoplay) params.set('autoplay', '1');
        const query = params.size ? `?${params}` : '';
        // Vimeo takes the resume position as a #t= fragment
        const fragment = start ? `#t=${Math.floor(start)}s` : '';
        return `https://player.vimeo.com/video/${vimeoId}${query}${fragment}`;
    }

    return false;
};
