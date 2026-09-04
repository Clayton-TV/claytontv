import { computed, type MaybeRefOrGetter, toValue } from 'vue';

export interface SuggestionOption {
    id: string;
    name: string;
}

export interface Enrichment {
    summary: string;
    topics: string[];
    audience: string;
    bible_passages: { book: string; label?: string }[];
    keywords: string[];
    generated_at: string | null;
}

export interface SuggestionTaxonomy {
    topics: SuggestionOption[];
    demographics: SuggestionOption[];
    bible_books: SuggestionOption[];
}

export interface ResolvedField {
    matched: SuggestionOption[];
    unmatched: string[];
}

// Resolve free-text suggestion names against existing taxonomy (case-insensitive,
// exact). Matched names map to real options the editor can add; unmatched names
// are surfaced as "new" hints — we never create taxonomy from unreviewed output.
function resolve(options: SuggestionOption[], names: string[]): ResolvedField {
    const byName = new Map(options.map((o) => [o.name.trim().toLowerCase(), o]));
    const matched: SuggestionOption[] = [];
    const unmatched: string[] = [];
    for (const raw of names) {
        const hit = byName.get(raw.trim().toLowerCase());
        if (hit) {
            if (!matched.some((m) => m.id === hit.id)) matched.push(hit);
        } else {
            unmatched.push(raw);
        }
    }
    return { matched, unmatched };
}

const hasItems = (f: ResolvedField) => f.matched.length > 0 || f.unmatched.length > 0;

/**
 * Derive the inline editor suggestions from a video's stored enrichment, resolved
 * against the current taxonomy. `enrichment` is reactive (a ref or getter) so the
 * suggestions update after a regenerate reloads the prop.
 */
export function useSuggestions(enrichment: MaybeRefOrGetter<Enrichment | null>, taxonomy: SuggestionTaxonomy) {
    const current = computed(() => toValue(enrichment));

    const summary = computed(() => current.value?.summary ?? '');
    const topics = computed(() => resolve(taxonomy.topics, current.value?.topics ?? []));
    const audience = computed(() => resolve(taxonomy.demographics, current.value?.audience ? [current.value.audience] : []));
    const books = computed(() =>
        resolve(
            taxonomy.bible_books,
            (current.value?.bible_passages ?? []).map((p) => p.book),
        ),
    );
    const keywords = computed(() => current.value?.keywords ?? []);
    const generatedAt = computed(() => current.value?.generated_at ?? null);

    const has = computed(() => current.value !== null);
    // A field-level count for the page banner: how many fields carry a suggestion.
    const count = computed(
        () => (summary.value ? 1 : 0) + (hasItems(topics.value) ? 1 : 0) + (hasItems(audience.value) ? 1 : 0) + (hasItems(books.value) ? 1 : 0),
    );

    return { summary, topics, audience, books, keywords, generatedAt, has, count };
}
