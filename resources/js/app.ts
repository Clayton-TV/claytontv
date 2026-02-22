import '../css/app.css';

import { createInertiaApp } from '@inertiajs/vue3';
import { createApp, DefineComponent, h } from 'vue';
import { resolvePageComponent } from '~/lib/inertia-helper';
import { initializeTheme } from './composables/useAppearance';

import AppLayout from '~/layouts/AppLayout.vue';

const appName = import.meta.env.VITE_APP_NAME || 'Clayton TV';

createInertiaApp({
    title: (title) => (title.trim() === '' ? appName : `${title} - ${appName}`),
    resolve: (name) => {
        const page = resolvePageComponent(`./pages/${name}.vue`, import.meta.glob<DefineComponent>('./pages/**/*.vue'));

        page.then((module) => {
            const page = module.default;
            let layout = page.layout;

            if (layout === undefined) {
                layout = AppLayout;
            }

            page.layout = layout;
        });

        return page;
    },
    setup({ el, App, props, plugin }) {
        createApp({ render: () => h(App, props) })
            .use(plugin)
            .mount(el);
    },
    progress: {
        color: '#4B5563',
    },
});

initializeTheme();
