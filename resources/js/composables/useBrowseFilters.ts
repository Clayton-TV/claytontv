import { router } from '@inertiajs/vue3';

/**
 * URL-driven faceted-browse state. Builds the query string explicitly with
 * repeated keys (speaker=1&speaker=2) so Django's request.GET.getlist sees
 * them — Inertia/axios would otherwise serialise arrays as speaker[]=.
 *
 * Navigations are partial reloads that keep the (static, global) facet option
 * lists, the scroll position and the mounted sidebar — only the results +
 * active state refresh, so filtering feels instant and keeps the viewer's place.
 */

type Active = {
    speaker: string[];
    book: string[];
    audience: string[];
    type: string;
    length: string;
};

const MULTI: (keyof Active)[] = ['speaker', 'book', 'audience'];
const SINGLE: (keyof Active)[] = ['type', 'length'];
const REFRESH = ['videos', 'active', 'total', 'page', 'num_pages', 'has_prev_page', 'has_next_page'];

export function useBrowseFilters(getActive: () => Active) {
    const params = () => {
        const active = getActive();
        const p = new URLSearchParams();
        for (const facet of MULTI) (active[facet] as string[]).forEach((v) => p.append(facet, v));
        for (const facet of SINGLE) if (active[facet]) p.set(facet, active[facet] as string);
        return p;
    };

    const go = (p: URLSearchParams) => {
        const query = p.toString();
        router.get(`/browse/${query ? `?${query}` : ''}`, {}, { preserveState: true, preserveScroll: true, only: REFRESH });
    };

    const toggleMulti = (facet: keyof Active, value: string | number) => {
        const p = params();
        const current = p.getAll(facet);
        p.delete(facet);
        const value_ = String(value);
        const next = current.includes(value_) ? current.filter((v) => v !== value_) : [...current, value_];
        next.forEach((v) => p.append(facet, v));
        go(p);
    };

    const setSingle = (facet: keyof Active, value: string) => {
        const p = params();
        p.get(facet) === value ? p.delete(facet) : p.set(facet, value);
        go(p);
    };

    const remove = (facet: keyof Active, value: string | number) => {
        if (MULTI.includes(facet)) toggleMulti(facet, value);
        else setSingle(facet, String(value));
    };

    const clearAll = () => router.get('/browse/', {}, { preserveScroll: true });

    const isActive = (facet: keyof Active, value: string | number) => {
        const active = getActive();
        const value_ = String(value);
        return MULTI.includes(facet) ? (active[facet] as string[]).map(String).includes(value_) : active[facet] === value_;
    };

    const activeCount = () => {
        const active = getActive();
        return MULTI.reduce((n, f) => n + (active[f] as string[]).length, 0) + SINGLE.filter((f) => active[f]).length;
    };

    return { toggleMulti, setSingle, remove, clearAll, isActive, activeCount };
}
