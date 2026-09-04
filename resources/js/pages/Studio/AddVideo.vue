<script setup lang="ts">
import ClassificationFields from '@/molecules/ClassificationFields.vue';
import { Button } from '@/ui/button';
import { Input } from '@/ui/input';
import { Head, Link, useForm } from '@inertiajs/vue3';
import { useDebounceFn } from '@vueuse/core';
import { ArrowLeft, CircleAlert, LoaderCircle } from 'lucide-vue-next';
import { computed, ref, watch } from 'vue';
import { getCsrfToken } from '~/lib/csrf';
import { formatDuration } from '~/lib/duration';

interface Option {
    id: string;
    name: string;
}

const props = defineProps<{
    taxonomy: {
        speakers: Option[];
        series: Option[];
        topics: Option[];
        bible_books: Option[];
        demographics: Option[];
        ministries: Option[];
    };
}>();

// One form for the whole intake. Metadata fetch fills the descriptive fields;
// the editor confirms/edits and classifies, then saves as draft or publishes.
const form = useForm<{
    url: string;
    name: string;
    description: string;
    thumbnail: string;
    duration_seconds: number | null;
    date_recorded: string;
    status: 'draft' | 'published';
    speaker_ids: string[];
    topic_ids: string[];
    bible_book_ids: string[];
    demographic_ids: string[];
    ministry_ids: string[];
    series_id: string | null;
}>({
    url: '',
    name: '',
    description: '',
    thumbnail: '',
    duration_seconds: null,
    date_recorded: '',
    status: 'draft',
    speaker_ids: [],
    topic_ids: [],
    bible_book_ids: [],
    demographic_ids: [],
    ministry_ids: [],
    series_id: null,
});

// --- metadata preview (fetched as the editor pastes) ---------------------
interface Preview {
    platform: string;
    thumbnail: string | null;
    duration_seconds: number | null;
    date_recorded: string | null;
}

const fetching = ref(false);
const fetchError = ref('');
const preview = ref<Preview | null>(null);
const duplicate = ref<{ id: string; name: string } | null>(null);

async function fetchMetadata() {
    const url = form.url.trim();
    if (!url) {
        preview.value = null;
        fetchError.value = '';
        duplicate.value = null;
        return;
    }
    fetching.value = true;
    fetchError.value = '';
    try {
        const res = await fetch('/studio/api/fetch-metadata', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-XSRF-TOKEN': getCsrfToken() },
            body: JSON.stringify({ url }),
        });
        const data = await res.json();
        if (!data.ok) {
            fetchError.value = data.error || 'Could not read that video.';
            preview.value = null;
            duplicate.value = null;
            return;
        }
        const m = data.metadata;
        form.name = m.name || '';
        form.description = m.description || '';
        form.thumbnail = m.thumbnail || '';
        form.duration_seconds = m.duration_seconds ?? null;
        form.date_recorded = m.date_recorded || '';
        form.url = m.url || url; // canonical form
        preview.value = m;
        duplicate.value = data.duplicate;
    } catch {
        fetchError.value = 'Something went wrong fetching that video. Check the link and try again.';
        preview.value = null;
    } finally {
        fetching.value = false;
    }
}

const debouncedFetch = useDebounceFn(fetchMetadata, 600);
watch(() => form.url, debouncedFetch);

// --- save ----------------------------------------------------------------
const canSave = computed(() => !!preview.value && !!form.name.trim() && !duplicate.value);

function save(status: 'draft' | 'published') {
    form.status = status;
    form.post('/studio/videos/create', { preserveScroll: true });
}

const recordedLabel = computed(() => (preview.value?.date_recorded ? preview.value.date_recorded : null));
</script>

