<script setup>
import { computed } from "vue"
import { IconPlayerPlay } from "@tabler/icons-vue"
import { Link, router } from "@inertiajs/vue3"
import VideoCardList from "@/Organisms/VideoCardList.vue"

const props = defineProps({
})


const formModel = [
    {field: "demographic", text: "Demographic", value: null },
    {field: "labels", text: "Labels", value: null },
    {field: "ministry", text: "Ministry", value: null },
    {field: "series", text: "Series", value: null },
    {field: "subseries", text: "Subseries", value: null },
    {field: "episode", text: "Episode", value: null },
    {field: "speaker", text: "Speaker / Artist", value: null },
    {field: "biblebooks", text: "Bible Books", value: null },
    {field: "daterecorded", text: "Date Recorded", value: null, type: "date" },
    {field: "datecreated", text: "Date Created", value: null, type: "date" },
    {field: "datemodified", text: "Date Modified", value: null, type: "date" },
    {field: "islivestream", text: "Is Livestream", value: null, type: "checkbox" },
    {field: "channel", text: "Channel", value: null },
    {field: "topic", text: "Topic", value: null },
]

const submitForm = () => {
    console.log(formModel)
}
</script>

<template>

<form @submit.prevent="submitForm" class="m-10 text-gray-100">
    <div class="flex flex-col items-start sm:grid sm:grid-cols-[auto_minmax(12rem,90vw)] gap-2">
        <div v-for="param in formModel" class="contents">
            <label :for="`input_`+param.field" class="py-2 w-auto">{{ param.text }}:</label>
            <input :id="`input_`+param.field" @input="(e) => {param.value = e.target.value}" :type="param.type ? param.type : `text`" :name="param.field" class="outline-none px-2 h-full bg-transparent w-full border-b" />
        </div>
        <input type="submit" class="h-8 bg-claytonYellow w-full text-gray-900 col-span-2" text="Submit!!"></input>
    </div>
</form>

</template>
