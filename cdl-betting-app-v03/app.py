

# Import shiny, shinyswatch, faicons, and asyncio
from shiny import App, reactive, render, ui
from shiny.types import ImgData
import shinyswatch
import asyncio

# Import os for filepaths
import os

# Import setup
from setup.setup import *

# Import webscraper & helpers
from webscraper import *
from seaborn_helpers import *
from datagrid_and_value_box_helpers import *
from app_helpers import *

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

# Dictionary of team abbreviations by team name
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

# Dictionary of team icons by team name
team_icons = {
    "Atlanta FaZe": "FaZe",
    "Boston Breach": "Breach",
    "Carolina Royal Ravens": "Ravens", 
    "Las Vegas Legion": "Legion",
    "Los Angeles Guerrillas": "Guerrillas", 
    "Los Angeles Thieves": "Thieves", 
    "Miami Heretics": "Heretics", 
    "Minnesota ROKKR": "ROKKR", 
    "New York Subliners": "Subliners",
    "OpTic Texas": "OpTic", 
    "Seattle Surge": "Surge", 
    "Toronto Ultra": "Ultra"
}

# Dictionary of gamemode abbreviations for value box titles
gamemode_abbrs = {
    "Hardpoint": "HP", 
    "Search & Destroy": "SnD", 
    "Control": "Control"
}

# Global color variables
theme_color_light = "#2fa4e7"
theme_color_dark = "#1b6ead"
team_a_color = theme_color_light
team_b_color = theme_color_dark

# Major 3 Qualifiers Start Date (String)
start_date = '2024-04-12' 

# Load in four instance of cdl data for testing
cdlDF = load_and_clean_cdl_data()

# Build Maps 1 - 3 Totals Dataframe
adj_1_thru_3_totals = build_1_thru_3_totals(cdlDF).copy()

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
app_ui = ui.page_navbar(

    # 1st Page: Kills per Map
    ui.nav_panel("Kills per Map",
                 
        # Sidebar Layout
        ui.layout_sidebar(

            # Sidebar with inputs
            ui.sidebar(

                # Theme picker
                # shinyswatch.theme_picker_ui(),
                
                # Set theme: cerulean
                shinyswatch.theme.cerulean,
                
                # Inputs
                ui.input_action_button(id = "scrape", label = "Get PrizePicks Lines", class_ = "btn-info"), 
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
                ui.input_select(id = "x_axis", label = "Player Card X-Axis", selected = "Time",
                                choices = ["Time", "Score Differential"]),

                # BG & FG Colors for Sidebar
                # bg = "#033c73",
                # fg = "#ffffff"

            ),

            # Row 1 of 4
            ui.layout_columns(
                
                # Column 1 of 6: Team A Logo
                ui.output_image("team_a_logo", width = "120px", height = "120px"), 

                # Column 2 of 6: Placeholder Column
                ui.layout_columns(),
                
                # Column 3 of 6: H2H Series Record
                ui.value_box(
                    title = "Series H2H (Overall)",
                    value = ui.output_ui("h2h_series_record"),
                    showcase = ICONS["crosshairs"]
                ), 

                # Column 4 of 6: Date of Last Match
                ui.value_box(
                    title = "Last H2H Match",
                    value = ui.output_ui("last_match_date"),
                    showcase = ICONS["calendar"]
                ), 

                # Column 5 of 6: Placeholder Column
                ui.layout_columns(),
                
                # Column 6 of 6: Team B Logo
                ui.output_image("team_b_logo", width = "120px", height = "120px"), 

                # Row Height
                height = "120px"

            ),

            # Row 2 of 4
            ui.layout_columns(
                
                # Team A Standing
                ui.value_box(
                    title = "Major III Standing",
                    value = ui.output_ui("team_a_standing"),
                    showcase = ICONS["headset"]
                ),

                # Team A Win Streak
                ui.value_box(
                    title = ui.output_ui("team_a_win_streak_title"),
                    value = ui.output_ui("team_a_win_streak"),
                    showcase = ui.output_ui("change_team_a_win_streak_icon")
                ), 
                
                # Team A Win % 
                ui.value_box(
                    title = ui.output_ui("team_a_map_record_title"),
                    value = ui.output_ui("team_a_map_record"),
                    showcase = ui.output_ui("team_a_win_percent_icon")
                ), 
                
                # H2H W - L
                # ui.value_box(
                #     title = ui.output_ui("map_h2h_title"),
                #     value = ui.output_ui("h2h_map_record"),
                #     showcase = ICONS["crosshairs"]
                # ),
                
                # Team B Win %
                ui.value_box(
                    title = ui.output_ui("team_b_map_record_title"),
                    value = ui.output_ui("team_b_map_record"),
                    showcase = ui.output_ui("team_b_win_percent_icon")
                ), 
                
                # Team B Win Streak
                ui.value_box(
                    title = ui.output_ui("team_b_win_streak_title"),
                    value = ui.output_ui("team_b_win_streak"),
                    showcase = ui.output_ui("change_team_b_win_streak_icon")
                ),

                # Team B Standing
                ui.value_box(
                    title = "Major III Standing",
                    value = ui.output_ui("team_b_standing"),
                    showcase = ICONS["headset"]
                ), 
                
                # Row Height
                height = "120px"
            ),

            # Row 3 of 4
            ui.layout_columns(

                # Column 1: Card with Pill Tabset of Player O/U Stats
                ui.navset_card_pill( 
                    player_panel("1"), 
                    player_panel("2"), 
                    player_panel("3"), 
                    player_panel("4"), 
                    player_panel("5"), 
                    player_panel("6"), 
                    player_panel("7"), 
                    player_panel("8"), 
                    title = "Player Cards"
                ),

                # Column 2: Ridgeline Plots Wrapped
                ui.layout_column_wrap(

                    # Series Results
                    ui.card(ui.card_header("Series Results"), 
                            ui.output_plot("series_diffs")),
                    # Map Results
                    ui.card(ui.card_header("Map Results"), 
                            ui.output_plot("score_diffs")),

                    width = 1, 
                ),

                # Row Height
                height = "640px",

                # Column Widths
                col_widths = [8, 4]

            ),

            # Row 4 of 4: Scoreboards & Maps Played
            ui.layout_columns(

                # Column 1: Scoreboards
                ui.card(ui.card_header("Scoreboards"), 
                        ui.output_data_frame("scoreboards"), 
                        full_screen = True),

                # Column 2: Team A Maps Played
                ui.card(ui.card_header(ui.output_text("team_a_name")), 
                        ui.output_plot("team_a_maps_played")),

                # Column 3: Team B Maps Played
                ui.card(ui.card_header(ui.output_text("team_b_name")), 
                        ui.output_plot("team_b_maps_played")),

                # Row Height
                height = "360px",
                
                # Column Widths
                col_widths = [6, 3, 3]

            ), 

            # Import CSS Styling
            ui.include_css(
                os.path.dirname(__file__) + "\\styles.css"
            ),    
        )
    ), 

    # 2nd Page: Kills per Maps 1 - 3
    ui.nav_panel("Kills per Maps 1 - 3", 
                 
        # Sidebar Layout
        ui.layout_sidebar(

            # Sidebar with inputs
            ui.sidebar(
                
                # Inputs
                ui.input_action_button(id = "p2_scrape", label = "Get PrizePicks Lines", class_ = "btn-info"), 
                ui.input_select(id = "p2_team_a", label = "Team A", selected = "Carolina Royal Ravens",
                                choices = sorted(cdlDF['team'].unique())), 
                ui.input_select(id = "p2_team_b", label = "Team B", selected = "New York Subliners",
                                choices = sorted(cdlDF['team'].unique())), 
                ui.input_select(id = "p2_map_one", label = "Map 1", selected = "All",
                                choices = ["All", "6 Star", "Karachi", "Rio", "Sub Base", "Vista"]), 
                ui.input_select(id = "p2_map_two", label = "Map 2", selected = "All",
                                choices = ["All", "6 Star", "Highrise", "Invasion", "Karachi", "Rio"]), 
                ui.input_select(id = "p2_map_three", label = "Map 3", selected = "All",
                                choices = ["All", "Highrise", "Invasion", "Karachi"]), 
                ui.input_select(id = "p2_x_axis", label = "Player Card X-Axis", selected = "Time",
                                choices = ["Time", "Mapset", "Hardpoint Map", "Control Map"]), 
                
                # BG & FG Colors for Sidebar
                # bg = "#033c73",
                # fg = "#ffffff"
            ), 

            # Row 1 of 4
            ui.layout_columns(
                
                # Column 1 of 6: Team A Logo
                ui.output_image("p2_team_a_logo", width = "120px", height = "120px"), 

                # Column 2 of 6: Placeholder Column
                ui.layout_columns(),
                
                # Column 3 of 6: H2H Series Record
                ui.value_box(
                    title = "Series H2H (Overall)",
                    value = ui.output_ui("p2_h2h_series_record"),
                    showcase = ICONS["crosshairs"]
                ), 

                # Column 4 of 6: Date of Last Match
                ui.value_box(
                    title = "Last H2H Match",
                    value = ui.output_ui("p2_last_match_date"),
                    showcase = ICONS["calendar"]
                ), 

                # Column 5 of 6: Placeholder Column
                ui.layout_columns(),
                
                # Column 6 of 6: Team B Logo
                ui.output_image("p2_team_b_logo", width = "120px", height = "120px"), 

                # Row Height
                height = "120px"

            ),

            # Row 2 of 4
            ui.layout_columns(
                
                # Team A Standing
                ui.value_box(
                    title = "Major III Standing",
                    value = ui.output_ui("p2_team_a_standing"),
                    showcase = ICONS["headset"]
                ),
                
                # Team A HP Win % 
                ui.value_box(
                    title = ui.output_ui("team_a_hp_title"),
                    value = ui.output_ui("team_a_hp_record"),
                    showcase = ICONS["mound"]
                ), 

                # Team A Ctrl Win % 
                ui.value_box(
                    title = ui.output_ui("team_a_ctrl_title"),
                    value = ui.output_ui("team_a_ctrl_record"),
                    showcase = ICONS["flag"]
                ), 
                
                # Team B HP Win %
                ui.value_box(
                    title = ui.output_ui("team_b_hp_title"),
                    value = ui.output_ui("team_b_hp_record"),
                    showcase = ICONS["mound"]
                ), 

                # Team B Ctrl Win %
                ui.value_box(
                    title = ui.output_ui("team_b_ctrl_title"),
                    value = ui.output_ui("team_b_ctrl_record"),
                    showcase = ICONS["flag"]
                ), 

                # Team B Standing
                ui.value_box(
                    title = "Major III Standing",
                    value = ui.output_ui("p2_team_b_standing"),
                    showcase = ICONS["headset"]
                ), 
                
                # Row Height
                height = "120px"
            ), 

            # Row 3 of 4
            ui.layout_columns(

                # Column 1: Card with Pill Tabset of Player O/U Stats
                ui.navset_card_pill( 
                    p2_player_panel("1"), 
                    p2_player_panel("2"), 
                    p2_player_panel("3"), 
                    p2_player_panel("4"), 
                    p2_player_panel("5"), 
                    p2_player_panel("6"), 
                    p2_player_panel("7"), 
                    p2_player_panel("8"), 
                    title = "Player Cards"
                ),

                # Column 2: Ridgeline Plots Wrapped
                ui.layout_column_wrap(

                    # Series Results
                    ui.card(ui.card_header("Series Results"), 
                            ui.output_plot("p2_series_diffs")),

                    # Map Results Differentials
                    ui.navset_card_pill(
                        ui.nav_panel("Hardpoint", ui.output_plot("p2_hp_score_diffs")), 
                        ui.nav_panel("Control", ui.output_plot("p2_ctrl_score_diffs")),
                        title = "Map Results"
                        
                    ),

                    width = 1

                ),

                # Row Height
                height = "640px",

                # Column Widths
                col_widths = [8, 4]
            ), 

            # Row 4 of 4: Scoreboards & Score Differentials
            ui.layout_columns(

                # Column 1: Scoreboards
                ui.card(ui.card_header("Scoreboards"), 
                        ui.output_data_frame("p2_scoreboards"), 
                        full_screen = True),

                # Column 2: Team A Maps Played: HP & Ctrl
                ui.navset_card_pill( 
                    ui.nav_panel("Hardpoint", ui.output_plot("p2_team_a_hps")), 
                    ui.nav_panel("Control", ui.output_plot("p2_team_a_ctrls")),
                    title = ui.output_text("p2_team_a_name")
                ),

                # Column 3: Team B Maps Played
                ui.navset_card_pill( 
                    ui.nav_panel("Hardpoint", ui.output_plot("p2_team_b_hps")), 
                    ui.nav_panel("Control", ui.output_plot("p2_team_b_ctrls")),
                    title = ui.output_text("p2_team_b_name")
                ),
                    
                # Row Height
                height = "360px",
                
                # Column Widths
                col_widths = [6, 3, 3]

            ), 
        )
    ),

    # 4th Page: Map Vetoes
    ui.nav_panel("Vetoes",

        # ui.card(ui.card_header("Vetoes"), 
        #         ui.output_data_frame("vetoes"), 
        #         full_screen = True),


    ),

    # App Title
    title = "CDL Bets on PrizePicks", 

    # Background Color of Navbar
    # bg = "#e9ecef"
    inverse = True

)


