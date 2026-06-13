<script setup>
import { IconX } from '@tabler/icons-vue';
import { computed } from 'vue';

// Active filters as removable chips, so an elderly user always sees, in plain
// words, exactly what's narrowing the list — and can drop one with a big tap.
const props = defineProps({
    facets: { type: Object, required: true },
    active: { type: Object, required: true },
});
const emit = defineEmits(['remove', 'clear']);

const label = (facet, value) => {
    const opt = (props.facets[facet] || []).find((o) => String(o.value) === String(value));
    return opt ? opt.label : value;
};

const chips = computed(() => {
    const out = [];
    for (const facet of ['speaker', 'book', 'audience']) {
        for (const value of props.active[facet] || []) out.push({ facet, value, label: label(facet, value) });
    }
    for (const facet of ['type', 'length']) {
        if (props.active[facet]) out.push({ facet, value: props.active[facet], label: label(facet, props.active[facet]) });
    }
    return out;
});
</script>

<template>
    <div v-if="chips.length" class="flex flex-wrap items-center gap-2">
        <button
            v-for="chip in chips"
            :key="`${chip.facet}-${chip.value}`"
            @click="emit('remove', chip.facet, chip.value)"
            class="bg-primary/15 text-primary focus-visible:ring-ring hover:bg-primary/25 inline-flex min-h-9 cursor-pointer items-center gap-1.5 rounded-full px-3 text-sm font-medium outline-none focus-visible:ring-2"
        >
            {{ chip.label }}
            <IconX class="h-3.5 w-3.5" aria-hidden="true" />
            <span class="sr-only">Remove filter</span>
        </button>
        <button
            @click="emit('clear')"
            class="focus-visible:ring-ring text-muted-foreground hover:text-foreground min-h-9 cursor-pointer rounded-full px-3 text-sm outline-none focus-visible:ring-2"
        >
            Clear all
        </button>
    </div>
</template>
