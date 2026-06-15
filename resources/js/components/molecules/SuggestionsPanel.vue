<script setup lang="ts">
import { Button } from '@/ui/button';
import { Lightbulb } from 'lucide-vue-next';
import { computed } from 'vue';

// A quiet editorial assist: shows stored suggestions for a video and lets the
// editor copy them into the form. Deliberately NOT branded as "AI" — church
// audiences may distrust visible AI, and these are unreviewed model output, so
// the framing is "Suggested — review before applying". Keywords are shown for
// transparency only (they already help search); they don't map to a form field.

interface Option {
    id: string;
    name: string;
}
interface Passage {
    book: string;
    label?: string;
}
interface Enrichment {
    summary: string;
    topics: string[];
    audience: string;
    bible_passages: Passage[];
    keywords: string[];
    generated_at: string | null;
}

const props = defineProps<{
    enrichment: Enrichment | null;
    taxonomy: {
        topics: Option[];
        demographics: Option[];
        bible_books: Option[];
    };
}>();

const emit = defineEmits<{
    (e: 'apply', payload: { description?: string; topic_ids?: string[]; demographic_ids?: string[]; bible_book_ids?: string[] }): void;
    (e: 'regenerate'): void;
}>();

// Resolve free-text suggestion names against existing taxonomy (case-insensitive,
// exact). We never create taxonomy from unreviewed suggestions — unmatched names
// are shown muted and simply skipped on apply.
function resolve(options: Option[], names: string[]) {
    const byName = new Map(options.map((o) => [o.name.trim().toLowerCase(), o]));
    const matched: Option[] = [];
    const unmatched: string[] = [];
    for (const raw of names) {
        const hit = byName.get(raw.trim().toLowerCase());
        if (hit) matched.push(hit);
        else unmatched.push(raw);
    }
    return { matched, unmatched };
}

const topics = computed(() => resolve(props.taxonomy.topics, props.enrichment?.topics ?? []));
const audience = computed(() => resolve(props.taxonomy.demographics, props.enrichment?.audience ? [props.enrichment.audience] : []));
const passages = computed(() =>
    resolve(
        props.taxonomy.bible_books,
        (props.enrichment?.bible_passages ?? []).map((p) => p.book),
    ),
);

const ids = (matched: Option[]) => matched.map((o) => o.id);

function applyAll() {
    const payload: { description?: string; topic_ids?: string[]; demographic_ids?: string[]; bible_book_ids?: string[] } = {};
    if (props.enrichment?.summary) payload.description = props.enrichment.summary;
    if (topics.value.matched.length) payload.topic_ids = ids(topics.value.matched);
    if (audience.value.matched.length) payload.demographic_ids = ids(audience.value.matched);
    if (passages.value.matched.length) payload.bible_book_ids = ids(passages.value.matched);
    emit('apply', payload);
}

const generatedLabel = computed(() => {
    if (!props.enrichment?.generated_at) return '';
    const d = new Date(props.enrichment.generated_at);
    return Number.isNaN(d.getTime()) ? '' : d.toLocaleDateString(undefined, { day: 'numeric', month: 'short', year: 'numeric' });
});
</script>

