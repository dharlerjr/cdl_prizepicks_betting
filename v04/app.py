
# Import shiny, shinyswatch, faicons, and asyncio
from shiny import App, reactive, render, ui
from shiny.types import ImgData
import shinyswatch
import asyncio

# Import os for filepaths
import os

# Import setup
from utils.setup.setup import *

# Import other utils
from utils.webscraper import *
from utils.seaborn_helpers import *
from utils.datagrid_and_value_box_helpers import *

# Import player card modules
from player_cards_pg1 import *

# Dictionary of faicons for value boxes
ICONS = {
    "crosshairs": fa.icon_svg("crosshairs", height = icon_height, ),
    "headset": fa.icon_svg("headset", height = icon_height), 
    "plus": fa.icon_svg("plus", height = icon_height), 
    "minus": fa.icon_svg("minus", height = icon_height), 
    "calendar": fa.icon_svg("calendar", height = icon_height), 
    "check": fa.icon_svg("circle-check", height = icon_height), 
    "exclamation": fa.icon_svg("circle-exclamation", height = icon_height), 
    "flag": fa.icon_svg("flag", height = icon_height), 
    "mound": fa.icon_svg("mound", height = icon_height), 
    "circle_question": fa.icon_svg("circle-question", height = "16px"), 
}

# Dictionary to map map_num to gamemode
map_nums_to_gamemode = {
    1: "Hardpoint", 
    2: "Search & Destroy", 
    3: "Control", 
    4: "Hardpoint", 
    5: "Search & Destroy"
}

# Dictionary of paths to saved team logo images
team_logo_path = "\\images\\team_logos\\"
team_logos = {
    "Atlanta FaZe": team_logo_path + "ATL.webp",
    "Boston Breach": team_logo_path + "BOS.webp",
    "Carolina Royal Ravens": team_logo_path + "CAR.webp", 
    "Las Vegas Legion": team_logo_path + "LV.webp",
    "Los Angeles Guerrillas": team_logo_path + "LAG.webp", 
    "Los Angeles Thieves": team_logo_path + "LAT.webp", 
    "Miami Heretics": team_logo_path + "MIA.webp", 
    "Minnesota ROKKR": team_logo_path + "MIN.webp", 
    "New York Subliners": team_logo_path + "NYSL.webp",
    "OpTic Texas": team_logo_path + "TX.webp", 
    "Seattle Surge": team_logo_path + "SEA.webp", 
    "Toronto Ultra": team_logo_path + "TOR.webp"
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


# Load in cdl data
cdlDF = load_and_clean_cdl_data()

# Build Maps 1 - 3 Totals Dataframe
adj_1_thru_3_totals = build_1_thru_3_totals(cdlDF)

# Build series summaries
series_score_diffs = build_series_summaries(cdlDF).copy()

# Filter maps from cdlDF
cdlDF = filter_maps(cdlDF)

# Build team summaries
team_summaries_DF = build_team_summaries(cdlDF).copy()

# Build rosters
rostersDF = build_rosters(cdlDF).copy()

# Load and pivot vetoes
vetoes_wide = load_vetoes()
vetoes_df = pivot_vetoes(vetoes_wide)

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
                                choices = ['All', '6 Star', 'Karachi', 'Rio', 'Sub Base', 'Vista']),
                ui.input_select(id = "x_axis", label = "Player Card X-Axis", selected = "Time",
                                choices = ["Time", "Score Differential"]),

            ),

            # Row 1 of 4
            ui.layout_columns(
                
                # Column 1 of 6: Team A Logo
                ui.layout_columns(
                    ui.output_image("team_a_logo", width = "120px", height = "120px"), 
                    class_ = "d-flex justify-content-center"
                ),

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
                ui.layout_columns(
                    ui.output_image("team_b_logo", width = "120px", height = "120px"), 
                    class_ = "d-flex justify-content-center"
                ),

                # Row Height
                height = "120px", 

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

                # Column 1:Player cards
                ui.navset_card_pill(
                    player_card_ui_pg1("p1", 1), 
                    player_card_ui_pg1("p2", 2), 
                    player_card_ui_pg1("p3", 3), 
                    player_card_ui_pg1("p4", 4), 
                    player_card_ui_pg1("p5", 5), 
                    player_card_ui_pg1("p6", 6), 
                    player_card_ui_pg1("p7", 7), 
                    player_card_ui_pg1("p8", 8), 
                    title = "Player Cards"
                ),

                # Column 2: Ridgeline Plots Wrapped
                ui.layout_column_wrap(

                    # Series Results
                    ui.card(
                        ui.card_header(
                            "Series Results", 
                            ui.tooltip(
                                ui.span(ICONS["circle_question"]),
                                "Distribution of Series Results by Team",
                                placement = "right"
                            ), 
                            class_ = "d-flex justify-content-between align-items-center",
                        ), 
                        ui.output_plot("series_diffs")
                    ),
                    # Map Results
                    ui.card(
                        ui.card_header(
                            "Map Results", 
                            ui.tooltip(
                                ui.span(ICONS["circle_question"]),
                                "Distribution of Map Results by Team, for selected Map & Mode",
                                placement = "right"
                            ), 
                            class_ = "d-flex justify-content-between align-items-center",
                        ), 
                        ui.output_plot("score_diffs")
                    ),

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
                os.path.dirname(__file__) + "\\styles\\styles.css"
            )
        )
    ), 

    # App Title
    title = "CDL Bets on PrizePicks", 

    # Navbar color
    inverse = True
)

# Define server logic
def server(input, output, session):

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
    
    # Reactive event to update map_name list based on map_num input
    @reactive.effect
    def _():
        x = map_num()

        if map_num() == 1 or map_num() == 4:
            map_list = ['All', '6 Star', 'Karachi', 'Rio', 'Sub Base', 'Vista']
        elif map_num() == 2 or map_num() == 5:
            map_list = ['All', '6 Star', 'Highrise', 'Invasion', 'Karachi', 'Rio']
        else:
            map_list = ['All', 'Highrise', 'Invasion', 'Karachi']

        ui.update_select("map_name", choices = map_list, selected = "All")

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
            return f"{input.map_name()} {gamemode_abbrs[gamemode()]} Win Streak"\
            
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
            team_summaries_DF, input.team_a(), gamemode()
        )
    
    # Team B Donut Chart of % Maps Played
    @render.plot
    def team_b_maps_played():
        return team_percent_maps_played(
            team_summaries_DF, input.team_b(), gamemode()
        )
    
    # Team A Name for Maps Played Card Header
    @render.text
    def team_a_name():
        return team_icons[input.team_a()] + " Maps Played"
    
    # Team B Name for Maps Played Card Header
    @render.text
    def team_b_name():
        return team_icons[input.team_b()] + " Maps Played"
    
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
    
    # Team A Player Cards
    [player_card_server_pg1(
        "p" + str(player_num), cdlDF, rostersDF, player_props_df, input.team_a,
        player_num, map_num, team_a_color, gamemode, input.map_name, input.x_axis
    ) for player_num in range(1, 5)]

    # Team B Player Cards
    [player_card_server_pg1(
        "p" + str(player_num + 4), cdlDF, rostersDF, player_props_df, input.team_b,
        player_num, map_num, team_b_color, gamemode, input.map_name, input.x_axis
    ) for player_num in range(1, 5)]
        

# Run app
app = App(app_ui, server)