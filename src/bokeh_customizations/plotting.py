from pathlib import Path
from typing import Any, Sequence, Type, TypeVar

import numpy as np
import numpy.typing as npt
import pandas as pd
from bokeh.layouts import column
from bokeh.models import (
    Column,
    CrosshairTool,
    CustomJS,
    DataRange1d,
    GlyphRenderer,
    Span,
    Tool,
    WheelZoomTool,
)
from bokeh.palettes import Category20
from bokeh.plotting import figure

from .models import KeyboardShortcutsTool

__all__ = [
    "standard_figure",
    "enable_keyboard_shortcuts",
    "apply_click_policy_mute_others",
    "insert_line_plot_with_segmented_coloring",
    "get_column_layout_with_shared_x",
    "find_bokeh_tool_in_figure"
]

ToolTypeVar = TypeVar("ToolTypeVar", bound=Tool)


def find_bokeh_tool_in_figure(p: figure, tool_type: Type[ToolTypeVar]) -> ToolTypeVar | None:
    return next((tool for tool in p.tools if isinstance(tool, tool_type)), None)


def enable_keyboard_shortcuts(p: figure) -> KeyboardShortcutsTool:
    """
    Enables keyboard shortcuts for an existing figure by adding the KeyboardShortcutsTool.

    Args:
        p: The Bokeh figure to add keyboard shortcuts to.

    Returns:
        The KeyboardShortcutsTool instance that was added (or already present).
    """
    # Check if the tool is already present to avoid duplicates.
    tool = find_bokeh_tool_in_figure(p, KeyboardShortcutsTool)
    if tool is not None:
        return tool

    # The description is now handled by the tool's class defaults.
    shortcuts_tool = KeyboardShortcutsTool()
    p.add_tools(shortcuts_tool)
    return shortcuts_tool


def standard_figure(
    title: str | None = None,
    *args: Any,
    **kwargs: Any,
) -> figure:
    """
    Creates a figure with standard defaults and keyboard shortcuts enabled.

    Args:
        title: Optional title for the figure.
        *args: Additional positional arguments passed to bokeh.plotting.figure.
        **kwargs: Additional keyword arguments passed to bokeh.plotting.figure.

    Returns:
        A configured Figure instance with keyboard shortcuts enabled,
        scroll wheel zoom with shift and add other default tools added,
        and stretching to available width and the webgl backend activated.
    """
    kwargs.setdefault("sizing_mode", "stretch_width")
    kwargs.setdefault("output_backend", "webgl")
    # Standard tools that work well with the keyboard shortcuts.
    kwargs.setdefault("tools", "pan,box_zoom,reset,save,undo,redo")

    p = figure(title=title, *args, **kwargs)

    # Add wheel zoom with shift modifier. Shift is used to allow normal
    # page scrolling while the mouse is over the plot.
    try:
        zoom_tool = WheelZoomTool(modifiers="shift")
    except AttributeError:  # Fallback for older Bokeh versions if needed
        zoom_tool = WheelZoomTool()

    p.add_tools(zoom_tool)
    p.toolbar.active_scroll = zoom_tool  # type: ignore

    # Add our custom keyboard shortcuts tool.
    enable_keyboard_shortcuts(p)

    return p


_module_dir = Path(__file__).parent


def apply_click_policy_mute_others(plot: figure) -> None:
    """
    Configures the plot so that clicking a legend entry mutes all other renderers.
    Useful for focusing on a single data series in a crowded plot.

    Args:
        plot: The Bokeh figure to configure with the mute-others behavior.
    """
    plot.legend.click_policy = "mute"

    # Load the JavaScript from the pre-built file
    js_path = _module_dir / "js" / "mute_others.js"
    # We use a simple script that wraps the compiled JS if needed,
    # but since tsc -m ES2022 produces clean JS, we can wrap it or use it.
    # Note: compiled JS might have 'export' which Bokeh CustomJS doesn't like directly.
    # We'll need to be careful with the build output.

    with open(js_path, "r") as f:
        js_content = f.read()

    # The compiled JS is CommonJS, so we wrap it in a function that provides exports
    # We'll use the compiled JS directly and access the exported function.
    js_code = f"""
const exports = {{}};
const module = {{ exports }};
{js_content}
(module.exports.mute_others || exports.mute_others)(renderers, index);
"""

    renderers = plot.renderers
    if not isinstance(renderers, Sequence):
        raise ValueError("Couldn't find any Glyphs to apply mute others click policy to.")

    for i, renderer in enumerate(renderers):
        r_dict = {f"r{idx}": r for idx, r in enumerate(renderers)}
        callback = CustomJS(args={"renderers": r_dict, "index": i}, code=js_code)
        renderer.js_on_change("muted", callback)


