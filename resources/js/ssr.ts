import { createInertiaApp } from '@inertiajs/vue3';
import createServer from '@inertiajs/vue3/server';
import { type DefineComponent, createSSRApp, h } from 'vue';
import { renderToString } from 'vue/server-renderer';
import { resolvePageComponent } from '~/lib/inertia-helper';

import AppLayout from '@/layouts/AppLayout.vue';

const appName = import.meta.env.VITE_APP_NAME || 'Clayton TV';

createServer((page) =>
    createInertiaApp({
        page,
        render: renderToString,
        title: (title) => (title.trim() === '' ? appName : `${title} - ${appName}`),
        resolve: (name) => {
            const pageComponent = resolvePageComponent(`./pages/${name}.vue`, import.meta.glob<DefineComponent>('./pages/**/*.vue'));

            pageComponent.then((module) => {
                const component = module.default;

                if (component.layout === undefined) {
                    component.layout = AppLayout;
                }
            });

            return pageComponent;
        },
        setup({ App, props, plugin }) {
            return createSSRApp({ render: () => h(App, props) }).use(plugin);
        },
    }),
);
