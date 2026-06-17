import ClassificationFields from '@/molecules/ClassificationFields.vue';
import { mount } from '@vue/test-utils';
import { describe, expect, it } from 'vitest';

const taxonomy = {
    speakers: [{ id: '1', name: 'Andy' }],
    series: [{ id: 's1', name: 'Romans' }],
    topics: [],
    bible_books: [],
    demographics: [],
    ministries: [],
};

describe('ClassificationFields', () => {
    it('renders all six taxonomy pickers', () => {
        const wrapper = mount(ClassificationFields, {
            props: {
                taxonomy,
                speakerIds: [],
                topicIds: [],
                bibleBookIds: [],
                demographicIds: [],
                ministryIds: [],
                seriesId: null,
            },
        });
        for (const label of ['Speakers', 'Series', 'Topics', 'Bible books', 'Audiences', 'Ministries']) {
            expect(wrapper.text()).toContain(label);
        }
    });

    it('shows no suggestion chips when suggestions are omitted (e.g. Add-a-video)', () => {
        const wrapper = mount(ClassificationFields, {
            props: { taxonomy, topicIds: [], demographicIds: [], bibleBookIds: [], speakerIds: [], ministryIds: [], seriesId: null },
        });
        expect(wrapper.text()).not.toContain('Suggested');
    });

    it('adds a suggested topic to the selection when its chip is clicked', async () => {
        const wrapper = mount(ClassificationFields, {
            props: {
                taxonomy: { ...taxonomy, topics: [{ id: 't1', name: 'Grace' }] },
                topicIds: [],
                demographicIds: [],
                bibleBookIds: [],
                speakerIds: [],
                ministryIds: [],
                seriesId: null,
                suggestions: {
                    topics: { matched: [{ id: 't1', name: 'Grace' }], unmatched: [] },
                    audiences: { matched: [], unmatched: [] },
                    books: { matched: [], unmatched: [] },
                },
            },
        });
        const chip = wrapper.findAll('button').find((b) => b.text().includes('Grace'));
        await chip!.trigger('click');
        expect(wrapper.emitted('update:topicIds')?.at(-1)).toEqual([['t1']]);
    });
});
