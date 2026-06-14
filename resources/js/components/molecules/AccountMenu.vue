<script setup lang="ts">
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from '@/ui/dropdown-menu';
import { Link, router } from '@inertiajs/vue3';
import { LayoutGrid, LogOut } from 'lucide-vue-next';
import { computed } from 'vue';

/**
 * The signed-in user's account menu — an avatar (initials) at the far right of
 * the header that opens a dropdown with their identity, a link into the Studio
 * (editors only), and Sign out. The standard app-shell place for these, so
 * "Sign out" lives here rather than bolted onto a page header. Only rendered
 * when there's a user (see AppHeader); the slot is where a future public "Sign
 * in" entry point would go.
 */

const props = defineProps<{
    user: { name: string; email: string; can_edit?: boolean };
}>();

// Up to two initials from the display name, for the avatar.
const initials = computed(() => {
    const parts = props.user.name.trim().split(/\s+/).filter(Boolean);
    if (!parts.length) return '?';
    const first = parts[0][0];
    const last = parts.length > 1 ? parts[parts.length - 1][0] : '';
    return (first + last).toUpperCase();
});

function signOut() {
    router.post('/studio/logout');
}
</script>

<template>
    <DropdownMenu>
        <DropdownMenuTrigger
            class="focus-visible:ring-ring bg-secondary text-secondary-foreground hover:bg-accent hover:text-accent-foreground inline-flex size-10 shrink-0 items-center justify-center rounded-full text-sm font-semibold transition-colors outline-none focus-visible:ring-2"
            aria-label="Account menu"
        >
            {{ initials }}
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" class="w-56">
            <DropdownMenuLabel class="flex flex-col gap-0.5">
                <span class="text-foreground truncate text-sm font-medium">{{ user.name }}</span>
                <span v-if="user.email" class="text-muted-foreground truncate text-xs font-normal">{{ user.email }}</span>
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem v-if="user.can_edit" as-child>
                <Link href="/studio" class="flex cursor-pointer items-center gap-2">
                    <LayoutGrid class="size-4" aria-hidden="true" />
                    Studio
                </Link>
            </DropdownMenuItem>
            <DropdownMenuItem class="cursor-pointer" @select="signOut">
                <LogOut class="size-4" aria-hidden="true" />
                Sign out
            </DropdownMenuItem>
        </DropdownMenuContent>
    </DropdownMenu>
</template>
