<script setup lang="ts">
import type { TabsTriggerProps } from 'reka-ui';
import type { HTMLAttributes } from 'vue';
import { cn } from '@/lib/utils';
import { reactiveOmit } from '@vueuse/core';
import { TabsTrigger, useForwardProps } from 'reka-ui';

const props = defineProps<TabsTriggerProps & { class?: HTMLAttributes['class'] }>();

const delegatedProps = reactiveOmit(props, 'class');
const forwarded = useForwardProps(delegatedProps);
</script>

<template>
    <TabsTrigger
        data-slot="tabs-trigger"
        v-bind="forwarded"
        :class="
            cn(
                'data-[state=active]:bg-background data-[state=active]:text-foreground focus-visible:ring-ring text-muted-foreground inline-flex h-8 flex-1 items-center justify-center gap-1.5 rounded-md px-3 py-1 text-sm font-medium whitespace-nowrap transition-colors outline-none focus-visible:ring-2 disabled:pointer-events-none disabled:opacity-50 data-[state=active]:shadow-sm [&_svg]:size-4 [&_svg]:shrink-0',
                props.class,
            )
        "
    >
        <slot />
    </TabsTrigger>
</template>
