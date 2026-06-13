<script setup>
import { IconBrandWhatsapp, IconCheck, IconLink, IconShare } from '@tabler/icons-vue';
import { computed, ref } from 'vue';
import { useToast } from '~/composables/useToast';

const props = defineProps({
    title: { type: String, required: true },
});

const toast = useToast();

const copied = ref(false);
const menuOpen = ref(false);

// navigator.share isn't reactive, but it's stable per device; compute once
const canNativeShare = computed(() => typeof navigator !== 'undefined' && !!navigator.share);

const shareUrl = () => (typeof window !== 'undefined' ? window.location.href : '');

const nativeShare = async () => {
    try {
        await navigator.share({ title: props.title, url: shareUrl() });
    } catch {
        // user cancelled — nothing to do
    }
};

const copyLink = async () => {
    try {
        await navigator.clipboard.writeText(shareUrl());
        copied.value = true;
        toast.success('Link copied to clipboard');
        setTimeout(() => (copied.value = false), 2000);
    } catch {
        copied.value = false;
        toast.error('Could not copy the link');
    }
};

const whatsappUrl = computed(() => `https://wa.me/?text=${encodeURIComponent(`${props.title} ${shareUrl()}`)}`);

const onClick = () => {
    if (canNativeShare.value) {
        nativeShare();
    } else {
        menuOpen.value = !menuOpen.value;
    }
};
</script>

<template>
    <div class="relative">
        <button
            @click="onClick"
            class="focus-visible:ring-ring border-input text-foreground hover:border-ring hover:text-foreground inline-flex min-h-11 items-center gap-2 rounded-lg border px-4 text-sm font-medium transition-colors duration-150 outline-none focus-visible:ring-2"
            aria-label="Share this video"
        >
            <IconShare class="h-4 w-4" aria-hidden="true" />
            Share
        </button>

        <!-- Fallback menu for desktop browsers without the native share sheet -->
        <div
            v-if="menuOpen && !canNativeShare"
            class="border-border bg-card absolute top-full left-0 z-20 mt-2 w-56 rounded-xl border p-1.5 shadow-xl"
        >
            <button
                @click="copyLink"
                class="focus-visible:ring-ring text-foreground hover:bg-accent flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left text-sm outline-none focus-visible:ring-2"
            >
                <IconCheck v-if="copied" class="text-primary h-4 w-4" aria-hidden="true" />
                <IconLink v-else class="text-muted-foreground h-4 w-4" aria-hidden="true" />
                {{ copied ? 'Link copied' : 'Copy link' }}
            </button>
            <a
                :href="whatsappUrl"
                target="_blank"
                rel="noopener"
                class="focus-visible:ring-ring text-foreground hover:bg-accent flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left text-sm outline-none focus-visible:ring-2"
            >
                <IconBrandWhatsapp class="text-muted-foreground h-4 w-4" aria-hidden="true" />
                Share on WhatsApp
            </a>
        </div>
    </div>
</template>
