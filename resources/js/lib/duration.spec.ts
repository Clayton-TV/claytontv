import { describe, expect, it } from 'vitest';
import { formatDuration } from '~/lib/duration';

describe('formatDuration', () => {
    it('formats minutes:seconds under an hour', () => {
        expect(formatDuration(90)).toBe('1:30');
        expect(formatDuration(59)).toBe('0:59');
    });

    it('formats h:mm:ss at/over an hour', () => {
        expect(formatDuration(3661)).toBe('1:01:01');
    });

    it('returns empty string for null/undefined/zero', () => {
        expect(formatDuration(null)).toBe('');
        expect(formatDuration(undefined)).toBe('');
        expect(formatDuration(0)).toBe('');
    });
});
