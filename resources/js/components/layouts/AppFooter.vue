<script setup lang="ts">
import BrandVimeo from '@/atoms/BrandVimeo.vue';
import LogoMark from '@/atoms/LogoMark.vue';
import TextSizeControl from '@/molecules/TextSizeControl.vue';
import ThemeToggle from '@/molecules/ThemeToggle.vue';
import type { SharedData } from '~/types';
import { Link, usePage } from '@inertiajs/vue3';
import { Github, Youtube } from 'lucide-vue-next';
import { computed } from 'vue';

const year = new Date().getFullYear();

// Discreet editor entry point. Reads as "Studio" once signed in, "Editor sign
// in" otherwise — both go to /studio (the gate redirects anonymous users on to
// the login page). Kept visually quiet: muted, in the bottom utility row.
// auth.user is real-or-null (anonymous), so treat it as nullable here.
const page = usePage<SharedData>();
const studioLabel = computed(() => (page.props.auth.user ? 'Studio' : 'Editor sign in'));

const socials = [
    { name: 'YouTube', href: 'https://www.youtube.com/channel/UCvME6kEF02MqliB5TNHFLZA', icon: Youtube },
    { name: 'Vimeo', href: 'https://vimeo.com/user22232841', icon: BrandVimeo },
    { name: 'GitHub', href: 'https://github.com/Clayton-TV', icon: Github },
];

const columns = [
    {
        heading: 'Watch',
        links: [
            { name: 'Latest', href: '/latest' },
            { name: 'Series', href: '/series' },
            { name: 'Services', href: '/livestreams' },
        ],
    },
    {
        heading: 'Browse',
        links: [
            { name: 'Topics', href: '/topic' },
            { name: 'Speakers', href: '/speaker' },
            { name: 'Bible books', href: '/book' },
            { name: 'Ministries', href: '/ministry' },
        ],
    },
];
</script>

<template>
    <footer class="border-border mt-16 border-t">
        <div class="mx-auto grid max-w-6xl gap-10 px-4 py-12 sm:grid-cols-[1.2fr_1fr_1fr] lg:px-8">
            <div>
                <div class="flex items-center gap-2.5">
                    <LogoMark class="fill-primary h-6 w-auto" />
                    <span class="font-display text-foreground text-sm font-bold tracking-wide">Clayton&nbsp;TV</span>
                </div>
                <p class="text-muted-foreground mt-3 max-w-xs text-sm leading-relaxed">
                    Christian media you can trust — sermons, series and courses, free and always here.
                </p>
            </div>
            <nav v-for="column in columns" :key="column.heading" :aria-label="column.heading">
                <p class="text-muted-foreground text-xs font-semibold tracking-wider uppercase">{{ column.heading }}</p>
                <ul class="mt-3 space-y-2">
                    <li v-for="link in column.links" :key="link.name">
                        <Link
                            :href="link.href"
                            class="focus-visible:ring-ring text-muted-foreground hover:text-foreground rounded text-sm transition-colors duration-150 outline-none focus-visible:ring-2"
                        >
                            {{ link.name }}
                        </Link>
                    </li>
                </ul>
            </nav>
        </div>
        <div class="border-border border-t">
            <div class="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3 px-4 py-5 lg:px-8">
                <div class="text-muted-foreground flex items-center gap-3 text-xs">
                    <p>© {{ year }} Clayton TV</p>
                    <Link
                        href="/studio"
                        class="focus-visible:ring-ring hover:text-foreground rounded transition-colors duration-150 outline-none focus-visible:ring-2"
                    >
                        {{ studioLabel }}
                    </Link>
                </div>
                <div class="flex flex-wrap items-center gap-x-4 gap-y-2">
                    <div class="flex items-center gap-2">
                        <span class="text-muted-foreground text-xs">Theme</span>
                        <ThemeToggle />
                    </div>
                    <div class="flex items-center gap-2">
                        <span class="text-muted-foreground text-xs">Text size</span>
                        <TextSizeControl />
                    </div>
                    <div class="flex gap-1">
                        <a
                            v-for="social in socials"
                            :key="social.name"
                            :href="social.href"
                            :aria-label="social.name"
                            rel="noopener"
                            target="_blank"
                            class="focus-visible:ring-ring text-muted-foreground hover:text-foreground inline-flex min-h-11 min-w-11 items-center justify-center rounded-md transition-colors duration-150 outline-none focus-visible:ring-2"
                        >
                            <component :is="social.icon" class="h-5 w-5 stroke-[1.5]" aria-hidden="true" />
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </footer>
</template>
