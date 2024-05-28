
# Import shiny
from shiny import module, ui, render, reactive

# Import faicons
import faicons as fa

# Import utils
from utils.seaborn_helpers import *
from utils.datagrid_and_value_box_helpers \
    import get_line, player_ou, player_over_under_streak

# String containing value for Icon Height in Pixels
icon_height = "48px"

# Dictionary of faicons for value boxes
ICONS = {
    "crosshairs": fa.icon_svg("crosshairs", height = icon_height, ),
    "headset": fa.icon_svg("headset", height = icon_height), 
    "plus": fa.icon_svg("plus", height = icon_height), 
    "minus": fa.icon_svg("minus", height = icon_height), 
    "chevron_up": fa.icon_svg("chevron-up", height = icon_height, 
                              fill = prizepicks_color, fill_opacity = 0.85),
    "chevron_down": fa.icon_svg("chevron-down", height = icon_height,
                                fill = prizepicks_color, fill_opacity = 0.85),
    "calendar": fa.icon_svg("calendar", height = icon_height), 
    "crown": fa.icon_svg("crown", height = icon_height, 
                         fill = prizepicks_color, fill_opacity = 0.85),
    "check": fa.icon_svg("circle-check", height = icon_height), 
    "exclamation": fa.icon_svg("circle-exclamation", height = icon_height), 
    "flag": fa.icon_svg("flag", height = icon_height), 
    "mound": fa.icon_svg("mound", height = icon_height), 
    "circle_question": fa.icon_svg("circle-question", height = "16px"), 
}

@module.ui
def player_panel_ui(player_num: int):
    return ui.nav_panel(
        str(player_num), 
        ui.output_plot("player_plot"), 
        ui.layout_columns(),
        ui.layout_columns(
            ui.value_box(
                "O/U",
                ui.output_text("player_ou"),
                showcase = ui.output_ui("player_ou_icon"), 
                showcase_layout = "left center", 
                max_height = "100px"
            ), 
            ui.value_box(
                "O/U Streak", 
                ui.output_ui("player_ou_streak"), 
                showcase = ICONS["crown"],
                showcase_layout = "left center", 
                max_height = "100px"
            )
        ),
    )

@module.server
def player_panel_server(
    input, output, session, cdlDF: pd.DataFrame, rostersDF: pd.DataFrame,
    propsDF, team_input, player_num: int, map_num, 
    team_color: str, gamemode_input, map_input, x_axis
    ):

    # Player Name
    @reactive.Calc
    def player():
        return rostersDF[rostersDF['team'] == team_input()].iloc[player_num - 1]['player']

    
    # Player Line
    @reactive.Calc
    def player_line():
        return get_line(propsDF(), player(), map_num())

    # Player Plot
    @output
    @render.plot
    def player_plot():
        if x_axis() == "Time":
            return player_kills_vs_time(
                cdlDF, 
                player(),
                team_color,
                gamemode_input(), 
                player_line(),
                map_input()
            )
        else:
            return player_kills_vs_score_diff(
                cdlDF, 
                player(),
                team_color, 
                gamemode_input(), 
                player_line(),
                map_input()
            )