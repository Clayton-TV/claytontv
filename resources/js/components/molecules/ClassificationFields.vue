<script setup lang="ts">
import SuggestionChips from '@/molecules/SuggestionChips.vue';
import TaxonomySelect from '@/molecules/TaxonomySelect.vue';

/**
 * The shared classification grid: speakers · series · topics · Bible books ·
 * audiences · ministries, each a searchable {@link TaxonomySelect}. Used by both
 * the Add-a-video form and the editor so the two stay in lockstep. Series is
 * single-select (one series per video); the rest are multi.
 *
 * When `suggestions` is supplied (the editor), each suggestible field shows an
 * inline {@link SuggestionChips} row beneath its picker; matched chips add to the
 * field's selection. Add-a-video omits it, so no chips render there.
 */

interface Option {
    id: string;
    name: string;
}
interface ResolvedField {
    matched: Option[];
    unmatched: string[];
}

defineProps<{
    taxonomy: {
        speakers: Option[];
        series: Option[];
        topics: Option[];
        bible_books: Option[];
        demographics: Option[];
        ministries: Option[];
    };
    suggestions?: {
        topics: ResolvedField;
        audiences: ResolvedField;
        books: ResolvedField;
    } | null;
}>();

const speakerIds = defineModel<string[]>('speakerIds', { default: () => [] });
const topicIds = defineModel<string[]>('topicIds', { default: () => [] });
const bibleBookIds = defineModel<string[]>('bibleBookIds', { default: () => [] });
const demographicIds = defineModel<string[]>('demographicIds', { default: () => [] });
const ministryIds = defineModel<string[]>('ministryIds', { default: () => [] });
const seriesId = defineModel<string | null>('seriesId', { default: null });

// Merge suggested ids into a field (deduped). Named per field because refs are
// auto-unwrapped in the template — we can't pass the model ref through there.
const addTopics = (ids: string[]) => {
    topicIds.value = Array.from(new Set([...topicIds.value, ...ids]));
};
const addBooks = (ids: string[]) => {
    bibleBookIds.value = Array.from(new Set([...bibleBookIds.value, ...ids]));
};
const addAudiences = (ids: string[]) => {
    demographicIds.value = Array.from(new Set([...demographicIds.value, ...ids]));
};
</script>

<template>
    <div class="grid gap-4 sm:grid-cols-2">
        <TaxonomySelect id="tax-speakers" label="Speakers" :options="taxonomy.speakers" v-model="speakerIds" multiple placeholder="Add speakers…" />
        <TaxonomySelect id="tax-series" label="Series" :options="taxonomy.series" v-model="seriesId" placeholder="Choose a series…" />

        <div>
            <TaxonomySelect id="tax-topics" label="Topics" :options="taxonomy.topics" v-model="topicIds" multiple placeholder="Add topics…" />
            <SuggestionChips v-if="suggestions" :matched="suggestions.topics.matched" :unmatched="suggestions.topics.unmatched" @apply="addTopics" />
        </div>

        <div>
            <TaxonomySelect
                id="tax-books"
                label="Bible books"
                :options="taxonomy.bible_books"
                v-model="bibleBookIds"
                multiple
                placeholder="Add Bible books…"
            />
            <SuggestionChips v-if="suggestions" :matched="suggestions.books.matched" :unmatched="suggestions.books.unmatched" @apply="addBooks" />
        </div>

        <div>
            <TaxonomySelect
                id="tax-audiences"
                label="Audiences"
                :options="taxonomy.demographics"
                v-model="demographicIds"
                multiple
                placeholder="Add audiences…"
            />
            <SuggestionChips
                v-if="suggestions"
                :matched="suggestions.audiences.matched"
                :unmatched="suggestions.audiences.unmatched"
                @apply="addAudiences"
            />
        </div>

        <TaxonomySelect
            id="tax-ministries"
            label="Ministries"
            :options="taxonomy.ministries"
            v-model="ministryIds"
            multiple
            placeholder="Add ministries…"
        />
    </div>
</template>
