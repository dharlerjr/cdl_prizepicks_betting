
# Import shiny
from shiny import module, ui, render

# Import faicons
import faicons as fa

# Import map_summary_pg3
from map_summary_pg3 import *

# Import pandas
import pandas as pd

# String containing value for Icon Height in Pixels
icon_height = "48px"

# Dictionary of faicons 
match_analysis_icons = {
    "Hardpoint": fa.icon_svg("mound", height = icon_height), 
    "Search & Destroy": fa.icon_svg("bomb", height = icon_height), 
    "Control": fa.icon_svg("flag", height = icon_height), 
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




@module.server
def map_summaries_server_p3(
    input, output, session, cdlDF: pd.DataFrame, match_id: int, map_num: int
    ):
    
    # Map Name and Number
    @output
    @render.ui
    def map_name_num():
        map_name = cdlDF[
            (cdlDF["match_id"] == match_id) &
            (cdlDF["map_num"] == map_num)
        ].reset_index(drop = True).at[0, "map_name"]
        return f"Map {map_num} {map_name} {gamemode_abbrs[map_nums_to_gamemode[map_num]]}"
