<script setup lang="ts">
import ErrorBoundary from '@/ErrorBoundary.vue';
import AppFooter from '@/layouts/AppFooter.vue';
import AppHeader from '@/layouts/AppHeader.vue';
import CookieConsent from '@/organisms/CookieConsent.vue';
import PersistentPlayer from '@/organisms/PersistentPlayer.vue';
import Toaster from '@/organisms/Toaster.vue';
import { usePage } from '@inertiajs/vue3';
import { ChevronUp } from 'lucide-vue-next';
import { computed, ref } from 'vue';

// The mini-player shows on watch contexts. In the Studio it's allowed on the
// browse-like surfaces (Library + Review, where clicking a thumbnail previews a
// video) but kept off the form/editor surfaces so it never overlaps their UI.
const page = usePage();
const STUDIO_PLAYER_PATHS = ['/studio', '/studio/', '/studio/review'];
const showPlayer = computed(() => {
    const path = page.url.split('?')[0];
    if (!path.startsWith('/studio')) return true;
    return STUDIO_PLAYER_PATHS.includes(path);
});

const jumpTopButtonShowThresh = window.innerHeight * 0.25;
const jumpTopButtonHideThresh = jumpTopButtonShowThresh * 0.75;
const jumpTopButtonVisible = ref(false);
const onPageScroll = () => {
    const pos = window.scrollY;
    if (pos > jumpTopButtonShowThresh) {
        jumpTopButtonVisible.value = true;
    } else if (pos < jumpTopButtonHideThresh || pos == 0) {
        jumpTopButtonVisible.value = false;
    }
};
window.addEventListener('scroll', onPageScroll);
</script>

<style type="text/css">
.jumpButton-enter-active,
.jumpButton-leave-active {
    transition: all 0.5s ease;
}

.jumpButton-enter-active {
    transition: transform 0.5s cubic-bezier(0.5, 0.4, 0.5, 1.3);
}

.jumpButton-enter-from,
.jumpButton-leave-to {
    opacity: 0;
    transform: translateY(100%);
}

html {
    scroll-behavior: smooth;
}
</style>

<template>
    <!-- relative: PersistentPlayer's docked mode positions in document coords.
         overflow-x-clip: belt-and-braces against any descendant forcing
         horizontal scroll on mobile (clip, not hidden, so sticky still works). -->
    <div class="bg-background relative flex min-h-full flex-col overflow-x-clip scroll-auto">
        <!-- Keyboard users skip the nav straight to content -->
        <a
            href="#main"
            class="bg-primary text-primary-foreground sr-only z-50 rounded-md px-4 py-2 text-sm font-semibold focus:not-sr-only focus:absolute focus:top-3 focus:left-3 focus:ring-2 focus:ring-white focus:outline-none"
        >
            Skip to content
        </a>
        <AppHeader />
        <main id="main" tabindex="-1" class="flex-1 outline-none">
            <!-- Contains a page render error to a calm fallback; the shell survives -->
            <ErrorBoundary>
                <slot />
            </ErrorBoundary>
        </main>
        <AppFooter />
        <!-- The shared player + toasts outlive page navigations (persistent layout) -->
        <PersistentPlayer v-if="showPlayer" />
        <Toaster />
        <CookieConsent />
    </div>

    <Transition name="jumpButton">
        <div
            id="jumpTopButton"
            class="fixed right-3 bottom-3 z-100 aspect-square cursor-pointer rounded-full bg-gray-600 text-white opacity-75 hover:bg-red-400 hover:opacity-100"
            title="Scroll to top"
            v-show="jumpTopButtonVisible"
            onclick="window.scrollTo(0, 0)"
        >
            <ChevronUp class="m-2 size-9 md:size-12" />
        </div>
    </Transition>
</template>
