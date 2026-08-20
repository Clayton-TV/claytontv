import VideoCardGrid from '@/organisms/VideoCardGrid.vue';
import { mount } from '@vue/test-utils';
import { describe, expect, it, vi } from 'vitest';

vi.mock('@inertiajs/vue3', () => ({
    Link: { template: '<a><slot /></a>' },
    router: { get: vi.fn() },
}));
vi.mock('~/lib/analytics', () => ({ EVENTS: {}, track: vi.fn() }));

const videos = [{ id: '1', name: 'A talk', url: 'https://youtu.be/abc123' }];

const pageNumbers = (wrapper: ReturnType<typeof mount>) =>
    wrapper
        .findAll('nav')[1]
        .findAll('button')
        .map((b) => b.text())
        .filter((t) => t !== '');

describe('VideoCardGrid pagination', () => {
    it('passes the page count through to the nav so it can draw page numbers', () => {
        // #329: the grid used not to receive num_pages on /search, so the nav
        // fell back to its default of 1 and rendered a lone "1".
        const wrapper = mount(VideoCardGrid, {
            props: { videos, num_pages: 3, page: 2, has_prev_page: true, has_next_page: true },
        });

        expect(pageNumbers(wrapper)).toEqual(['1', '2', '3']);
    });

    it('tells the nav which page was served', () => {
        const wrapper = mount(VideoCardGrid, {
            props: { videos, num_pages: 3, page: 2, has_prev_page: true, has_next_page: true },
        });

        const two = wrapper
            .findAll('nav')[1]
            .findAll('button')
            .find((b) => b.text() === '2');
        expect(two!.attributes('disabled')).toBeDefined();
    });
});
