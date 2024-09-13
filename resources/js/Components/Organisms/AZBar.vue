<template>
    <div class="p-2 bg-gray-200">
        <div class="text-lg px-3 pb-2">
            Filter A-Z:
        </div>
        <ul class="grid grid-flow-col auto-cols-fr text-nowrap text-center text-lg" role="radio">
            <li v-for="x in 'ABCDEFGHIJKLM'" class="m-0.5 border-2 rounded border-gray-400 hover:border-red-600">
                {{x}}
            </li>
            <li class="lg:hidden xl:hidden 2xl:hidden">
            ...
            </li>
            <li v-for="x in 'NOPQRSTUVWXYZ'" class="m-0.5 border-2 rounded border-gray-400 hover:border-red-600 hidden lg:inline xl:inline 2xl:inline">
                {{x}}
            </li>
            <li class="m-0.5 border-2 rounded border-gray-400 hover:border-red-600 hidden lg:inline xl:inline 2xl:inline">
                0-9
            </li>
        </ul>
    </div>
</template>
