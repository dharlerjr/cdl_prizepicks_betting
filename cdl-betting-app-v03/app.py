

# Import shiny, shinyswatch, and faicons
from shiny import App, reactive, render, ui
from shiny.types import ImgData
import shinyswatch
import faicons as fa

# Import os for filepaths
import os

# Import setup
from setup.setup import *

# Import webscraper & helpers
from webscraper import *
from seaborn_helpers import *
from datagrid_and_value_box_helpers import *


# Dictionary to map map_num to gamemode
map_nums_to_gamemode = {
    1: "Hardpoint", 
    2: "Search & Destroy", 
    3: "Control", 
    4: "Hardpoint", 
    5: "Search & Destroy"
}

# Dictionary of paths to saved team logo images
team_logos = {
    "Atlanta FaZe": "\\team_logos\\ATL.webp",
    "Boston Breach": "\\team_logos\\BOS.webp",
    "Carolina Royal Ravens": "\\team_logos\\CAR.webp", 
    "Las Vegas Legion": "\\team_logos\\LV.webp",
    "Los Angeles Guerrillas": "\\team_logos\\LAG.webp", 
    "Los Angeles Thieves": "\\team_logos\\LAT.webp", 
    "Miami Heretics": "\\team_logos\\MIA.webp", 
    "Minnesota ROKKR": "\\team_logos\\MIN.webp", 
    "New York Subliners": "\\team_logos\\NYSL.webp",
    "OpTic Texas": "\\team_logos\\TX.webp", 
    "Seattle Surge": "\\team_logos\\SEA.webp", 
    "Toronto Ultra": "\\team_logos\\TOR.webp"
}

# Dictionary of team names to abbreviations
team_abbrs = {
    "Atlanta FaZe": "ATL",
    "Boston Breach": "BOS",
    "Carolina Royal Ravens": "CAR", 
    "Las Vegas Legion": "LV",
    "Los Angeles Guerrillas": "LAG", 
    "Los Angeles Thieves": "LAT", 
    "Miami Heretics": "MIA", 
    "Minnesota ROKKR": "MIN", 
    "New York Subliners": "NYSL",
    "OpTic Texas": "TX", 
    "Seattle Surge": "SEA", 
    "Toronto Ultra": "TOR"
}

# Dictionary of faicons for value boxes
ICONS = {
    "red_crosshairs": fa.icon_svg("crosshairs").add_class("text-danger"), 
    "green_crosshairs": fa.icon_svg("crosshairs").add_class("text-success"), 
    "crosshairs": fa.icon_svg("crosshairs"),
    "percent": fa.icon_svg("percent"), 
    "headset": fa.icon_svg("headset"), 
    "plus": fa.icon_svg("plus"), 
    "minus": fa.icon_svg("minus"), 
    "chevron_up": fa.icon_svg("chevron-up").add_class("text-purple"),
    "chevron_down": fa.icon_svg("chevron-down").add_class("text-purple")
}

# Major 3 Qualifiers Start Date (String)
start_date = '2024-04-12' 

# Load in four instance of cdl data for testing
cdlDF = load_and_clean_cdl_data()

# Build series summaries
series_score_diffs = build_series_summaries(cdlDF).copy()

# Filter maps from cdlDF
cdlDF = filter_maps(cdlDF)

# Build team summaries
team_summaries_DF = build_team_summaries(cdlDF).copy()

# Build rosters
rostersDF = build_rosters(cdlDF).copy()

# Compute CDL Standings for Major III Qualifiers
current_standings = \
    cdlDF[(cdlDF["match_date"] >= start_date)] \
    [["match_id", "team", "series_result"]] \
    .drop_duplicates() \
    .groupby("team") \
    .agg(
        wins = ("series_result", lambda x: sum(x)), 
        losses = ("series_result", lambda x: len(x) - sum(x))
    ) \
    .reset_index().copy()

# Initialize player props dataframe
initial_player_props = build_intial_props(rostersDF).copy()


