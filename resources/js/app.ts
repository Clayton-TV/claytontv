import '../css/app.css';

import { createInertiaApp } from '@inertiajs/vue3';
import { createApp, createSSRApp, DefineComponent, h } from 'vue';
import { initializeAnalytics } from '~/lib/analytics';
import { resolvePageComponent } from '~/lib/inertia-helper';
import { initializeTheme } from './composables/useAppearance';
import { initializeTextScale } from './composables/useTextScale';

import AppLayout from '@/layouts/AppLayout.vue';

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
        // Hydrate when the page arrived server-rendered, mount fresh otherwise
        const create = el.hasChildNodes() ? createSSRApp : createApp;

        create({ render: () => h(App, props) })
            .use(plugin)
            .mount(el);
    },
    progress: {
        // Brand red (matches --primary) so navigation feedback reads as intentional
        color: 'oklch(0.637 0.237 25.331)',
    },
});

initializeTheme();
initializeTextScale();
initializeAnalytics();
