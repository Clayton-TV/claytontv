<script setup lang="ts">
import { Link } from '@inertiajs/vue3'
import { Github, Youtube } from 'lucide-vue-next'
import LogoMark from '@/atoms/LogoMark.vue'
import { Button } from '@/ui/button'
import { Input } from '@/ui/input'

const year = new Date().getFullYear()
</script>

<template>
    <footer class="bg-gradient-to-b from-gray-800 to-gray-950 text-gray-300">
        <div class="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
            <!-- Newsletter -->
            <div class="mx-auto max-w-lg">
                <h3 class="text-xl font-bold text-white">Want some occasional updates from us?</h3>
                <form class="mt-4 flex flex-col gap-3">
                    <Input
                        type="email"
                        name="email"
                        placeholder="Enter your email"
                        required
                        class="h-12 w-full rounded-lg border-white/20 bg-white/10 text-sm text-white placeholder:text-gray-400 focus:border-white/40"
                    />
                    <Button type="submit" class="h-12 w-full text-base font-semibold">Subscribe</Button>
                </form>
            </div>

            <!-- Branding + socials -->
            <div class="mt-12 flex flex-col items-center gap-4">
                <Link href="/" class="flex items-center gap-3">
                    <LogoMark class="size-12 fill-red-500" />
                    <span class="text-3xl font-bold text-white">Clayton TV</span>
                </Link>
                <p class="text-base italic text-gray-400">Your digital catalogue for Godly content.</p>

                <!-- Social icons -->
                <div class="mt-2 flex items-center gap-3">
                    <a
                        href="https://www.youtube.com/@ClaytonTV"
                        target="_blank"
                        rel="noopener noreferrer"
                        class="flex size-12 items-center justify-center rounded-lg bg-white/10 text-gray-300 transition-colors hover:bg-white/20 hover:text-white"
                        aria-label="YouTube"
                    >
                        <Youtube class="size-6" />
                    </a>
                    <a
                        href="https://vimeo.com/claytontv"
                        target="_blank"
                        rel="noopener noreferrer"
                        class="flex size-12 items-center justify-center rounded-lg bg-white/10 text-gray-300 transition-colors hover:bg-white/20 hover:text-white"
                        aria-label="Vimeo"
                    >
                        <svg class="size-6" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M23.977 6.416c-.105 2.338-1.739 5.543-4.894 9.609C15.9 20.48 12.96 22.5 10.548 22.5c-1.49 0-2.751-1.38-3.783-4.135l-2.07-7.584C3.966 8.023 3.19 6.643 2.358 6.643c-.188 0-.845.396-1.97 1.185L-.001 7.23c1.238-1.09 2.46-2.18 3.658-3.269 1.65-1.427 2.888-2.178 3.715-2.253 1.952-.189 3.152 1.146 3.604 4.005.486 3.086.824 5.006 1.012 5.756.562 2.556 1.18 3.834 1.855 3.834.524 0 1.311-.829 2.36-2.487 1.047-1.66 1.608-2.924 1.68-3.792.15-1.435-.414-2.153-1.69-2.153-.601 0-1.22.138-1.856.414 1.232-4.038 3.587-5.999 7.066-5.883 2.58.075 3.796 1.749 3.574 5.034z" />
                        </svg>
                    </a>
                    <a
                        href="https://github.com/Clayton-TV"
                        target="_blank"
                        rel="noopener noreferrer"
                        class="flex size-12 items-center justify-center rounded-lg bg-white/10 text-gray-300 transition-colors hover:bg-white/20 hover:text-white"
                        aria-label="GitHub"
                    >
                        <Github class="size-6" />
                    </a>
                </div>
            </div>

            <!-- Copyright -->
            <p class="mt-10 text-center text-sm text-gray-500">&copy; {{ year }} The Jesmond Trust. All rights reserved.</p>
        </div>
    </footer>
</template>
