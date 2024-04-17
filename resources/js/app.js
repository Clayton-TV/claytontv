import '../css/app.css'

import { createInertiaApp } from "@inertiajs/vue3"
import { createApp, h } from 'vue'
import { resolvePageComponent } from './inertia-helpers.js'

console.log('Hello, world!')

import AppLayout from '@/Layouts/AppLayout.vue'

const appName = window.document.getElementsByTagName("title")[0]?.innerText || "ClaytonTV";

createInertiaApp({
    title: (title) => title.trim() === '' ? appName : `${title} - ${appName}`,
    resolve: (name) => {
        const page = resolvePageComponent(
            `./Components/Pages/${name}.vue`,
            import.meta.glob('./Components/Pages/**/*.vue')
        )

        page.then((module) => {
            const page = module.default
            let layout = page.layout

            if (layout === undefined) {
                layout = AppLayout
            }

            page.layout = layout
        })

        return page
    },
    setup({ el, App, props, plugin }) {
        console.log(el)
        const app = createApp({ render: () => h(App, props) })

        app.use(plugin)

        return app.mount(el)
    },
    progress: {
        color: '#3b82f6',
    }
})