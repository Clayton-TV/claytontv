<script setup>
defineProps({
    rowCount: {
        type: Number,
    },
    customClasses: {
        type: String,
    },
});
</script>

<template>
    <div role="status" class="animate-pulse rounded-md p-4 shadow-sm md:p-6" :class="customClasses">
        <div class="bg-muted mb-4 h-2.5 w-[80%] rounded-full"></div>
        <div v-for="rowIndex in rowCount" :key="`card-row-${rowIndex}`" class="bg-muted mb-2.5 h-2 w-full rounded-full"></div>
        <span class="sr-only">Loading...</span>
    </div>
</template>
