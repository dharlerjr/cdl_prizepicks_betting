
# Import shiny
from shiny import module, ui, render, reactive

# Import faicons
import faicons as fa

# Import utils
from utils.plots import *
from utils.datagrids_and_value_boxes \
    import get_line, compute_player_1_thru_3_ou, compute_player_1_thru_3_ou_streak

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
def player_card_ui_pg2(player_num: int):
    return ui.nav_panel(
        str(player_num), 
        ui.output_plot("player_plot_pg2"), 
        ui.layout_columns(),
        ui.layout_columns(
            ui.value_box(
                "O/U",
                ui.output_text("player_ou_pg2"),
                showcase = ui.output_ui("player_ou_icon_pg2"), 
                showcase_layout = "left center", 
                max_height = "100px"
            ), 
            ui.value_box(
                "O/U Streak", 
                ui.output_ui("player_ou_streak_pg2"), 
                showcase = player_card_icons["crown"],
                showcase_layout = "left center", 
                max_height = "100px"
            )
        )
    )

@module.server
def player_card_server_pg2(
    input, output, session, cdlDF: pd.DataFrame, maps_1_thru_3_df: pd.DataFrame,
    rostersDF: pd.DataFrame, propsDF, team_input, player_num: int, 
    team_color: str, map_one, map_two, map_three, x_axis
    ):

    # Player Name
    @reactive.Calc
    def player():
        return rostersDF[rostersDF['team'] == team_input()].iloc[player_num - 1]['player']

    
    # Player Maps 1 - 3 Line
    @reactive.Calc
    def player_line():
        return get_line(propsDF(), player(), 0)
    
    # Player Map 1 Line
    @reactive.Calc
    def map_1_line():
        return get_line(propsDF(), player(), 1)
    
    # Player Map 3 Line
    @reactive.Calc
    def map_3_line():
        return get_line(propsDF(), player(), 3)

    # Player Plot
    @output
    @render.plot
    def player_plot_pg2():
        if x_axis() == "Time":
            return player_1_thru_3_kills_vs_time(
                maps_1_thru_3_df,
                player(),
                team_color,
                player_line()
            )
        elif x_axis() == "Hardpoint Map":
            return player_kills_by_map(
                cdlDF, 
                player(),
                "Hardpoint",
                map_1_line()
            )
        elif x_axis() == "Control Map":
            return player_kills_by_map(
                cdlDF, 
                player(),
                "Control",
                map_3_line()
            )
        else:
            return player_kills_by_mapset(
                cdlDF, 
                player(),
                map_one(),
                map_two(),
                map_three()
            )
        
    # Player Maps 1 - 3 O/U Stats
    @reactive.calc
    def player_ou_stats_pg2():
        return compute_player_1_thru_3_ou(
            maps_1_thru_3_df, 
            player(),
            player_line()
            )
    
    # Player Maps 1 - 3 O/U %
    @output
    @render.text
    def player_ou_pg2():
        over_under, percentage, overs, unders, hooks = player_ou_stats_pg2()
        if over_under == "Never Played":
            return over_under
        return f"{over_under} {percentage}% ({overs} - {unders} - {hooks})"
    
    # Player O/U Icon
    @output
    @render.ui
    def player_ou_icon_pg2():
        over_under = player_ou_stats_pg2()[0]
        return player_card_icons["chevron_up"] if over_under == "Over" else player_card_icons["chevron_down"]
    
    # Player O/U Streak
    @output
    @render.ui
    def player_ou_streak_pg2():
        ou, streak = compute_player_1_thru_3_ou_streak(
            maps_1_thru_3_df, 
            player(),
            player_line()
        )
        return f"{ou} {streak}"