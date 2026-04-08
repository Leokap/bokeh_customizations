import {ActionTool, ActionToolView} from "models/tools/actions/action_tool"
import {Tool} from "models/tools/tool"
import {PlotView} from "models/plots/plot_canvas"
import {Toolbar} from "models/tools/toolbar"
import {View} from "core/view"
import * as p from "core/properties"

declare global {
  interface HTMLElement {
    _bokeh_custom_shortcuts_attached?: boolean;
  }
}

export class KeyboardShortcutsToolView extends ActionToolView {
  declare model: KeyboardShortcutsTool

  override async lazy_initialize(): Promise<void> {
    await super.lazy_initialize()
    this._try_init_events()
  }

  doit(_arg?: unknown): void {
    alert(this.model.description)
  }

  protected _try_init_events(): void {
    const plot_view = this._get_plot_view()

    if (plot_view) {
      if (plot_view.has_finished()) {
        this._init_keyboard_events(plot_view)
      } else {
        plot_view.ready.then(() => {
          this._init_keyboard_events(plot_view)
        })
      }
    } else {
      setTimeout(() => this._try_init_events(), 200)
    }
  }

  protected _get_plot_view(): PlotView | null {
    let plot_view: PlotView | null = this.resolve_plot() as PlotView | null
    
    if (!plot_view) {
      let curr: View | null = this.parent
      while (curr) {
        if (curr.model.type === "Plot" || curr.model.type === "Figure") {
          plot_view = curr as PlotView
          break
        }
        curr = curr.parent
      }
    }
    return plot_view
  }

  protected _init_keyboard_events(plot_view: PlotView): void {
    const canvas = plot_view.canvas_view.events_el
    if (!canvas || canvas._bokeh_custom_shortcuts_attached) return

    canvas.tabIndex = 0
    canvas.style.outline = "none"

    canvas.addEventListener("keydown", (e: KeyboardEvent) => {
      const toolbar: Toolbar = plot_view.model.toolbar
      const tools = toolbar.tools
      
      const findTool = (type_name: string) => tools.find((t) => t.type.toLowerCase().includes(type_name))

      switch (e.key.toLowerCase()) {
        case "h":
          e.preventDefault()
          plot_view.model.reset.emit()
          break
        case "z":
          e.preventDefault()
          const undo = findTool("undo")
          if (undo instanceof ActionTool) undo.do.emit(undefined)
          break
        case "y":
          e.preventDefault()
          const redo = findTool("redo")
          if (redo instanceof ActionTool) redo.do.emit(undefined)
          break
        case "o":
          e.preventDefault()
          const box_zoom = findTool("boxzoom")
          if (box_zoom instanceof Tool) box_zoom.active = true
          break
        case "p":
          e.preventDefault()
          const pan = findTool("pan")
          if (pan instanceof Tool) pan.active = true
          break
        case "v":
          e.preventDefault()
          const hover = findTool("hover")
          if (hover instanceof Tool) hover.active = !hover.active
          break
        case "escape":
          e.preventDefault()
          this._moveFocusUp(canvas)
          break
      }
    })
    
    canvas._bokeh_custom_shortcuts_attached = true
  }

  protected _moveFocusUp(element: HTMLElement): void {
    let parent: Node | null = element.parentNode
    while (parent) {
      if (parent instanceof ShadowRoot) {
        parent = parent.host
        continue
      }
      if (parent instanceof HTMLElement) {
        if (parent.tabIndex >= 0 || parent.tagName === "BODY") {
          parent.focus()
          break
        }
      }
      parent = parent.parentNode
    }
  }
}

export namespace KeyboardShortcutsTool {
  export type Attrs = p.AttrsOf<Props>
  export type Props = ActionTool.Props & {
  }
}

export interface KeyboardShortcutsTool extends KeyboardShortcutsTool.Attrs {}

export class KeyboardShortcutsTool extends ActionTool {
  declare properties: KeyboardShortcutsTool.Props
  declare __view_type__: KeyboardShortcutsToolView

  constructor(attrs?: Partial<KeyboardShortcutsTool.Attrs>) {
    super(attrs)
  }

  static {
    this.prototype.default_view = KeyboardShortcutsToolView

    this.override<KeyboardShortcutsTool.Props>({
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
    })

    this.register_alias("keyboard_shortcuts" as any, () => new KeyboardShortcutsTool())
  }
}
