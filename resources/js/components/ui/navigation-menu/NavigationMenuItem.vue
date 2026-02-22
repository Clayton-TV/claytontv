<script setup lang="ts">
import type { NavigationMenuItemProps } from 'reka-ui'
import type { HTMLAttributes } from 'vue'
import { reactiveOmit } from '@vueuse/core'
import { NavigationMenuItem, useForwardProps } from 'reka-ui'
import { cn } from '@/lib/utils'

const props = defineProps<NavigationMenuItemProps & { class?: HTMLAttributes['class'] }>()

const delegatedProps = reactiveOmit(props, 'class')
const forwardedProps = useForwardProps(delegatedProps)
</script>

<template>
    <NavigationMenuItem
        data-slot="navigation-menu-item"
        v-bind="forwardedProps"
        :class="cn('relative', props.class)"
    >
        <slot />
    </NavigationMenuItem>
</template>
