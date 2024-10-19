import colors from "tailwindcss/colors.js"

/** @type {import("tailwindcss").Config} */
export default {
    content: ["./templates/*.html", "./resources/js/**/*.{html,vue}"],
    theme: {
        extend: {
            colors: {
                claytonBlack: "#15062b",
                claytonRed: "#c21212",
                claytonGreen: "#68ed98",
                claytonYellow: "#f6be2d",
            },
        },
    },
    plugins: [],
}
