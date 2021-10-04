"""
All of the good stuff. This is should be the main point for app configuration.
"""

# General
app_name = "Jenkins"

# Styling
style = "clean"
style_map = {
    "default": {
        "root_node": "bold red",
        "folder": "bold magenta",
        "node": "bright_green",
        "node_on_hover": "underline",
        "multibranch_node": "magenta",
        "tree_guide": "black",
        "tree_guide_on_hover": "bold not dim red",
        "scroll_bar_foreground": "red",
        "scroll_bar_foreground_grabbed": "white",
        "scroll_bar_background": "#444444",
        "scroll_bar_background_on_hover": "#555555",
    },
    "clean": {
        "root_node": "gray",
        "folder": "gray",
        "node": "gray",
        "node_on_hover": "underline",
        "multibranch_node": "gray",
        "tree_guide": "black",
        "tree_guide_on_hover": "white",
        "scroll_bar_foreground": "#6e6d6d",
        "scroll_bar_grabbed_foreground": "#9c9a9a",
        "scroll_bar_background": "#444444",
        "scroll_bar_background_on_hover": "#444444",
        "footer_style": "white on #444444",
    },
}
