<script setup lang="ts">
import { Plus } from 'lucide-vue-next';

// A quiet inline suggestion row shown under a taxonomy picker: matched names are
// add-chips (click to add), unmatched names are muted "new" hints (we never
// create taxonomy from unreviewed model output). Deliberately unbranded — no
// "AI" wording, calm neutral styling, red reserved for the page's primary action.

interface Option {
    id: string;
    name: string;
}

defineProps<{
    matched: Option[];
    unmatched: string[];
}>();

const emit = defineEmits<{
    (e: 'apply', ids: string[]): void;
}>();
</script>

<template>
    <div v-if="matched.length || unmatched.length" class="mt-1.5 flex flex-wrap items-center gap-1.5">
        <span class="text-muted-foreground mr-0.5 text-xs">Suggested</span>

        <button
            v-for="o in matched"
            :key="`m-${o.id}`"
            type="button"
            class="border-border text-muted-foreground hover:bg-accent hover:text-accent-foreground focus-visible:ring-ring inline-flex cursor-pointer items-center gap-1 rounded-full border border-dashed px-2.5 py-0.5 text-xs transition-colors outline-none focus-visible:ring-2"
            @click="emit('apply', [o.id])"
        >
            <Plus class="size-3" aria-hidden="true" />
            {{ o.name }}
        </button>

        <span
            v-for="(name, i) in unmatched"
            :key="`u-${i}`"
            class="text-muted-foreground/70 border-border/60 inline-flex items-center rounded-full border border-dashed px-2.5 py-0.5 text-xs"
            title="Not in your taxonomy yet"
        >
            {{ name }} · new
        </span>

        <button
            v-if="matched.length > 1"
            type="button"
            class="text-muted-foreground hover:text-foreground ml-0.5 cursor-pointer text-xs underline-offset-2 hover:underline"
            @click="
                emit(
                    'apply',
                    matched.map((o) => o.id),
                )
            "
        >
            Add all
        </button>
    </div>
</template>
