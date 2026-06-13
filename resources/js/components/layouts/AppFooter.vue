<script setup lang="ts">
import LogoMark from '@/atoms/LogoMark.vue';
import TextSizeControl from '@/molecules/TextSizeControl.vue';
import { Link } from '@inertiajs/vue3';
import { IconBrandGithub, IconBrandVimeo, IconBrandYoutube } from '@tabler/icons-vue';

const year = new Date().getFullYear();

const socials = [
    { name: 'YouTube', href: 'https://www.youtube.com/channel/UCvME6kEF02MqliB5TNHFLZA', icon: IconBrandYoutube },
    { name: 'Vimeo', href: 'https://vimeo.com/user22232841', icon: IconBrandVimeo },
    { name: 'GitHub', href: 'https://github.com/Clayton-TV', icon: IconBrandGithub },
];

const columns = [
    {
        heading: 'Watch',
        links: [
            { name: 'Latest', href: '/latest' },
            { name: 'Series', href: '/series' },
            { name: 'Past live streams', href: '/livestreams' },
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
    <footer class="mt-16 border-t border-white/5">
        <div class="mx-auto grid max-w-6xl gap-10 px-4 py-12 sm:grid-cols-[1.2fr_1fr_1fr] lg:px-8">
            <div>
                <div class="flex items-center gap-2.5">
                    <LogoMark class="fill-primary h-6 w-auto" />
                    <span class="font-display text-sm font-bold tracking-wide text-gray-50">Clayton&nbsp;TV</span>
                </div>
                <p class="mt-3 max-w-xs text-sm leading-relaxed text-gray-500">
                    Christian media you can trust — sermons, series and courses, free and always here.
                </p>
            </div>
            <nav v-for="column in columns" :key="column.heading" :aria-label="column.heading">
                <p class="text-xs font-semibold tracking-wider text-gray-500 uppercase">{{ column.heading }}</p>
                <ul class="mt-3 space-y-2">
                    <li v-for="link in column.links" :key="link.name">
                        <Link
                            :href="link.href"
                            class="focus-visible:ring-ring rounded text-sm text-gray-400 transition-colors duration-150 outline-none hover:text-white focus-visible:ring-2"
                        >
                            {{ link.name }}
                        </Link>
                    </li>
                </ul>
            </nav>
        </div>
        <div class="border-t border-white/5">
            <div class="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3 px-4 py-5 lg:px-8">
                <p class="text-xs text-gray-600">© {{ year }} Clayton TV</p>
                <div class="flex items-center gap-3">
                    <div class="flex items-center gap-2">
                        <span class="text-xs text-gray-600">Text size</span>
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
                            class="focus-visible:ring-ring inline-flex min-h-11 min-w-11 items-center justify-center rounded-md text-gray-500 transition-colors duration-150 outline-none hover:text-white focus-visible:ring-2"
                        >
                            <component :is="social.icon" class="h-5 w-5 stroke-[1.5]" aria-hidden="true" />
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </footer>
</template>
