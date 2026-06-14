<script setup lang="ts">
import type { TabsContentProps } from 'reka-ui';
import type { HTMLAttributes } from 'vue';
import { cn } from '@/lib/utils';
import { reactiveOmit } from '@vueuse/core';
import { TabsContent, useForwardProps } from 'reka-ui';

const props = defineProps<TabsContentProps & { class?: HTMLAttributes['class'] }>();

const delegatedProps = reactiveOmit(props, 'class');
const forwarded = useForwardProps(delegatedProps);
</script>

<template>
    <TabsContent
        data-slot="tabs-content"
        v-bind="forwarded"
        :class="cn('flex-1 outline-none', props.class)"
    >
        <slot />
    </TabsContent>
</template>
