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
});
