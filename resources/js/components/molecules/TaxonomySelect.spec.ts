import TaxonomySelect from '@/molecules/TaxonomySelect.vue';
import { mount } from '@vue/test-utils';
import { describe, expect, it } from 'vitest';

const options = [
    { id: '1', name: 'Andy Acheson' },
    { id: '2', name: 'Beth Baker' },
    { id: '3', name: 'Carl Coekin' },
];

function open(wrapper: ReturnType<typeof mount>) {
    return wrapper.get('button[aria-haspopup="listbox"]').trigger('click');
}

describe('TaxonomySelect', () => {
    it('shows the placeholder when nothing is selected', () => {
        const wrapper = mount(TaxonomySelect, {
            props: { id: 't', label: 'Speakers', options, modelValue: [], multiple: true, placeholder: 'Add speakers…' },
        });
        expect(wrapper.text()).toContain('Add speakers…');
    });

    it('filters options by the search query', async () => {
        const wrapper = mount(TaxonomySelect, {
            props: { id: 't', label: 'Speakers', options, modelValue: [], multiple: true },
        });
        await open(wrapper);
        await wrapper.get('input[type="search"]').setValue('beth');
        const shown = wrapper.findAll('[role="option"]');
        expect(shown).toHaveLength(1);
        expect(shown[0].text()).toContain('Beth Baker');
    });

    it('multi-select emits an array of ids and toggles', async () => {
        const wrapper = mount(TaxonomySelect, {
            props: { id: 't', label: 'Speakers', options, modelValue: [], multiple: true },
        });
        await open(wrapper);
        await wrapper.findAll('[role="option"]')[1].trigger('click'); // Beth → id 2
        expect(wrapper.emitted('update:modelValue')?.at(-1)).toEqual([['2']]);
    });

    it('single-select emits the bare id', async () => {
        const wrapper = mount(TaxonomySelect, {
            props: { id: 't', label: 'Series', options, modelValue: null },
        });
        await open(wrapper);
        await wrapper.findAll('[role="option"]')[0].trigger('click'); // id 1
        expect(wrapper.emitted('update:modelValue')?.at(-1)).toEqual(['1']);
    });

    it('renders a chip for each selected id (multiple)', () => {
        const wrapper = mount(TaxonomySelect, {
            props: { id: 't', label: 'Speakers', options, modelValue: ['1', '3'], multiple: true },
        });
        expect(wrapper.text()).toContain('Andy Acheson');
        expect(wrapper.text()).toContain('Carl Coekin');
    });
});
