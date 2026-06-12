import VimeoPlayer from '@vimeo/player';
import { onBeforeUnmount, ref, type Ref } from 'vue';
import { detectProvider } from '~/lib/embeds';

/**
 * One control surface over both embedded players (YouTube iframe API,
 * Vimeo player SDK) — the keystone of the connected app layer. Everything
 * that makes the site feel like an app (resume, watched-at-80%, autoplay
 * next, keyboard control, mini-player scrubbing) hangs off this.
 *
 * The iframe src must come from getEmbedUrl() so the YouTube embed carries
 * enablejsapi=1 — without it the API silently never attaches.
 */

export interface PlayerCallbacks {
    /** ~1s heartbeat while playing; also fired on pause (positions are final then) */
    onProgress?: (seconds: number, duration: number) => void;
    onEnded?: () => void;
}

declare global {
    interface Window {
        YT?: any;
        onYouTubeIframeAPIReady?: () => void;
    }
}

let youtubeApiPromise: Promise<void> | null = null;

function loadYoutubeApi(): Promise<void> {
    youtubeApiPromise ??= new Promise((resolve) => {
        if (window.YT?.Player) return resolve();
        const previous = window.onYouTubeIframeAPIReady;
        window.onYouTubeIframeAPIReady = () => {
            previous?.();
            resolve();
        };
        const script = document.createElement('script');
        script.src = 'https://www.youtube.com/iframe_api';
        document.head.appendChild(script);
    });
    return youtubeApiPromise;
}

export function usePlayer(iframe: Ref<HTMLIFrameElement | null>, videoUrl: string, callbacks: PlayerCallbacks = {}) {
    const ready = ref(false);
    const playing = ref(false);
    const position = ref(0);
    const duration = ref(0);
    const muted = ref(false);

    const provider = detectProvider(videoUrl);
    let youtube: any = null;
    let vimeo: VimeoPlayer | null = null;
    let heartbeat: ReturnType<typeof setInterval> | null = null;
    let destroyed = false;
    let attached = false;

    const stopHeartbeat = () => {
        if (heartbeat) clearInterval(heartbeat);
        heartbeat = null;
    };

    // YouTube has no timeupdate event; poll while playing
    const startYoutubeHeartbeat = () => {
        stopHeartbeat();
        heartbeat = setInterval(() => {
            position.value = youtube?.getCurrentTime?.() ?? 0;
            duration.value = youtube?.getDuration?.() ?? 0;
            callbacks.onProgress?.(position.value, duration.value);
        }, 1000);
    };

    const attachYoutube = async () => {
        await loadYoutubeApi();
        if (destroyed || !iframe.value) return;
        youtube = new window.YT!.Player(iframe.value, {
            events: {
                onReady: () => {
                    ready.value = true;
                    duration.value = youtube.getDuration?.() ?? 0;
                },
                onStateChange: (event: { data: number }) => {
                    const states = window.YT!.PlayerState;
                    playing.value = event.data === states.PLAYING;
                    if (event.data === states.PLAYING) startYoutubeHeartbeat();
                    if (event.data === states.PAUSED) {
                        stopHeartbeat();
                        position.value = youtube.getCurrentTime?.() ?? position.value;
                        callbacks.onProgress?.(position.value, duration.value);
                    }
                    if (event.data === states.ENDED) {
                        stopHeartbeat();
                        playing.value = false;
                        callbacks.onEnded?.();
                    }
                },
            },
        });
    };

    const attachVimeo = () => {
        if (!iframe.value) return;
        vimeo = new VimeoPlayer(iframe.value);
        vimeo.ready().then(() => (ready.value = true));
        vimeo.getDuration().then((d) => (duration.value = d));
        vimeo.on('timeupdate', (data: { seconds: number; duration: number }) => {
            position.value = data.seconds;
            duration.value = data.duration;
            callbacks.onProgress?.(data.seconds, data.duration);
        });
        vimeo.on('play', () => (playing.value = true));
        vimeo.on('pause', () => (playing.value = false));
        vimeo.on('ended', () => {
            playing.value = false;
            callbacks.onEnded?.();
        });
    };

    const attach = () => {
        if (attached) return; // iframe load can fire more than once
        attached = true;
        if (provider === 'youtube') attachYoutube();
        if (provider === 'vimeo') attachVimeo();
    };

    const play = () => {
        youtube?.playVideo?.();
        vimeo?.play().catch(() => {});
    };
    const pause = () => {
        youtube?.pauseVideo?.();
        vimeo?.pause().catch(() => {});
    };
    const toggle = () => (playing.value ? pause() : play());
    const seekTo = (seconds: number) => {
        const target = Math.max(0, seconds);
        youtube?.seekTo?.(target, true);
        vimeo?.setCurrentTime(target).catch(() => {});
        position.value = target;
    };
    const seekBy = (seconds: number) => seekTo(position.value + seconds);
    const toggleMute = () => {
        if (youtube) {
            muted.value ? youtube.unMute?.() : youtube.mute?.();
            muted.value = !muted.value;
        }
        vimeo?.getMuted().then((m) => {
            vimeo!.setMuted(!m);
            muted.value = !m;
        });
    };

    const destroy = () => {
        destroyed = true;
        stopHeartbeat();
        youtube?.destroy?.();
        vimeo?.unload().catch(() => {});
        youtube = null;
        vimeo = null;
    };

    onBeforeUnmount(destroy);

    return { provider, ready, playing, position, duration, muted, attach, play, pause, toggle, seekTo, seekBy, toggleMute, destroy };
}
