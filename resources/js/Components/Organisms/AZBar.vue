<script setup>
    const lettersAM = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M'];
    const lettersNZ = ['N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '0-9'];
    var letters = "A-M";

    function switchLetters() {
        if (letters == "A-M") {
            // Hide 1st half of alphabet, show 2nd, move dots to start
            letters = "N-Z";
            document.getElementById("lettersDivAM").style.display = "none";
            document.getElementById("lettersDivNZ").style.display = "contents";
            document.getElementById("lettersDots").style.order = "-9999";
        } else {
            // Hide 2nd half of alphabet, show 1st, move dots to end
            letters = "A-M";
            document.getElementById("lettersDivNZ").style.display = "none";
            document.getElementById("lettersDivAM").style.display = "contents";
            document.getElementById("lettersDots").style.order = "9999";
        }
    }
</script>

<template>
    <div class="p-2 bg-gray-200">
        <div class="text-lg px-3 pb-2">
            Filter A-Z:
        </div>
        <ul class="grid grid-flow-col auto-cols-fr text-nowrap text-center text-lg" role="radio">
            <!-- Full list will be visible on larger screens -->
            <div id="fullList" class="hidden lg:contents xl:contents 2xl:contents">
                <li v-for="x in lettersAM" class="m-0.5 border-2 rounded border-gray-400 hover:border-red-600">
                    {{x}}
                </li>
                <li v-for="x in lettersNZ" class="m-0.5 border-2 rounded border-gray-400 hover:border-red-600">
                    {{x}}
                </li>
            </div>

            <!-- For smaller screens the list is split and shown one part at a time -->
            <div id="splitList" class="contents lg:hidden xl:hidden 2xl:hidden">
                <div id="lettersDivAM" class="contents">
                    <li v-for="x in lettersAM" class="m-0.5 border-2 rounded border-gray-400 hover:border-red-600">
                        {{x}}
                    </li>
                </div>
                <div id="lettersDivNZ" class="hidden">
                    <li v-for="x in lettersNZ" class="m-0.5 border-2 rounded border-gray-400 hover:border-red-600">
                        {{x}}
                    </li>
                </div>
                <li id="lettersDots" v-on:click="switchLetters()">
                    ...
                </li>
            </div>
        </ul>
    </div>
</template>
