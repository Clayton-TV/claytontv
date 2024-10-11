<style type="text/css">
/* Pointing-finger cursor to make it obvious the labels are clickable */
#browseMenuCheckboxLabel, #moreMenuCheckboxLabel {
    cursor: pointer;
}
/* Make the menu div visible whenever its checkbox is ticked. Tailwind classes make it always visible on larger screens */
#browseMenuCheckbox:checked ~ #browseMenuDiv {
    display: contents;
}
#moreMenuCheckbox:checked ~ #moreMenuDiv {
    display: block;
}
</style>

<template>
    <header class="bg-claytonBlack text-claytonRed">
        <nav
            class="flex flex-wrap items-center justify-between px-4 py-4 lg:px-6 select-none"
            aria-label="Global">
            <h1 class="my-4 text-4xl md:text-5xl lg:text-6xl font-bold">Clayton&nbsp;TV</h1>

            <!-- Use so-called "checkbox hack" for the menu. Label is used as menu button and is hidden on larger screens, checkbox itself is always hidden -->
            <input type="checkbox" id="browseMenuCheckbox" hidden></input>
            <label id="browseMenuCheckboxLabel" for="browseMenuCheckbox" onclick="document.getElementById('moreMenuCheckbox').checked=false" class="border border-claytonRed rounded p-2 mx-1 ml-auto lg:hidden">Browse</label>

            <input type="checkbox" id="moreMenuCheckbox" hidden></input>
            <label id="moreMenuCheckboxLabel" for="moreMenuCheckbox" onclick="document.getElementById('browseMenuCheckbox').checked=false" class="order-9 border border-claytonRed rounded p-2 mx-1">Menu</label>

            <div id="browseMenuDiv" class="hidden lg:contents">
                <div class="block w-full items-center lg:w-auto lg:flex lg:grow lg:place-content-end lg:px-2 order-last lg:order-none">
                    <a href="#" class="underline font-bold mx-2 mb-3 lg:my-0 flex">Categories</a>
                    <a href="#" class="underline font-bold mx-2 mb-3 lg:my-0 flex">Browse All A-Z</a>
                    <a href="#" class="underline font-bold mx-2 mb-3 lg:my-0 flex">Latest Videos</a>
                    <a href="#" class="underline font-bold mx-2 mb-3 lg:my-0 flex">Livestreams</a>

                    <div id="searchBox" class="mx-2 mb-1 mt-5 lg:my-0 lg:mr-0 lg:flex grow min-w-40 lg:max-w-96">
                        <form class="rounded-xl hover:outline-claytonRed focus-within:outline-claytonRed bg-gray-800 hover:outline focus-within:outline focus-within:bg-gray-700 flex flex-wrap shrink grow">
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

            <div id="moreMenuDiv" class="hidden lg:relative w-full order-10">
                <div class="w-full items-center lg:w-60 lg:absolute bg-claytonBlack border-claytonRed lg:border-2 rounded-tl-xl rounded-b-xl right-0 z-50">
                    <a href="#" class="underline font-bold mx-2 mb-3 flex" onclick="document.getElementById('moreMenuCheckbox').checked = false;">About</a>
                    <a href="#" class="underline font-bold mx-2 mb-3 flex" onclick="document.getElementById('moreMenuCheckbox').checked = false;">Contact</a>
                    <a href="#" class="underline font-bold mx-2 mb-3 flex" onclick="document.getElementById('moreMenuCheckbox').checked = false;">Subscribe</a>
                    <a href="#" class="underline font-bold mx-2 mb-3 flex" onclick="document.getElementById('moreMenuCheckbox').checked = false;">Another item</a>
                </div>
            </div>
        </nav>
    </header>
</template>

