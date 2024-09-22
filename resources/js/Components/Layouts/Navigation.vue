<script setup>
const toggleMenuVisibility = () => {
    let menuDiv = document.getElementById("menuDiv");
    if (menuDiv.style.display == "none") {
        menuDiv.style.display = "contents";
    } else {
        menuDiv.style.display = "none";
    }
}
</script>

<template>
    <header class="bg-claytonBlack text-claytonRed">
        <nav
            class="flex flex-wrap items-center justify-between px-6 py-4 lg:px-8"
            aria-label="Global">
            <h1 class="my-4 text-4xl md:text-5xl lg:text-6xl font-bold">Clayton&nbsp;TV</h1>

            <!-- Button for the menu, hidden on larger screens -->
            <button class="border rounded p-2 lg:hidden" @click="toggleMenuVisibility()">Menu</button>

            <div id="menuDiv" class="contents">
            <div class="block w-full items-center lg:w-auto lg:flex lg:grow lg:place-content-end lg:pl-2">
                <a href="#" class="underline font-bold m-3 flex">Categories</a>
                <a href="#" class="underline font-bold m-3 flex">Browse All A-Z</a>
                <a href="#" class="underline font-bold m-3 flex">Latest Videos</a>
                <a href="#" class="underline font-bold m-3 flex">Livestreams</a>

                <div id="searchBox" class="m-3 lg:mr-0 lg:flex grow min-w-40 lg:max-w-96">
                    <form class="rounded-xl border-claytonRed hover:outline-claytonRed focus-within:outline-claytonRed bg-gray-800 hover:outline focus-within:outline focus-within:bg-gray-700 flex flex-wrap shrink grow">
                        <input
                            type="search"
                            id="navbar-search"
                            class="p-2 text-gray-100 bg-transparent outline-none w-20 flex shrink grow"
                            placeholder="Search"
                            required />
                        <button
                            type="submit"
                            class="bg-claytonRed hover:bg-claytonRed focus:outline-claytonRed rounded-br-lg rounded-tr-lg p-2 text-gray-900 focus:outline focus:outline-1 grow-0">
                            Search
                        </button>
                    </form>
                </div>
            </div>
            </div>
        </nav>
    </header>
</template>

