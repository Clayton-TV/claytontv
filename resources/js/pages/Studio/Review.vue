<script setup lang="ts">
import EmptyState from '@/molecules/EmptyState.vue';
import PaginationNav from '@/molecules/PaginationNav.vue';
import { Button } from '@/ui/button';
import { Checkbox } from '@/ui/checkbox';
import { Dialog, DialogClose, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/ui/dialog';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/ui/table';
import { Head, Link, router } from '@inertiajs/vue3';
import { ArrowLeft, Check, CircleCheckBig, Film, Pencil, Trash2 } from 'lucide-vue-next';
import { computed, ref, watch } from 'vue';
import { formatDuration } from '~/lib/duration';

// Plain dicts from app/studio/services.list_videos (drafts only).
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
    total: number;
    page: number;
    num_pages: number;
    has_prev_page: boolean;
    has_next_page: boolean;
    page_range: string[];
}>();

const nextTarget = computed(() => (props.page > 1 ? `/studio/review?page=${props.page}` : '/studio/review'));

// --- selection (for bulk approve) ----------------------------------------
const selected = ref<Set<string>>(new Set());
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

// --- mutations (reuse the Library endpoints) -----------------------------
function post(url: string, data: Record<string, unknown>) {
    router.post(url, { ...data, next: nextTarget.value }, { preserveScroll: true, onSuccess: () => (selected.value = new Set()) });
}
function approve(id: string) {
    post(`/studio/videos/${id}/status`, { status: 'published' });
}
function approveSelected() {
    if (selectedIds.value.length) post('/studio/videos/bulk-status', { status: 'published', ids: selectedIds.value });
}

// Reject = soft delete, behind a confirm.
const rejecting = ref<VideoRow | null>(null);
function confirmReject() {
    if (rejecting.value) post('/studio/videos/delete', { ids: [rejecting.value.id] });
    rejecting.value = null;
}

const countLabel = computed(() => `${props.total} ${props.total === 1 ? 'draft awaiting review' : 'drafts awaiting review'}`);
</script>

<template>
    <Head title="Studio — Review" />

    <div class="mx-auto max-w-5xl px-4 py-8 lg:px-8">
        <Link
            href="/studio"
            class="text-muted-foreground hover:text-foreground focus-visible:ring-ring -ml-1 inline-flex items-center gap-1.5 rounded text-sm transition-colors outline-none focus-visible:ring-2"
        >
            <ArrowLeft class="size-4" aria-hidden="true" />
            Back to Library
        </Link>

        <div class="mt-3 flex flex-wrap items-center justify-between gap-4">
            <div>
                <h1 class="font-display text-foreground text-2xl font-bold sm:text-3xl">Review</h1>
                <p class="text-muted-foreground mt-1 text-sm tabular-nums">{{ countLabel }}</p>
            </div>
            <Button v-if="selectedIds.length" @click="approveSelected">
                <CircleCheckBig class="size-4" aria-hidden="true" />
                Approve {{ selectedIds.length }} selected
            </Button>
        </div>

        <EmptyState
            v-if="!videos.length"
            class="mt-10"
            :icon="CircleCheckBig"
            title="All caught up"
            message="There are no drafts waiting to be reviewed."
        />

        <div v-else class="mt-6 overflow-hidden rounded-xl border">
            <Table>
                <TableHeader>
                    <TableRow>
                        <TableHead class="w-10">
                            <Checkbox :model-value="headerState" aria-label="Select all" @update:model-value="toggleAll" />
                        </TableHead>
                        <TableHead class="w-20">Thumbnail</TableHead>
                        <TableHead>Title</TableHead>
                        <TableHead class="hidden md:table-cell">Speaker</TableHead>
                        <TableHead class="hidden lg:table-cell">Date</TableHead>
                        <TableHead class="text-right">Actions</TableHead>
                    </TableRow>
                </TableHeader>
                <TableBody>
                    <TableRow v-for="video in videos" :key="video.id">
                        <TableCell>
                            <Checkbox
                                :model-value="selected.has(video.id)"
                                :aria-label="`Select ${video.name}`"
                                @update:model-value="(value) => toggleRow(video.id, value)"
                            />
                        </TableCell>
                        <TableCell>
                            <div class="bg-muted relative aspect-video w-16 overflow-hidden rounded">
                                <img v-if="video.thumbnail" :src="video.thumbnail" alt="" class="h-full w-full object-cover" loading="lazy" />
                                <Film v-else class="text-muted-foreground absolute inset-0 m-auto size-5" aria-hidden="true" />
                            </div>
                        </TableCell>
                        <TableCell>
                            <p class="text-foreground line-clamp-2 font-medium">{{ video.name }}</p>
                            <p v-if="video.series" class="text-muted-foreground text-xs">{{ video.series }}</p>
                            <p v-if="video.duration_seconds" class="text-muted-foreground text-xs tabular-nums md:hidden">
                                {{ formatDuration(video.duration_seconds) }}
                            </p>
                        </TableCell>
                        <TableCell class="text-muted-foreground hidden md:table-cell">{{ video.speakers.join(', ') || '—' }}</TableCell>
                        <TableCell class="text-muted-foreground hidden tabular-nums lg:table-cell">{{ video.date || '—' }}</TableCell>
                        <TableCell>
                            <div class="flex items-center justify-end gap-1.5">
                                <Button size="sm" @click="approve(video.id)">
                                    <Check class="size-4" aria-hidden="true" />
                                    Approve
                                </Button>
                                <Button variant="outline" size="sm" as-child>
                                    <Link :href="`/studio/videos/${video.id}/edit`">
                                        <Pencil class="size-4" aria-hidden="true" />
                                        Edit
                                    </Link>
                                </Button>
                                <Button variant="ghost" size="icon" :aria-label="`Reject ${video.name}`" @click="rejecting = video">
                                    <Trash2 class="size-4" aria-hidden="true" />
                                </Button>
                            </div>
                        </TableCell>
                    </TableRow>
                </TableBody>
            </Table>
        </div>

        <div class="mt-6">
            <PaginationNav :page-range="page_range" :has-prev-page="has_prev_page" :has-next-page="has_next_page" />
        </div>

        <!-- Reject confirm -->
        <Dialog :open="!!rejecting" @update:open="(open) => !open && (rejecting = null)">
            <DialogContent>
                <DialogHeader>
                    <DialogTitle>Reject this draft?</DialogTitle>
                    <DialogDescription>
                        “{{ rejecting?.name }}” will be moved to the trash. It's hidden from the Library and the public site, but can be restored by
                        an administrator.
                    </DialogDescription>
                </DialogHeader>
                <DialogFooter>
                    <DialogClose as-child>
                        <Button variant="outline">Cancel</Button>
                    </DialogClose>
                    <Button variant="destructive" @click="confirmReject">Reject</Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    </div>
</template>
