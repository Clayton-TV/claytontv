<script setup lang="ts">
import { Button } from '@/ui/button';
import { Input } from '@/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/ui/tabs';
import { Head, Link } from '@inertiajs/vue3';
import { ArrowLeft, CheckCircle2, CircleAlert, Copy, LoaderCircle } from 'lucide-vue-next';
import { computed, ref } from 'vue';
import { getCsrfToken } from '~/lib/csrf';

interface Result {
    url: string;
    status: 'created' | 'duplicate' | 'error';
    name?: string;
    error?: string;
    id?: string;
}
interface Summary {
    results: Result[];
    created: number;
    duplicates: number;
    errors: number;
}

const mode = ref<'links' | 'playlist'>('links');
const linksText = ref('');
const playlistUrl = ref('');

const submitting = ref(false);
const topError = ref('');
const summary = ref<Summary | null>(null);

const lineCount = computed(() => linksText.value.split('\n').filter((l) => l.trim()).length);
const canSubmit = computed(() => (mode.value === 'links' ? lineCount.value > 0 : !!playlistUrl.value.trim()));

async function submit() {
    if (!canSubmit.value || submitting.value) return;
    submitting.value = true;
    topError.value = '';
    summary.value = null;
    const payload = mode.value === 'links' ? { urls: linksText.value } : { playlist_url: playlistUrl.value.trim() };
    try {
        const res = await fetch('/studio/api/bulk-create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-XSRF-TOKEN': getCsrfToken() },
            body: JSON.stringify(payload),
        });
        const data = await res.json();
        if (!data.ok) {
            topError.value = data.error || 'Something went wrong.';
            return;
        }
        summary.value = data;
    } catch {
        topError.value = 'Something went wrong reaching the server. Try again.';
    } finally {
        submitting.value = false;
    }
}

function reset() {
    summary.value = null;
    linksText.value = '';
    playlistUrl.value = '';
}

const STATUS_META: Record<Result['status'], { class: string; label: string }> = {
    created: { class: 'text-primary', label: 'Draft created' },
    duplicate: { class: 'text-muted-foreground', label: 'Already in library' },
    error: { class: 'text-destructive', label: 'Skipped' },
};
</script>

<template>
    <Head title="Studio — Add several" />

    <div class="mx-auto max-w-3xl px-4 py-8 lg:px-8">
        <Link
            href="/studio"
            class="text-muted-foreground hover:text-foreground focus-visible:ring-ring -ml-1 inline-flex items-center gap-1.5 rounded text-sm transition-colors outline-none focus-visible:ring-2"
        >
            <ArrowLeft class="size-4" aria-hidden="true" />
            Back to Library
        </Link>

        <h1 class="font-display text-foreground mt-3 text-2xl font-bold sm:text-3xl">Add several at once</h1>
        <p class="text-muted-foreground mt-1 text-sm">
            Paste a batch of links or a whole YouTube playlist. Each becomes a draft for review — up to 100 at a time.
        </p>

        <!-- Input (hidden once we have results) -->
        <div v-if="!summary" class="mt-8">
            <Tabs v-model="mode">
                <TabsList class="w-full sm:w-auto">
                    <TabsTrigger value="links">Paste links</TabsTrigger>
                    <TabsTrigger value="playlist">YouTube playlist</TabsTrigger>
                </TabsList>

                <TabsContent value="links" class="space-y-2">
                    <label for="bulk-links" class="text-foreground block text-sm font-medium">One link per line</label>
                    <textarea
                        id="bulk-links"
                        v-model="linksText"
                        rows="8"
                        placeholder="https://www.youtube.com/watch?v=…&#10;https://vimeo.com/…"
                        class="border-input bg-background focus-visible:ring-ring w-full rounded-lg border px-3 py-2 font-mono text-sm outline-none focus-visible:ring-2"
                    ></textarea>
                    <p class="text-muted-foreground text-xs tabular-nums">{{ lineCount }} {{ lineCount === 1 ? 'link' : 'links' }}</p>
                </TabsContent>

                <TabsContent value="playlist" class="space-y-2">
                    <label for="bulk-playlist" class="text-foreground block text-sm font-medium">YouTube playlist link</label>
                    <Input
                        id="bulk-playlist"
                        v-model="playlistUrl"
                        type="url"
                        inputmode="url"
                        placeholder="https://www.youtube.com/playlist?list=…"
                        class="text-base"
                    />
                    <p class="text-muted-foreground text-xs">We'll pull in every video on the playlist (newest first), up to 100.</p>
                </TabsContent>
            </Tabs>

            <p v-if="topError" role="alert" class="text-destructive mt-3 flex items-center gap-1.5 text-sm">
                <CircleAlert class="size-4 shrink-0" aria-hidden="true" />
                {{ topError }}
            </p>

            <div class="mt-6 flex items-center gap-3 border-t pt-6">
                <Button :disabled="!canSubmit || submitting" @click="submit">
                    <LoaderCircle v-if="submitting" class="size-4 animate-spin motion-reduce:animate-none" aria-hidden="true" />
                    {{ submitting ? 'Fetching…' : 'Fetch & create drafts' }}
                </Button>
                <span class="text-muted-foreground text-sm">Drafts wait in Review until you publish them.</span>
            </div>
        </div>

        <!-- Results -->
        <div v-else class="mt-8 space-y-6">
            <div class="border-border bg-card flex flex-wrap items-center gap-x-6 gap-y-1 rounded-xl border p-4 text-sm">
                <span class="text-foreground font-medium">
                    <CheckCircle2 class="text-primary mr-1 inline size-4" aria-hidden="true" />
                    {{ summary.created }} created
                </span>
                <span class="text-muted-foreground">{{ summary.duplicates }} already in library</span>
                <span class="text-muted-foreground">{{ summary.errors }} skipped</span>
            </div>

            <ul class="divide-border divide-y rounded-xl border">
                <li v-for="(r, i) in summary.results" :key="i" class="flex items-start gap-3 px-4 py-3 text-sm">
                    <Copy class="text-muted-foreground mt-0.5 size-4 shrink-0" aria-hidden="true" />
                    <div class="min-w-0 flex-1">
                        <p class="text-foreground truncate">{{ r.name || r.url }}</p>
                        <p class="text-muted-foreground truncate text-xs">{{ r.url }}</p>
                        <p v-if="r.error" class="text-destructive text-xs">{{ r.error }}</p>
                    </div>
                    <span :class="['shrink-0 text-xs font-medium', STATUS_META[r.status].class]">{{ STATUS_META[r.status].label }}</span>
                </li>
            </ul>

            <div class="flex flex-wrap items-center gap-3 border-t pt-6">
                <Button as-child>
                    <Link href="/studio/review">Go to Review</Link>
                </Button>
                <Button variant="outline" @click="reset">Add more</Button>
            </div>
        </div>
    </div>
</template>
