import { enableAutoUnmount, mount } from '@vue/test-utils';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { reactive } from 'vue';

const { track } = vi.hoisted(() => ({ track: vi.fn() }));
const inertiaPage = reactive({ url: '' });

vi.mock('@inertiajs/vue3', () => ({
    Head: { template: '<div />' },
    Link: { template: '<a><slot /></a>' },
    usePage: () => inertiaPage,
}));

vi.mock('~/lib/analytics', () => ({
    EVENTS: { searchPerformed: 'search_performed' },
    track,
}));

import Search from './Search.vue';

enableAutoUnmount(afterEach);

function mountSearch(url: string) {
    inertiaPage.url = url;

    return mount(Search, {
        props: { categories: [], videos: [], title: 'Search' },
        global: {
            stubs: {
                VideoCardGrid: {
                    props: ['emptyTitle', 'emptyMessage'],
                    template: '<div>{{ emptyTitle }} {{ emptyMessage }}</div>',
                },
            },
        },
    });
}

describe('Search', () => {
    beforeEach(() => {
        track.mockClear();
    });

    it('uses the final repeated search value, matching Django QueryDict.get', () => {
        const wrapper = mountSearch('/search?search=grace&search=%20%20%20');

        expect(wrapper.text()).toContain('Nothing to show yet');
        expect(track).not.toHaveBeenCalled();
    });

    it('tracks the final repeated search value and shows its empty state', () => {
        const wrapper = mountSearch('/search?search=%20%20%20&search=grace');

        expect(wrapper.text()).toContain('No matching videos');
        expect(track).toHaveBeenCalledTimes(1);
        expect(track).toHaveBeenCalledWith('search_performed', {
            query: 'grace',
            results_count: 0,
            category_count: 0,
            is_zero_results: true,
        });
    });
});
