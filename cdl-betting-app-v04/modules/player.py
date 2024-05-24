
from shiny import module, ui, render, reactive, event

@module.ui
def player_panel_ui(player_num: int):
    return ui.card(
        ui.nav_panel(str(player_num), ui.output_plot("player_plot")),
    )

@module.server
def player_panel_server(input, output, session, player_num: int):

    @render.plot
    def player_plot():
        return player_kills_vs_time(
            cdlDF, 
            rostersDF[rostersDF['team'] == input.team_a()].iloc[0]['player'],
            team_a_color,
            gamemode(), 
            player_1_line(),
            input.map_name()
        )