# Define ui
app_ui = ui.page_sidebar(

    # Sidebar with inputs
    ui.sidebar(

        # Theme picker
        shinyswatch.theme_picker_ui(),
        
        # Set theme: cerulean
        # shinyswatch.theme.cerulean,
        
        # Inputs
        ui.input_action_button(id = "scrape", label = "Get PrizePicks Lines"), 
        ui.input_select(id = "team_a", label = "Team A", selected = "OpTic Texas",
                        choices = sorted(cdlDF['team'].unique())), 
        ui.input_select(id = "team_b", label = "Team B", selected = "Atlanta FaZe",
                        choices = sorted(cdlDF['team'].unique())), 
        ui.input_select(id = "map_num_and_gamemode", label = "Map Number", selected = 1,
                        choices = [
                            "Map 1 Hardpoint", 
                            "Map 2 Search & Destroy", 
                            "Map 3 Control", 
                            "Map 4 Hardpoint", 
                            "Map 5 Search & Destroy"
                        ]), 
        ui.input_select(id = "map_name", label = "Map", selected = "All",
                        choices = ["All"] + sorted(filter_maps(cdlDF)['map_name'].unique())), 
        ui.input_select(id = "x_axis", label = "X-Axis", selected = "Time",
                        choices = ["Time", "Score Differential"])

    ),

    # Row 1 of 2
    ui.layout_columns(
        
        # Column 1 of 5: Team A Logo & Standing, wrapped
        ui.layout_columns(
            ui.output_image("team_a_logo", width = "120px", height = "120px"), 
            ui.value_box(
                title = "Series W-L (Major III Qualifiers)", 
                value = ui.output_ui("team_a_series_record"),
                showcase = ICONS["headset"]
            ), 
            row_heights = (2, 1)
            ),

        # Column 2 of 5: Blank
        ui.markdown(""),
        
        # Column 3 of 5
        ui.value_box(
            title = "Series H2H (Overall)",
            value = ui.output_ui("h2h_series_record"),
            showcase = ICONS["crosshairs"]
        ), 
        
        # Column 4 of 5: Blank
        ui.markdown(""),
        
        # Column 5 of 5: Team B Logo & Standing, wrapped
        ui.layout_columns(
            ui.output_image("team_b_logo", width = "120px", height = "120px"), 
            ui.value_box(
                title = "Series W-L (Major III Qualifiers)", 
                value = ui.output_ui("team_b_series_record"),
                showcase = ICONS["headset"]
            ), 
            row_heights = (2, 1)
            ),
    ),

    # Row 2 of 2
    ui.layout_columns(),

    # App Title
    title = "CDL Bets on PrizePicks" 
)


# Define server logic
def server(input, output, session):
    
    # Theme picker
    shinyswatch.theme_picker_server()

    # Intialize reactive dataframe of player props
    player_props_df = reactive.value(initial_player_props)

    # Reactive event to update player props dataframe
    @reactive.effect
    @reactive.event(input.scrape)
    def scrape_props():
        newVal = merge_player_props(
            player_props_df(), 
            scrape_prizepicks(), 
            rostersDF
        )
        player_props_df.set(newVal)

    # Reactive calc to get map_num from map_num input
    @reactive.calc
    def map_num():
        return int(input.map_num_and_gamemode().split()[1])

    # Reactive calc to translate map num to gamemode
    @reactive.calc
    def gamemode():
        return map_nums_to_gamemode[map_num()]
    
    # Team A Logo
    @render.image
    def team_a_logo():
        img: ImgData = {"src": os.path.dirname(__file__) + team_logos[input.team_a()], 
                        "width": "120px", "height": "120px", "image-align": "left"}
        return img
    
    # Team B Logo
    @render.image
    def team_b_logo():
        img: ImgData = {"src": os.path.dirname(__file__) + team_logos[input.team_b()], 
                        "width": "120px", "height": "120px", "image-align": "right"}
        return img
    
    # Team A Series Record for Major 3 Quals
    @render.ui
    def team_a_series_record():
        wins = current_standings.loc[current_standings['team'] == input.team_a(), 'wins'].reset_index(drop=True)[0]
        losses = current_standings.loc[current_standings['team'] == input.team_a(), 'losses'].reset_index(drop=True)[0]
        return f"{wins} - {losses}"

    # Team B Series Record for Major 3 Quals
    @render.ui
    def team_b_series_record():
        wins = current_standings.loc[current_standings['team'] == input.team_b(), 'wins'].reset_index(drop=True)[0]
        losses = current_standings.loc[current_standings['team'] == input.team_b(), 'losses'].reset_index(drop=True)[0]
        return f"{wins} - {losses}"
    
    # H2H Series Record for User-Selected Map & Mode Combination
    @render.ui
    def h2h_series_record():
        return compute_h2h_series_record(cdlDF, input.team_a(), input.team_b())

# Run app
app = App(app_ui, server)