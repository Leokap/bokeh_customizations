import {GlyphRenderer} from "models/renderers/glyph_renderer"

declare global {
    interface Window {
        _bokeh_last_mute_update?: number;
    }
}

export function mute_others(renderers: {[key: string]: GlyphRenderer}, index: number): void {
    /*
     * This function assumes there are two possible states of mute:
     * 1. All renderers are unmuted. In that case clicking on a line should mute all others.
     *
     * 2. Only one renderer is unmuted. In that case there are two possible events:
     *      1. The unmuted line is clicked. Then everything should be reverted to unmuted again.
     *      2. A muted line is clicked. Then it should unmute that line and mute the currently unmuted line.
     */
    const now = Date.now();
    // debounce change events that might be triggered by
    // a previous event running this same callback.
    if (window._bokeh_last_mute_update && (now - window._bokeh_last_mute_update < 200)) {
        return;
    }
    window._bokeh_last_mute_update = now;

    const all_renderers = Object.values(renderers);
    const clicked = all_renderers[index];

    // We will now check if the clicked renderer is already muted.
    // NOTE: at this point the click will already have triggered
    // a toggle of the renderers mute-state.
    // thus clicked.muted is the opposite of what it was before the click.
    if (clicked.muted) {
        // It was NOT muted *before* the click.
        // Thus this handles cases 1 and 2.1 from the docstring above.
        // As always we want the clicked line to be unmuted.
        // But also: if the other lines where unmuted, they should become muted.
        // if they were muted, we would unmute them. Thus:
        // Everything needs to be toggled!
        for (const r of all_renderers) {
            r.muted = !r.muted;
            r.change.emit();
        }
    } else {
        // It was muted *before* the click.
        // thus, this handles case 2.2 from the docstring.
        // Bokeh already unmuted the clicked line. Now lets mute all other lines.
        for (let i = 0; i < all_renderers.length; i++) {
            if (i !== index) {
                all_renderers[i].muted = true;
                all_renderers[i].change.emit();
            }
        }
    }
}


