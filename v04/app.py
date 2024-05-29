
# Import shiny, shinyswatch, faicons, and asyncio
from shiny import App, reactive, render, ui, req
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
from player_cards_pg2 import *
from map_summaries_pg3 import *

# Dictionary of faicons for value boxes
ICONS = {
    "crosshairs": fa.icon_svg("crosshairs", height = icon_height),
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
og_cdlDF = load_and_clean_cdl_data()

# Build Maps 1 - 3 Totals Dataframe
adj_1_thru_3_totals = build_1_thru_3_totals(og_cdlDF)

# Build series summaries
series_score_diffs = build_series_summaries(og_cdlDF).copy()

# Filter maps from cdlDF
cdlDF = filter_maps(og_cdlDF).copy()

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
                ui.input_action_button(id = "p2_reset_maps", label = "Reset maps")
                
            ), 

            # Row 1 of 4
            ui.layout_columns(
                
                # Column 1 of 6: Team A Logo
                ui.layout_columns(
                    ui.output_image("p2_team_a_logo", width = "120px", height = "120px"), 
                    class_ = "d-flex justify-content-center"
                ), 

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
                ui.layout_columns(
                    ui.output_image("p2_team_b_logo", width = "120px", height = "120px"), 
                    class_ = "d-flex justify-content-center"
                ),

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
                    player_card_ui_pg2("p9", "1"), 
                    player_card_ui_pg2("p10", "2"), 
                    player_card_ui_pg2("p11", "3"), 
                    player_card_ui_pg2("p12", "4"), 
                    player_card_ui_pg2("p13", "5"), 
                    player_card_ui_pg2("p14", "6"), 
                    player_card_ui_pg2("p15", "7"), 
                    player_card_ui_pg2("p16", "8"), 
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
                        ui.output_plot("p2_series_diffs")),

                    # Map Results Differentials
                    ui.navset_card_pill(
                        ui.nav_panel("HP", ui.output_plot("p2_hp_score_diffs")), 
                        ui.nav_panel("Ctrl", ui.output_plot("p2_ctrl_score_diffs")),
                        title = ui.tooltip(
                            ui.span("Map Results ", ICONS["circle_question"]),
                            "Distribution of Map Results by Team, for selected Map & Mode",
                            placement = "right"
                        )
                        
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
                    ui.nav_panel("HP", ui.output_plot("p2_team_a_hps")), 
                    ui.nav_panel("Ctrl", ui.output_plot("p2_team_a_ctrls")),
                    title = ui.output_text("p2_team_a_name")
                ),

                # Column 3: Team B Maps Played
                ui.navset_card_pill( 
                    ui.nav_panel("HP", ui.output_plot("p2_team_b_hps")), 
                    ui.nav_panel("Ctrl", ui.output_plot("p2_team_b_ctrls")),
                    title = ui.output_text("p2_team_b_name")
                ),
                    
                # Row Height
                height = "360px",
                
                # Column Widths
                col_widths = [6, 3, 3]

            )
        )        
    ),

    # 3rd Page: Match Summary Page
    ui.nav_panel("Match Summaries",
                 
        # Sidebar Layout
        ui.layout_sidebar(

            # Sidebar with Dataframe of Matches
            ui.sidebar(
                ui.output_data_frame("match_df"), 
                width = 400, 
                title = "Select a match"
            ), 

            # Row 1: Team Logos and Date of Last Match
            ui.layout_columns(
                ui.layout_columns(ui.output_image("p3_team_a_logo", width = "120px", height = "120px"), 
                                  class_ = "d-flex justify-content-center"), 
                ui.value_box(
                    title = "Match Date",
                    value = ui.output_ui("p3_match_date"),
                    showcase = ICONS["calendar"]
                ), 
                ui.layout_columns(ui.output_image("p3_team_b_logo", width = "120px", height = "120px"), 
                                  class_ = "d-flex justify-content-center"), 
                height = "120px",
                col_widths = [5, 2, 5]
            ),

            # Row 2: Map Summaries 
            ui.layout_columns(
                map_value_box_ui_p3("m1"), 
                map_value_box_ui_p3("m2"), 
                map_value_box_ui_p3("m3"), 
                ui.output_ui("conditional_m4_value_box"), 
                ui.output_ui("conditional_m5_value_box"), 
                height = "120px"
            ), 

            # Row 3: Map Scoreboards
            ui.layout_columns(
                ui.navset_card_pill(
                    ui.nav_panel(1, map_scoreboard_ui_pg3("m1")), 
                    ui.nav_panel(2, map_scoreboard_ui_pg3("m2")), 
                    ui.nav_panel(3, map_scoreboard_ui_pg3("m3")),
                    ui.nav_panel(4, ui.output_ui("conditional_m4_scoreboard")),
                    ui.nav_panel(5, ui.output_ui("conditional_m5_scoreboard")),
                    title = "Scoreboards"
                ),
                height = "440px",
                col_widths = [-3, 6, -3]
            )
        )        
    ),

    # 4th Page: Map Vetoes
    ui.nav_panel("Vetoes",

        # Sidebar Layout
        ui.layout_sidebar(

            # Sidebar with inputs
            ui.sidebar(
                # Inputs
                ui.input_select(id = "p4_team_a", label = "Team A", selected = "Toronto Ultra",
                                choices = sorted(cdlDF['team'].unique())), 
                ui.input_select(id = "p4_team_b", label = "Team B", selected = "Los Angeles Thieves",
                                choices = sorted(cdlDF['team'].unique())), 
                ui.input_select(id = "p4_gamemode", label = "Gamemode", selected = "New York Subliners",
                                choices = ["Hardpoint", "Search & Destroy", "Control"]), 
                ui.input_slider(id = "p4_stage", label = "Stage", min = 1, max = 4, value = [1, 4])
            ), 

            # Row 1 of 3: Team Logos
            ui.layout_columns(
                ui.layout_columns(ui.output_image("p4_team_a_logo", width = "120px", height = "120px"), 
                                  class_ = "d-flex justify-content-center"), 
                ui.value_box(
                    title = "Last H2H Match",
                    value = ui.output_ui("p4_last_match_date"),
                    showcase = ICONS["calendar"]
                ), 
                ui.layout_columns(ui.output_image("p4_team_b_logo", width = "120px", height = "120px"), 
                                  class_ = "d-flex justify-content-center"), 
                col_widths = [5, 2, 5],
                height = "120px"
            ),

            # Row 2 of 3
            ui.layout_columns(

                # Column 1: Team A Picks
                ui.card(ui.card_header(ui.output_text("p4_team_a_picks_title")),
                        ui.output_plot("team_a_picks")),
                # Column 2: Team A Bans
                ui.card(ui.card_header(ui.output_text("p4_team_a_bans_title")),
                        ui.output_plot("team_a_bans")),
                # Column 3: Team B Picks
                ui.card(ui.card_header(ui.output_text("p4_team_b_picks_title")),
                        ui.output_plot("team_b_picks")),
                # Column 4: Team B Bans
                ui.card(ui.card_header(ui.output_text("p4_team_b_bans_title")),
                        ui.output_plot("team_b_bans")),

                # Row Height
                height = "420px"

            ), 

            # Row 3 of 3
            ui.layout_columns(
                
                ui.card(ui.card_header("Vetoes"), 
                    ui.output_data_frame("vetoes"), 
                    full_screen = True),

                # Column Widths
                col_widths = [-2, 8, -2],

                # Row Height
                height = "360px"
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

    # Reactive event to update player props dataframe
    # Displays progress bar while scraping
    @reactive.effect
    @reactive.event(input.p2_scrape)
    async def p2_scrape_props():
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

    # Reactive event to reset map filters | Page 2
    @reactive.effect
    @reactive.event(input.p2_reset_maps)
    def __():
        ui.update_select("p2_map_one", selected = "All")
        ui.update_select("p2_map_two", selected = "All")
        ui.update_select("p2_map_three", selected = "All")

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
    
    # Team A Player Cards | Page 1
    [player_card_server_pg1(
        "p" + str(player_num), cdlDF, rostersDF, player_props_df, input.team_a,
        player_num, map_num, team_a_color, gamemode, input.map_name, input.x_axis
    ) for player_num in range(1, 5)]

    # Team B Player Cards | Page 1
    [player_card_server_pg1(
        "p" + str(player_num + 4), cdlDF, rostersDF, player_props_df, input.team_b,
        player_num, map_num, team_b_color, gamemode, input.map_name, input.x_axis
    ) for player_num in range(1, 5)]

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
        
    # Team A Name for Maps Played Card Header | Page 2
    @render.text
    def p2_team_a_name():
        return team_icons[input.p2_team_a()] + " Maps Played"
    
    # Team B Name for Maps Played Card Header | Page2
    @render.text
    def p2_team_b_name():
        return team_icons[input.p2_team_b()] + " Maps Played"
        
    # Team A Donut Chart of HPs Played | Page 2
    @render.plot
    def p2_team_a_hps():
        return team_percent_maps_played(
            team_summaries_DF, input.p2_team_a(), "Hardpoint"
        )
    
    # Team A Donut Chart of Controls Played | Page 2
    @render.plot
    def p2_team_a_ctrls():
        return team_percent_maps_played(
            team_summaries_DF, input.p2_team_a(), "Control"
        )
    
    # Team B Donut Chart of HPs Played | Page 2
    @render.plot
    def p2_team_b_hps():
        return team_percent_maps_played(
            team_summaries_DF, input.p2_team_b(), "Hardpoint"
        )
    
    # Team B Donut Chart of Controls Played | Page 2
    @render.plot
    def p2_team_b_ctrls():
        return team_percent_maps_played(
            team_summaries_DF, input.p2_team_b(), "Control"
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
    def p2_ctrl_score_diffs():
        return score_diffs_ridge(
            cdlDF, 
            team_icons[input.p2_team_a()], team_icons[input.p2_team_b()], 
            team_a_color, team_b_color, 
            "Control", 
            input.p2_map_three()
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
    
    # Team A Player Cards | Page 2
    [player_card_server_pg2(
        "p" + str(player_num + 8), cdlDF, adj_1_thru_3_totals, rostersDF, 
        player_props_df, input.p2_team_a, player_num, team_a_color, 
        input.p2_map_one, input.p2_map_two, input.p2_map_three, input.p2_x_axis
    ) for player_num in range(1, 5)]

    # Team B Player Cards | Page 2
    [player_card_server_pg2(
        "p" + str(player_num + 12), cdlDF, adj_1_thru_3_totals, rostersDF, 
        player_props_df, input.p2_team_b, player_num, team_b_color, 
        input.p2_map_one, input.p2_map_two, input.p2_map_three, input.p2_x_axis

    ) for player_num in range(1, 5)]

    # Dataframe of All Matches | Page 3
    @render.data_frame
    def match_df():
        return render.DataGrid(
            data = display_matches(og_cdlDF),
            filters = True, 
            summary = False, 
            selection_mode = "row"
        )
    
    # Reactive Dataframe containing the current match | Page 3
    @reactive.calc
    def cur_match_df():
        data_selected = match_df.data_view(selected = True)
        req(not data_selected.empty)
        return data_selected
    
    # Reactive Value containing the current Match ID | Page 3
    @reactive.calc
    def cur_match_id():
        return cur_match_df().reset_index(drop = True).at[0, "Match ID"]
    
    # Reactive value containing number of maps for selected match | Page 3
    @reactive.calc
    def number_of_maps():
        return len(og_cdlDF[(og_cdlDF["match_id"] == cur_match_id())]["map_num"].unique())
    
    # Reactive Calc containing Team A Abbr | Page 3
    def cur_team_a():
        return cur_match_df().reset_index(drop = True).at[0, "Team"]
    
    # Reactive Calc containing Team B Abbr | Page 3
    def cur_team_b():
        return cur_match_df().reset_index(drop = True).at[0, "Opponent"]

    # Team A Logo | Page 3
    @render.image
    def p3_team_a_logo():
        img: ImgData = \
        {"src": os.path.dirname(__file__) + 
         team_logos[team_names[cur_team_a()]], "width": "120px", "height": "120px"}
        return img
    
    # Team B Logo | Page 3
    @render.image
    def p3_team_b_logo():
        img: ImgData = \
        {"src": os.path.dirname(__file__) + 
         team_logos[team_names[cur_team_b()]], "width": "120px", "height": "120px"}
        return img
    
    # Match Date | Page 3
    @render.ui
    def p3_match_date():
        return cur_match_df().reset_index(drop = True).at[0, "Date"]
    
    # Maps 1 - 5 Summaries | Page 3
    map_summary_server_p3("m1", og_cdlDF.copy(), cur_match_id, 1, cur_team_a, cur_team_b, number_of_maps)
    map_summary_server_p3("m2", og_cdlDF.copy(), cur_match_id, 2, cur_team_a, cur_team_b, number_of_maps)
    map_summary_server_p3("m3", og_cdlDF.copy(), cur_match_id, 3, cur_team_a, cur_team_b, number_of_maps)
    map_summary_server_p3("m4", og_cdlDF.copy(), cur_match_id, 4, cur_team_a, cur_team_b, number_of_maps)
    map_summary_server_p3("m5", og_cdlDF.copy(), cur_match_id, 5, cur_team_a, cur_team_b, number_of_maps)

    # Map 4 Summary | Page 3
    @render.ui
    def conditional_m4_value_box():
        if number_of_maps() >= 4:
            return map_value_box_ui_p3("m4")
        
    # Map 5 Summary | Page 3
    @render.ui
    def conditional_m5_value_box():
        if number_of_maps() >= 5:
            return map_value_box_ui_p3("m5")
        
    # Map 4 Scoreboard | Page 3
    @render.ui
    def conditional_m4_scoreboard():
        if number_of_maps() >= 4:
            return map_scoreboard_ui_pg3("m4")
        
    # Map 5 Scoreboard | Page 3
    @render.ui
    def conditional_m5_scoreboard():
        if number_of_maps() >= 5:
            return map_scoreboard_ui_pg3("m5")
    
    # Team A Logo | Page 4
    @render.image
    def p4_team_a_logo():
        img: ImgData = {"src": os.path.dirname(__file__) + team_logos[input.p4_team_a()], 
                        "width": "120px", "height": "120px"}
        return img
    
    # Team B Logo | Page 4
    @render.image
    def p4_team_b_logo():
        img: ImgData = {"src": os.path.dirname(__file__) + team_logos[input.p4_team_b()], 
                        "width": "120px", "height": "120px"}
        return img
    
   # Date of Last Match | Page 4
    @render.ui
    def p4_last_match_date():
        return compute_last_match(cdlDF, input.p4_team_a(), input.p4_team_b())
    
    # Title for Team A Picks Bar Chart | Page 4
    @render.text
    def p4_team_a_picks_title():
        return f"{team_icons[input.p4_team_a()]} {input.p4_gamemode()} Picks"
    
    # Title for Team A Bans Bar Chart | Page 4
    @render.text
    def p4_team_a_bans_title():
        return f"{team_icons[input.p4_team_a()]} {input.p4_gamemode()} Bans"
    
    # Title for Team B Picks Bar Chart | Page 4
    @render.text
    def p4_team_b_picks_title():
        return f"{team_icons[input.p4_team_b()]} {input.p4_gamemode()} Picks"
    
    # Title for Team B Bans Bar Chart | Page 4
    @render.text
    def p4_team_b_bans_title():
        return f"{team_icons[input.p4_team_b()]} {input.p4_gamemode()} Bans"
    
    # Dataframe of vetoes
    @render.data_frame
    def vetoes():
        return render.DataGrid(
            display_vetoes(
                vetoes_wide, 
                input.p4_team_a(),
                input.p4_team_b()
            ), 
            filters = True, 
            summary = False
        )
    
    # Function to chart Team A Picks for Selected Gamemode | Page 4 
    @render.plot
    def team_a_picks():
        return chart_vetoes(vetoes_df, input.p4_team_a(), "pick", 
                            input.p4_gamemode(), team_a_color, 
                            input.p4_stage()[0], input.p4_stage()[1])
    
    # Function to chart Team A Bans for Selected Gamemode | Page 4 
    @render.plot
    def team_a_bans():
        return chart_vetoes(vetoes_df, input.p4_team_a(), "ban", 
                            input.p4_gamemode(), team_a_color, 
                            input.p4_stage()[0], input.p4_stage()[1])
    
    # Function to chart Team B Picks for Selected Gamemode | Page 4 
    @render.plot
    def team_b_picks():
        return chart_vetoes(vetoes_df, input.p4_team_b(), "pick", 
                            input.p4_gamemode(), team_b_color, 
                            input.p4_stage()[0], input.p4_stage()[1])
    
    # Function to chart Team B Bans for Selected Gamemode | Page 4 
    @render.plot
    def team_b_bans():
        return chart_vetoes(vetoes_df, input.p4_team_b(), "ban", 
                            input.p4_gamemode(), team_b_color, 
                            input.p4_stage()[0], input.p4_stage()[1])
        
        

# Run app
app = App(app_ui, server)