def _process_color_segments(
    x: npt.NDArray,
    y: npt.NDArray,
    color_indices: npt.NDArray[np.integer],
    n_colors: int | None = None,
) -> tuple[list[list[float]], list[list[float]]]:
    """
    Splits a single line into multiple segments for multi-color plotting.
    Inserts NaNs at segment boundaries to create distinct lines without
    connecting different segments of the same color.

    Args:
        x: X-coordinate data (1d array).
        y: Y-coordinate data (1d array).
        color_indices: Array of color indices for each point.
        n_colors: Optional number of colors. If None, inferred from color_indices.

    Returns:
        A tuple of (xs, ys) where each is a list of lists, with each inner list
        corresponding to one color.
    """
    if n_colors is None:
        n_colors = int(color_indices.max() + 1)
    else:
        if n_colors < int(color_indices.max() + 1):
            raise ValueError(
                "Some of the passed color indices are higher than the explicitly passed n_colors."
            )

    xs: list[list[float]] = [[] for _ in range(n_colors)]
    ys: list[list[float]] = [[] for _ in range(n_colors)]

    last_c = color_indices[0]
    for i in range(len(x)):
        x_val = float(x[i])
        y_val = float(y[i])
        c = int(color_indices[i])

        if i > 0 and c != last_c:
            # Calculate midpoint to ensure continuous-looking line segments.
            mid_x = (float(x[i - 1]) + x_val) / 2
            mid_y = (float(y[i - 1]) + y_val) / 2

            xs[last_c].extend([mid_x, np.nan])
            ys[last_c].extend([mid_y, np.nan])
            xs[c].append(mid_x)
            ys[c].append(mid_y)

        xs[c].append(x_val)
        ys[c].append(y_val)
        last_c = c

    return xs, ys


# Reordered Category20 for better visual contrast when less than 10 are needed.
CATEGORICAL_COLORS = [Category20[20][2 * i] for i in range(10)] + [
    Category20[20][2 * i + 1] for i in range(10)
]


def insert_line_plot_with_segmented_coloring(
    p: figure,
    x: npt.ArrayLike | pd.DatetimeIndex,
    y: npt.ArrayLike,
    color_indices: npt.NDArray[np.integer],
    line_colors: Sequence[str] = CATEGORICAL_COLORS,
    legend_labels: Sequence[str] | None = None,
    **kwargs: Any,
) -> list[GlyphRenderer]:
    """
    Adds a segmented line plot to the figure. Each segment color is handled
    as a separate renderer.

    Args:
        p: The Bokeh figure to add the line plot to.
        x: X-coordinate data (array-like, can be numeric or datetime).
        y: Y-coordinate data (array-like).
        color_indices: Array of color indices for each point.
        line_colors: Sequence of color values for each segment.
        legend_labels: Optional sequence of legend labels for each segment.
        **kwargs: Additional keyword arguments passed to p.line() for each segment.
            - legend_label applied to all colors is explicitly supported. However
              it will cause weird behaviour when used in combination with click policy mute others.

    Returns:
        List of GlyphRenderer instances created for each color segment.
    """
    y = np.asarray(y)
    n_colors = None if legend_labels is None else len(legend_labels)
    if isinstance(x, pd.DatetimeIndex):
        xs, ys = _process_color_segments(x.view("int64"), y, color_indices, n_colors=n_colors)
        xs = [pd.to_datetime(xs_c) for xs_c in xs]
    else:
        xs, ys = _process_color_segments(np.asarray(x), y, color_indices, n_colors=n_colors)

    # Handle single legend_label for all segments or individual labels.
    default_label = kwargs.pop("legend_label", "")

    if legend_labels is None:
        legend_labels = [default_label] * len(xs)
    assert len(legend_labels) == len(xs), "legend_labels and xs should have same length."

    renderers: list[GlyphRenderer] = []
    for x_c, y_c, color, label in zip(xs, ys, line_colors, legend_labels):
        renderers.append(
            p.line(np.asarray(x_c), np.asarray(y_c), line_color=color, legend_label=label, **kwargs)
        )

    return renderers


def get_column_layout_with_shared_x(
    n: int,
    titles: Sequence[str | None] | None = None,
    layout_kwargs: dict[str, Any] | None = None,
    **kwargs: Any,
) -> Column:
    """
    Creates a column layout with n plots sharing the same x-range and
    synchronized vertical crosshairs.

    Args:
        n: Number of plots to create.
        titles: Optional list of titles for each plot. If None, all plots have no title.
        layout_kwargs: Optional dictionary of layout-specific keyword arguments.
        **kwargs: Additional keyword arguments passed to standard_figure for each plot.

    Returns:
        A Column layout containing the configured plots.
    """
    if titles is None:
        titles = [None] * n
    if layout_kwargs is None:
        layout_kwargs = {}

    shared_x_range = DataRange1d()
    shared_vspan = Span(dimension="height")

    plots: list[figure] = []
    for i in range(n):
        # Crosshair synchronizes the vertical line across all plots in the column.
        crosshair = CrosshairTool(overlay=(shared_vspan, Span(dimension="width")))
        p = standard_figure(title=titles[i], x_range=shared_x_range, **kwargs)
        p.add_tools(crosshair)
        plots.append(p)

    return column(*plots, sizing_mode="stretch_width", **layout_kwargs)
