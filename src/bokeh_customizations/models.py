from pathlib import Path

from bokeh.core.properties import Override
from bokeh.models import ActionTool
from bokeh.util.compiler import JavaScript, TypeScript

# Paths to the implementation files
_module_dir = Path(__file__).parent
_js_dir = _module_dir / "js"


def load_js_implementation(js_filename: str) -> JavaScript | TypeScript:
    """
    Loads a pre-compiled JavaScript implementation from the js directory.
    If the .js file is missing, it falls back to the .ts source.

    Args:
        js_filename: The filename of the JavaScript implementation to load.

    Returns:
        A JavaScript or TypeScript object containing the implementation code.

    Raises:
        FileNotFoundError: If neither the .js file nor the .ts source file exists.
    """
    js_path = _js_dir / js_filename
    if js_path.exists():
        with open(js_path, "r") as f:
            # We return a JavaScript object so our hook in __init__.py can catch it
            return JavaScript(f.read(), file=str(js_path))

    # Fallback to .ts for development if Node is available
    ts_path = (
        _module_dir.parent.parent / "ts" / "src" / js_filename.replace(".js", ".ts")
    )
    if ts_path.exists():
        with open(ts_path, "r") as f:
            # We return a TypeScript object. Our hook will ignore this,
            # so Bokeh will attempt to compile it using Node.js.
            return TypeScript(f.read(), file=str(ts_path))

    raise FileNotFoundError(f"Neither {js_path} nor {ts_path} found.")


SHORTCUTS_DESCRIPTION = """
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
"""


class KeyboardShortcutsTool(ActionTool):
    """
    A Bokeh tool that enables keyboard shortcuts and displays a help dialog.
    """

    __implementation__ = load_js_implementation("keyboard_shortcuts.js")

    description: Override[str] = Override(default=SHORTCUTS_DESCRIPTION)
    icon: Override[str] = Override(
        default="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIGNsYXNzPSJmZWF0aGVyIGZlYXRoZXItaGVscC1jaXJjbGUiPjxjaXJjbGUgY3g9IjEyIiBjeT0iMTIiIHI9IjEwIj48L2NpcmNsZT48cGF0aCBkPSJNOS4wOSA5YTMgMyAwIDAgMSA1LjgzIDFjMCAyLTMgMy0zIDMiPjwvcGF0aD48bGluZSB4MT0iMTIiIHkxPSIxNyIgeDI9IjEyLjAxIiB5Mj0iMTciPjwvbGluZT48L3N2Zz4="
    )
