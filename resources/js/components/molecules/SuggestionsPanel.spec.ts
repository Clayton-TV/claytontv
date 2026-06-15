import SuggestionsPanel from '@/molecules/SuggestionsPanel.vue';
import { mount } from '@vue/test-utils';
import { describe, expect, it } from 'vitest';

const taxonomy = {
    topics: [{ id: 't1', name: 'Grace' }],
    demographics: [{ id: 'd1', name: 'Adults' }],
    bible_books: [{ id: 'b1', name: 'Romans' }],
};

const enrichment = {
    summary: 'A sermon on grace.',
    topics: ['Grace', 'Unknown topic'],
    audience: 'Adults',
    bible_passages: [{ book: 'Romans', label: 'Romans 8' }],
    keywords: ['grace', 'adoption'],
    generated_at: '2026-06-15T10:00:00Z',
};

function clickButton(wrapper: ReturnType<typeof mount>, text: string) {
    const btn = wrapper.findAll('button').find((b) => b.text().includes(text));
    if (!btn) throw new Error(`No button matching "${text}". Buttons: ${wrapper.findAll('button').map((b) => b.text())}`);
    return btn.trigger('click');
}

describe('SuggestionsPanel', () => {
    it('shows an empty state with a generate action when there is no enrichment', () => {
        const wrapper = mount(SuggestionsPanel, { props: { enrichment: null, taxonomy } });
        expect(wrapper.text()).toContain('No suggestions yet');
        expect(wrapper.findAll('button').some((b) => b.text().includes('Generate suggestions'))).toBe(true);
    });

    it('renders the stored suggestions', () => {
        const wrapper = mount(SuggestionsPanel, { props: { enrichment, taxonomy } });
        expect(wrapper.text()).toContain('A sermon on grace.');
        expect(wrapper.text()).toContain('Grace');
        expect(wrapper.text()).toContain('Romans 8');
        expect(wrapper.text()).toContain('adoption'); // a keyword
    });

    it('is not branded as AI', () => {
        const wrapper = mount(SuggestionsPanel, { props: { enrichment, taxonomy } });
        expect(wrapper.text()).not.toMatch(/\bAI\b/);
        expect(wrapper.text()).not.toContain('✨');
    });

    it('emits the summary as a description', async () => {
        const wrapper = mount(SuggestionsPanel, { props: { enrichment, taxonomy } });
        await clickButton(wrapper, 'Use as description');
        expect(wrapper.emitted('apply')?.[0]).toEqual([{ description: 'A sermon on grace.' }]);
    });

    it('applies only topics that match existing taxonomy', async () => {
        const wrapper = mount(SuggestionsPanel, { props: { enrichment, taxonomy } });
        await clickButton(wrapper, 'Add 1 topic');
        expect(wrapper.emitted('apply')?.[0]).toEqual([{ topic_ids: ['t1'] }]);
    });

    it('shows an unmatched suggestion but excludes it from apply', () => {
        const wrapper = mount(SuggestionsPanel, { props: { enrichment, taxonomy } });
        expect(wrapper.text()).toContain('Unknown topic'); // displayed
        // ...but the apply button only offers the one match.
        expect(wrapper.findAll('button').some((b) => b.text().includes('Add 1 topic'))).toBe(true);
    });

    it('apply all bundles every matched field', async () => {
        const wrapper = mount(SuggestionsPanel, { props: { enrichment, taxonomy } });
        await clickButton(wrapper, 'Apply all');
        expect(wrapper.emitted('apply')?.[0]).toEqual([
            { description: 'A sermon on grace.', topic_ids: ['t1'], demographic_ids: ['d1'], bible_book_ids: ['b1'] },
        ]);
    });

    it('emits regenerate', async () => {
        const wrapper = mount(SuggestionsPanel, { props: { enrichment, taxonomy } });
        await clickButton(wrapper, 'Regenerate');
        expect(wrapper.emitted('regenerate')).toHaveLength(1);
    });

    it('disables the topic apply when nothing matches', () => {
        const wrapper = mount(SuggestionsPanel, {
            props: { enrichment: { ...enrichment, topics: ['Nope'] }, taxonomy },
        });
        const btn = wrapper.findAll('button').find((b) => b.text().includes('topic'));
        expect(btn?.attributes('disabled')).toBeDefined();
    });
});