<template>
    <Head title="Studio — Add a video" />

    <div class="mx-auto max-w-3xl px-4 py-8 lg:px-8">
        <Link
            href="/studio"
            class="text-muted-foreground hover:text-foreground focus-visible:ring-ring -ml-1 inline-flex items-center gap-1.5 rounded text-sm transition-colors outline-none focus-visible:ring-2"
        >
            <ArrowLeft class="size-4" aria-hidden="true" />
            Back to Library
        </Link>

        <h1 class="font-display text-foreground mt-3 text-2xl font-bold sm:text-3xl">Add a video</h1>
        <p class="text-muted-foreground mt-1 text-sm">
            Paste a YouTube or Vimeo link and we'll fetch the details. Review, classify, then save. Got several?
            <Link href="/studio/bulk" class="text-primary hover:underline">Add a batch or a playlist</Link>.
        </p>

        <!-- Step 1: the URL -->
        <div class="mt-8 space-y-1.5">
            <label for="video-url" class="text-foreground block text-sm font-medium">Video link</label>
            <div class="relative">
                <Input
                    id="video-url"
                    v-model="form.url"
                    type="url"
                    inputmode="url"
                    placeholder="https://www.youtube.com/watch?v=…"
                    class="pr-10 text-base"
                    autofocus
                    :aria-invalid="!!fetchError || undefined"
                />
                <LoaderCircle
                    v-if="fetching"
                    class="text-muted-foreground absolute top-1/2 right-3 size-4 -translate-y-1/2 animate-spin motion-reduce:animate-none"
                    aria-label="Fetching"
                />
            </div>
            <p v-if="fetchError" role="alert" class="text-destructive flex items-center gap-1.5 text-sm">
                <CircleAlert class="size-4 shrink-0" aria-hidden="true" />
                {{ fetchError }}
            </p>
            <p v-if="form.errors.url" role="alert" class="text-destructive flex items-center gap-1.5 text-sm">
                <CircleAlert class="size-4 shrink-0" aria-hidden="true" />
                {{ form.errors.url }}
            </p>
        </div>

        <!-- Duplicate warning -->
        <div v-if="duplicate" class="border-destructive/40 bg-destructive/10 mt-4 flex items-start gap-3 rounded-lg border p-4">
            <CircleAlert class="text-destructive mt-0.5 size-5 shrink-0" aria-hidden="true" />
            <div class="text-sm">
                <p class="text-foreground font-medium">This video is already in the library.</p>
                <Link :href="`/video/${duplicate.id}`" class="text-primary hover:underline"> Open “{{ duplicate.name }}” </Link>
            </div>
        </div>

        <!-- Step 2: preview + edit (once fetched, no dup) -->
        <div v-if="preview && !duplicate" class="mt-8 space-y-6">
            <!-- Preview card -->
            <div class="border-border bg-card flex gap-4 rounded-xl border p-4">
                <div class="bg-muted relative aspect-video w-40 shrink-0 overflow-hidden rounded-lg">
                    <img v-if="form.thumbnail" :src="form.thumbnail" alt="" class="h-full w-full object-cover" loading="lazy" />
                    <span
                        v-if="form.duration_seconds"
                        class="bg-background/80 text-foreground absolute right-1 bottom-1 rounded px-1.5 py-0.5 text-xs font-medium tabular-nums"
                    >
                        {{ formatDuration(form.duration_seconds) }}
                    </span>
                </div>
                <div class="min-w-0 flex-1 text-sm">
                    <span class="text-muted-foreground text-xs tracking-wide uppercase">{{ preview.platform }}</span>
                    <p class="text-foreground mt-0.5 line-clamp-2 font-medium">{{ form.name || 'Untitled' }}</p>
                    <p v-if="recordedLabel" class="text-muted-foreground mt-1 tabular-nums">Recorded {{ recordedLabel }}</p>
                </div>
            </div>

            <!-- Title + description -->
            <div class="space-y-1.5">
                <label for="video-name" class="text-foreground block text-sm font-medium">Title</label>
                <Input id="video-name" v-model="form.name" type="text" class="text-base" maxlength="200" />
            </div>

            <div class="space-y-1.5">
                <label for="video-description" class="text-foreground block text-sm font-medium">Description</label>
                <textarea
                    id="video-description"
                    v-model="form.description"
                    rows="4"
                    class="border-input bg-background focus-visible:ring-ring w-full rounded-lg border px-3 py-2 text-base outline-none focus-visible:ring-2"
                ></textarea>
            </div>

            <!-- Classification -->
            <fieldset class="space-y-4">
                <legend class="text-foreground text-base font-semibold">Classification</legend>
                <p class="text-muted-foreground -mt-2 text-sm">All optional — you can refine these later.</p>
                <ClassificationFields
                    :taxonomy="props.taxonomy"
                    v-model:speaker-ids="form.speaker_ids"
                    v-model:topic-ids="form.topic_ids"
                    v-model:bible-book-ids="form.bible_book_ids"
                    v-model:demographic-ids="form.demographic_ids"
                    v-model:ministry-ids="form.ministry_ids"
                    v-model:series-id="form.series_id"
                />
            </fieldset>

            <!-- Actions -->
            <div class="flex flex-wrap items-center gap-3 border-t pt-6">
                <Button :disabled="!canSave || form.processing" @click="save('published')">
                    {{ form.processing && form.status === 'published' ? 'Publishing…' : 'Publish' }}
                </Button>
                <Button variant="outline" :disabled="!canSave || form.processing" @click="save('draft')">
                    {{ form.processing && form.status === 'draft' ? 'Saving…' : 'Save as draft' }}
                </Button>
                <span class="text-muted-foreground text-sm">Drafts stay hidden from the public site until published.</span>
            </div>
        </div>
    </div>
</template>
