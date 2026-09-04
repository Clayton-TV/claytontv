import SuggestionChips from '@/molecules/SuggestionChips.vue';
import { mount } from '@vue/test-utils';
import { describe, expect, it } from 'vitest';

const matched = [
    { id: 't1', name: 'Ethics' },
    { id: 't2', name: 'Law' },
];

describe('SuggestionChips', () => {
    it('renders nothing when there are no suggestions', () => {
        const wrapper = mount(SuggestionChips, { props: { matched: [], unmatched: [] } });
        expect(wrapper.text()).toBe('');
    });

    it('emits the option id when a matched chip is clicked', async () => {
        const wrapper = mount(SuggestionChips, { props: { matched, unmatched: [] } });
        await wrapper.findAll('button')[0].trigger('click');
        expect(wrapper.emitted('apply')?.[0]).toEqual([['t1']]);
    });

    it('offers "Add all" that emits every matched id', async () => {
        const wrapper = mount(SuggestionChips, { props: { matched, unmatched: [] } });
        const addAll = wrapper.findAll('button').find((b) => b.text() === 'Add all');
        await addAll!.trigger('click');
        expect(wrapper.emitted('apply')?.at(-1)).toEqual([['t1', 't2']]);
    });

    it('shows unmatched names as non-clickable "new" hints', () => {
        const wrapper = mount(SuggestionChips, { props: { matched: [], unmatched: ['Human rights'] } });
        expect(wrapper.text()).toContain('Human rights · new');
        expect(wrapper.findAll('button')).toHaveLength(0); // no add affordance for unmatched
    });

    it('is unbranded — no "AI" wording', () => {
        const wrapper = mount(SuggestionChips, { props: { matched, unmatched: ['Foo'] } });
        expect(wrapper.text()).not.toMatch(/\bAI\b/);
    });
});
