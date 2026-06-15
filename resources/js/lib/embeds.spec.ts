import { describe, expect, it } from 'vitest';
import { detectProvider, getEmbedUrl, getYoutubeId } from '~/lib/embeds';

describe('getYoutubeId', () => {
    it('extracts the id from common YouTube URL shapes', () => {
        expect(getYoutubeId('https://www.youtube.com/watch?v=dQw4w9WgXcQ')).toBe('dQw4w9WgXcQ');
        expect(getYoutubeId('https://youtu.be/dQw4w9WgXcQ')).toBe('dQw4w9WgXcQ');
        expect(getYoutubeId('https://www.youtube.com/embed/dQw4w9WgXcQ')).toBe('dQw4w9WgXcQ');
    });

    it('returns undefined for non-YouTube URLs', () => {
        expect(getYoutubeId('https://vimeo.com/76979871')).toBeUndefined();
        expect(getYoutubeId('https://example.com')).toBeUndefined();
    });
});

describe('detectProvider', () => {
    it('classifies YouTube, Vimeo, and neither', () => {
        expect(detectProvider('https://youtu.be/abc')).toBe('youtube');
        expect(detectProvider('https://vimeo.com/123')).toBe('vimeo');
        expect(detectProvider('https://example.com/x')).toBeNull();
    });
});

describe('getEmbedUrl', () => {
    it('builds a privacy-domain YouTube embed, honouring start', () => {
        const url = getEmbedUrl('https://www.youtube.com/watch?v=abc123', { start: 90 });
        expect(url).toContain('youtube-nocookie.com/embed/abc123');
        expect(url).toContain('start=90');
    });

    it('builds a Vimeo embed, carrying the privacy hash and start fragment', () => {
        const url = getEmbedUrl('https://vimeo.com/76979871/abcdef', { start: 30 });
        expect(url).toContain('player.vimeo.com/video/76979871');
        expect(url).toContain('h=abcdef');
        expect(url).toContain('#t=30s');
    });

    it('returns false for an unsupported URL', () => {
        expect(getEmbedUrl('https://example.com/not-a-video')).toBe(false);
    });
});