# Define server logic
def server(input, output, session):
    
    # Theme picker
    # shinyswatch.theme_picker_server()

    # Intialize reactive dataframe of player props
    player_props_df = reactive.value(initial_player_props)
    
    # Reactive event to update player props dataframe
    # Displays progress bar while scraping
    @reactive.effect
    @reactive.event(input.scrape)
    async def scrape_props():
        with ui.Progress(min = 1, max = 15) as p:
            p.set(message = "Scraping PrizePicks", detail = "Please wait...")
            
            newVal = merge_player_props(
                player_props_df(), 
                scrape_prizepicks(), 
                rostersDF
            )
            player_props_df.set(newVal)

            for i in range(1, 15):
                if i <= 10:
                    p.set(i, message = "Scraping PrizePicks")
                else:
                    p.set(i, message = "Finished")
                await asyncio.sleep(0.1)

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
                        "width": "120px", "height": "120px"}
        return img
    
    # Team B Logo
    @render.image
    def team_b_logo():
        img: ImgData = {"src": os.path.dirname(__file__) + team_logos[input.team_b()], 
                        "width": "120px", "height": "120px"}
        return img
    
    # Date of Last Match
    @render.ui
    def last_match_date():
        return compute_last_match(cdlDF, input.team_a(), input.team_b())
    
    # Team A Series Record for Major 3 Quals
    @render.ui
    def team_a_standing():
        wins = current_standings.loc[current_standings['team'] == input.team_a(), 'wins'].reset_index(drop=True)[0]
        losses = current_standings.loc[current_standings['team'] == input.team_a(), 'losses'].reset_index(drop=True)[0]
        return f"{wins} - {losses}"

    # Team B Series Record for Major 3 Quals
    @render.ui
    def team_b_standing():
        wins = current_standings.loc[current_standings['team'] == input.team_b(), 'wins'].reset_index(drop=True)[0]
        losses = current_standings.loc[current_standings['team'] == input.team_b(), 'losses'].reset_index(drop=True)[0]
        return f"{wins} - {losses}"
    
    # H2H Series Record for User-Selected Map & Mode Combination
    @render.ui
    def h2h_series_record():
        return compute_h2h_series_record(cdlDF, input.team_a(), input.team_b())
    
    # Title for Team A Map Record Value Box
    @render.ui
    def team_a_map_record_title():
        if input.map_name() == "All":
            return f"{gamemode_abbrs[gamemode()]} Win %"
        else:
            return f"{input.map_name()} {gamemode_abbrs[gamemode()]} Win %"
        
    # Title for Team B Map Record Value Box
    @render.ui
    def team_b_map_record_title():
        if input.map_name() == "All":
            return f"{gamemode_abbrs[gamemode()]} Win %"
        else:
            return f"{input.map_name()} {gamemode_abbrs[gamemode()]} Win %"
        
    # Title for H2H Value Box
    @render.ui
    def map_h2h_title():
        if input.map_name() == "All":
            return f"{gamemode_abbrs[gamemode()]} H2H"
        else:
            return f"{input.map_name()} {gamemode_abbrs[gamemode()]} H2H"
        
    # Team A Map Record for User-Selected Map & Mode Combination
    @render.ui
    def team_a_map_record():
        if input.map_name() == "All":
            map_to_search_for = "Overall"
        else:
            map_to_search_for = input.map_name()
        wins = team_summaries_DF.loc[
            (team_summaries_DF['team'] == input.team_a()) &
            (team_summaries_DF['gamemode'] == gamemode()) & 
            (team_summaries_DF['map_name'] == map_to_search_for), 'wins'].reset_index(drop=True)[0]
        losses = team_summaries_DF.loc[
            (team_summaries_DF['team'] == input.team_a()) &
            (team_summaries_DF['gamemode'] == gamemode()) & 
            (team_summaries_DF['map_name'] == map_to_search_for), 'losses'].reset_index(drop=True)[0]
        win_percentage = team_summaries_DF.loc[
            (team_summaries_DF['team'] == input.team_a()) &
            (team_summaries_DF['gamemode'] == gamemode()) & 
            (team_summaries_DF['map_name'] == map_to_search_for), 'win_percentage'].reset_index(drop=True)[0]
        return f"{win_percentage:.0%} ({wins} - {losses})"
    
    # Team A Map Win Percentage Icon
    @render.ui
    def team_a_win_percent_icon():
        map_to_search_for = "Overall" if input.map_name() == "All" else input.map_name()
        win_percentage = team_summaries_DF.loc[
            (team_summaries_DF['team'] == input.team_a()) &
            (team_summaries_DF['gamemode'] == gamemode()) & 
            (team_summaries_DF['map_name'] == map_to_search_for), 'win_percentage'].reset_index(drop=True)[0]
        return ICONS["plus"] if win_percentage >= 0.5 else ICONS["minus"]
                

    # Team B Map Record for User-Selected Map & Mode Combination
    @render.ui
    def team_b_map_record():
        if input.map_name() == "All":
            map_to_search_for = "Overall"
        else:
            map_to_search_for = input.map_name()
        wins = team_summaries_DF.loc[
            (team_summaries_DF['team'] == input.team_b()) &
            (team_summaries_DF['gamemode'] == gamemode()) & 
            (team_summaries_DF['map_name'] == map_to_search_for), 'wins'].reset_index(drop=True)[0]
        losses = team_summaries_DF.loc[
            (team_summaries_DF['team'] == input.team_b()) &
            (team_summaries_DF['gamemode'] == gamemode()) & 
            (team_summaries_DF['map_name'] == map_to_search_for), 'losses'].reset_index(drop=True)[0]
        win_percentage = team_summaries_DF.loc[
            (team_summaries_DF['team'] == input.team_b()) &
            (team_summaries_DF['gamemode'] == gamemode()) & 
            (team_summaries_DF['map_name'] == map_to_search_for), 'win_percentage'].reset_index(drop=True)[0]
        return f"{win_percentage:.0%} ({wins} - {losses})"
    
    # Team B Map Win Percentage Icon
    @render.ui
    def team_b_win_percent_icon():
        map_to_search_for = "Overall" if input.map_name() == "All" else input.map_name()
        win_percentage = team_summaries_DF.loc[
            (team_summaries_DF['team'] == input.team_b()) &
            (team_summaries_DF['gamemode'] == gamemode()) & 
            (team_summaries_DF['map_name'] == map_to_search_for), 'win_percentage'].reset_index(drop=True)[0]
        return ICONS["plus"] if win_percentage >= 0.5 else ICONS["minus"]

    # H2H Map Record for User-Selected Map & Mode Combination
    @render.ui
    def h2h_map_record():
        return compute_h2h_map_record(cdlDF, input.team_a(), input.team_b(), 
                                      gamemode(), input.map_name())
    
    # Title for Team A Win Streak Value Box
    @render.ui
    def team_a_win_streak_title():
        if input.map_name() == "All":
            return f"{gamemode_abbrs[gamemode()]} Win Streak"
        else:
            return f"{input.map_name()} {gamemode_abbrs[gamemode()]} Win Streak"
        
    # Title for Team B Win Streak Value Box
    @render.ui
    def team_b_win_streak_title():
        if input.map_name() == "All":
            return f"{gamemode_abbrs[gamemode()]} Win Streak"
        else:
            return f"{input.map_name()} {gamemode_abbrs[gamemode()]} Win Streak"
        
    # Compute Team A Win Streak
    @reactive.calc
    def compute_team_a_win_streak():
        return compute_win_streak(cdlDF, input.team_a(), gamemode(), input.map_name())
    
    # Compute Team B Win Streak
    @reactive.calc
    def compute_team_b_win_streak():
        return compute_win_streak(cdlDF, input.team_b(), gamemode(), input.map_name())

    # Team A Win Streak for User-Selected Map & Mode Combination
    @render.ui
    def team_a_win_streak():
        return str(compute_team_a_win_streak())
    
    # Team B Win Streak for User-Selected Map & Mode Combination
    @render.ui
    def team_b_win_streak():
        return str(compute_team_b_win_streak())
    
    # Change Win Streak Icon Based on Sign of Win Streak
    @render.ui
    def change_team_a_win_streak_icon():
        win_streak = compute_team_a_win_streak()
        return ICONS["check"] if win_streak > 0 else ICONS["exclamation"]
    
    # Change Win Streak Icon Based on Sign of Win Streak
    @render.ui
    def change_team_b_win_streak_icon():
        win_streak = compute_team_b_win_streak()
        return ICONS["check"] if win_streak > 0 else ICONS["exclamation"]
    
    # Ridgeline Plots of Score Diffs
    @render.plot
    def score_diffs():
        return score_diffs_ridge(
            cdlDF, 
            team_icons[input.team_a()], team_icons[input.team_b()], 
            team_a_color, team_b_color,
            gamemode(), 
            input.map_name()
        )
    
    # Team A Donut Chart of % Maps Played
    @render.plot
    def team_a_maps_played():
        return team_percent_maps_played(
            team_summaries_DF, team_icons[input.team_a()], gamemode()
        )
    
    # Team B Donut Chart of % Maps Played
    @render.plot
    def team_b_maps_played():
        return team_percent_maps_played(
            team_summaries_DF, team_icons[input.team_b()], gamemode()
        )
    
    # Team A Series Differentials Histogram
    @render.plot
    def series_diffs():
        return series_diff_ridge(
            series_score_diffs,
            team_icons[input.team_a()], team_icons[input.team_b()], 
            team_a_color, team_b_color
        )
    
    # Datagrid of Player Kills and Map Results for Selected Teams
    # Aka. Scoreboards
    @render.data_frame
    def scoreboards():
        return render.DataGrid(
            build_scoreboards(
                cdlDF, 
                input.team_a(),
                input.team_b(),
                gamemode(), 
                input.map_name()
            ), 
            filters = True, 
            summary = False
        )
    
    # Player One Line
    @reactive.Calc
    def player_1_line():
        return get_line(player_props_df.get(), input.team_a(), 1, map_num())
    
    # Player Two Line
    @reactive.Calc
    def player_2_line():
        return get_line(player_props_df.get(), input.team_a(), 2, map_num())
    
    # Player Three Line
    @reactive.Calc
    def player_3_line():
        return get_line(player_props_df.get(), input.team_a(), 3, map_num())
    
    # Player Four Line
    @reactive.Calc
    def player_4_line():
        return get_line(player_props_df.get(), input.team_a(), 4, map_num())
    
    # Player Five Line
    @reactive.Calc
    def player_5_line():
        return get_line(player_props_df.get(), input.team_b(), 1, map_num())
    
    # Player Six Line
    @reactive.Calc
    def player_6_line():
        return get_line(player_props_df.get(), input.team_b(), 2, map_num())
    
    # Player Seven Line
    @reactive.Calc
    def player_7_line():
        return get_line(player_props_df.get(), input.team_b(), 3, map_num())
    
    # Player Eight Line
    @reactive.Calc
    def player_8_line():
        return get_line(player_props_df.get(), input.team_b(), 4, map_num())
    
    # Player One Plot
    @render.plot
    def player_1_plot():
        if input.x_axis() == "Time":
            return player_kills_vs_time(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.team_a()].iloc[0]['player'],
                team_a_color,
                gamemode(), 
                player_1_line(),
                input.map_name()
            )
        else:
            return player_kills_vs_score_diff(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.team_a()].iloc[0]['player'],
                team_a_color,
                gamemode(), 
                player_1_line(),
                input.map_name()
            )
        
    # Player Two Plot
    @render.plot
    def player_2_plot():
        if input.x_axis() == "Time":
            return player_kills_vs_time(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.team_a()].iloc[1]['player'],
                team_a_color,
                gamemode(), 
                player_2_line(),
                input.map_name()
            )
        else:
            return player_kills_vs_score_diff(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.team_a()].iloc[1]['player'],
                team_a_color,
                gamemode(), 
                player_2_line(),
                input.map_name()
            )
        
    # Player Three Plot
    @render.plot
    def player_3_plot():
        if input.x_axis() == "Time":
            return player_kills_vs_time(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.team_a()].iloc[2]['player'],
                team_a_color,
                gamemode(), 
                player_3_line(),
                input.map_name()
            )
        else:
            return player_kills_vs_score_diff(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.team_a()].iloc[2]['player'],
                team_a_color,
                gamemode(), 
                player_3_line(),
                input.map_name()
            )
        
    # Player Four Plot
    @render.plot
    def player_4_plot():
        if input.x_axis() == "Time":
            return player_kills_vs_time(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.team_a()].iloc[3]['player'],
                team_a_color,
                gamemode(), 
                player_4_line(),
                input.map_name()
            )
        else:
            return player_kills_vs_score_diff(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.team_a()].iloc[3]['player'],
                team_a_color,
                gamemode(), 
                player_4_line(),
                input.map_name()
            )
        
    # Player Five Plot
    @render.plot
    def player_5_plot():
        if input.x_axis() == "Time":
            return player_kills_vs_time(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.team_b()].iloc[0]['player'],
                team_b_color,
                gamemode(), 
                player_5_line(),
                input.map_name()
            )
        else:
            return player_kills_vs_score_diff(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.team_b()].iloc[0]['player'],
                team_b_color,
                gamemode(), 
                player_5_line(),
                input.map_name()
            )
        
    # Player Six Plot
    @render.plot
    def player_6_plot():
        if input.x_axis() == "Time":
            return player_kills_vs_time(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.team_b()].iloc[1]['player'],
                team_b_color,
                gamemode(), 
                player_6_line(),
                input.map_name()
            )
        else:
            return player_kills_vs_score_diff(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.team_b()].iloc[1]['player'],
                team_b_color,
                gamemode(), 
                player_6_line(),
                input.map_name()
            )
        
    # Player Seven Plot
    @render.plot
    def player_7_plot():
        if input.x_axis() == "Time":
            return player_kills_vs_time(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.team_b()].iloc[2]['player'],
                team_b_color,
                gamemode(), 
                player_7_line(),
                input.map_name()
            )
        else:
            return player_kills_vs_score_diff(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.team_b()].iloc[2]['player'],
                team_b_color,
                gamemode(), 
                player_7_line(),
                input.map_name()
            )
        
    # Player Eight Plot
    @render.plot
    def player_8_plot():
        if input.x_axis() == "Time":
            return player_kills_vs_time(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.team_b()].iloc[3]['player'],
                team_b_color,
                gamemode(), 
                player_8_line(),
                input.map_name()
            )
        else:
            return player_kills_vs_score_diff(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.team_b()].iloc[3]['player'],
                team_b_color,
                gamemode(), 
                player_8_line(),
                input.map_name()
            )

    # Player One O/U Calcs
    @reactive.calc
    def player_1_ou_stats():
        return player_over_under_percentage(
            cdlDF, 
            rostersDF[rostersDF['team'] == input.team_a()].iloc[0]['player'], 
            gamemode(), 
            player_1_line(), 
            input.map_name()
            )
    
    # Player Two O/U Calcs
    @reactive.calc
    def player_2_ou_stats():
        return player_over_under_percentage(
            cdlDF, 
            rostersDF[rostersDF['team'] == input.team_a()].iloc[1]['player'], 
            gamemode(), 
            player_2_line(), 
            input.map_name()
            )
    
    # Player Three O/U Calcs
    @reactive.calc
    def player_3_ou_stats():
        return player_over_under_percentage(
            cdlDF, 
            rostersDF[rostersDF['team'] == input.team_a()].iloc[2]['player'], 
            gamemode(), 
            player_3_line(), 
            input.map_name()
            )
    
    # Player Four O/U Calcs
    @reactive.calc
    def player_4_ou_stats():
        return player_over_under_percentage(
            cdlDF, 
            rostersDF[rostersDF['team'] == input.team_a()].iloc[3]['player'], 
            gamemode(), 
            player_4_line(), 
            input.map_name()
            )
    
    # Player Five O/U Calcs
    @reactive.calc
    def player_5_ou_stats():
        return player_over_under_percentage(
            cdlDF, 
            rostersDF[rostersDF['team'] == input.team_b()].iloc[0]['player'], 
            gamemode(), 
            player_5_line(), 
            input.map_name()
            )
    
    # Player Six O/U Calcs
    @reactive.calc
    def player_6_ou_stats():
        return player_over_under_percentage(
            cdlDF, 
            rostersDF[rostersDF['team'] == input.team_b()].iloc[1]['player'], 
            gamemode(), 
            player_6_line(), 
            input.map_name()
            )
    
    # Player Seven O/U Calcs
    @reactive.calc
    def player_7_ou_stats():
        return player_over_under_percentage(
            cdlDF, 
            rostersDF[rostersDF['team'] == input.team_b()].iloc[2]['player'], 
            gamemode(), 
            player_7_line(), 
            input.map_name()
            )
    
    # Player Eight O/U Calcs
    @reactive.calc
    def player_8_ou_stats():
        return player_over_under_percentage(
            cdlDF, 
            rostersDF[rostersDF['team'] == input.team_b()].iloc[3]['player'], 
            gamemode(), 
            player_8_line(), 
            input.map_name()
            )

    # Player One O/U %
    @render.text
    def player_1_ou():
        over_under, percentage, overs, unders, hooks = player_1_ou_stats()
        if over_under == "Never Played":
            return over_under
        return f"{over_under} {percentage}%\n({overs} - {unders} - {hooks})"
    
    # Player Two O/U %
    @render.text
    def player_2_ou():
        over_under, percentage, overs, unders, hooks = player_2_ou_stats()
        if over_under == "Never Played":
            return over_under
        return f"{over_under} {percentage}%\n({overs} - {unders} - {hooks})"

    # Player Three O/U %
    @render.text
    def player_3_ou():
        over_under, percentage, overs, unders, hooks = player_3_ou_stats()
        if over_under == "Never Played":
            return over_under
        return f"{over_under} {percentage}%\n({overs} - {unders} - {hooks})"

    # Player Four O/U %
    @render.text
    def player_4_ou():
        over_under, percentage, overs, unders, hooks = player_4_ou_stats()
        if over_under == "Never Played":
            return over_under
        return f"{over_under} {percentage}%\n({overs} - {unders} - {hooks})"

    # Player Five O/U %
    @render.text
    def player_5_ou():
        over_under, percentage, overs, unders, hooks = player_5_ou_stats()
        if over_under == "Never Played":
            return over_under
        return f"{over_under} {percentage}%\n({overs} - {unders} - {hooks})"

    # Player Six O/U %
    @render.text
    def player_6_ou():
        over_under, percentage, overs, unders, hooks = player_6_ou_stats()
        if over_under == "Never Played":
            return over_under
        return f"{over_under} {percentage}%\n({overs} - {unders} - {hooks})"

    # Player Seven O/U %
    @render.text
    def player_7_ou():
        over_under, percentage, overs, unders, hooks = player_7_ou_stats()
        if over_under == "Never Played":
            return over_under
        return f"{over_under} {percentage}%\n({overs} - {unders} - {hooks})"

    # Player Eight O/U %
    @render.text
    def player_8_ou():
        over_under, percentage, overs, unders, hooks = player_8_ou_stats()
        if over_under == "Never Played":
            return over_under
        return f"{over_under} {percentage}%\n({overs} - {unders} - {hooks})"
    
    # Player One O/U Icon
    @render.ui
    def player_1_ou_icon():
        over_under = player_1_ou_stats()[0]
        return ICONS["chevron_up"] if over_under == "Over" else ICONS["chevron_down"]
        
    # Player Two O/U Icon
    @render.ui
    def player_2_ou_icon():
        over_under = player_2_ou_stats()[0]
        return ICONS["chevron_up"] if over_under == "Over" else ICONS["chevron_down"]
        
    # Player Three O/U Icon
    @render.ui
    def player_3_ou_icon():
        over_under = player_3_ou_stats()[0]
        return ICONS["chevron_up"] if over_under == "Over" else ICONS["chevron_down"]
        
    # Player Four O/U Icon
    @render.ui
    def player_4_ou_icon():
        over_under = player_4_ou_stats()[0]
        return ICONS["chevron_up"] if over_under == "Over" else ICONS["chevron_down"]
        
    # Player Five O/U Icon
    @render.ui
    def player_5_ou_icon():
        over_under = player_5_ou_stats()[0]
        return ICONS["chevron_up"] if over_under == "Over" else ICONS["chevron_down"]
        
    # Player Six O/U Icon
    @render.ui
    def player_6_ou_icon():
        over_under = player_6_ou_stats()[0]
        return ICONS["chevron_up"] if over_under == "Over" else ICONS["chevron_down"]
        
    # Player Seven O/U Icon
    @render.ui
    def player_7_ou_icon():
        over_under = player_7_ou_stats()[0]
        return ICONS["chevron_up"] if over_under == "Over" else ICONS["chevron_down"]
        
    # Player Eight O/U Icon
    @render.ui
    def player_8_ou_icon():
        over_under = player_8_ou_stats()[0]
        return ICONS["chevron_up"] if over_under == "Over" else ICONS["chevron_down"]
        
    # Player 1 O/U Streak
    @render.ui
    def player_1_ou_streak():
        ou, streak = player_over_under_streak(
            cdlDF, 
            rostersDF[rostersDF['team'] == input.team_a()].iloc[0]['player'], 
            gamemode(), 
            player_1_line(), 
            input.map_name()
        )
        return f"{ou} {streak}"
    
    # Player 2 O/U Streak
    @render.ui
    def player_2_ou_streak():
        ou, streak = player_over_under_streak(
            cdlDF, 
            rostersDF[rostersDF['team'] == input.team_a()].iloc[1]['player'], 
            gamemode(), 
            player_2_line(), 
            input.map_name()
        )
        return f"{ou} {streak}"
    
    # Player 3 O/U Streak
    @render.ui
    def player_3_ou_streak():
        ou, streak = player_over_under_streak(
            cdlDF, 
            rostersDF[rostersDF['team'] == input.team_a()].iloc[2]['player'], 
            gamemode(), 
            player_3_line(), 
            input.map_name()
        )
        return f"{ou} {streak}"
    
    # Player 4 O/U Streak
    @render.ui
    def player_4_ou_streak():
        ou, streak = player_over_under_streak(
            cdlDF, 
            rostersDF[rostersDF['team'] == input.team_a()].iloc[3]['player'], 
            gamemode(), 
            player_4_line(), 
            input.map_name()
        )
        return f"{ou} {streak}"
    
    # Player 5 O/U Streak
    @render.ui
    def player_5_ou_streak():
        ou, streak = player_over_under_streak(
            cdlDF, 
            rostersDF[rostersDF['team'] == input.team_b()].iloc[0]['player'], 
            gamemode(), 
            player_5_line(), 
            input.map_name()
        )
        return f"{ou} {streak}"
    
    # Player 6 O/U Streak
    @render.ui
    def player_6_ou_streak():
        ou, streak = player_over_under_streak(
            cdlDF, 
            rostersDF[rostersDF['team'] == input.team_b()].iloc[1]['player'], 
            gamemode(), 
            player_6_line(), 
            input.map_name()
        )
        return f"{ou} {streak}"
    
    # Player 7 O/U Streak
    @render.ui
    def player_7_ou_streak():
        ou, streak = player_over_under_streak(
            cdlDF, 
            rostersDF[rostersDF['team'] == input.team_b()].iloc[2]['player'], 
            gamemode(), 
            player_7_line(), 
            input.map_name()
        )
        return f"{ou} {streak}"
    
    # Player 8 O/U Streak
    @render.ui
    def player_8_ou_streak():
        ou, streak = player_over_under_streak(
            cdlDF, 
            rostersDF[rostersDF['team'] == input.team_b()].iloc[3]['player'], 
            gamemode(), 
            player_8_line(), 
            input.map_name()
        )
        return f"{ou} {streak}"
    
    # Team A Name for Maps Played Card Header
    @render.text
    def team_a_name():
        return team_icons[input.team_a()] + " Maps Played"
    
    # Team B Name for Maps Played Card Header
    @render.text
    def team_b_name():
        return team_icons[input.team_b()] + " Maps Played"
    
    # Team A Name for Maps Played Card Header | Page 2
    @render.text
    def p2_team_a_name():
        return team_icons[input.p2_team_a()] + " Maps Played"
    
    # Team B Name for Maps Played Card Header | Page2
    @render.text
    def p2_team_b_name():
        return team_icons[input.p2_team_b()] + " Maps Played"
    
    # Team A Logo | Page 2
    @render.image
    def p2_team_a_logo():
        img: ImgData = {"src": os.path.dirname(__file__) + team_logos[input.p2_team_a()], 
                        "width": "120px", "height": "120px"}
        return img
    
    # Team B Logo | Page 2
    @render.image
    def p2_team_b_logo():
        img: ImgData = {"src": os.path.dirname(__file__) + team_logos[input.p2_team_b()], 
                        "width": "120px", "height": "120px"}
        return img
    
    # Date of Last Match | Page 2
    @render.ui
    def p2_last_match_date():
        return compute_last_match(cdlDF, input.p2_team_a(), input.p2_team_b())
    
    # Team A Series Record for Major 3 Quals | Page 2
    @render.ui
    def p2_team_a_standing():
        wins = current_standings.loc[current_standings['team'] == input.p2_team_a(), 'wins'].reset_index(drop=True)[0]
        losses = current_standings.loc[current_standings['team'] == input.p2_team_a(), 'losses'].reset_index(drop=True)[0]
        return f"{wins} - {losses}"

    # Team B Series Record for Major 3 Quals | Page 2
    @render.ui
    def p2_team_b_standing():
        wins = current_standings.loc[current_standings['team'] == input.p2_team_b(), 'wins'].reset_index(drop=True)[0]
        losses = current_standings.loc[current_standings['team'] == input.p2_team_b(), 'losses'].reset_index(drop=True)[0]
        return f"{wins} - {losses}"
    
    # H2H Series Record for User-Selected Map & Mode Combination | Page 2
    @render.ui
    def p2_h2h_series_record():
        return compute_h2h_series_record(cdlDF, input.p2_team_a(), input.p2_team_b())
    
    # Team A HP Record for User-Selected Map | Page 2
    @render.ui
    def team_a_hp_record():
        if input.p2_map_one() == "All":
            map_to_search_for = "Overall"
        else:
            map_to_search_for = input.p2_map_one()
        wins = team_summaries_DF.loc[
            (team_summaries_DF['team'] == input.p2_team_a()) &
            (team_summaries_DF['gamemode'] == "Hardpoint") & 
            (team_summaries_DF['map_name'] == map_to_search_for), 'wins'].reset_index(drop=True)[0]
        losses = team_summaries_DF.loc[
            (team_summaries_DF['team'] == input.p2_team_a()) &
            (team_summaries_DF['gamemode'] == "Hardpoint") & 
            (team_summaries_DF['map_name'] == map_to_search_for), 'losses'].reset_index(drop=True)[0]
        win_percentage = team_summaries_DF.loc[
            (team_summaries_DF['team'] == input.p2_team_a()) &
            (team_summaries_DF['gamemode'] == "Hardpoint") & 
            (team_summaries_DF['map_name'] == map_to_search_for), 'win_percentage'].reset_index(drop=True)[0]
        return f"{win_percentage:.0%} ({wins} - {losses})"
    
    # Team B HP Record for User-Selected Map | Page 2
    @render.ui
    def team_b_hp_record():
        if input.p2_map_one() == "All":
            map_to_search_for = "Overall"
        else:
            map_to_search_for = input.p2_map_one()
        wins = team_summaries_DF.loc[
            (team_summaries_DF['team'] == input.p2_team_b()) &
            (team_summaries_DF['gamemode'] == "Hardpoint") & 
            (team_summaries_DF['map_name'] == map_to_search_for), 'wins'].reset_index(drop=True)[0]
        losses = team_summaries_DF.loc[
            (team_summaries_DF['team'] == input.p2_team_b()) &
            (team_summaries_DF['gamemode'] == "Hardpoint") & 
            (team_summaries_DF['map_name'] == map_to_search_for), 'losses'].reset_index(drop=True)[0]
        win_percentage = team_summaries_DF.loc[
            (team_summaries_DF['team'] == input.p2_team_b()) &
            (team_summaries_DF['gamemode'] == "Hardpoint") & 
            (team_summaries_DF['map_name'] == map_to_search_for), 'win_percentage'].reset_index(drop=True)[0]
        return f"{win_percentage:.0%} ({wins} - {losses})"
    
    # Team A Control Record for User-Selected Map | Page 2
    @render.ui
    def team_a_ctrl_record():
        if input.p2_map_three() == "All":
            map_to_search_for = "Overall"
        else:
            map_to_search_for = input.p2_map_three()
        wins = team_summaries_DF.loc[
            (team_summaries_DF['team'] == input.p2_team_a()) &
            (team_summaries_DF['gamemode'] == "Control") & 
            (team_summaries_DF['map_name'] == map_to_search_for), 'wins'].reset_index(drop=True)[0]
        losses = team_summaries_DF.loc[
            (team_summaries_DF['team'] == input.p2_team_a()) &
            (team_summaries_DF['gamemode'] == "Control") & 
            (team_summaries_DF['map_name'] == map_to_search_for), 'losses'].reset_index(drop=True)[0]
        win_percentage = team_summaries_DF.loc[
            (team_summaries_DF['team'] == input.p2_team_a()) &
            (team_summaries_DF['gamemode'] == "Control") & 
            (team_summaries_DF['map_name'] == map_to_search_for), 'win_percentage'].reset_index(drop=True)[0]
        return f"{win_percentage:.0%} ({wins} - {losses})"
    
    # Team B Control Record for User-Selected Map | Page 2
    @render.ui
    def team_b_ctrl_record():
        if input.p2_map_three() == "All":
            map_to_search_for = "Overall"
        else:
            map_to_search_for = input.p2_map_three()
        wins = team_summaries_DF.loc[
            (team_summaries_DF['team'] == input.p2_team_b()) &
            (team_summaries_DF['gamemode'] == "Control") & 
            (team_summaries_DF['map_name'] == map_to_search_for), 'wins'].reset_index(drop=True)[0]
        losses = team_summaries_DF.loc[
            (team_summaries_DF['team'] == input.p2_team_b()) &
            (team_summaries_DF['gamemode'] == "Control") & 
            (team_summaries_DF['map_name'] == map_to_search_for), 'losses'].reset_index(drop=True)[0]
        win_percentage = team_summaries_DF.loc[
            (team_summaries_DF['team'] == input.p2_team_b()) &
            (team_summaries_DF['gamemode'] == "Control") & 
            (team_summaries_DF['map_name'] == map_to_search_for), 'win_percentage'].reset_index(drop=True)[0]
        return f"{win_percentage:.0%} ({wins} - {losses})"
    
    # Title for Team A HP Record Value Box | Page 2 
    @render.ui
    def team_a_hp_title():
        if input.p2_map_one() == "All":
            return "HP Win %"
        else:
            return f"{input.p2_map_one()} HP Win %"
        
    # Title for Team A HP Record Value Box | Page 2 
    @render.ui
    def team_b_hp_title():
        if input.p2_map_one() == "All":
            return "HP Win %"
        else:
            return f"{input.p2_map_one()} HP Win %"
        
    # Title for Team A HP Record Value Box | Page 2 
    @render.ui
    def team_a_ctrl_title():
        if input.p2_map_one() == "All":
            return "Control Win %"
        else:
            return f"{input.p2_map_three()} Control Win %"
        
    # Title for Team A HP Record Value Box | Page 2 
    @render.ui
    def team_b_ctrl_title():
        if input.p2_map_one() == "All":
            return "Control Win %"
        else:
            return f"{input.p2_map_three()} Control Win %"
        
    # Team A Donut Chart of HPs Played | Page 2
    @render.plot
    def p2_team_a_hps():
        return team_percent_maps_played(
            team_summaries_DF, team_icons[input.p2_team_a()], "Hardpoint"
        )
    
    # Team A Donut Chart of Controls Played | Page 2
    @render.plot
    def p2_team_a_ctrls():
        return team_percent_maps_played(
            team_summaries_DF, team_icons[input.p2_team_a()], "Control"
        )
    
    # Team B Donut Chart of HPs Played | Page 2
    @render.plot
    def p2_team_b_hps():
        return team_percent_maps_played(
            team_summaries_DF, team_icons[input.p2_team_b()], "Hardpoint"
        )
    
    # Team B Donut Chart of Controls Played | Page 2
    @render.plot
    def p2_team_b_ctrls():
        return team_percent_maps_played(
            team_summaries_DF, team_icons[input.p2_team_b()], "Control"
        )
    
    # Ridgeline Plot of Series Diffs | Page 2
    @render.plot
    def p2_series_diffs():
        return series_diff_ridge(
            series_score_diffs, 
            team_icons[input.p2_team_a()], team_icons[input.p2_team_b()], 
            team_a_color, team_b_color
            )
    
    # Ridgeline Plot of Hardpoint Score Diffs | Page 2
    @render.plot
    def p2_hp_score_diffs():
        return score_diffs_ridge(
            cdlDF, 
            team_icons[input.p2_team_a()], team_icons[input.p2_team_b()], 
            team_a_color, team_b_color, 
            "Hardpoint", 
            input.p2_map_one()
            )
    
    # Ridgeline Plot of Control Score Diffs | Page 2
    @render.plot
    def p2_hp_score_diffs():
        return score_diffs_ridge(
            cdlDF, 
            team_icons[input.p2_team_a()], team_icons[input.p2_team_b()], 
            team_a_color, team_b_color, 
            "Control", 
            input.p2_map_one()
            )
    
    # Datagrid of Player Kills and Map Results for Selected Teams | Page 2
    # Aka. Scoreboards
    @render.data_frame
    def p2_scoreboards():
        return render.DataGrid(
            build_scoreboards(
                cdlDF, 
                input.p2_team_a(),
                input.p2_team_b()
            ), 
            filters = True, 
            summary = False
        )
    
    # Player One Line | Page 2
    @reactive.Calc
    def p2_player_1_line():
        return get_line(player_props_df.get(), input.p2_team_a(), 1, 0)
    
    # Player One Map One Line | Page 2
    @reactive.Calc
    def p2_player_1_map_1_line():
        return get_line(player_props_df.get(), input.p2_team_a(), 1, 1)
    
    # Player One Map Three Line | Page 2
    @reactive.Calc
    def p2_player_1_map_3_line():
        return get_line(player_props_df.get(), input.p2_team_a(), 1, 3)
    
    # Player Two Line | Page 2
    @reactive.Calc
    def p2_player_2_line():
        return get_line(player_props_df.get(), input.p2_team_a(), 2, 0)
    
    # Player Two Map One Line | Page 2
    @reactive.Calc
    def p2_player_2_map_1_line():
        return get_line(player_props_df.get(), input.p2_team_a(), 2, 1)
    
    # Player Two Map Three Line | Page 2
    @reactive.Calc
    def p2_player_2_map_3_line():
        return get_line(player_props_df.get(), input.p2_team_a(), 2, 3)
    
    # Player Three Line | Page 2
    @reactive.Calc
    def p2_player_3_line():
        return get_line(player_props_df.get(), input.p2_team_a(), 3, 0)
    
    # Player Three Map One Line | Page 2
    @reactive.Calc
    def p2_player_3_map_1_line():
        return get_line(player_props_df.get(), input.p2_team_a(), 3, 1)
    
    # Player Three Map Three Line | Page 2
    @reactive.Calc
    def p2_player_3_map_3_line():
        return get_line(player_props_df.get(), input.p2_team_a(), 3, 3)
    
    # Player Four Line | Page 2
    @reactive.Calc
    def p2_player_4_line():
        return get_line(player_props_df.get(), input.p2_team_a(), 4, 0)
    
    # Player Four Map One Line | Page 2
    @reactive.Calc
    def p2_player_4_map_1_line():
        return get_line(player_props_df.get(), input.p2_team_a(), 4, 1)
    
    # Player Four Map Three Line | Page 2
    @reactive.Calc
    def p2_player_4_map_3_line():
        return get_line(player_props_df.get(), input.p2_team_a(), 4, 3)
    
    # Player Five Line | Page 2
    @reactive.Calc
    def p2_player_5_line():
        return get_line(player_props_df.get(), input.p2_team_b(), 1, 0)
    
    # Player Five Map One Line | Page 2
    @reactive.Calc
    def p2_player_5_map_1_line():
        return get_line(player_props_df.get(), input.p2_team_b(), 1, 1)
    
    # Player Five Map Three Line | Page 2
    @reactive.Calc
    def p2_player_5_map_3_line():
        return get_line(player_props_df.get(), input.p2_team_b(), 1, 3)
    
    # Player Six Line | Page 2
    @reactive.Calc
    def p2_player_6_line():
        return get_line(player_props_df.get(), input.p2_team_b(), 2, 0)
    
    # Player Six Map One Line | Page 2
    @reactive.Calc
    def p2_player_6_map_1_line():
        return get_line(player_props_df.get(), input.p2_team_b(), 2, 2)
    
    # Player Six Map Three Line | Page 2
    @reactive.Calc
    def p2_player_6_map_3_line():
        return get_line(player_props_df.get(), input.p2_team_b(), 2, 3)
    
    # Player Seven Line | Page 2
    @reactive.Calc
    def p2_player_7_line():
        return get_line(player_props_df.get(), input.p2_team_b(), 3, 0)
    # Player Seven Map One Line | Page 2
    @reactive.Calc
    def p2_player_7_map_1_line():
        return get_line(player_props_df.get(), input.p2_team_b(), 3, 1)
    
    # Player Seven Map Three Line | Page 2
    @reactive.Calc
    def p2_player_7_map_3_line():
        return get_line(player_props_df.get(), input.p2_team_b(), 3, 3)
    
    # Player Eight Line | Page 2
    @reactive.Calc
    def p2_player_8_line():
        return get_line(player_props_df.get(), input.p2_team_b(), 4, 0)
    
    # Player Eight Map One Line | Page 2
    @reactive.Calc
    def p2_player_8_map_1_line():
        return get_line(player_props_df.get(), input.p2_team_b(), 4, 1)
    
    # Player Eight Map Three Line | Page 2
    @reactive.Calc
    def p2_player_8_map_3_line():
        return get_line(player_props_df.get(), input.p2_team_b(), 4, 3)
    
    # Player One Plot | Page 2
    @render.plot
    def p2_player_1_plot():
        if input.p2_x_axis() == "Time":
            return player_1_thru_3_kills_vs_time(
                adj_1_thru_3_totals,
                rostersDF[rostersDF['team'] == input.p2_team_a()].iloc[0]['player'],
                team_a_color,
                p2_player_1_line(),
            )
        elif input.p2_x_axis() == "Hardpoint Map":
            return player_kills_by_map(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.p2_team_a()].iloc[0]['player'],
                "Hardpoint",
                p2_player_1_map_1_line()
            )
        elif input.p2_x_axis() == "Control Map":
            return player_kills_by_map(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.p2_team_a()].iloc[0]['player'],
                "Control",
                p2_player_1_map_3_line()
            )
        else:
            return player_kills_by_mapset(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.p2_team_a()].iloc[0]['player'],
                input.p2_map_one(),
                input.p2_map_two(),
                input.p2_map_three()
            )
        
    # Player Two Plot | Page 2
    @render.plot
    def p2_player_2_plot():
        if input.p2_x_axis() == "Time":
            return player_1_thru_3_kills_vs_time(
                adj_1_thru_3_totals,
                rostersDF[rostersDF['team'] == input.p2_team_a()].iloc[1]['player'],
                team_a_color,
                p2_player_1_line(),
            )
        elif input.p2_x_axis() == "Hardpoint Map":
            return player_kills_by_map(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.p2_team_a()].iloc[1]['player'],
                "Hardpoint",
                p2_player_1_map_1_line()
            )
        elif input.p2_x_axis() == "Control Map":
            return player_kills_by_map(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.p2_team_a()].iloc[1]['player'],
                "Control",
                p2_player_1_map_3_line()
            )
        else:
            return player_kills_by_mapset(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.p2_team_a()].iloc[1]['player'],
                input.p2_map_one(),
                input.p2_map_two(),
                input.p2_map_three()
            )
        
    # Player Three Plot | Page 2
    @render.plot
    def p2_player_3_plot():
        if input.p2_x_axis() == "Time":
            return player_1_thru_3_kills_vs_time(
                adj_1_thru_3_totals,
                rostersDF[rostersDF['team'] == input.p2_team_a()].iloc[2]['player'],
                team_a_color,
                p2_player_1_line(),
            )
        elif input.p2_x_axis() == "Hardpoint Map":
            return player_kills_by_map(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.p2_team_a()].iloc[2]['player'],
                "Hardpoint",
                p2_player_1_map_1_line()
            )
        elif input.p2_x_axis() == "Control Map":
            return player_kills_by_map(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.p2_team_a()].iloc[2]['player'],
                "Control",
                p2_player_1_map_3_line()
            )
        else:
            return player_kills_by_mapset(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.p2_team_a()].iloc[2]['player'],
                input.p2_map_one(),
                input.p2_map_two(),
                input.p2_map_three()
            )
        
    # Player Four Plot | Page 2
    @render.plot
    def p2_player_4_plot():
        if input.p2_x_axis() == "Time":
            return player_1_thru_3_kills_vs_time(
                adj_1_thru_3_totals,
                rostersDF[rostersDF['team'] == input.p2_team_a()].iloc[3]['player'],
                team_a_color,
                p2_player_1_line(),
            )
        elif input.p2_x_axis() == "Hardpoint Map":
            return player_kills_by_map(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.p2_team_a()].iloc[3]['player'],
                "Hardpoint",
                p2_player_1_map_1_line()
            )
        elif input.p2_x_axis() == "Control Map":
            return player_kills_by_map(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.p2_team_a()].iloc[3]['player'],
                "Control",
                p2_player_1_map_3_line()
            )
        else:
            return player_kills_by_mapset(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.p2_team_a()].iloc[3]['player'],
                input.p2_map_one(),
                input.p2_map_two(),
                input.p2_map_three()
            )
        
    # Player Five Plot | Page 2
    @render.plot
    def p2_player_5_plot():
        if input.p2_x_axis() == "Time":
            return player_1_thru_3_kills_vs_time(
                adj_1_thru_3_totals,
                rostersDF[rostersDF['team'] == input.p2_team_b()].iloc[0]['player'],
                team_b_color,
                p2_player_1_line(),
            )
        elif input.p2_x_axis() == "Hardpoint Map":
            return player_kills_by_map(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.p2_team_b()].iloc[0]['player'],
                "Hardpoint",
                p2_player_1_map_1_line()
            )
        elif input.p2_x_axis() == "Control Map":
            return player_kills_by_map(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.p2_team_b()].iloc[0]['player'],
                "Control",
                p2_player_1_map_3_line()
            )
        else:
            return player_kills_by_mapset(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.p2_team_b()].iloc[0]['player'],
                input.p2_map_one(),
                input.p2_map_two(),
                input.p2_map_three()
            )
        
    # Player Six Plot | Page 2
    @render.plot
    def p2_player_6_plot():
        if input.p2_x_axis() == "Time":
            return player_1_thru_3_kills_vs_time(
                adj_1_thru_3_totals,
                rostersDF[rostersDF['team'] == input.p2_team_b()].iloc[1]['player'],
                team_b_color,
                p2_player_1_line(),
            )
        elif input.p2_x_axis() == "Hardpoint Map":
            return player_kills_by_map(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.p2_team_b()].iloc[1]['player'],
                "Hardpoint",
                p2_player_1_map_1_line()
            )
        elif input.p2_x_axis() == "Control Map":
            return player_kills_by_map(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.p2_team_b()].iloc[1]['player'],
                "Control",
                p2_player_1_map_3_line()
            )
        else:
            return player_kills_by_mapset(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.p2_team_b()].iloc[1]['player'],
                input.p2_map_one(),
                input.p2_map_two(),
                input.p2_map_three()
            )
        
    # Player Seven Plot | Page 2
    @render.plot
    def p2_player_7_plot():
        if input.p2_x_axis() == "Time":
            return player_1_thru_3_kills_vs_time(
                adj_1_thru_3_totals,
                rostersDF[rostersDF['team'] == input.p2_team_b()].iloc[2]['player'],
                team_b_color,
                p2_player_1_line(),
            )
        elif input.p2_x_axis() == "Hardpoint Map":
            return player_kills_by_map(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.p2_team_b()].iloc[2]['player'],
                "Hardpoint",
                p2_player_1_map_1_line()
            )
        elif input.p2_x_axis() == "Control Map":
            return player_kills_by_map(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.p2_team_b()].iloc[2]['player'],
                "Control",
                p2_player_1_map_3_line()
            )
        else:
            return player_kills_by_mapset(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.p2_team_b()].iloc[2]['player'],
                input.p2_map_one(),
                input.p2_map_two(),
                input.p2_map_three()
            )
        
    # Player Eight Plot | Page 2
    @render.plot
    def p2_player_8_plot():
        if input.p2_x_axis() == "Time":
            return player_1_thru_3_kills_vs_time(
                adj_1_thru_3_totals,
                rostersDF[rostersDF['team'] == input.p2_team_b()].iloc[3]['player'],
                team_b_color,
                p2_player_1_line(),
            )
        elif input.p2_x_axis() == "Hardpoint Map":
            return player_kills_by_map(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.p2_team_b()].iloc[3]['player'],
                "Hardpoint",
                p2_player_1_map_1_line()
            )
        elif input.p2_x_axis() == "Control Map":
            return player_kills_by_map(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.p2_team_b()].iloc[3]['player'],
                "Control",
                p2_player_1_map_3_line()
            )
        else:
            return player_kills_by_mapset(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.p2_team_b()].iloc[3]['player'],
                input.p2_map_one(),
                input.p2_map_two(),
                input.p2_map_three()
            )
        
    # Player 1 O/U Streak | Page 2
    @render.ui
    def p2_player_1_ou_streak():
        ou, streak = player_1_thru_3_ou_streak(
            adj_1_thru_3_totals, 
            rostersDF[rostersDF['team'] == input.p2_team_a()].iloc[0]['player'], 
            p2_player_1_line()
        )
        return f"{ou} {streak}"
    
    # Player 2 O/U Streak | Page 2
    @render.ui
    def p2_player_2_ou_streak():
        ou, streak = player_1_thru_3_ou_streak(
            adj_1_thru_3_totals, 
            rostersDF[rostersDF['team'] == input.p2_team_a()].iloc[1]['player'], 
            p2_player_2_line()
        )
        return f"{ou} {streak}"
    
    # Player 3 O/U Streak | Page 2
    @render.ui
    def p2_player_3_ou_streak():
        ou, streak = player_1_thru_3_ou_streak(
            adj_1_thru_3_totals, 
            rostersDF[rostersDF['team'] == input.p2_team_a()].iloc[2]['player'], 
            p2_player_3_line()
        )
        return f"{ou} {streak}"
    
    # Player 4 O/U Streak | Page 2
    @render.ui
    def p2_player_4_ou_streak():
        ou, streak = player_1_thru_3_ou_streak(
            adj_1_thru_3_totals, 
            rostersDF[rostersDF['team'] == input.p2_team_a()].iloc[3]['player'], 
            p2_player_4_line()
        )
        return f"{ou} {streak}"
    
    # Player 5 O/U Streak | Page 2
    @render.ui
    def p2_player_5_ou_streak():
        ou, streak = player_1_thru_3_ou_streak(
            adj_1_thru_3_totals, 
            rostersDF[rostersDF['team'] == input.p2_team_b()].iloc[0]['player'], 
            p2_player_5_line()
        )
        return f"{ou} {streak}"
    
    # Player 6 O/U Streak | Page 2
    @render.ui
    def p2_player_6_ou_streak():
        ou, streak = player_1_thru_3_ou_streak(
            adj_1_thru_3_totals, 
            rostersDF[rostersDF['team'] == input.p2_team_b()].iloc[1]['player'], 
            p2_player_6_line()
        )
        return f"{ou} {streak}"
    
    # Player 7 O/U Streak | Page 2
    @render.ui
    def p2_player_7_ou_streak():
        ou, streak = player_1_thru_3_ou_streak(
            adj_1_thru_3_totals, 
            rostersDF[rostersDF['team'] == input.p2_team_b()].iloc[2]['player'], 
            p2_player_7_line()
        )
        return f"{ou} {streak}"
    
    # Player 8 O/U Streak | Page 2
    @render.ui
    def p2_player_8_ou_streak():
        ou, streak = player_1_thru_3_ou_streak(
            adj_1_thru_3_totals, 
            rostersDF[rostersDF['team'] == input.p2_team_b()].iloc[3]['player'], 
            p2_player_8_line()
        )
        return f"{ou} {streak}"
        

# Run app
app = App(app_ui, server)