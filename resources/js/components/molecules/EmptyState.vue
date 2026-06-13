<script setup>
import { Link } from '@inertiajs/vue3';
import { SearchX } from 'lucide-vue-next';

// A calm, reusable "nothing here" panel — icon, heading, a reassuring line,
// and an optional way forward. Used for empty grids, no search results, and
// not-found pages so a non-technical user is never left staring at a blank.
defineProps({
    icon: { type: [Object, Function], default: () => SearchX },
    title: { type: String, required: true },
    message: { type: String, default: '' },
    ctaHref: { type: String, default: '' },
    ctaLabel: { type: String, default: '' },
});
</script>

<template>
    <div class="border-border bg-card flex flex-col items-center justify-center rounded-xl border px-6 py-16 text-center">
        <component :is="icon" class="text-muted-foreground h-12 w-12" aria-hidden="true" />
        <p class="font-display text-foreground mt-4 text-xl font-bold">{{ title }}</p>
        <p v-if="message" class="text-muted-foreground mt-2 max-w-md text-sm leading-relaxed">{{ message }}</p>
        <Link
            v-if="ctaHref && ctaLabel"
            :href="ctaHref"
            class="bg-primary text-primary-foreground focus-visible:ring-ring hover:bg-primary/90 focus-visible:ring-offset-background mt-6 inline-flex min-h-11 items-center rounded-lg px-5 text-sm font-semibold transition-colors duration-150 outline-none focus-visible:ring-2 focus-visible:ring-offset-2"
        >
            {{ ctaLabel }}
        </Link>
        <!-- Lets callers add extra actions (e.g. "Clear filters") -->
        <div v-if="$slots.actions" class="mt-6"><slot name="actions" /></div>
    </div>
</template>
