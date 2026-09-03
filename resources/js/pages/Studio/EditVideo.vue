<script setup lang="ts">
import ClassificationFields from '@/molecules/ClassificationFields.vue';
import { Badge } from '@/ui/badge';
import { Button } from '@/ui/button';
import { Input } from '@/ui/input';
import { Switch } from '@/ui/switch';
import { Head, Link, router, useForm } from '@inertiajs/vue3';
import { ArrowLeft, ChevronDown, ExternalLink, Lightbulb, Play, Plus, Trash2 } from 'lucide-vue-next';
import { computed, onBeforeUnmount, onMounted, ref } from 'vue';
import { type Enrichment, useSuggestions } from '~/composables/useSuggestions';
import { formatDuration } from '~/lib/duration';
import { getEmbedUrl } from '~/lib/embeds';

interface Option {
    id: string;
    name: string;
}
interface AlternateUrl {
    url: string;
    platform: string;
}
interface Resource {
    kind: string;
    url: string;
}

const props = defineProps<{
    video: {
        id: string;
        name: string;
        description: string;
        url: string;
        thumbnail: string | null;
        duration_seconds: number | null;
        date_recorded: string | null;
        is_livestream: boolean;
        number_in_series: number | null;
        status: 'draft' | 'published';
        alternate_urls: AlternateUrl[];
        speaker_ids: string[];
        topic_ids: string[];
        bible_book_ids: string[];
        demographic_ids: string[];
        ministry_ids: string[];
        series_id: string | null;
        related_resources: Resource[];
        enrichment: Enrichment | null;
    };
    taxonomy: {
        speakers: Option[];
        series: Option[];
        topics: Option[];
        bible_books: Option[];
        demographics: Option[];
        ministries: Option[];
    };
}>();

const v = props.video;
const form = useForm({
    name: v.name,
    description: v.description ?? '',
    url: v.url,
    thumbnail: v.thumbnail ?? '',
    duration_seconds: v.duration_seconds,
    date_recorded: v.date_recorded ?? '',
    is_livestream: v.is_livestream,
    number_in_series: v.number_in_series,
    speaker_ids: [...v.speaker_ids],
    topic_ids: [...v.topic_ids],
    bible_book_ids: [...v.bible_book_ids],
    demographic_ids: [...v.demographic_ids],
    ministry_ids: [...v.ministry_ids],
    series_id: v.series_id,
    alternate_urls: v.alternate_urls.map((a) => ({ ...a })),
    related_resources: v.related_resources.map((r) => ({ ...r })),
});

const isPublished = computed(() => props.video.status === 'published');
const embedUrl = computed(() => getEmbedUrl(form.url) || '');
const editPath = computed(() => `/studio/videos/${props.video.id}/edit`);

// --- suggestions (Epic #201) — resolved inline, shown beside their fields ---
const suggestions = useSuggestions(() => props.video.enrichment, props.taxonomy);
const classificationSuggestions = computed(() => ({
    topics: suggestions.topics.value,
    audiences: suggestions.audience.value,
    books: suggestions.books.value,
}));
const summaryDismissed = ref(false);
const showSummary = computed(() => !summaryDismissed.value && Boolean(suggestions.summary.value));

function useSummary() {
    form.description = suggestions.summary.value;
    summaryDismissed.value = true;
}

// --- preview (compact + collapsible; reference, not the main act) ----------
const previewOpen = ref(false);

// --- collapsible form sections --------------------------------------------
const sourcesOpen = ref(false);
const resourcesOpen = ref(false);

// --- alternate URLs + resources (inline row editors) ---------------------
function addAlternate() {
    form.alternate_urls.push({ url: '', platform: 'other' });
}
function removeAlternate(i: number) {
    form.alternate_urls.splice(i, 1);
}
function addResource() {
    form.related_resources.push({ kind: 'transcript', url: '' });
}
function removeResource(i: number) {
    form.related_resources.splice(i, 1);
}

// --- save + publish ------------------------------------------------------
// Status changes go through the existing set-status endpoint; Save is
// status-neutral. `allowNav` lets our own visits bypass the dirty guard.
let allowNav = false;

function save() {
    allowNav = true;
    form.post(`/studio/videos/${props.video.id}/update`, { preserveScroll: true });
}

function togglePublish() {
    allowNav = true;
    router.post(`/studio/videos/${props.video.id}/status`, {
        status: isPublished.value ? 'draft' : 'published',
        next: editPath.value,
    });
}

function regenerate() {
    allowNav = true;
    router.post(`/studio/videos/${props.video.id}/suggest`, {}, { preserveScroll: true });
}

