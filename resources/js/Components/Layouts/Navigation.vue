<template>
    <header class="bg-claytonBlack text-claytonRed">
        <nav
            class="flex flex-wrap items-center justify-between p-6 lg:px-8"
            aria-label="Global">
            <div class="flex items-center"><h1 class="my-4 text-5xl font-bold">Clayton&nbsp;TV</h1></div>

            <!-- Search box -->
            <form class="my-2 block rounded-xl border-claytonRed hover:outline-claytonRed focus-within:outline-claytonRed bg-gray-800 hover:outline focus-within:outline focus-within:bg-gray-700">
                <input
                    type="search"
                    id="navbar-search"
                    class="p-2 w-auto text-gray-100 bg-transparent outline-none"
                    placeholder="Search"
                    required />
                <button
                    type="submit"
                    class="bg-claytonRed hover:bg-claytonRed focus:outline-claytonRed rounded-br-lg rounded-tr-lg p-2 text-gray-900 focus:outline focus:outline-1">
                    Search
                </button>
            </form>

        </nav>
    </header>
</template>
