<script setup lang="ts">
import LogoMark from '@/atoms/LogoMark.vue';
import { Button } from '@/ui/button';
import { Input } from '@/ui/input';
import { Head, Link, useForm } from '@inertiajs/vue3';
import { computed } from 'vue';

// A focused, layout-free auth screen: editors meet our design from the first
// pixel, with nothing else on the page to distract. app.ts only applies the
// default AppLayout when `layout` is undefined, so an explicit null opts out.
// (Cast: Inertia's Vue types don't list null, but the resolver honours it.)
defineOptions({ layout: null as unknown as undefined });

const props = defineProps<{
    // Where to send the editor after a successful sign-in (defaults to /studio).
    next?: string;
}>();

// inertia-django 1.2 has no built-in error bag; the view shares
// `errors: { detail }` on a bad login and useForm surfaces it on `form.errors`
// (read below as `error`). The CSRF cookie is set server-side via
// @ensure_csrf_cookie so axios echoes X-CSRFToken on this POST.
const form = useForm({
    username: '',
    password: '',
    next: props.next ?? '/studio',
});

// The server shares a single `detail` error (not tied to a form field), so read
// it off the error bag directly — useForm's types only know the field names.
const error = computed(() => (form.errors as Record<string, string>).detail);

const submit = () => {
    form.post('/studio/login', {
        // Keep the typed username if the server re-renders with an error.
        onError: () => form.reset('password'),
    });
};
</script>

<template>
    <Head title="Editor sign in" />
    <div class="bg-background flex min-h-svh flex-col items-center justify-center px-4 py-12">
        <div class="w-full max-w-sm">
            <Link
                href="/"
                class="focus-visible:ring-ring mb-8 flex items-center justify-center gap-2.5 rounded outline-none focus-visible:ring-2"
                aria-label="Clayton TV home"
            >
                <LogoMark class="fill-primary h-7 w-auto" />
                <span class="font-display text-foreground text-base font-bold tracking-wide">Clayton&nbsp;TV</span>
            </Link>

            <div class="border-border bg-card rounded-xl border p-6 shadow-sm sm:p-8">
                <h1 class="text-foreground text-lg font-semibold">Studio sign in</h1>
                <p class="text-muted-foreground mt-1 text-sm">For editors. Accounts are created by an administrator.</p>

                <form class="mt-6 space-y-4" novalidate @submit.prevent="submit">
                    <div class="space-y-1.5">
                        <label for="username" class="text-foreground block text-sm font-medium">Username</label>
                        <Input
                            id="username"
                            v-model="form.username"
                            name="username"
                            type="text"
                            autocomplete="username"
                            autocapitalize="none"
                            autofocus
                            class="text-base"
                            :aria-invalid="!!error || undefined"
                        />
                    </div>

                    <div class="space-y-1.5">
                        <label for="password" class="text-foreground block text-sm font-medium">Password</label>
                        <Input
                            id="password"
                            v-model="form.password"
                            name="password"
                            type="password"
                            autocomplete="current-password"
                            class="text-base"
                            :aria-invalid="!!error || undefined"
                        />
                    </div>

                    <!-- Single shared error: we never reveal which field was wrong. -->
                    <p v-if="error" role="alert" class="text-destructive text-sm">
                        {{ error }}
                    </p>

                    <Button type="submit" class="w-full" :disabled="form.processing">
                        {{ form.processing ? 'Signing in…' : 'Sign in' }}
                    </Button>
                </form>
            </div>

            <p class="text-muted-foreground mt-6 text-center text-sm">
                <Link href="/" class="focus-visible:ring-ring hover:text-foreground rounded transition-colors outline-none focus-visible:ring-2">
                    Back to Clayton TV
                </Link>
            </p>
        </div>
    </div>
</template>
