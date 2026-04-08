"use strict";
var _a;
Object.defineProperty(exports, "__esModule", { value: true });
exports.KeyboardShortcutsTool = exports.KeyboardShortcutsToolView = void 0;
const action_tool_1 = require("models/tools/actions/action_tool");
const tool_1 = require("models/tools/tool");
class KeyboardShortcutsToolView extends action_tool_1.ActionToolView {
    async lazy_initialize() {
        await super.lazy_initialize();
        this._try_init_events();
    }
    doit(_arg) {
        alert(this.model.description);
    }
    _try_init_events() {
        const plot_view = this._get_plot_view();
        if (plot_view) {
            if (plot_view.has_finished()) {
                this._init_keyboard_events(plot_view);
            }
            else {
                plot_view.ready.then(() => {
                    this._init_keyboard_events(plot_view);
                });
            }
        }
        else {
            setTimeout(() => this._try_init_events(), 200);
        }
    }
    _get_plot_view() {
        let plot_view = this.resolve_plot();
        if (!plot_view) {
            let curr = this.parent;
            while (curr) {
                if (curr.model.type === "Plot" || curr.model.type === "Figure") {
                    plot_view = curr;
                    break;
                }
                curr = curr.parent;
            }
        }
        return plot_view;
    }
    _init_keyboard_events(plot_view) {
        const canvas = plot_view.canvas_view.events_el;
        if (!canvas || canvas._bokeh_custom_shortcuts_attached)
            return;
        canvas.tabIndex = 0;
        canvas.style.outline = "none";
        canvas.addEventListener("keydown", (e) => {
            const toolbar = plot_view.model.toolbar;
            const tools = toolbar.tools;
            const findTool = (type_name) => tools.find((t) => t.type.toLowerCase().includes(type_name));
            switch (e.key.toLowerCase()) {
                case "h":
                    e.preventDefault();
                    plot_view.model.reset.emit();
                    break;
                case "z":
                    e.preventDefault();
                    const undo = findTool("undo");
                    if (undo instanceof action_tool_1.ActionTool)
                        undo.do.emit(undefined);
                    break;
                case "y":
                    e.preventDefault();
                    const redo = findTool("redo");
                    if (redo instanceof action_tool_1.ActionTool)
                        redo.do.emit(undefined);
                    break;
                case "o":
                    e.preventDefault();
                    const box_zoom = findTool("boxzoom");
                    if (box_zoom instanceof tool_1.Tool)
                        box_zoom.active = true;
                    break;
                case "p":
                    e.preventDefault();
                    const pan = findTool("pan");
                    if (pan instanceof tool_1.Tool)
                        pan.active = true;
                    break;
                case "v":
                    e.preventDefault();
                    const hover = findTool("hover");
                    if (hover instanceof tool_1.Tool)
                        hover.active = !hover.active;
                    break;
                case "escape":
                    e.preventDefault();
                    this._moveFocusUp(canvas);
                    break;
            }
        });
        canvas._bokeh_custom_shortcuts_attached = true;
    }
    _moveFocusUp(element) {
        let parent = element.parentNode;
        while (parent) {
            if (parent instanceof ShadowRoot) {
                parent = parent.host;
                continue;
            }
            if (parent instanceof HTMLElement) {
                if (parent.tabIndex >= 0 || parent.tagName === "BODY") {
                    parent.focus();
                    break;
                }
            }
            parent = parent.parentNode;
        }
    }
}
exports.KeyboardShortcutsToolView = KeyboardShortcutsToolView;
KeyboardShortcutsToolView.__name__ = "KeyboardShortcutsToolView";
class KeyboardShortcutsTool extends action_tool_1.ActionTool {
    constructor(attrs) {
        super(attrs);
    }
}
exports.KeyboardShortcutsTool = KeyboardShortcutsTool;
_a = KeyboardShortcutsTool;
KeyboardShortcutsTool.__name__ = "KeyboardShortcutsTool";
(() => {
    _a.prototype.default_view = KeyboardShortcutsToolView;
    _a.override({
        description: `
Press shift to zoom via scroll wheel.
Doing so over one axis, scrolls just that axis.

Keyboard Shortcuts:
- H: Reset the plot to its original view (Home).
- Z: Undo the last action.
- Y: Redo the last undone action.
- O: Activate box zoom tool for zooming into specific areas.
- P: Activate pan tool to move the plot.
- V: Toggle visibility of hover tooltips.
- Esc: Release focus from the plot to re-enable JupyterLab shortcuts.
`,
        icon: 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIGNsYXNzPSJmZWF0aGVyIGZlYXRoZXItaGVscC1jaXJjbGUiPjxjaXJjbGUgY3g9IjEyIiBjeT0iMTIiIHI9IjEwIj48L2NpcmNsZT48cGF0aCBkPSJNOS4wOSA5YTMgMyAwIDAgMSA1LjgzIDFjMCAyLTMgMy0zIDMiPjwvcGF0aD48bGluZSB4MT0iMTIiIHkxPSIxNyIgeDI9IjEyLjAxIiB5Mj0iMTciPjwvbGluZT48L3N2Zz4='
    });
    _a.register_alias("keyboard_shortcuts", () => new _a());
})();
//# sourceMappingURL=keyboard_shortcuts.js.map