// --- unsaved-changes guard ----------------------------------------------
const onBeforeUnload = (e: BeforeUnloadEvent) => {
    if (form.isDirty) {
        e.preventDefault();
        e.returnValue = '';
    }
};

let stopGuard: (() => void) | undefined;

onMounted(() => {
    window.addEventListener('beforeunload', onBeforeUnload);
    // Cancel in-app navigations away from a dirty form (but not our own
    // save/publish visits, which set allowNav first).
    stopGuard = router.on('before', () => {
        if (allowNav) {
            allowNav = false;
            return;
        }
        if (form.isDirty && !window.confirm('You have unsaved changes. Leave without saving?')) {
            return false;
        }
    });
});

onBeforeUnmount(() => {
    window.removeEventListener('beforeunload', onBeforeUnload);
    stopGuard?.();
});
</script>

<template>
    <Head :title="`Studio — Editing ${form.name}`" />

    <div class="mx-auto max-w-4xl px-4 py-8 lg:px-8">
        <Link
            href="/studio"
            class="text-muted-foreground hover:text-foreground focus-visible:ring-ring -ml-1 inline-flex items-center gap-1.5 rounded text-sm transition-colors outline-none focus-visible:ring-2"
        >
            <ArrowLeft class="size-4" aria-hidden="true" />
            Back to Library
        </Link>

        <!-- Header + action spine -->
        <div class="mt-3 flex flex-wrap items-center justify-between gap-4">
            <div class="flex items-center gap-3">
                <h1 class="font-display text-foreground text-2xl font-bold sm:text-3xl">Edit video</h1>
                <Badge :variant="isPublished ? 'default' : 'secondary'">{{ isPublished ? 'Published' : 'Draft' }}</Badge>
            </div>
            <div class="flex items-center gap-2">
                <Button variant="outline" @click="togglePublish">{{ isPublished ? 'Unpublish' : 'Publish' }}</Button>
                <Button :disabled="form.processing || !form.isDirty" @click="save">
                    {{ form.processing ? 'Saving…' : 'Save changes' }}
                </Button>
            </div>
        </div>

        <!-- Compact, collapsible preview (reference, not the main act) -->
        <div class="border-border mt-5 overflow-hidden rounded-xl border">
            <button
                type="button"
                class="hover:bg-muted/40 focus-visible:ring-ring flex w-full items-center gap-3 p-3 text-left transition-colors outline-none focus-visible:ring-2 focus-visible:ring-inset"
                :aria-expanded="previewOpen"
                @click="previewOpen = !previewOpen"
            >
                <div class="bg-muted relative aspect-video w-28 flex-none overflow-hidden rounded-md">
                    <img v-if="form.thumbnail" :src="form.thumbnail" alt="" class="h-full w-full object-cover" />
                    <span class="absolute inset-0 flex items-center justify-center">
                        <Play
                            class="text-muted-foreground size-5"
                            :class="form.thumbnail ? 'fill-white text-white drop-shadow' : ''"
                            aria-hidden="true"
                        />
                    </span>
                </div>
                <div class="min-w-0 flex-1">
                    <div class="text-foreground truncate font-medium">{{ form.name }}</div>
                    <div class="text-muted-foreground mt-0.5 text-sm">
                        <span v-if="form.duration_seconds" class="tabular-nums">{{ formatDuration(form.duration_seconds) }}</span>
                        <span v-if="form.duration_seconds && form.date_recorded"> · </span>
                        <span v-if="form.date_recorded">recorded {{ form.date_recorded }}</span>
                    </div>
                </div>
                <ChevronDown
                    class="text-muted-foreground size-5 flex-none transition-transform"
                    :class="previewOpen ? 'rotate-180' : ''"
                    aria-hidden="true"
                />
            </button>
            <div v-if="previewOpen" class="border-border border-t p-3">
                <div class="bg-muted aspect-video w-full overflow-hidden rounded-lg">
                    <iframe
                        v-if="embedUrl"
                        :src="embedUrl"
                        class="h-full w-full"
                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                        allowfullscreen
                        :title="form.name"
                    ></iframe>
                    <div v-else class="text-muted-foreground flex h-full items-center justify-center text-sm">No preview for this link</div>
                </div>
                <a
                    :href="props.video.url"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="text-muted-foreground hover:text-foreground mt-2 inline-flex items-center gap-1 text-sm"
                >
                    Open source <ExternalLink class="size-3.5" aria-hidden="true" />
                </a>
            </div>
        </div>

        <!-- Suggestions banner (quiet signpost; assistance lives at each field) -->
        <div class="bg-muted/40 mt-6 flex flex-wrap items-center justify-between gap-3 rounded-lg px-4 py-2.5">
            <div class="text-muted-foreground flex items-center gap-2 text-sm">
                <Lightbulb class="size-4" aria-hidden="true" />
                <span v-if="suggestions.has.value">
                    {{ suggestions.count.value }} suggestion{{ suggestions.count.value === 1 ? '' : 's' }} — shown beside the fields below
                </span>
                <span v-else>No suggestions yet for this video</span>
            </div>
            <Button v-if="suggestions.has.value" variant="ghost" size="sm" @click="regenerate">Regenerate</Button>
            <Button v-else variant="outline" size="sm" @click="regenerate">Generate suggestions</Button>
        </div>

        <!-- Details -->
        <section class="mt-8 space-y-5">
            <h2 class="text-muted-foreground text-sm font-medium">Details</h2>
            <div class="space-y-1.5">
                <label class="text-foreground block text-sm font-medium">URL</label>
                <p class="text-muted-foreground text-base tabular-nums">
                    {{ form.url }}
                </p>
            </div>
            <div class="space-y-1.5">
                <label for="edit-name" class="text-foreground block text-sm font-medium">Title</label>
                <Input id="edit-name" v-model="form.name" type="text" class="text-base" maxlength="200" />
            </div>
            <div class="space-y-1.5">
                <label for="edit-description" class="text-foreground block text-sm font-medium">Description</label>
                <textarea
                    id="edit-description"
                    v-model="form.description"
                    rows="5"
                    class="border-input bg-background focus-visible:ring-ring w-full rounded-lg border px-3 py-2 text-base outline-none focus-visible:ring-2"
                ></textarea>
                <!-- inline suggestion: AI summary, applied into the field on demand -->
                <div v-if="showSummary" class="bg-muted/40 border-border mt-2 rounded-lg border p-3">
                    <div class="text-muted-foreground flex items-center gap-1.5 text-xs">
                        <Lightbulb class="size-3.5" aria-hidden="true" /> Suggested summary
                    </div>
                    <p class="text-foreground mt-1.5 text-sm leading-relaxed">{{ suggestions.summary.value }}</p>
                    <div class="mt-2.5 flex items-center gap-2">
                        <Button variant="outline" size="sm" @click="useSummary">Use as description</Button>
                        <Button variant="ghost" size="sm" @click="summaryDismissed = true">Dismiss</Button>
                    </div>
                </div>
            </div>
            <div class="grid gap-5 sm:grid-cols-2">
                <div class="space-y-1.5">
                    <label for="edit-date" class="text-foreground block text-sm font-medium">Date recorded</label>
                    <Input id="edit-date" v-model="form.date_recorded" type="date" class="text-base" />
                </div>
                <div class="space-y-1.5">
                    <label class="text-foreground block text-sm font-medium">Runtime</label>
                    <p class="text-muted-foreground py-2 text-base tabular-nums">
                        {{ form.duration_seconds ? formatDuration(form.duration_seconds) : '—' }}
                    </p>
                </div>
                <div class="space-y-1.5">
                    <label for="edit-number" class="text-foreground block text-sm font-medium">Number in series</label>
                    <Input
                        id="edit-number"
                        :model-value="form.number_in_series ?? undefined"
                        @update:model-value="(val) => (form.number_in_series = val === '' || val == null ? null : Number(val))"
                        type="number"
                        min="1"
                        class="text-base"
                    />
                    <p class="text-muted-foreground text-xs">Episode position, for ordering within a series.</p>
                </div>
            </div>
            <div class="space-y-1.5">
                <label for="edit-thumbnail" class="text-foreground block text-sm font-medium">Thumbnail URL</label>
                <Input id="edit-thumbnail" v-model="form.thumbnail" type="url" class="text-base" />
                <img v-if="form.thumbnail" :src="form.thumbnail" alt="" class="mt-2 aspect-video w-40 rounded-lg object-cover" />
            </div>
            <label class="flex items-center gap-3">
                <Switch v-model="form.is_livestream" />
                <span class="text-foreground text-sm font-medium">This is a livestream recording</span>
            </label>
        </section>

        <div class="bg-border/60 my-7 h-px"></div>

        <!-- Classification -->
        <section class="space-y-4">
            <h2 class="text-muted-foreground text-sm font-medium">Classification</h2>
            <ClassificationFields
                :taxonomy="props.taxonomy"
                :suggestions="classificationSuggestions"
                v-model:speaker-ids="form.speaker_ids"
                v-model:topic-ids="form.topic_ids"
                v-model:bible-book-ids="form.bible_book_ids"
                v-model:demographic-ids="form.demographic_ids"
                v-model:ministry-ids="form.ministry_ids"
                v-model:series-id="form.series_id"
            />
        </section>

        <div class="bg-border/60 my-7 h-px"></div>

        <!-- Sources (collapsible) -->
        <section>
            <button
                type="button"
                class="text-foreground flex w-full items-center justify-between py-1.5 text-sm font-medium"
                :aria-expanded="sourcesOpen"
                @click="sourcesOpen = !sourcesOpen"
            >
                Sources
                <ChevronDown class="text-muted-foreground size-4 transition-transform" :class="sourcesOpen ? 'rotate-180' : ''" aria-hidden="true" />
            </button>
            <div v-show="sourcesOpen" class="mt-3 space-y-5">
                <div class="space-y-1.5">
                    <label for="edit-url" class="text-foreground block text-sm font-medium">Primary link</label>
                    <Input id="edit-url" v-model="form.url" type="url" class="text-base" />
                    <p v-if="form.errors.url" role="alert" class="text-destructive text-sm">{{ form.errors.url }}</p>
                </div>
                <div class="space-y-2">
                    <p class="text-foreground text-sm font-medium">Other places this is hosted</p>
                    <div v-for="(alt, i) in form.alternate_urls" :key="i" class="flex items-center gap-2">
                        <Input v-model="alt.url" type="url" placeholder="https://…" class="flex-1 text-base" />
                        <select v-model="alt.platform" class="border-input bg-background h-9 rounded-md border px-2 text-sm" aria-label="Platform">
                            <option value="youtube">YouTube</option>
                            <option value="vimeo">Vimeo</option>
                            <option value="other">Other</option>
                        </select>
                        <Button variant="ghost" size="icon" :aria-label="`Remove alternate link ${i + 1}`" @click="removeAlternate(i)">
                            <Trash2 class="size-4" aria-hidden="true" />
                        </Button>
                    </div>
                    <Button variant="outline" size="sm" @click="addAlternate">
                        <Plus class="size-4" aria-hidden="true" />
                        Add a link
                    </Button>
                </div>
            </div>
        </section>

        <div class="bg-border/60 my-7 h-px"></div>

        <!-- Resources (collapsible) -->
        <section>
            <button
                type="button"
                class="text-foreground flex w-full items-center justify-between py-1.5 text-sm font-medium"
                :aria-expanded="resourcesOpen"
                @click="resourcesOpen = !resourcesOpen"
            >
                Resources
                <ChevronDown
                    class="text-muted-foreground size-4 transition-transform"
                    :class="resourcesOpen ? 'rotate-180' : ''"
                    aria-hidden="true"
                />
            </button>
            <div v-show="resourcesOpen" class="mt-3 space-y-2">
                <p class="text-muted-foreground text-sm">Transcript, audio or study-material links that live on other sites.</p>
                <div v-for="(res, i) in form.related_resources" :key="i" class="flex items-center gap-2">
                    <select v-model="res.kind" class="border-input bg-background h-9 rounded-md border px-2 text-sm" aria-label="Resource type">
                        <option value="transcript">Transcript</option>
                        <option value="audio">Audio</option>
                        <option value="other">Other</option>
                    </select>
                    <Input v-model="res.url" type="url" placeholder="https://…" class="flex-1 text-base" />
                    <Button variant="ghost" size="icon" :aria-label="`Remove resource ${i + 1}`" @click="removeResource(i)">
                        <Trash2 class="size-4" aria-hidden="true" />
                    </Button>
                </div>
                <Button variant="outline" size="sm" @click="addResource">
                    <Plus class="size-4" aria-hidden="true" />
                    Add a resource
                </Button>
            </div>
        </section>

        <!-- Provenance legend -->
        <div class="border-border text-muted-foreground mt-8 flex flex-wrap gap-x-5 gap-y-2 border-t pt-4 text-xs">
            <span class="inline-flex items-center gap-1.5">
                <span class="bg-secondary border-border inline-block size-2.5 rounded-full border"></span> set — saved value
            </span>
            <span class="inline-flex items-center gap-1.5">
                <span class="border-border inline-block size-2.5 rounded-full border border-dashed"></span> suggested — review before applying
            </span>
            <span class="inline-flex items-center gap-1.5"><Plus class="size-3" aria-hidden="true" /> · new — not in your taxonomy yet</span>
        </div>
    </div>
</template>
