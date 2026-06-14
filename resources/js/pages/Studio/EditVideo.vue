<script setup lang="ts">
import ClassificationFields from '@/molecules/ClassificationFields.vue';
import { Badge } from '@/ui/badge';
import { Button } from '@/ui/button';
import { Input } from '@/ui/input';
import { Switch } from '@/ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/ui/tabs';
import { Head, Link, router, useForm } from '@inertiajs/vue3';
import { ArrowLeft, ExternalLink, Plus, Trash2 } from 'lucide-vue-next';
import { computed, onBeforeUnmount, onMounted } from 'vue';
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

        <!-- Header + actions -->
        <div class="mt-3 flex flex-wrap items-start justify-between gap-4">
            <div class="min-w-0">
                <div class="flex items-center gap-3">
                    <h1 class="font-display text-foreground truncate text-2xl font-bold sm:text-3xl">Edit video</h1>
                    <Badge :variant="isPublished ? 'default' : 'secondary'">{{ isPublished ? 'Published' : 'Draft' }}</Badge>
                </div>
                <a
                    :href="props.video.url"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="text-muted-foreground hover:text-foreground mt-1 inline-flex items-center gap-1 text-sm"
                >
                    Open source <ExternalLink class="size-3.5" aria-hidden="true" />
                </a>
            </div>
            <div class="flex items-center gap-2">
                <Button variant="outline" @click="togglePublish">{{ isPublished ? 'Unpublish' : 'Publish' }}</Button>
                <Button :disabled="form.processing || !form.isDirty" @click="save">
                    {{ form.processing ? 'Saving…' : 'Save' }}
                </Button>
            </div>
        </div>

        <!-- Live preview -->
        <div class="bg-muted relative mt-6 aspect-video w-full overflow-hidden rounded-xl">
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

        <Tabs default-value="details" class="mt-6">
            <TabsList class="w-full sm:w-auto">
                <TabsTrigger value="details">Details</TabsTrigger>
                <TabsTrigger value="classification">Classification</TabsTrigger>
                <TabsTrigger value="sources">Sources</TabsTrigger>
                <TabsTrigger value="resources">Resources</TabsTrigger>
            </TabsList>

            <!-- Details -->
            <TabsContent value="details" class="space-y-5">
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
            </TabsContent>

            <!-- Classification -->
            <TabsContent value="classification">
                <ClassificationFields
                    :taxonomy="props.taxonomy"
                    v-model:speaker-ids="form.speaker_ids"
                    v-model:topic-ids="form.topic_ids"
                    v-model:bible-book-ids="form.bible_book_ids"
                    v-model:demographic-ids="form.demographic_ids"
                    v-model:ministry-ids="form.ministry_ids"
                    v-model:series-id="form.series_id"
                />
            </TabsContent>

            <!-- Sources -->
            <TabsContent value="sources" class="space-y-5">
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
            </TabsContent>

            <!-- Resources -->
            <TabsContent value="resources" class="space-y-2">
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
            </TabsContent>
        </Tabs>
    </div>
</template>
