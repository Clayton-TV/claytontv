<script setup>
    const letters = [
        ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'],
        ['J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R'],
        ['S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '0-9']
    ];
    let lettersSet = 0;

    function updateShownLetters(dir: number) {
        // dir = 1 for next set, -1 for previous, or leave to refresh display of current set
        if (dir == 1 && lettersSet < 2) {
            // Hide 1st half of alphabet, show 2nd, move dots to start
            lettersSet++;
        } else if (dir == -1 && lettersSet > 0) {
            // Hide 2nd half of alphabet, show 1st, move dots to end
            lettersSet--;
        }
        for (let i = 0; i < 3; i++) {
            // Show only the current set of letters (set its div display property to "contents", others to "none")
            document.getElementById("lettersDiv" + i)!.style.display = (i == lettersSet) ? "contents" : "none";
        }
        // Hide move-forward-dots if on last set of letters
        document.getElementById("lettersDotsFwd")!.style.display = (lettersSet == 2) ? "none" : "contents";
        // Hide move-backward-dots if on first set of letters
        document.getElementById("lettersDotsBack")!.style.display = (lettersSet == 0) ? "none" : "contents";
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
                <div v-for="lettersGroup in letters" class="contents">
                    <li v-for="x in lettersGroup" class="m-0.5 border-2 rounded border-gray-400 hover:border-claytonRed">
                        {{ x }}
                    </li>
                </div>
            </div>

            <!-- For smaller screens the list is split and shown one part at a time, with dots to move fwd/back -->
            <div id="splitList" class="contents lg:hidden xl:hidden 2xl:hidden">
                <div id="lettersDotsBack" style="display: none">
                    <li v-on:click="updateShownLetters(-1)">
                        ...
                    </li>
                </div>
                <!-- Create a div per letter group, each with its own id, and only show one to start with -->
                <div v-for="(lettersGroup, lettersIndex) in letters" v-bind:id="'lettersDiv' + lettersIndex" v-bind:style="lettersSet == lettersIndex ? 'display: contents' : 'display: none'">
                    <li v-for="x in lettersGroup" class="m-0.5 border-2 rounded border-gray-400 hover:border-claytonRed">
                        {{ x }}
                    </li>
                </div>
                <div id="lettersDotsFwd">
                    <li v-on:click="updateShownLetters(1)">
                        ...
                    </li>
                </div>
            </div>
        </ul>
    </div>
</template>
