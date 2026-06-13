<script setup>
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/ui/dialog';
import { usePalette } from '~/composables/usePalette';

const { helpOpen } = usePalette();

const sections = [
    {
        heading: 'Anywhere',
        shortcuts: [
            { keys: ['⌘', 'K'], label: 'Search everything' },
            { keys: ['/'], label: 'Search everything' },
            { keys: ['?'], label: 'This help' },
        ],
    },
    {
        heading: 'While watching',
        shortcuts: [
            { keys: ['Space'], label: 'Play / pause' },
            { keys: ['←', '→'], label: 'Back / forward 10 seconds' },
            { keys: ['M'], label: 'Mute' },
        ],
    },
];
</script>

<template>
    <Dialog v-model:open="helpOpen">
        <DialogContent class="max-w-md">
            <DialogHeader>
                <DialogTitle>Keyboard shortcuts</DialogTitle>
                <DialogDescription>Quicker ways around Clayton TV.</DialogDescription>
            </DialogHeader>
            <div class="space-y-5">
                <section v-for="section in sections" :key="section.heading">
                    <h3 class="text-muted-foreground text-xs font-semibold tracking-wider uppercase">{{ section.heading }}</h3>
                    <ul class="mt-2 space-y-1.5">
                        <li
                            v-for="shortcut in section.shortcuts"
                            :key="shortcut.label + shortcut.keys.join()"
                            class="flex items-center justify-between gap-4"
                        >
                            <span class="text-foreground text-sm">{{ shortcut.label }}</span>
                            <span class="flex gap-1">
                                <kbd
                                    v-for="key in shortcut.keys"
                                    :key="key"
                                    class="border-input bg-muted text-foreground rounded border px-1.5 py-0.5 font-sans text-xs"
                                >
                                    {{ key }}
                                </kbd>
                            </span>
                        </li>
                    </ul>
                </section>
            </div>
        </DialogContent>
    </Dialog>
</template>
