import colors from "tailwindcss/colors.js"

/** @type {import("tailwindcss").Config} */
export default {
    content: [
        "./templates/*.html",
        "./resources/js/**/*.{html,vue}",
    ],
    theme: {
        colors: {
            gray: colors.zinc,
            red: colors.red,
        },
        extend: {},
    },
    plugins: [],
}

