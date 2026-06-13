<script setup lang="ts">
import { cn } from '@/lib/utils';
import type { ToastVariant } from '~/composables/useToast';
import { IconAlertTriangle, IconCircleCheck, IconInfoCircle, IconX } from '@tabler/icons-vue';
import { ToastClose, ToastDescription, ToastRoot } from 'reka-ui';
import { computed } from 'vue';

const props = defineProps<{
    variant: ToastVariant;
    message: string;
    duration: number;
}>();

const emit = defineEmits<{ close: [] }>();

// Coloured left accent + matching icon per variant. Success and info lean on
// the brand/neutral palette; error reuses the destructive token.
const variants = {
    success: { icon: IconCircleCheck, accent: 'border-l-primary', iconColor: 'text-primary' },
    error: { icon: IconAlertTriangle, accent: 'border-l-destructive', iconColor: 'text-destructive' },
    info: { icon: IconInfoCircle, accent: 'border-l-muted-foreground', iconColor: 'text-muted-foreground' },
} as const;

const current = computed(() => variants[props.variant]);
</script>

<template>
    <ToastRoot
        :duration="duration"
        @update:open="(open: boolean) => !open && emit('close')"
        :class="
            cn(
                'bg-card text-card-foreground border-border flex items-center gap-3 rounded-lg border border-l-4 p-3.5 shadow-lg',
                // Slide up + fade in on enter, fade out on exit; swipe-to-dismiss
                // tracks the drag. prefers-reduced-motion users get instant
                // show/hide via the media query below.
                'data-[state=open]:animate-in data-[state=open]:fade-in-0 data-[state=open]:slide-in-from-bottom-2 data-[state=open]:duration-200 data-[state=open]:ease-out',
                'data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=closed]:duration-150 data-[state=closed]:ease-out',
                'data-[swipe=move]:translate-x-(--reka-toast-swipe-move-x) data-[swipe=cancel]:translate-x-0 data-[swipe=cancel]:transition-transform data-[swipe=end]:animate-out data-[swipe=end]:fade-out-0',
                'motion-reduce:animate-none motion-reduce:transition-none',
                current.accent,
            )
        "
    >
        <component :is="current.icon" :class="cn('size-5 shrink-0', current.iconColor)" aria-hidden="true" />
        <ToastDescription class="flex-1 text-sm">{{ message }}</ToastDescription>
        <ToastClose
            class="text-muted-foreground hover:text-foreground focus-visible:ring-ring -m-1 shrink-0 rounded-sm p-1 outline-none focus-visible:ring-2"
            aria-label="Dismiss notification"
        >
            <IconX class="size-4" aria-hidden="true" />
        </ToastClose>
    </ToastRoot>
</template>
