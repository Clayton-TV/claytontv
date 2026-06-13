<script setup>
import { Link } from '@inertiajs/vue3';

defineProps({
    video: {
        type: Object,
        required: true,
    },
    video_metadata: {
        type: Object,
        required: false,
    },
});
</script>

<template>
    <div class="mx-4 mb-4 w-fit">
        <h1 class="text-l pb-3 font-bold lg:text-xl">Other content in...</h1>
        <div class="grid grid-cols-[auto_auto] gap-x-4 gap-y-3">
            <div class="contents" v-if="video_metadata.channel">
                <div class="py-2">Channel</div>
                <div class="flex flex-wrap gap-y-2">
                    <Link :href="video_metadata.channel.url" class="bg-muted text-foreground rounded-full px-4 py-2 font-bold hover:bg-red-400">{{
                        video_metadata.channel.name
                    }}</Link>
                </div>
            </div>

            <div class="contents" v-if="video_metadata.series">
                <div class="py-2">Series</div>
                <div class="flex flex-wrap gap-y-2">
                    <Link :href="video_metadata.series.url" class="bg-muted text-foreground rounded-full px-4 py-2 font-bold hover:bg-red-400">{{
                        video_metadata.series.name
                    }}</Link>
                </div>
            </div>

            <div class="contents" v-if="video_metadata.topic.length">
                <div class="py-2">Topic</div>
                <div class="flex flex-wrap gap-y-2">
                    <Link
                        v-for="x in video_metadata.topic"
                        :href="x.url"
                        :key="x.name"
                        class="bg-muted text-foreground mr-2 rounded-full px-4 py-2 font-bold hover:bg-red-400"
                        >{{ x.name }}</Link
                    >
                </div>
            </div>

            <div class="contents" v-if="video_metadata.ministry.length">
                <div class="py-2">Ministry</div>
                <div class="flex flex-wrap gap-y-2">
                    <Link
                        v-for="x in video_metadata.ministry"
                        :href="x.url"
                        :key="x.name"
                        class="bg-muted text-foreground mr-2 rounded-full px-4 py-2 font-bold hover:bg-red-400"
                        >{{ x.name }}</Link
                    >
                </div>
            </div>

            <div class="contents" v-if="video_metadata.speaker.length">
                <div class="py-2">Speaker</div>
                <div class="flex flex-wrap gap-y-2">
                    <Link
                        v-for="x in video_metadata.speaker"
                        :href="x.url"
                        :key="x.name"
                        class="bg-muted text-foreground mr-2 rounded-full px-4 py-2 font-bold hover:bg-red-400"
                        >{{ x.name }}</Link
                    >
                </div>
            </div>

            <div class="contents" v-if="video_metadata.bible_book.length">
                <div class="py-2">Book</div>
                <div class="flex flex-wrap gap-y-2">
                    <Link
                        v-for="x in video_metadata.bible_book"
                        :href="x.url"
                        :key="x.name"
                        class="bg-muted text-foreground mr-2 rounded-full px-4 py-2 font-bold whitespace-nowrap hover:bg-red-400"
                        >{{ x.name }}</Link
                    >
                </div>
            </div>

            <div class="contents" v-if="video_metadata.demographic.length">
                <div class="py-2">Demographic</div>
                <div>
                    <Link
                        v-for="x in video_metadata.demographic"
                        :href="x.url"
                        :key="x.name"
                        class="bg-muted text-foreground mr-2 rounded-full px-4 py-2 font-bold hover:bg-red-400"
                        >{{ x.name }}</Link
                    >
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped></style>
