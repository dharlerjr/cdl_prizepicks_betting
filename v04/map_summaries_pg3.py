
# Import shiny
from shiny import module, ui, render, reactive

# Import faicons
import faicons as fa

# Import pandas
import pandas as pd

# String containing value for Icon Height in Pixels
icon_height = "48px"

# Dictionary of faicons by map_num
map_num_icons = {
    1: fa.icon_svg("mound", height = icon_height), 
    2: fa.icon_svg("bomb", height = icon_height), 
    3: fa.icon_svg("flag", height = icon_height), 
    4: fa.icon_svg("mound", height = icon_height), 
    5: fa.icon_svg("bomb", height = icon_height)
}

# Dictionary to map map_num to gamemode
map_nums_to_gamemode = {
    1: "Hardpoint", 
    2: "Search & Destroy", 
    3: "Control", 
    4: "Hardpoint", 
    5: "Search & Destroy"
}

# Dictionary of gamemode abbreviations for value box titles
gamemode_abbrs = {
    "Hardpoint": "HP", 
    "Search & Destroy": "SnD", 
    "Control": "Control"
}

@module.ui
def map_value_box_ui_p3():
    return ui.value_box(
        title = ui.output_ui("map_name_num"),
        value = ui.output_ui("map_score"),
        showcase = ui.output_ui("gamemode_icon"), 

    )


@module.server
def map_value_box_server_p3(
    input, output, session, cdlDF_input: pd.DataFrame, match_id: int, map_num: int, 
    team_a_abbr, team_b_abbr, total_maps
    ):

    # Filter Dataframe for Current Match & Map
    @reactive.calc
    def map_summary_df():
        if map_num <= total_maps():
            return cdlDF_input[(cdlDF_input["match_id"] == match_id()) & (cdlDF_input["map_num"] == map_num)].reset_index(drop = True)
    
    # Map Name and Number
    @output
    @render.ui
    def map_name_num():
        if map_num <= total_maps():
            map_name = map_summary_df().at[0, "map_name"]
            return f"Map {map_num} {map_name} {gamemode_abbrs[map_nums_to_gamemode[map_num]]}"
    
    # Map Score
    @output
    @render.ui
    def map_score():
        if map_num <= total_maps():
            team_a_score = map_summary_df()[
                map_summary_df()["team_abbr"] == team_a_abbr()
            ].reset_index(drop = True).at[0, "team_score"]
            team_b_score = map_summary_df()[
                map_summary_df()["opp_abbr"] == team_b_abbr()
            ].reset_index(drop = True).at[0, "opp_score"]
            return f"{team_a_score} - {team_b_score}"
    
    # Gamemode Icon
    @output
    @render.ui
    def gamemode_icon():
        if map_num <= total_maps():
            return map_num_icons[map_num]