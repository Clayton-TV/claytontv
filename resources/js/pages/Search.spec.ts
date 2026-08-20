import { mount } from '@vue/test-utils';
import { describe, expect, it, vi } from 'vitest';
import Search from '~/pages/Search.vue';

// The page under test only needs Inertia's url (for ?search=) and inert Head/Link.
vi.mock('@inertiajs/vue3', () => ({
    Head: { template: '<div />' },
    Link: { template: '<a><slot /></a>' },
    router: { get: vi.fn() },
    usePage: () => ({ url: '/search?search=grace&page=2' }),
}));
vi.mock('~/lib/analytics', () => ({ EVENTS: { searchPerformed: 'search_performed' }, track: vi.fn() }));

const videos = [{ id: '1', name: 'Grace abounds', url: 'https://youtu.be/abc123' }];

describe('Search page pagination wiring', () => {
    it('hands the page count and the served page down to the nav', () => {
        // #329: the page used not to declare or forward num_pages, so the nav
        // fell back to its default of 1 and drew a lone "1" between the chevrons
        // — the whole chain (view → page → grid → nav) has to hold.
        const wrapper = mount(Search, {
            props: { videos, num_pages: 4, page: 2, has_prev_page: true, has_next_page: true, categories: [] },
        });

        const nav = wrapper.findAll('nav')[1];
        expect(
            nav
                .findAll('button')
                .map((b) => b.text())
                .filter((t) => t !== ''),
        ).toEqual(['1', '2', '3', '4']);

        const two = nav.findAll('button').find((b) => b.text() === '2');
        expect(two!.attributes('disabled')).toBeDefined(); // the served page, not the URL's
    });
});
