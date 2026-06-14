<script setup lang="ts">
import EmptyState from '@/molecules/EmptyState.vue';
import PaginationNav from '@/molecules/PaginationNav.vue';
import { Badge } from '@/ui/badge';
import { Button } from '@/ui/button';
import { Checkbox } from '@/ui/checkbox';
import {
    Dialog,
    DialogClose,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from '@/ui/dialog';
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from '@/ui/dropdown-menu';
import { Input } from '@/ui/input';
import { Skeleton } from '@/ui/skeleton';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/ui/table';
import { Head, router } from '@inertiajs/vue3';
import { useDebounceFn } from '@vueuse/core';
import { ExternalLink, Film, MoreHorizontal, Pencil, Plus, Search } from 'lucide-vue-next';
import { computed, ref, watch } from 'vue';
import { formatDuration } from '~/lib/duration';

// The strict Inertia encoder hands us plain dicts only (app/studio/services.py).
interface VideoRow {
    id: string;
    name: string;
    thumbnail: string | null;
    speakers: string[];
    series: string | null;
    date: string | null;
    status: 'draft' | 'published';
    duration_seconds: number | null;
}

const props = defineProps<{
    videos: VideoRow[];
    q: string;
    status: 'all' | 'draft' | 'published';
    total: number;
    page: number;
    num_pages: number;
    has_prev_page: boolean;
    has_next_page: boolean;
}>();

// --- filters: search (debounced) + status -------------------------------
const search = ref(props.q);
// While a partial reload is in flight we show a skeleton row block.
const loading = ref(false);

// Re-fetch only the list-shaped props, preserving scroll + form state so the
// page doesn't jump and the input keeps focus.
function reload(params: Record<string, string>) {
    loading.value = true;
    router.get('/studio/', params, {
        only: ['videos', 'q', 'status', 'total', 'page', 'num_pages', 'has_prev_page', 'has_next_page'],
        preserveState: true,
        preserveScroll: true,
        replace: true,
        onFinish: () => (loading.value = false),
    });
}

// The query string for a given (search, status) pair — the single place we
// decide which params survive a reload (omit defaults to keep URLs clean).
const buildParams = (status: 'all' | 'draft' | 'published') => {
    const params: Record<string, string> = {};
    if (search.value.trim()) params.q = search.value.trim();
    if (status !== 'all') params.status = status;
    return params;
};

const runSearch = useDebounceFn(() => reload(buildParams(props.status)), 300);

watch(search, () => runSearch());

const statusFilters = [
    { value: 'all', label: 'All' },
    { value: 'published', label: 'Published' },
    { value: 'draft', label: 'Drafts' },
] as const;

function setStatusFilter(value: 'all' | 'draft' | 'published') {
    if (value === props.status) return;
    reload(buildParams(value));
}

// Keep `next` (the redirect target after a mutation) on the current filters so
// editors stay where they were after publishing/deleting.
const nextTarget = computed(() => {
    const qs = new URLSearchParams(buildParams(props.status));
    if (props.page > 1) qs.set('page', String(props.page));
    const s = qs.toString();
    return s ? `/studio/?${s}` : '/studio/';
});

// --- row selection -------------------------------------------------------
const selected = ref<Set<string>>(new Set());

// Drop selections that are no longer on the page after a reload.
watch(
    () => props.videos,
    (rows) => {
        const ids = new Set(rows.map((r) => r.id));
        selected.value = new Set([...selected.value].filter((id) => ids.has(id)));
    },
);

const allSelected = computed(() => props.videos.length > 0 && props.videos.every((v) => selected.value.has(v.id)));
const someSelected = computed(() => selected.value.size > 0 && !allSelected.value);
const headerState = computed<boolean | 'indeterminate'>(() => (someSelected.value ? 'indeterminate' : allSelected.value));

function toggleAll(value: boolean | 'indeterminate') {
    selected.value = value === true ? new Set(props.videos.map((v) => v.id)) : new Set();
}

function toggleRow(id: string, value: boolean | 'indeterminate') {
    const next = new Set(selected.value);
    if (value === true) next.add(id);
    else next.delete(id);
    selected.value = next;
}

const selectedIds = computed(() => [...selected.value]);

// --- mutations -----------------------------------------------------------
const confirmingDelete = ref(false);

function postMutation(url: string, data: Record<string, unknown>) {
    router.post(
        url,
        { ...data, next: nextTarget.value },
        {
            preserveScroll: true,
            onSuccess: () => (selected.value = new Set()),
        },
    );
}

function setRowStatus(id: string, status: 'draft' | 'published') {
    postMutation(`/studio/videos/${id}/status`, { status });
}

function bulkStatus(status: 'draft' | 'published') {
    if (!selectedIds.value.length) return;
    postMutation('/studio/videos/bulk-status', { status, ids: selectedIds.value });
}

function confirmDelete() {
    postMutation('/studio/videos/delete', { ids: selectedIds.value });
    confirmingDelete.value = false;
}

const resultLabel = computed(() => {
    const n = props.total;
    const noun = n === 1 ? 'video' : 'videos';
    if (props.q) return `${n} ${noun} matching “${props.q}”`;
    if (props.status === 'draft') return `${n} draft ${n === 1 ? 'video' : 'videos'}`;
    if (props.status === 'published') return `${n} published ${noun}`;
    return `${n} ${noun}`;
});
</script>

<template>
    <Head title="Studio — Library" />

    <div class="mx-auto max-w-6xl px-4 py-8 lg:px-8">
        <!-- Header -->
        <div class="flex flex-wrap items-start justify-between gap-4">
            <div>
                <h1 class="font-display text-foreground text-2xl font-bold sm:text-3xl">Studio — Library</h1>
                <p class="text-muted-foreground mt-1 text-sm tabular-nums">{{ resultLabel }}</p>
            </div>
            <!-- Add a video lands in Slice 3 -->
            <Button disabled title="Coming in the next slice" class="cursor-not-allowed">
                <Plus class="size-4" aria-hidden="true" />
                Add a video
            </Button>
        </div>

        <!-- Filter bar -->
        <div class="mt-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div class="relative w-full sm:max-w-xs">
                <Search class="text-muted-foreground pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2" aria-hidden="true" />
                <label class="sr-only" for="library-search">Search videos</label>
                <Input
                    id="library-search"
                    v-model="search"
                    type="search"
                    placeholder="Search videos…"
                    class="pl-9 text-base"
                />
            </div>

            <div class="inline-flex rounded-lg border p-0.5" role="group" aria-label="Filter by status">
                <button
                    v-for="filter in statusFilters"
                    :key="filter.value"
                    type="button"
                    @click="setStatusFilter(filter.value)"
                    :aria-pressed="props.status === filter.value"
                    :class="[
                        'focus-visible:ring-ring rounded-md px-3 py-1.5 text-sm font-medium transition-colors outline-none focus-visible:ring-2',
                        props.status === filter.value ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:text-foreground',
                    ]"
                >
                    {{ filter.label }}
                </button>
            </div>
        </div>

        <!-- Bulk action bar -->
        <div
            v-if="selectedIds.length"
            class="border-border bg-card mt-4 flex flex-wrap items-center gap-3 rounded-lg border px-4 py-3 shadow-sm"
        >
            <span class="text-foreground text-sm font-medium tabular-nums">{{ selectedIds.length }} selected</span>
            <div class="ml-auto flex flex-wrap gap-2">
                <Button size="sm" variant="outline" @click="bulkStatus('published')">Publish</Button>
                <Button size="sm" variant="outline" @click="bulkStatus('draft')">Unpublish</Button>
                <Button size="sm" variant="destructive" @click="confirmingDelete = true">Delete</Button>
            </div>
        </div>

        <!-- Table -->
        <div class="border-border mt-4 overflow-hidden rounded-xl border">
            <Table>
                <TableHeader>
                    <TableRow class="bg-muted/40">
                        <TableHead class="w-10">
                            <Checkbox
                                :model-value="headerState"
                                @update:model-value="toggleAll"
                                aria-label="Select all videos on this page"
                            />
                        </TableHead>
                        <TableHead class="w-20">Thumbnail</TableHead>
                        <TableHead>Title</TableHead>
                        <TableHead class="hidden md:table-cell">Speaker</TableHead>
                        <TableHead class="hidden lg:table-cell">Series</TableHead>
                        <TableHead class="hidden sm:table-cell">Date</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead class="hidden sm:table-cell">Runtime</TableHead>
                        <TableHead class="w-10"><span class="sr-only">Actions</span></TableHead>
                    </TableRow>
                </TableHeader>

                <TableBody v-if="loading">
                    <TableRow v-for="n in 6" :key="`skeleton-${n}`">
                        <TableCell><Skeleton class="size-4" /></TableCell>
                        <TableCell><Skeleton class="h-9 w-16 rounded" /></TableCell>
                        <TableCell><Skeleton class="h-4 w-48" /></TableCell>
                        <TableCell class="hidden md:table-cell"><Skeleton class="h-4 w-24" /></TableCell>
                        <TableCell class="hidden lg:table-cell"><Skeleton class="h-4 w-24" /></TableCell>
                        <TableCell class="hidden sm:table-cell"><Skeleton class="h-4 w-20" /></TableCell>
                        <TableCell><Skeleton class="h-5 w-16 rounded-md" /></TableCell>
                        <TableCell class="hidden sm:table-cell"><Skeleton class="h-4 w-12" /></TableCell>
                        <TableCell><Skeleton class="size-6 rounded" /></TableCell>
                    </TableRow>
                </TableBody>

                <TableBody v-else-if="videos.length">
                    <TableRow v-for="video in videos" :key="video.id" :data-state="selected.has(video.id) ? 'selected' : undefined">
                        <TableCell>
                            <Checkbox
                                :model-value="selected.has(video.id)"
                                @update:model-value="(v: boolean | 'indeterminate') => toggleRow(video.id, v)"
                                :aria-label="`Select ${video.name}`"
                            />
                        </TableCell>
                        <TableCell>
                            <div class="bg-muted aspect-video w-16 overflow-hidden rounded">
                                <img
                                    v-if="video.thumbnail"
                                    :src="video.thumbnail"
                                    alt=""
                                    loading="lazy"
                                    class="h-full w-full object-cover"
                                />
                            </div>
                        </TableCell>
                        <TableCell class="max-w-xs">
                            <span class="text-foreground line-clamp-2 font-medium whitespace-normal">{{ video.name }}</span>
                        </TableCell>
                        <TableCell class="text-muted-foreground hidden md:table-cell">
                            {{ video.speakers.length ? video.speakers.join(', ') : '—' }}
                        </TableCell>
                        <TableCell class="text-muted-foreground hidden lg:table-cell">{{ video.series ?? '—' }}</TableCell>
                        <TableCell class="text-muted-foreground hidden tabular-nums sm:table-cell">{{ video.date ?? '—' }}</TableCell>
                        <TableCell>
                            <Badge
                                variant="outline"
                                :class="
                                    video.status === 'published'
                                        ? 'border-emerald-500/30 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400'
                                        : 'border-amber-500/30 bg-amber-500/10 text-amber-600 dark:text-amber-400'
                                "
                            >
                                {{ video.status === 'published' ? 'Published' : 'Draft' }}
                            </Badge>
                        </TableCell>
                        <TableCell class="text-muted-foreground hidden tabular-nums sm:table-cell">
                            {{ formatDuration(video.duration_seconds) || '—' }}
                        </TableCell>
                        <TableCell>
                            <DropdownMenu>
                                <DropdownMenuTrigger as-child>
                                    <Button variant="ghost" size="icon" :aria-label="`Actions for ${video.name}`">
                                        <MoreHorizontal class="size-4" aria-hidden="true" />
                                    </Button>
                                </DropdownMenuTrigger>
                                <DropdownMenuContent align="end">
                                    <DropdownMenuItem v-if="video.status === 'draft'" @click="setRowStatus(video.id, 'published')">
                                        Publish
                                    </DropdownMenuItem>
                                    <DropdownMenuItem v-else @click="setRowStatus(video.id, 'draft')">Unpublish</DropdownMenuItem>
                                    <DropdownMenuSeparator />
                                    <DropdownMenuItem as-child>
                                        <a :href="`/video/${video.id}`" target="_blank" rel="noopener">
                                            <ExternalLink class="size-4" aria-hidden="true" />
                                            Open on site
                                        </a>
                                    </DropdownMenuItem>
                                    <DropdownMenuItem disabled>
                                        <Pencil class="size-4" aria-hidden="true" />
                                        Edit (coming soon)
                                    </DropdownMenuItem>
                                </DropdownMenuContent>
                            </DropdownMenu>
                        </TableCell>
                    </TableRow>
                </TableBody>
            </Table>

            <!-- Empty state lives outside the table so it spans full width -->
            <div v-if="!loading && !videos.length" class="p-2">
                <EmptyState
                    :icon="Film"
                    title="No videos here"
                    :message="
                        q
                            ? `Nothing matches “${q}”. Try a different search.`
                            : status === 'draft'
                              ? 'No drafts waiting. New imports will land here.'
                              : 'No videos yet.'
                    "
                />
            </div>
        </div>

        <div class="mt-8">
            <PaginationNav :has-prev-page="has_prev_page" :has-next-page="has_next_page" />
        </div>
    </div>

    <!-- Delete confirmation -->
    <Dialog v-model:open="confirmingDelete">
        <DialogContent class="max-w-md">
            <DialogHeader>
                <DialogTitle>Delete {{ selectedIds.length }} {{ selectedIds.length === 1 ? 'video' : 'videos' }}?</DialogTitle>
                <DialogDescription>
                    This permanently removes {{ selectedIds.length === 1 ? 'it' : 'them' }} from the catalogue. This can’t be undone.
                </DialogDescription>
            </DialogHeader>
            <DialogFooter>
                <DialogClose as-child>
                    <Button variant="outline">Cancel</Button>
                </DialogClose>
                <Button variant="destructive" @click="confirmDelete">Delete</Button>
            </DialogFooter>
        </DialogContent>
    </Dialog>
</template>
