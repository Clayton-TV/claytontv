<template>
    <header class="bg-claytonBlack text-claytonRed">
        <nav
            class="mx-auto flex flex-wrap items-center justify-between p-6 lg:px-8"
            aria-label="Global">
            <h1 class="my-4 ml-4 text-5xl font-bold">Clayton&nbsp;TV</h1>
            <form class="relative my-2 mr-4 rounded-2xl">
                <input
                    type="search"
                    id="navbar-search"
                    class="border-claytonRed hover:outline-claytonRed focus:outline-claytonRed rounded-xl border-2 bg-gray-800 p-2 text-gray-100 hover:outline focus:bg-gray-700 focus:outline"
                    placeholder="Search"
                    required />
                <button
                    type="submit"
                    class="bg-claytonRed hover:bg-claytonRed focus:outline-claytonRed absolute bottom-1 end-1 rounded-br-lg rounded-tr-lg p-1.5 text-gray-900 focus:outline focus:outline-1">
                    Search
                </button>
            </form>
        </nav>
    </header>
</template>
