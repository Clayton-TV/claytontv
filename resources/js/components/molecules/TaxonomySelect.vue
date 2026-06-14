<script setup lang="ts">
import { onClickOutside } from '@vueuse/core';
import { Check, ChevronsUpDown, X } from 'lucide-vue-next';
import { computed, nextTick, ref } from 'vue';

/**
 * A searchable picker for one taxonomy (speakers, series, topics…). Single- or
 * multi-select. Options are filtered client-side and capped so even the ~2,600
 * series list stays snappy — the editor narrows with the search box.
 *
 * Self-contained on purpose (no popover/combobox dependency): a labelled
 * trigger button opens a panel with a search field and a scrollable result
 * list. Keyboard: Enter picks the top match, Escape closes.
 */

interface Option {
    id: string;
    name: string;
}

const props = withDefaults(
    defineProps<{
        id: string;
        label: string;
        options: Option[];
        // string[] when multiple, string | null when single.
        modelValue: string[] | string | null;
        multiple?: boolean;
        placeholder?: string;
        searchPlaceholder?: string;
        hint?: string;
    }>(),
    {
        multiple: false,
        placeholder: 'Select…',
        searchPlaceholder: 'Search…',
        hint: '',
    },
);

const emit = defineEmits<{ 'update:modelValue': [value: string[] | string | null] }>();

const MAX_RESULTS = 50;

const open = ref(false);
const query = ref('');
const root = ref<HTMLElement | null>(null);
const searchInput = ref<HTMLInputElement | null>(null);

onClickOutside(root, () => (open.value = false));

// Normalise the model to a Set of ids regardless of single/multiple shape.
const selectedIds = computed(() => {
    if (props.multiple) return new Set((props.modelValue as string[]) || []);
    return new Set(props.modelValue ? [props.modelValue as string] : []);
});

const byId = computed(() => new Map(props.options.map((o) => [o.id, o])));
const selectedOptions = computed(() => [...selectedIds.value].map((id) => byId.value.get(id)).filter(Boolean) as Option[]);

const filtered = computed(() => {
    const q = query.value.trim().toLowerCase();
    const matches = q ? props.options.filter((o) => o.name.toLowerCase().includes(q)) : props.options;
    return matches.slice(0, MAX_RESULTS);
});

const overflow = computed(() => {
    const q = query.value.trim().toLowerCase();
    const total = q ? props.options.filter((o) => o.name.toLowerCase().includes(q)).length : props.options.length;
    return Math.max(0, total - MAX_RESULTS);
});

async function toggleOpen() {
    open.value = !open.value;
    if (open.value) {
        await nextTick();
        searchInput.value?.focus();
    }
}

function isSelected(id: string) {
    return selectedIds.value.has(id);
}

function pick(option: Option) {
    if (props.multiple) {
        const next = new Set(selectedIds.value);
        if (next.has(option.id)) next.delete(option.id);
        else next.add(option.id);
        emit('update:modelValue', [...next]);
    } else {
        emit('update:modelValue', isSelected(option.id) ? null : option.id);
        open.value = false;
        query.value = '';
    }
}

function remove(id: string) {
    if (props.multiple) {
        emit(
            'update:modelValue',
            [...selectedIds.value].filter((x) => x !== id),
        );
    } else {
        emit('update:modelValue', null);
    }
}

function onEnter() {
    if (filtered.value.length) pick(filtered.value[0]);
}
</script>

<template>
    <div ref="root" class="relative">
        <label :for="id" class="text-foreground mb-1.5 block text-sm font-medium">{{ label }}</label>

        <!-- Trigger -->
        <button
            :id="id"
            type="button"
            @click="toggleOpen"
            :aria-expanded="open"
            aria-haspopup="listbox"
            class="border-input bg-background hover:bg-accent/40 focus-visible:ring-ring flex min-h-11 w-full items-center justify-between gap-2 rounded-lg border px-3 py-2 text-left text-base transition-colors outline-none focus-visible:ring-2"
        >
            <span v-if="!selectedOptions.length" class="text-muted-foreground">{{ placeholder }}</span>
            <!-- Selected: chips for multiple, plain text for single -->
            <span v-else-if="multiple" class="flex flex-wrap gap-1.5">
                <span
                    v-for="opt in selectedOptions"
                    :key="opt.id"
                    class="bg-secondary text-secondary-foreground inline-flex items-center gap-1 rounded-md py-0.5 pr-1 pl-2 text-sm"
                >
                    {{ opt.name }}
                    <span
                        role="button"
                        :aria-label="`Remove ${opt.name}`"
                        tabindex="0"
                        @click.stop="remove(opt.id)"
                        @keydown.enter.stop.prevent="remove(opt.id)"
                        class="hover:bg-background/60 rounded p-0.5"
                    >
                        <X class="size-3.5" aria-hidden="true" />
                    </span>
                </span>
            </span>
            <span v-else class="text-foreground truncate">{{ selectedOptions[0].name }}</span>

            <ChevronsUpDown class="text-muted-foreground size-4 shrink-0" aria-hidden="true" />
        </button>

        <p v-if="hint" class="text-muted-foreground mt-1 text-xs">{{ hint }}</p>

        <!-- Panel -->
        <Transition
            enter-active-class="transition duration-150 ease-out motion-reduce:transition-none"
            enter-from-class="opacity-0 -translate-y-1"
            leave-active-class="transition duration-100 ease-in motion-reduce:transition-none"
            leave-to-class="opacity-0"
        >
            <div v-if="open" class="bg-popover absolute z-20 mt-1.5 w-full overflow-hidden rounded-lg border shadow-lg">
                <div class="border-b p-2">
                    <input
                        ref="searchInput"
                        v-model="query"
                        type="search"
                        :placeholder="searchPlaceholder"
                        @keydown.enter.prevent="onEnter"
                        @keydown.esc="open = false"
                        class="bg-background focus-visible:ring-ring w-full rounded-md border px-3 py-2 text-base outline-none focus-visible:ring-2"
                    />
                </div>
                <ul role="listbox" class="max-h-64 overflow-y-auto p-1">
                    <li v-if="!filtered.length" class="text-muted-foreground px-3 py-6 text-center text-sm">No matches</li>
                    <li v-for="opt in filtered" :key="opt.id">
                        <button
                            type="button"
                            role="option"
                            :aria-selected="isSelected(opt.id)"
                            @click="pick(opt)"
                            class="hover:bg-accent flex w-full items-center justify-between gap-2 rounded-md px-3 py-2 text-left text-sm transition-colors"
                        >
                            <span class="truncate">{{ opt.name }}</span>
                            <Check v-if="isSelected(opt.id)" class="text-primary size-4 shrink-0" aria-hidden="true" />
                        </button>
                    </li>
                    <li v-if="overflow" class="text-muted-foreground px-3 py-2 text-center text-xs">+{{ overflow }} more — keep typing to narrow</li>
                </ul>
            </div>
        </Transition>
    </div>
</template>
