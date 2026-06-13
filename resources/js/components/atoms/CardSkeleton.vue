<script setup>
const props = defineProps({
    rowCount: {
        type: Number,
    },
    customClasses: {
        type: String,
    },
    darkText: {
        type: Boolean,
    },
});
</script>

<template>
    <div role="status" class="animate-pulse rounded-md p-4 shadow-sm md:p-6" :class="customClasses">
        <div class="mb-4 h-2.5 w-[80%] rounded-full" :class="darkText ? 'bg-muted' : 'bg-muted'"></div>
        <div
            v-for="rowIndex in rowCount"
            :key="`card-row-${rowIndex}`"
            class="mb-2.5 h-2 w-full rounded-full"
            :class="darkText ? 'bg-muted' : 'bg-muted'"
        ></div>
        <span class="sr-only">Loading...</span>
    </div>
</template>
