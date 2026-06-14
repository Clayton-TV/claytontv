<script setup lang="ts">
import TaxonomySelect from '@/molecules/TaxonomySelect.vue';

/**
 * The shared classification grid: speakers · series · topics · Bible books ·
 * audiences · ministries, each a searchable {@link TaxonomySelect}. Used by both
 * the Add-a-video form and the editor so the two stay in lockstep. Series is
 * single-select (one series per video); the rest are multi.
 */

interface Option {
    id: string;
    name: string;
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
}>();

const speakerIds = defineModel<string[]>('speakerIds', { default: () => [] });
const topicIds = defineModel<string[]>('topicIds', { default: () => [] });
const bibleBookIds = defineModel<string[]>('bibleBookIds', { default: () => [] });
const demographicIds = defineModel<string[]>('demographicIds', { default: () => [] });
const ministryIds = defineModel<string[]>('ministryIds', { default: () => [] });
const seriesId = defineModel<string | null>('seriesId', { default: null });
</script>

<template>
    <div class="grid gap-4 sm:grid-cols-2">
        <TaxonomySelect id="tax-speakers" label="Speakers" :options="taxonomy.speakers" v-model="speakerIds" multiple placeholder="Add speakers…" />
        <TaxonomySelect id="tax-series" label="Series" :options="taxonomy.series" v-model="seriesId" placeholder="Choose a series…" />
        <TaxonomySelect id="tax-topics" label="Topics" :options="taxonomy.topics" v-model="topicIds" multiple placeholder="Add topics…" />
        <TaxonomySelect
            id="tax-books"
            label="Bible books"
            :options="taxonomy.bible_books"
            v-model="bibleBookIds"
            multiple
            placeholder="Add Bible books…"
        />
        <TaxonomySelect
            id="tax-audiences"
            label="Audiences"
            :options="taxonomy.demographics"
            v-model="demographicIds"
            multiple
            placeholder="Add audiences…"
        />
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
