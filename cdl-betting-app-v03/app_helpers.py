
# Import shiny faicons
from shiny import ui
import faicons as fa

# String containing value for Icon Height in Pixels
icon_height = "48px"

# Dictionary of faicons for value boxes
ICONS = {
    "crosshairs": fa.icon_svg("crosshairs", height = icon_height, ),
    "headset": fa.icon_svg("headset", height = icon_height), 
    "plus": fa.icon_svg("plus", height = icon_height), 
    "minus": fa.icon_svg("minus", height = icon_height), 
    "chevron_up": fa.icon_svg("chevron-up", height = icon_height),
    "chevron_down": fa.icon_svg("chevron-down", height = icon_height), 
    "calendar": fa.icon_svg("calendar", height = icon_height), 
    "crown": fa.icon_svg("crown", height = icon_height), 
    "check": fa.icon_svg("circle-check", height = icon_height), 
    "exclamation": fa.icon_svg("circle-exclamation", height = icon_height), 
    "flag": fa.icon_svg("flag", height = icon_height), 
    "mound": fa.icon_svg("mound", height = icon_height), 
    "ellipsis": fa.icon_svg("ellipsis")
}

# Function to render one ui.nav_panel per player | Page 1, Kills per Map
def player_panel(player_num: str):
    return ui.nav_panel(
        player_num, 
        ui.output_plot(f"player_{player_num}_plot"),
        ui.layout_columns(),
        ui.layout_columns(
            ui.value_box(
                "O/U",
                ui.output_text(f"player_{player_num}_ou"),
                showcase = ui.output_ui(f"player_{player_num}_ou_icon"), 
                showcase_layout = "left center", 
                max_height = "100px"
            ), 
            ui.value_box(
                "Streak", 
                ui.output_ui(f"player_{player_num}_ou_streak"), 
                showcase = ICONS["crown"],
                showcase_layout = "left center", 
                max_height = "100px"
            )
        )
    )

# Function to render one ui.nav_panel per player | Page 2, Maps 1 - 3 Kills
def p2_player_panel(player_num: str):
    return ui.nav_panel(
        player_num, 
        ui.output_plot(f"p2_player_{player_num}_plot"),
        ui.layout_columns(),
        ui.layout_columns(
            ui.value_box(
                "O/U",
                ui.output_text(f"p2_player_{player_num}_ou"),
                showcase = ui.output_ui(f"p2_player_{player_num}_ou_icon"), 
                showcase_layout = "left center", 
                max_height = "100px"
            ), 
            ui.value_box(
                "Streak", 
                ui.output_ui(f"p2_player_{player_num}_ou_streak"), 
                showcase = ICONS["crown"],
                showcase_layout = "left center", 
                max_height = "100px"
            )
        )
    )

