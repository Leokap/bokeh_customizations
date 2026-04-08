from bokeh.plotting import show, save
from bokeh_customizations import standard_figure, insert_line_plot_with_segmented_coloring, apply_click_policy_mute_others
import numpy as np

# Create some dummy data
x = np.linspace(0, 10, 100)
y = np.sin(x)
color_indices = (x // 2).astype(int)

# Create a standard figure
p = standard_figure(title="New Bokeh Customizations Demo")

# Insert a segmented line plot
insert_line_plot_with_segmented_coloring(p, x, y, color_indices, legend_label="Sin Wave")

# Add another normal line to test "mute others"
p.line(x, np.cos(x), line_color="black", line_dash="dashed", legend_label="Cos Wave")

# Apply mute others policy
apply_click_policy_mute_others(p)

# In a real environment, you would call show(p)
# show(p)
save(p, "test.html")
print("Plot created successfully with KeyboardShortcutsTool.")
