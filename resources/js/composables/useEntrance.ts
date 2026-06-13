/**
 * One quiet entrance per page-load, staggered top-to-bottom in reading order —
 * information hierarchy, not decoration. CSS-driven (tw-animate-css), so it
 * costs no runtime JS and collapses entirely under prefers-reduced-motion.
 *
 * Usage:  <section v-bind="entrance(140)"> … </section>
 */
export function entrance(delayMs = 0) {
    return {
        class: 'animate-in fade-in-0 slide-in-from-bottom-3 fill-mode-both duration-300 ease-out motion-reduce:animate-none',
        style: { animationDelay: `${delayMs}ms` },
    };
}

export function useEntrance() {
    return { entrance };
}
