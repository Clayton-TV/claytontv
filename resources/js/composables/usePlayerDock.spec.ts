import { beforeEach, describe, expect, it } from 'vitest';
import { usePlayerDock } from '~/composables/usePlayerDock';

const VIDEO = { id: 1, name: 'A talk', url: 'https://youtu.be/abc' };

beforeEach(() => {
    usePlayerDock().close();
    localStorage.clear();
});

describe('usePlayerDock', () => {
    it('loads a video into the dock (mini mode when no placeholder)', () => {
        const dock = usePlayerDock();
        const changed = dock.load(VIDEO);
        expect(changed).toBe(true);
        expect(dock.current.value?.id).toBe(1);
        expect(dock.mode.value).toBe('mini');
    });

    it('is a no-op when loading the already-playing video', () => {
        const dock = usePlayerDock();
        dock.load(VIDEO);
        expect(dock.load(VIDEO)).toBe(false); // same id → seamless, no reload
    });

    it('close() clears the dock to hidden', () => {
        const dock = usePlayerDock();
        dock.load(VIDEO);
        dock.close();
        expect(dock.current.value).toBeNull();
        expect(dock.mode.value).toBe('hidden');
    });

    it('restore() rehydrates the last-played video from localStorage', () => {
        localStorage.setItem('ctv:active-player', JSON.stringify({ id: 9, name: 'Saved', url: 'https://youtu.be/xyz', position: 42 }));
        const dock = usePlayerDock();
        dock.restore();
        expect(dock.current.value?.id).toBe(9);
        expect(dock.position.value).toBe(42);
    });
});
