
# Import shiny & faicons
from shiny import ui
import faicons as fa

# Dictionary of faicons for value boxes
ICONS = {
    "crosshairs": fa.icon_svg("crosshairs", height = "48px"),
    "headset": fa.icon_svg("headset", height = "48px"), 
    "plus": fa.icon_svg("plus", height = "48px"), 
    "minus": fa.icon_svg("minus", height = "48px"), 
    "chevron_up": fa.icon_svg("chevron-up", height = "48px"),
    "chevron_down": fa.icon_svg("chevron-down", height = "48px"), 
    "calendar": fa.icon_svg("calendar", height = "48px"), 
    "crown": fa.icon_svg("crown", height = "48px"), 
    "check": fa.icon_svg("check", height = "48px"), 
    "exclamation": fa.icon_svg("exclamation", height = "48px")
}

# Function to render one ui.nav_panel per player
def player_panel(player_num: str):
    return ui.nav_panel(
        player_num, ui.output_plot(f"player_{player_num}_plot", width = "660px", height = "380px"),
        ui.layout_columns(),
        ui.layout_columns(
            ui.value_box(
                "O/U",
                ui.output_ui(f"player_{player_num}_ou"),
                showcase = ui.output_ui(f"player_{player_num}_ou_icon"), 
                showcase_layout = "left center", 
                max_height = "100px"
            ), 
            ui.value_box(
                "Streak", 
                ui.output_ui(f"player_{player_num}_ou_streak"), 
                showcase = ICONS["crown"],
                showcase_layout="left center", 
                max_height = "100px"
            ), 
        ),   
    )