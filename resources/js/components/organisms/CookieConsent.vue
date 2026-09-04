<script setup lang="ts">
import { Button } from '@/ui/button';
import { Switch } from '@/ui/switch';
import { Cookie } from 'lucide-vue-next';
import { ref, watch } from 'vue';
import { useCookieConsent } from '~/composables/useCookieConsent';

// PECR / UK-GDPR consent banner. Non-blocking (not a modal): visitors can keep
// reading while they decide. "Necessary" is always on; "Analytics" is opt-in and
// off by default, but "Accept all" is the prominent call to action.
const { open, analyticsGranted, acceptAll, rejectNonEssential, savePreferences } = useCookieConsent();

// Local mirror of the analytics toggle. Off by default; when the banner is
// reopened from the footer it reflects the visitor's current choice.
const analytics = ref(analyticsGranted.value);

watch(open, (isOpen) => {
    if (isOpen) analytics.value = analyticsGranted.value;
});

const PRIVACY_URL = 'https://clayton.tv/Clayton_TV_Data_Privacy_Notice.pdf';
</script>

<template>
    <Transition
        enter-active-class="transition duration-300 ease-out motion-reduce:transition-none"
        enter-from-class="translate-y-6 opacity-0"
        enter-to-class="translate-y-0 opacity-100"
        leave-active-class="transition duration-200 ease-in motion-reduce:transition-none"
        leave-from-class="translate-y-0 opacity-100"
        leave-to-class="translate-y-6 opacity-0"
    >
        <div v-if="open" class="pb-safe px-safe fixed inset-x-0 bottom-0 z-50 p-4" role="region" aria-label="Cookie consent">
            <div class="border-border bg-background/95 mx-auto max-w-3xl rounded-2xl border p-5 shadow-2xl backdrop-blur-md sm:p-6">
                <div class="flex items-start gap-3">
                    <span class="bg-primary/10 text-primary flex h-10 w-10 flex-none items-center justify-center rounded-full" aria-hidden="true">
                        <Cookie class="h-5 w-5" />
                    </span>
                    <div class="min-w-0">
                        <h2 class="font-display text-foreground text-base font-bold">A note on cookies</h2>
                        <p class="text-muted-foreground mt-1 text-sm leading-relaxed">
                            To improve the site we measure how people find and watch teaching. The essentials work without cookies; accepting also
                            enables cookies, heatmaps and masked session replays for richer insight. You can change this anytime.
                            <a
                                :href="PRIVACY_URL"
                                rel="noopener"
                                target="_blank"
                                class="text-primary focus-visible:ring-ring rounded font-medium underline-offset-4 outline-none hover:underline focus-visible:ring-2"
                            >
                                Privacy notice
                            </a>
                        </p>
                    </div>
                </div>

                <!-- Categories: necessary is locked on; analytics is opt-in -->
                <div class="border-border mt-4 grid gap-2.5 border-t pt-4">
                    <div class="flex items-center justify-between gap-4">
                        <div class="min-w-0">
                            <p class="text-foreground text-sm font-medium">Strictly necessary</p>
                            <p class="text-muted-foreground text-xs">Remembers your choices (theme, text size, this consent). Always on.</p>
                        </div>
                        <Switch :model-value="true" disabled aria-label="Strictly necessary cookies (always on)" />
                    </div>
                    <div class="flex items-center justify-between gap-4">
                        <div class="min-w-0">
                            <p class="text-foreground text-sm font-medium">Analytics &amp; session insights</p>
                            <p class="text-muted-foreground text-xs">
                                Usage trends, heatmaps and masked session replays that show where the site helps or frustrates.
                            </p>
                        </div>
                        <Switch v-model="analytics" aria-label="Analytics and session insights cookies" />
                    </div>
                </div>

                <div class="mt-5 flex flex-col-reverse gap-2 sm:flex-row sm:items-center">
                    <!-- Rejecting non-essential cookies is one click and as prominent as accepting (ICO). -->
                    <Button variant="outline" class="sm:mr-auto sm:min-w-32" @click="rejectNonEssential"> Reject all </Button>
                    <Button variant="outline" class="sm:min-w-32" @click="savePreferences(analytics)"> Save preferences </Button>
                    <Button class="sm:min-w-40" @click="acceptAll"> Accept all cookies </Button>
                </div>
            </div>
        </div>
    </Transition>
</template>
