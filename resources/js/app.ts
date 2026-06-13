import '../css/app.css';

import { createInertiaApp, router } from '@inertiajs/vue3';
import { createApp, createSSRApp, DefineComponent, h } from 'vue';
import { useFlash } from '~/composables/useFlash';
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

        const app = create({ render: () => h(App, props) }).use(plugin);

        // Last-resort handler for uncaught Vue errors that escape the
        // ErrorBoundary — surface a calm toast (and log for Sentry later).
        app.config.errorHandler = (err, _instance, info) => {
            console.error('[vue:errorHandler]', err, info);
            useFlash().push('Something went wrong. Please try again.', 'error');
        };

        app.mount(el);
    },
    progress: {
        // Brand red (matches --primary) so navigation feedback reads as intentional
        color: 'oklch(0.637 0.237 25.331)',
    },
});

// A failed visit (server 500 / non-Inertia response / network drop) shows a
// friendly toast instead of Inertia's raw error modal.
router.on('invalid', (event) => {
    event.preventDefault();
    useFlash().push("That page couldn't be loaded. Please try again.", 'error');
});
router.on('exception', () => {
    useFlash().push('A network error stopped that request. Please try again.', 'error');
});

initializeTheme();
initializeTextScale();
initializeAnalytics();
