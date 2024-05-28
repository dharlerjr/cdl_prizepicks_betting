
# Import shiny
from shiny import module, ui, render, reactive

# Import utils
from utils.seaborn_helpers import *
from utils.datagrid_and_value_box_helpers import get_line

@module.ui
def player_panel_ui(player_num: int):
    return ui.nav_panel(str(player_num), ui.output_plot("player_plot"))

@module.server
def player_panel_server(
    input, output, session, cdlDF_input: pd.DataFrame, rostersDF: pd.DataFrame,
    player_props_input, team_input, player_num: int, map_num_input, 
    team_color: str, gamemode_input, map_input, x_axis_input
    ):

    # Player Name
    @reactive.Calc
    def player():
        return rostersDF[rostersDF['team'] == team_input()].iloc[player_num - 1]['player']

    
    # Player Line
    @reactive.Calc
    def player_line():
        return get_line(player_props_input(), player(), map_num_input())

    # Player Plot
    @output
    @render.plot
    def player_plot():
        if x_axis_input() == "Time":
            return player_kills_vs_time(
                cdlDF_input, 
                player(),
                team_color,
                gamemode_input(), 
                player_line(),
                map_input()
            )
        else:
            return player_kills_vs_score_diff(
                cdlDF_input, 
                player(),
                team_color, 
                gamemode_input(), 
                player_line(),
                map_input()
            )