<template>
    <section class="bg-muted/40 rounded-xl border p-4" aria-labelledby="suggestions-heading">
        <div class="flex items-start justify-between gap-3">
            <div>
                <h2 id="suggestions-heading" class="text-foreground flex items-center gap-1.5 text-sm font-semibold">
                    <Lightbulb class="text-muted-foreground size-4" aria-hidden="true" />
                    Suggestions
                </h2>
                <p class="text-muted-foreground mt-0.5 text-xs">
                    Drawn from the title &amp; description — review before applying. Nothing is published automatically.
                </p>
            </div>
            <Button variant="ghost" size="sm" class="shrink-0" @click="emit('regenerate')">Regenerate</Button>
        </div>

        <!-- No suggestions yet -->
        <div v-if="!enrichment" class="mt-3 flex items-center justify-between gap-3">
            <p class="text-muted-foreground text-sm">No suggestions yet for this video.</p>
            <Button variant="outline" size="sm" @click="emit('regenerate')">Generate suggestions</Button>
        </div>

        <div v-else class="mt-3 space-y-4">
            <!-- Summary -->
            <div v-if="enrichment.summary" class="space-y-1.5">
                <div class="flex items-center justify-between gap-2">
                    <span class="text-foreground text-xs font-medium">Summary</span>
                    <Button variant="outline" size="sm" @click="emit('apply', { description: enrichment.summary })">Use as description</Button>
                </div>
                <p class="text-muted-foreground text-sm">{{ enrichment.summary }}</p>
            </div>

            <!-- Topics -->
            <div v-if="enrichment.topics.length" class="space-y-1.5">
                <div class="flex items-center justify-between gap-2">
                    <span class="text-foreground text-xs font-medium">Topics</span>
                    <Button variant="outline" size="sm" :disabled="!topics.matched.length" @click="emit('apply', { topic_ids: ids(topics.matched) })">
                        Add {{ topics.matched.length }} topic{{ topics.matched.length === 1 ? '' : 's' }}
                    </Button>
                </div>
                <div class="flex flex-wrap gap-1.5">
                    <span v-for="o in topics.matched" :key="`t-${o.id}`" class="bg-background rounded-full border px-2 py-0.5 text-xs">{{
                        o.name
                    }}</span>
                    <span
                        v-for="(name, i) in topics.unmatched"
                        :key="`tu-${i}`"
                        class="text-muted-foreground rounded-full border border-dashed px-2 py-0.5 text-xs"
                        title="Not in your topics — won't be added"
                        >{{ name }}</span
                    >
                </div>
            </div>

            <!-- Audience -->
            <div v-if="enrichment.audience" class="space-y-1.5">
                <div class="flex items-center justify-between gap-2">
                    <span class="text-foreground text-xs font-medium">Audience</span>
                    <Button
                        variant="outline"
                        size="sm"
                        :disabled="!audience.matched.length"
                        @click="emit('apply', { demographic_ids: ids(audience.matched) })"
                    >
                        Apply
                    </Button>
                </div>
                <div class="flex flex-wrap gap-1.5">
                    <span v-for="o in audience.matched" :key="`a-${o.id}`" class="bg-background rounded-full border px-2 py-0.5 text-xs">{{
                        o.name
                    }}</span>
                    <span
                        v-for="(name, i) in audience.unmatched"
                        :key="`au-${i}`"
                        class="text-muted-foreground rounded-full border border-dashed px-2 py-0.5 text-xs"
                        title="No matching audience — won't be added"
                        >{{ name }}</span
                    >
                </div>
            </div>

            <!-- Bible passages -->
            <div v-if="enrichment.bible_passages.length" class="space-y-1.5">
                <div class="flex items-center justify-between gap-2">
                    <span class="text-foreground text-xs font-medium">Bible passages</span>
                    <Button
                        variant="outline"
                        size="sm"
                        :disabled="!passages.matched.length"
                        @click="emit('apply', { bible_book_ids: ids(passages.matched) })"
                    >
                        Add {{ passages.matched.length }} book{{ passages.matched.length === 1 ? '' : 's' }}
                    </Button>
                </div>
                <div class="flex flex-wrap gap-1.5">
                    <span
                        v-for="p in enrichment.bible_passages"
                        :key="`p-${p.label ?? p.book}`"
                        class="bg-background rounded-full border px-2 py-0.5 text-xs"
                    >
                        {{ p.label ?? p.book }}
                    </span>
                </div>
            </div>

            <!-- Keywords (display only) -->
            <div v-if="enrichment.keywords.length" class="space-y-1.5">
                <span class="text-foreground text-xs font-medium">Keywords</span>
                <p class="text-muted-foreground text-xs">Already used to improve search — no action needed.</p>
                <div class="flex flex-wrap gap-1.5">
                    <span
                        v-for="(k, i) in enrichment.keywords"
                        :key="`k-${i}`"
                        class="text-muted-foreground rounded-full border border-dashed px-2 py-0.5 text-xs"
                        >{{ k }}</span
                    >
                </div>
            </div>

            <div class="flex items-center justify-between gap-3 border-t pt-3">
                <span v-if="generatedLabel" class="text-muted-foreground text-xs">Generated {{ generatedLabel }}</span>
                <Button size="sm" @click="applyAll">Apply all</Button>
            </div>
        </div>
    </section>
</template>
