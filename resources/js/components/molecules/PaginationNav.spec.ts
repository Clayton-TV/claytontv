import PaginationNav from '@/molecules/PaginationNav.vue';
import { mount } from '@vue/test-utils';
import { beforeEach, describe, expect, it, vi } from 'vitest';

const { get } = vi.hoisted(() => ({ get: vi.fn() }));
vi.mock('@inertiajs/vue3', () => ({ router: { get } }));

// The nav renders twice (a mobile and a desktop <nav>); read the desktop one.
const pageNumbers = (wrapper: ReturnType<typeof mount>) =>
    wrapper
        .findAll('nav')[1]
        .findAll('button')
        .map((b) => b.text())
        .filter((t) => t !== '');

const setUrl = (search: string) => {
    window.history.replaceState({}, '', `/search${search}`);
};

describe('PaginationNav', () => {
    beforeEach(() => {
        get.mockClear();
        setUrl('');
    });

    it('renders a numbered button per page', () => {
        const wrapper = mount(PaginationNav, { props: { numPages: 5, hasPrevPage: true, hasNextPage: true, currentPage: 3 } });

        expect(pageNumbers(wrapper)).toEqual(['1', '2', '3', '4', '5']);
    });

    it('disables the button for the page being shown', () => {
        const wrapper = mount(PaginationNav, { props: { numPages: 5, hasPrevPage: true, hasNextPage: true, currentPage: 3 } });

        const three = wrapper
            .findAll('nav')[1]
            .findAll('button')
            .find((b) => b.text() === '3');
        expect(three!.attributes('disabled')).toBeDefined();
    });

    it('trusts the current-page prop over the page in the URL', async () => {
        // The server clamps an out-of-range page; the URL still says 99999.
        setUrl('?search=grace&page=99999');
        const wrapper = mount(PaginationNav, { props: { numPages: 5, hasPrevPage: true, hasNextPage: false, currentPage: 5 } });

        const three = wrapper
            .findAll('nav')[1]
            .findAll('button')
            .find((b) => b.text() === '5');
        expect(three!.attributes('disabled')).toBeDefined();

        await wrapper.findAll('nav')[1].findAll('button')[0].trigger('click'); // Prev
        expect(get.mock.calls[0][0]).toContain('page=4'); // not 99998
    });

    it('falls back to the page in the URL when no prop is given', async () => {
        setUrl('?page=2');
        const wrapper = mount(PaginationNav, { props: { numPages: 3, hasPrevPage: true, hasNextPage: true } });

        const two = wrapper
            .findAll('nav')[1]
            .findAll('button')
            .find((b) => b.text() === '2');
        expect(two!.attributes('disabled')).toBeDefined();

        await wrapper.findAll('nav')[1].findAll('button').at(-1)!.trigger('click'); // Next
        expect(get.mock.calls[0][0]).toContain('page=3');
    });

    it('keeps the other query params when paging', async () => {
        setUrl('?search=grace&page=2');
        const wrapper = mount(PaginationNav, { props: { numPages: 3, hasPrevPage: true, hasNextPage: true, currentPage: 2 } });

        await wrapper.findAll('nav')[1].findAll('button').at(-1)!.trigger('click');
        expect(get.mock.calls[0][0]).toContain('search=grace');
    });
});
