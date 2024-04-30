
# Import shiny
from shiny import ui

def player_panel(player_num: str):
    return ui.nav_panel(
        player_num, ui.output_plot(f"player_{player_num}_plot", width = "660px", height = "380px"),
        ui.layout_columns(),
        ui.layout_columns(
            ui.value_box(
                "O/U",
                ui.output_ui(f"player_{player_num}_ou"),
                showcase = ui.output_ui(f"player_{player_num}_ou_icon"), 
                showcase_layout="left center", 
                max_height = "100px"
            ), 
            ui.value_box(
                "Streak", 
                ui.output_ui(f"player_{player_num}_ou_streak"), 
                showcase = ui.output_ui(f"player_{player_num}_ou_streak_icon"),
                showcase_layout="left center", 
                max_height = "100px"
            ), 
        ),   
    )