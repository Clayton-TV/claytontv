<script setup>
import { Link } from '@inertiajs/vue3';
import { computed } from 'vue';

// Presentational facet controls, shared by the desktop sidebar and the mobile
// filter Sheet. Single-select (type, length) and multi-select (audience, book,
// speaker) groups. The page owns URL state via useBrowseFilters.
const props = defineProps({
    facets: { type: Object, required: true },
    isActive: { type: Function, required: true },
});
const emit = defineEmits(['single', 'toggle']);

const otBooks = computed(() => (props.facets.book || []).filter((b) => b.testament === 'ot'));
const ntBooks = computed(() => (props.facets.book || []).filter((b) => b.testament === 'nt'));
</script>

<template>
    <div class="space-y-7">
        <!-- Type (single) -->
        <fieldset>
            <legend class="text-xs font-semibold tracking-wider text-gray-500 uppercase">Type</legend>
            <div class="mt-3 flex flex-col gap-1">
                <button
                    v-for="opt in facets.type"
                    :key="opt.value"
                    @click="emit('single', 'type', opt.value)"
                    :aria-pressed="isActive('type', opt.value)"
                    :class="isActive('type', opt.value) ? 'bg-primary/15 text-primary' : 'text-gray-300 hover:bg-white/5 hover:text-white'"
                    class="focus-visible:ring-ring flex min-h-10 items-center rounded-lg px-3 text-left text-sm outline-none focus-visible:ring-2"
                >
                    {{ opt.label }}
                </button>
            </div>
        </fieldset>

        <!-- Length (single) -->
        <fieldset>
            <legend class="text-xs font-semibold tracking-wider text-gray-500 uppercase">Length</legend>
            <div class="mt-3 flex flex-col gap-1">
                <button
                    v-for="opt in facets.length"
                    :key="opt.value"
                    @click="emit('single', 'length', opt.value)"
                    :aria-pressed="isActive('length', opt.value)"
                    :class="isActive('length', opt.value) ? 'bg-primary/15 text-primary' : 'text-gray-300 hover:bg-white/5 hover:text-white'"
                    class="focus-visible:ring-ring flex min-h-10 items-center rounded-lg px-3 text-left text-sm outline-none focus-visible:ring-2"
                >
                    {{ opt.label }}
                </button>
            </div>
        </fieldset>

        <!-- Audience (multi) -->
        <fieldset v-if="facets.audience.length">
            <legend class="text-xs font-semibold tracking-wider text-gray-500 uppercase">For</legend>
            <div class="mt-3 flex flex-col gap-1">
                <label
                    v-for="opt in facets.audience"
                    :key="opt.value"
                    class="flex min-h-10 cursor-pointer items-center gap-3 rounded-lg px-3 text-sm text-gray-300 hover:bg-white/5"
                >
                    <input
                        type="checkbox"
                        :checked="isActive('audience', opt.value)"
                        @change="emit('toggle', 'audience', opt.value)"
                        class="accent-primary h-4 w-4"
                    />
                    <span class="flex-1">{{ opt.label }}</span>
                    <span class="text-xs text-gray-500 tabular-nums">{{ opt.count }}</span>
                </label>
            </div>
        </fieldset>

        <!-- Speaker (multi, top voices) -->
        <fieldset v-if="facets.speaker.length">
            <legend class="text-xs font-semibold tracking-wider text-gray-500 uppercase">Speaker</legend>
            <div class="mt-3 flex max-h-64 flex-col gap-1 overflow-y-auto pr-1">
                <label
                    v-for="opt in facets.speaker"
                    :key="opt.value"
                    class="flex min-h-10 cursor-pointer items-center gap-3 rounded-lg px-3 text-sm text-gray-300 hover:bg-white/5"
                >
                    <input
                        type="checkbox"
                        :checked="isActive('speaker', opt.value)"
                        @change="emit('toggle', 'speaker', opt.value)"
                        class="accent-primary h-4 w-4"
                    />
                    <span class="flex-1 truncate">{{ opt.label }}</span>
                    <span class="text-xs text-gray-500 tabular-nums">{{ opt.count }}</span>
                </label>
            </div>
            <Link href="/speaker/" class="text-primary mt-2 inline-block text-xs hover:underline">More speakers →</Link>
        </fieldset>

        <!-- Book (multi, grouped) -->
        <fieldset v-if="facets.book.length">
            <legend class="text-xs font-semibold tracking-wider text-gray-500 uppercase">Bible book</legend>
            <div class="mt-3 max-h-64 space-y-3 overflow-y-auto pr-1">
                <div v-if="otBooks.length">
                    <p class="px-3 text-[11px] font-medium tracking-wide text-gray-600 uppercase">Old Testament</p>
                    <label
                        v-for="opt in otBooks"
                        :key="opt.value"
                        class="flex min-h-9 cursor-pointer items-center gap-3 rounded-lg px-3 text-sm text-gray-300 hover:bg-white/5"
                    >
                        <input
                            type="checkbox"
                            :checked="isActive('book', opt.value)"
                            @change="emit('toggle', 'book', opt.value)"
                            class="accent-primary h-4 w-4"
                        />
                        <span class="flex-1 truncate">{{ opt.label }}</span>
                        <span class="text-xs text-gray-500 tabular-nums">{{ opt.count }}</span>
                    </label>
                </div>
                <div v-if="ntBooks.length">
                    <p class="px-3 text-[11px] font-medium tracking-wide text-gray-600 uppercase">New Testament</p>
                    <label
                        v-for="opt in ntBooks"
                        :key="opt.value"
                        class="flex min-h-9 cursor-pointer items-center gap-3 rounded-lg px-3 text-sm text-gray-300 hover:bg-white/5"
                    >
                        <input
                            type="checkbox"
                            :checked="isActive('book', opt.value)"
                            @change="emit('toggle', 'book', opt.value)"
                            class="accent-primary h-4 w-4"
                        />
                        <span class="flex-1 truncate">{{ opt.label }}</span>
                        <span class="text-xs text-gray-500 tabular-nums">{{ opt.count }}</span>
                    </label>
                </div>
            </div>
        </fieldset>
    </div>
</template>
