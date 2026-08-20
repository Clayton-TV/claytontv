import { mount } from '@vue/test-utils';
import { describe, expect, it, vi } from 'vitest';
import Services from '~/pages/Services.vue';

vi.mock('@inertiajs/vue3', () => ({
    Head: { template: '<div />' },
    Link: { template: '<a><slot /></a>' },
    router: { get: vi.fn() },
}));
vi.mock('~/lib/analytics', () => ({ EVENTS: {}, track: vi.fn() }));

const past = [{ id: '1', name: 'Sunday service', url: 'https://youtu.be/abc123' }];

describe('Services page pagination wiring', () => {
    it('hands the page count and the served page down to the archive grid', () => {
        // The view has always sent num_pages; the page dropped it on the way to
        // the grid, so the past-services nav drew a lone "1" (#329).
        const wrapper = mount(Services, {
            props: { title: 'Services', live: [], upcoming: [], past, num_pages: 3, page: 2, has_prev_page: true, has_next_page: true },
        });

        const nav = wrapper.findAll('nav')[1];
        expect(
            nav
                .findAll('button')
                .map((b) => b.text())
                .filter((t) => t !== ''),
        ).toEqual(['1', '2', '3']);

        const two = nav.findAll('button').find((b) => b.text() === '2');
        expect(two!.attributes('disabled')).toBeDefined();
    });
});
