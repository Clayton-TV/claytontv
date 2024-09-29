<style type="text/css">
#menuCheckboxLabel {
    cursor: pointer;
}
/* Make the menuDiv visible whenever the menuCheckbox is ticked. Tailwind classes make it always visible on larger screens */
#menuCheckbox:checked ~ #menuDiv {
    display: contents;
}
</style>

<template>
    <header class="bg-claytonBlack text-claytonRed">
        <nav
            class="flex flex-wrap items-center justify-between px-6 py-4 lg:px-8"
            aria-label="Global">
            <h1 class="my-4 text-4xl md:text-5xl lg:text-6xl font-bold">Clayton&nbsp;TV</h1>

            <!-- Use so-called "checkbox hack" for the menu. Label is used as menu button and is hidden on larger screens, checkbox itself is always hidden -->
            <input type="checkbox" id="menuCheckbox" hidden></input>
            <label id="menuCheckboxLabel" for="menuCheckbox" class="border border-claytonRed rounded p-2 lg:hidden">MENU</label>

            <div id="menuDiv" class="hidden lg:contents">
                <div class="block w-full items-center lg:w-auto lg:flex lg:grow lg:place-content-end lg:pl-2">
                    <a href="#" class="underline font-bold m-3 flex">Categories</a>
                    <a href="#" class="underline font-bold m-3 flex">Browse All A-Z</a>
                    <a href="#" class="underline font-bold m-3 flex">Latest Videos</a>
                    <a href="#" class="underline font-bold m-3 flex">Livestreams</a>

                    <div id="searchBox" class="m-3 lg:mr-0 lg:flex grow min-w-40 lg:max-w-96">
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
        </nav>
    </header>
</template>

