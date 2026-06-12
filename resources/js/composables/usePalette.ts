import { ref } from 'vue';

// Shared open state: the header trigger, global ⌘K/'/' keys and the help
// sheet's "?" all drive the same two dialogs.
const paletteOpen = ref(false);
const helpOpen = ref(false);

export function usePalette() {
    return { paletteOpen, helpOpen };
}
