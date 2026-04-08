import re

from bokeh.util.compiler import (
    AttrDict,
    CustomModel,
    Implementation,
    JavaScript,
    get_cache_hook,
    set_cache_hook,
)

from .plotting import (
    apply_click_policy_mute_others,
    enable_keyboard_shortcuts,
    find_bokeh_tool_in_figure,
    get_column_layout_with_shared_x,
    insert_line_plot_with_segmented_coloring,
    standard_figure,
)

__all__ = [
    "standard_figure",
    "enable_keyboard_shortcuts",
    "apply_click_policy_mute_others",
    "insert_line_plot_with_segmented_coloring",
    "get_column_layout_with_shared_x",
    "find_bokeh_tool_in_figure",
]


"""
Here beginns the hijack of bokeh's caching system such that we can insert our own precompiled JS.

  How does the Hook skip compilation?
  Inside Bokeh's compiler.py, there is a function called _compile_models. Its logic looks roughly like this:

   1 # 1. Check if a "cache hook" is registered
   2 compiled = _CACHING_IMPLEMENTATION(model, impl)
   3
   4 # 2. If the hook returned nothing, call Node.js
   5 if compiled is None:
   6     compiled = nodejs_compile(impl.code, ...)

  By default, the hook is a "no-op" (returns None). By providing our own hook, we return an AttrDict containing the code and the deps. Bokeh sees this and says: "Great, I already have the compiled result and the dependency list from the cache. I don't need to call Node.js!"

"""


def _extract_deps(code: str) -> list[str]:
    """
    Extracts dependencies from require() calls in JavaScript code.
    This allows us to bypass the Node.js requirement for pre-compiled JS.
    Note: this isn't 100% accurate, just good enough for our usecases.
    It may return False Positives: Because we use Regex, a line like
    `// require("something")`
    in a comment will be incorrectly identified as a dependency and might
    cause Bokeh to fail if it can't find that module.

    Args:
        code: JavaScript code string to extract dependencies from.

    Returns:
        A list of dependency module names found in require() calls.
    """
    return re.findall(r'require\(["\']([^"\']+)["\']\)', code)


_original_hook = get_cache_hook()


def _bokeh_customizations_cache_hook(
    model: CustomModel, impl: Implementation
) -> AttrDict | None:
    """
    A cache hook that returns pre-compiled JavaScript implementation details,
    effectively bypassing the need for Node.js at runtime.

    This hook is registered with Bokeh's compiler to intercept model compilation.
    For pre-compiled JavaScript (identified by CommonJS exports), it extracts
    dependencies using regex and returns the code directly, skipping Node.js
    compilation entirely.

    Args:
        model: The Bokeh model being compiled.
        impl: The implementation object (JavaScript or TypeScript).

    Returns:
        An AttrDict with 'code' and 'deps' keys for pre-compiled JS, or None
        to fall back to the original hook or Node.js compilation.
    """
    if isinstance(impl, JavaScript):
        # We identify our pre-compiled models by the presence of CommonJS exports
        if (
            "exports.__esModule" in impl.code
            or 'Object.defineProperty(exports, "__esModule"' in impl.code
        ):
            return AttrDict(code=impl.code, deps=_extract_deps(impl.code))

    if _original_hook:
        return _original_hook(model, impl)
    return None


# Register the hook automatically when the package is imported
set_cache_hook(_bokeh_customizations_cache_hook)
