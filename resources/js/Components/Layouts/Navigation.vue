<style type="text/css">
#browseMenuCheckbox:checked ~ #browseMenuCheckboxLabel {
    box-shadow: inset 0px 0px 0px 2px;
    border-color: transparent;
}
/* Make the menu div visible whenever its checkbox is ticked. Tailwind classes make it always visible on larger screens */
#browseMenuCheckbox:checked ~ #browseMenuDiv {
    display: contents;
}
</style>

<script setup>
const browseMenuItems = [
    {
        url: "#",
        name: "Series",
    },
    {
        url: "#",
        name: "Topics",
    },
    {
        url: "#",
        name: "Livestream",
    },
]
</script>

<template>
    <header class="bg-claytonBlack text-claytonRed rounded-lg m-1 md:m-2">
        <nav
            class="flex flex-wrap items-center justify-between p-3 select-none"
            aria-label="Global">
            <h1 class="text-2xl md:text-3xl lg:text-4xl font-bold md:pr-2">Clayton&nbsp;TV</h1>

            <!-- Use so-called "checkbox hack" for the menu. Label is used as menu button and is hidden on larger screens, checkbox itself is always hidden -->
            <input type="checkbox" id="browseMenuCheckbox" hidden></input>
            <label id="browseMenuCheckboxLabel" for="browseMenuCheckbox" class="cursor-pointer border border-claytonRed rounded-lg p-1.5 ml-auto md:hidden">Browse</label>

            <div id="browseMenuDiv" class="hidden md:contents">
                <div class="block w-full items-center md:w-auto md:flex md:grow md:place-content-end order-last md:order-none">
                    <a v-for="(item, index) in browseMenuItems" :key="index" :href="item.url" class="hover:underline my-3 md:mx-2 md:my-0 flex">{{ item.name }}</a>

                    <div id="searchBox" class="mt-5 md:my-0 md:ml-2 md:mr-0 md:flex grow min-w-40 md:max-w-96">
                        <form class="rounded-lg hover:outline-claytonRed focus-within:outline-claytonRed bg-gray-800 hover:outline focus-within:outline focus-within:bg-gray-700 flex flex-wrap shrink grow outline-2">
                            <input
                                type="search"
                                id="navbar-search"
                                class="p-1.5 text-gray-100 bg-transparent outline-none w-20 flex shrink grow"
                                placeholder="Search"
                                required />
                            <button
                                type="submit"
                                class="bg-claytonRed hover:bg-claytonRed focus:outline-claytonRed rounded-r-md p-1.5 text-gray-900 focus:outline focus:outline-1 grow-0">
                                Search
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        </nav>
    </header>
</template>

