import { describe, expect, it } from 'vitest';
import { ref } from 'vue';
import { type Enrichment, useSuggestions } from '~/composables/useSuggestions';

const taxonomy = {
    topics: [
        { id: 't1', name: 'Grace' },
        { id: 't2', name: 'Ethics' },
    ],
    demographics: [{ id: 'd1', name: 'Adults' }],
    bible_books: [{ id: 'b1', name: 'Romans' }],
};

const enrichment: Enrichment = {
    summary: 'A talk on grace.',
    topics: ['Grace', 'Unknown topic'],
    audience: 'Adults',
    bible_passages: [{ book: 'Romans', label: 'Romans 8' }],
    keywords: ['grace', 'faith'],
    generated_at: '2026-06-17T10:00:00Z',
};

describe('useSuggestions', () => {
    it('resolves matched options and surfaces unmatched names', () => {
        const s = useSuggestions(() => enrichment, taxonomy);
        expect(s.topics.value.matched.map((o) => o.id)).toEqual(['t1']);
        expect(s.topics.value.unmatched).toEqual(['Unknown topic']);
        expect(s.audience.value.matched.map((o) => o.id)).toEqual(['d1']);
        expect(s.books.value.matched.map((o) => o.id)).toEqual(['b1']);
        expect(s.summary.value).toBe('A talk on grace.');
    });

    it('reports presence and a per-field count', () => {
        const s = useSuggestions(() => enrichment, taxonomy);
        expect(s.has.value).toBe(true);
        expect(s.count.value).toBe(4); // summary + topics + audience + books
    });

    it('is empty and absent when there is no enrichment', () => {
        const s = useSuggestions(() => null, taxonomy);
        expect(s.has.value).toBe(false);
        expect(s.count.value).toBe(0);
        expect(s.topics.value.matched).toEqual([]);
        expect(s.summary.value).toBe('');
    });

    it('reacts to the enrichment changing (e.g. after regenerate)', () => {
        const e = ref<Enrichment | null>(null);
        const s = useSuggestions(e, taxonomy);
        expect(s.has.value).toBe(false);
        e.value = enrichment;
        expect(s.has.value).toBe(true);
        expect(s.topics.value.matched.map((o) => o.id)).toEqual(['t1']);
    });

    it('dedupes a matched option suggested twice', () => {
        const e: Enrichment = { ...enrichment, topics: ['Grace', 'grace', 'GRACE'] };
        const s = useSuggestions(() => e, taxonomy);
        expect(s.topics.value.matched.map((o) => o.id)).toEqual(['t1']);
    });
});
