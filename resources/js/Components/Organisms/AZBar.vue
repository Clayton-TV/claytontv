<template>
    <div class="p-2 bg-gray-200">
        <div class="text-lg px-3 pb-2">
            Filter A-Z:
        </div>
        <ul class="grid grid-flow-col auto-cols-fr text-nowrap text-center text-xs sm:text-sm md:text-lg lg:text-xl" role="radio">
            <li v-for="x in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'" class="m-0.5 border-2 rounded border-gray-400 hover:border-red-600">
                {{x}}
            </li>
            <li class="m-0.5 border-2 rounded border-gray-400 hover:border-red-600">
                0-9
            </li>
        </ul>
    </div>
</template>
