
# Import shiny
from shiny import module, ui, render, reactive

# Import faicons
import faicons as fa

# Import utils
from utils.plots import *
from utils.datagrids_and_value_boxes \
    import get_line, compute_player_ou, compute_player_ou_streak

# String containing value for Icon Height in Pixels
icon_height = "48px"

# Dictionary of faicons for value boxes
player_card_icons = {
    "chevron_up": fa.icon_svg("chevron-up", height = icon_height, 
                              fill = prizepicks_color, fill_opacity = 0.85),
    "chevron_down": fa.icon_svg("chevron-down", height = icon_height,
                                fill = prizepicks_color, fill_opacity = 0.85),
    "crown": fa.icon_svg("crown", height = icon_height, 
                         fill = prizepicks_color, fill_opacity = 0.85)
}

@module.ui
def player_card_ui_pg1(player_num: int):
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
                showcase = player_card_icons["crown"],
                showcase_layout = "left center", 
                max_height = "100px"
            )
        )
    )

@module.server
def player_card_server_pg1(
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
        
    # Player O/U Stats
    @reactive.calc
    def player_ou_stats():
        return compute_player_ou(
            cdlDF, 
            player(),
            gamemode_input(), 
            player_line(),
            map_input()
            )
    
    # Player O/U %
    @output
    @render.text
    def player_ou():
        over_under, percentage, overs, unders, hooks = player_ou_stats()
        if over_under == "Never Played":
            return over_under
        return f"{over_under} {percentage}%\n({overs} - {unders} - {hooks})"
    
    # Player O/U Icon
    @output
    @render.ui
    def player_ou_icon():
        over_under = player_ou_stats()[0]
        return player_card_icons["chevron_up"] if over_under == "Over" else player_card_icons["chevron_down"]
    
    # Player O/U Streak
    @output
    @render.ui
    def player_ou_streak():
        ou, streak = compute_player_ou_streak(
            cdlDF, 
            player(),
            gamemode_input(), 
            player_line(), 
            map_input()
        )
        return f"{ou} {streak}"