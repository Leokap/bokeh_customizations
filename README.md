# Bokeh Customizations

A extension-based implementation of keyboard shortcuts and other UI customizations for Bokeh plots.

## Features

- **Keyboard Shortcuts**: Adds a custom `KeyboardShortcutsTool` to the toolbar that enables:
  - `H`: Reset plot
  - `Z`: Undo
  - `Y`: Redo
  - `O`: Box Zoom
  - `P`: Pan
  - `V`: Toggle Hover
  - `Esc`: Release focus
- **Mute Others Click Policy**: Click a legend entry to mute all other renderers.
- **Segmented Line Plots**: Easily create line plots colored by segments.
- **Shared X Layouts**: Helpers for creating vertically aligned plots with shared x-axes and synchronized crosshairs.

## Usage

```python
from bokeh_customizations import standard_figure, show

p = standard_figure()
p.line([1, 2, 3], [4, 5, 6], legend_label="Data")
show(p)
```

## Setup

- The python code is in `src/bokeh_customizations/`.
- The typescript code is in `ts/`
- compiling it writes the output js files to `src/bokeh_customizations/js/`
- the Python code should than load the pre compiled js files from there.

## Development & Node.js Requirement

Normally, Bokeh requires **Node.js** at runtime to compile custom models (even if they are already JavaScript) and to extract their dependencies. 

This library uses a **bypass mechanism** located in `src/bokeh_customizations/__init__.py` to allow running on systems without Node.js.

### How it works:
1. **Cache Hook Hijack**: We register a custom `set_cache_hook` with Bokeh's compiler.
2. **Pre-compiled Detection**: The hook identifies JavaScript code that has already been compiled (looking for CommonJS exports).
3. **Regex Dependency Extraction**: Instead of using a full JS parser (which requires Node), we use a simple Regex to find `require()` calls.
4. **Bypass**: The hook returns the code and dependencies directly to Bokeh, making it think the compilation was already done and cached.

### Build Process (for Developers):
While users don't need Node.js, **developers** need it to compile TypeScript source files:

1. **Type Checking**: Run `bun run tsc` in the `ts/` directory. The `tsconfig.json` is configured to find Bokeh's `.d.ts` files directly from your Python `.venv`, so no `npm install` is needed for types and we always type check against the current version of bokeh. (You can find your own location of those type declarations with `f"{bokeh.settings.bokehjs_path()}/js/lib/*"` in python.)
2. **Compilation**: Run `uv run python build_js.py`. This script uses Bokeh's internal compiler to produce the `.js` files in `src/bokeh_customizations/js/`.

### Important Limitations:
- **False Positives**: Because we use Regex, a line like `// require("something")` in a comment will be incorrectly identified as a dependency and might cause Bokeh to fail if it can't find that module.
- **Internal Deps Only**: This approach works perfectly for core Bokeh modules (e.g., `models/tools/tool`) because they are already present in the browser's BokehJS library.
- **External Deps**: If you need external NPM libraries (not part of Bokeh), this bypass **will not work** unless you also manually bundle those libraries or load them via a CDN global.
