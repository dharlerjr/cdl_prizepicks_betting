

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

    # Sidebar with Inputs
    ui.sidebar(
        # Theme picker
        # shinyswatch.theme_picker_ui(),
        # Set theme: cerulean
        shinyswatch.theme.cerulean,
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
    
    # First row: Team Logos, Standings, and Series H2H
    ui.layout_columns(
        ui.output_image("team_a_logo", width = "120px", height = "120px"), 
        ui.value_box(
            title = "Series W-L (Major III Qualifiers)", 
            value = ui.output_ui("team_a_series_record"),
            showcase = ICONS["headset"]
        ), 
        ui.value_box(
            title = "Series H2H (Overall)",
            value = ui.output_ui("h2h_series_record"),
            showcase = ICONS["crosshairs"]
        ), 
        ui.value_box(
            title = "Series W-L (Major III Qualifiers)", 
            value = ui.output_ui("team_b_series_record"),
            showcase = ICONS["headset"]
        ),
        ui.output_image("team_b_logo", width = "120px", height = "120px"), 
        # Col Widths: Automatic
        # Row Height
        height = "180px"
    ),

    # Second row: Team A Player Kills Plots & O/U %
    ui.layout_columns(
        # Card with Pill Tabset of Plots
        ui.navset_card_pill(
            ui.nav_panel(
                "1", 
                ui.layout_columns(
                    ui.output_plot("player_1_box", width = "200px"), 
                    ui.output_plot("player_1_scatter"), 
                    ui.layout_column_wrap(
                        ui.value_box(
                            title = "O/U", 
                            value = ui.output_ui("player_1_ou"),
                            showcase = ui.output_ui("player_1_ou_icon"), 
                            showcase_layout="left center"
                        ), 
                        ui.value_box(
                            title = "Streak", 
                            value = ui.output_ui("player_1_ou_streak"), 
                            showcase = ui.output_ui("change_player_1_ou_streak_icon"),
                            showcase_layout="left center"
                        ), 
                        width = 1
                    ), 
                    height = "400px"
                )
            ), 
            ui.nav_panel(                
                "2", 
                ui.layout_columns(
                    ui.output_plot("player_2_box", width = "200px"), 
                    ui.output_plot("player_2_scatter"), 
                    ui.layout_column_wrap(
                        ui.value_box(
                            title = "O/U", 
                            value = ui.output_ui("player_2_ou"),
                            showcase = ui.output_ui("player_2_ou_icon"), 
                            showcase_layout="left center"
                        ), 
                        ui.value_box(
                            title = "Streak", 
                            value = ui.output_ui("player_2_ou_streak"), 
                            showcase = ui.output_ui("change_player_2_ou_streak_icon"),
                            showcase_layout="left center"
                        ), 
                        width = 1
                    ), 
                    height = "400px"
                ), 
            ),
            ui.nav_panel(                
                "3", 
                ui.layout_columns(
                    ui.output_plot("player_3_box", width = "200px"), 
                    ui.output_plot("player_3_scatter"),
                    ui.layout_column_wrap(
                        ui.value_box(
                            title = "O/U", 
                            value = ui.output_ui("player_3_ou"),
                            showcase = ui.output_ui("player_3_ou_icon"), 
                            showcase_layout="left center"
                        ), 
                        ui.value_box(
                            title = "Streak", 
                            value = ui.output_ui("player_3_ou_streak"), 
                            showcase = ui.output_ui("change_player_3_ou_streak_icon"),
                            showcase_layout="left center"
                        ), 
                        width = 1
                    ), 
                    height = "400px"
                ), 
            ),
            ui.nav_panel(                
                "4", 
                ui.layout_columns(
                    ui.output_plot("player_4_box", width = "200px"), 
                    ui.output_plot("player_4_scatter"), 
                    ui.layout_column_wrap(
                        ui.value_box(
                            title = "O/U", 
                            value = ui.output_ui("player_4_ou"),
                            showcase = ui.output_ui("player_4_ou_icon"), 
                            showcase_layout="left center"
                        ),
                        ui.value_box(
                            title = "Streak", 
                            value = ui.output_ui("player_4_ou_streak"), 
                            showcase = ui.output_ui("change_player_4_ou_streak_icon"),
                            showcase_layout="left center"
                        ), 
                        width = 1
                    ), 
                    height = "400px"
                )
            )
        ),
        # Col Widths: Spans Full Page
        # Max Height
        max_height = "400px" 
    ),

    # Third row: Team B Player Kills Plots & O/U %
    ui.layout_columns(
        # Card with Pill Tabset of Plots
        ui.navset_card_pill(
            ui.nav_panel(
                "1", 
                ui.layout_columns(
                    ui.output_plot("player_5_box", width = "200px"), 
                    ui.output_plot("player_5_scatter"), 
                    ui.layout_column_wrap(
                        ui.value_box(
                            title = "O/U", 
                            value = ui.output_ui("player_5_ou"),
                            showcase = ui.output_ui("player_5_ou_icon"), 
                            showcase_layout="left center"
                        ), 
                        ui.value_box(
                            title = "Streak", 
                            value = ui.output_ui("player_5_ou_streak"), 
                            showcase = ui.output_ui("change_player_5_ou_streak_icon"),
                            showcase_layout="left center"
                        ), 
                        width = 1
                    ), 
                    height = "400px"
                )
            ), 
            ui.nav_panel(                
                "2", 
                ui.layout_columns(
                    ui.output_plot("player_6_box", width = "200px"), 
                    ui.output_plot("player_6_scatter"), 
                    ui.layout_column_wrap(
                        ui.value_box(
                            title = "O/U", 
                            value = ui.output_ui("player_6_ou"),
                            showcase = ui.output_ui("player_6_ou_icon"), 
                            showcase_layout="left center"
                        ), 
                        ui.value_box(
                            title = "Streak", 
                            value = ui.output_ui("player_6_ou_streak"), 
                            showcase = ui.output_ui("change_player_6_ou_streak_icon"),
                            showcase_layout="left center"
                        ), 
                        width = 1
                    ), 
                    height = "400px"
                )
            ), 
            ui.nav_panel(                
                "3", 
                ui.layout_columns(
                    ui.output_plot("player_7_box", width = "200px"), 
                    ui.output_plot("player_7_scatter"), 
                    ui.layout_column_wrap(
                        ui.value_box(
                            title = "O/U", 
                            value = ui.output_ui("player_7_ou"),
                            showcase = ui.output_ui("player_7_ou_icon"), 
                            showcase_layout="left center"
                        ), 
                        ui.value_box(
                            title = "Streak", 
                            value = ui.output_ui("player_7_ou_streak"), 
                            showcase = ui.output_ui("change_player_7_ou_streak_icon"),
                            showcase_layout="left center"
                        ), 
                        width = 1
                    ), 
                    height = "400px"
                )
            ), 
            ui.nav_panel(                
                "4", 
                ui.layout_columns(
                    ui.output_plot("player_8_box", width = "200px"), 
                    ui.output_plot("player_8_scatter"), 
                    ui.layout_column_wrap(
                        ui.value_box(
                            title = "O/U", 
                            value = ui.output_ui("player_8_ou"),
                            showcase = ui.output_ui("player_8_ou_icon"), 
                            showcase_layout="left center"
                        ), 
                        ui.value_box(
                            title = "Streak", 
                            value = ui.output_ui("player_8_ou_streak"), 
                            showcase = ui.output_ui("change_player_8_ou_streak_icon"),
                            showcase_layout="left center"
                        ), 
                        width = 1
                    ), 
                    height = "400px"
                )
            )
        ),
        # Col Widths: Spans Full Page
        # Max Height
        max_height = "400px" 
    ),

    # Fourth row: Kills Scoreboards
    ui.layout_columns(
        # Team A Logo
        ui.output_image("team_a_logo_2nd", width = "120px", height = "120px"), 
        # Kills Scoreboards
        ui.card(ui.output_data_frame("scoreboards")),
        # Team B Logo
        ui.output_image("team_b_logo_2nd", width = "120px", height = "120px"), 
        # Check Player Props
        # ui.card(ui.output_data_frame("show_player_props")),
        # Check CDL Dataframe
        # ui.card(ui.output_data_frame("all_data")),
        # Col Widths
        col_widths=[2, 8, 2],
        # Row Height
        height = "400px"
    ),

    # Fifth row: Value Boxes containing Map Win %s, Win Streaks, & H2H
    ui.layout_columns(
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
            showcase = ICONS["percent"]
        ), 
        # H2H W - L
        ui.value_box(
            title = ui.output_ui("map_h2h_title"),
            value = ui.output_ui("h2h_map_record"),
            showcase = ICONS["crosshairs"]
        ),
        # Team B Win %
            ui.value_box(
                title = ui.output_ui("team_b_map_record_title"),
                value = ui.output_ui("team_b_map_record"),
                showcase = ICONS["percent"]
            ), 
        # Team B Win Streak
        ui.value_box(
            title = ui.output_ui("team_b_win_streak_title"),
            value = ui.output_ui("team_b_win_streak"),
            showcase = ui.output_ui("change_team_b_win_streak_icon")
        ),
        # Col Widths: Automatic  
        # Row Height
        height = "180px"
    ),

    # Sixth row: Map & Mode Differentials
    ui.layout_columns(
        # Team A Histogram of Map & Mode Score Differentials
        ui.card(ui.output_plot("team_a_score_diffs")),
        # Team B Histogram of Map & Mode Score Differentials
        ui.card(ui.output_plot("team_b_score_diffs")),
        # Col Widths: Automatic
        # Row Height
        height = "400px"
    ), 

    # Seventh row: Series Score Differentials & Results
    ui.layout_columns(
        ui.card(ui.output_plot("team_a_series_diffs")), 
        ui.card(ui.output_data_frame("series_datagrid")),
        ui.card(ui.output_plot("team_b_series_diffs")),
        # Col Widths: Automatic
        # Row Height
        height = "300px"
    ),

    # App Title
    title = "CDL Bets on PrizePicks" 
)


# Define server logic
def server(input, output, session):
    
    # Theme picker
    # shinyswatch.theme_picker_server()

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
    
    # Team A Logo 2nd
    @render.image
    def team_a_logo_2nd():
        img: ImgData = {"src": os.path.dirname(__file__) + team_logos[input.team_a()], 
                        "width": "120px", "height": "120px", "image-align": "left"}
        return img
    
    # Team B Logo
    @render.image
    def team_b_logo():
        img: ImgData = {"src": os.path.dirname(__file__) + team_logos[input.team_b()], 
                        "width": "120px", "height": "120px", "image-align": "right"}
        return img
    
    # Team B Logo
    @render.image
    def team_b_logo_2nd():
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
    
    # Title for Team A Map Record Value Box
    @render.ui
    def team_a_map_record_title():
        if input.map_name() == "All":
            return f"{gamemode()} Win % (W - L)"
        else:
            return f"{input.map_name()} {gamemode()} Win % (W - L)"
        
    # Title for Team B Map Record Value Box
    @render.ui
    def team_b_map_record_title():
        if input.map_name() == "All":
            return f"{gamemode()} Win % (W - L)"
        else:
            return f"{input.map_name()} {gamemode()} Win % (W - L)"
        
    # Title for H2H Value Box
    @render.ui
    def map_h2h_title():
        if input.map_name() == "All":
            return f"{gamemode()} H2H"
        else:
            return f"{input.map_name()} {gamemode()} H2H"
    
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

    # H2H Map Record for User-Selected Map & Mode Combination
    @render.ui
    def h2h_map_record():
        return compute_h2h_map_record(cdlDF, input.team_a(), input.team_b(), 
                                      gamemode(), input.map_name())
    
    # H2H Series Record for User-Selected Map & Mode Combination
    @render.ui
    def h2h_series_record():
        return compute_h2h_series_record(cdlDF, input.team_a(), input.team_b())
    
    # Title for Team A Win Streak Value Box
    @render.ui
    def team_a_win_streak_title():
        if input.map_name() == "All":
            return f"{gamemode()} Win Streak"
        else:
            return f"{input.map_name()} {gamemode()} Win Streak"
        
    # Title for Team B Win Streak Value Box
    @render.ui
    def team_b_win_streak_title():
        if input.map_name() == "All":
            return f"{gamemode()} Win Streak"
        else:
            return f"{input.map_name()} {gamemode()} Win Streak"
        
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
        if win_streak > 0:
            icon = ICONS["plus"]
        else:
            icon = ICONS["minus"]
        icon.add_class(f"text-{('success' if win_streak > 0 else 'danger')}")
        return icon
    
    # Change Win Streak Icon Based on Sign of Win Streak
    @render.ui
    def change_team_b_win_streak_icon():
        win_streak = compute_team_b_win_streak()
        if win_streak > 0:
            icon = ICONS["plus"]
        else:
            icon = ICONS["minus"]
        icon.add_class(f"text-{('success' if win_streak > 0 else 'danger')}")
        return icon

    # Not implemented
    # # Team Summaries
    # @render.table
    # def team_summaries():
    #     return team_summaries_fn(team_summaries_DF, input.team_a(), input.team_b())
    
    # # H2H Summary
    # @render.table
    # def h2h_summary():
    #     return h2h_summary_fn(cdlDF, input.team_a(), input.team_b())
    
    # Team A Series Datagrid
    @render.data_frame
    def series_datagrid():
        return render.DataGrid(
            build_series_res_datagrid(
                series_score_diffs, 
                input.team_a(), 
                input.team_b()
                ), 
            filters = True, 
            summary = False
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

    # Test Render Player Props
    # @render.data_frame
    # def show_player_props():
    #     return render.DataGrid(
    #         player_props_df(),
    #         filters = True, 
    #         summary = False
    #     )
    
    # Test render all cdlDF
    # @render.data_frame
    # def all_data():
    #     return render.DataGrid(
    #         cdlDF,
    #         filters = True, 
    #         summary = False
    #     )

    # Team A Score Differentials Histogram
    @render.plot
    def team_a_score_diffs():
        return team_score_diffs(
            cdlDF, input.team_a(), gamemode(), input.map_name()
        )
    
    # Team B Score Differentials Histogram
    @render.plot
    def team_b_score_diffs():
        return team_score_diffs(
            cdlDF, input.team_b(), gamemode(), input.map_name()
        )

    # Team A Series Differentials Histogram
    @render.plot
    def team_a_series_diffs():
        return team_series_diffs(series_score_diffs, input.team_a())
    
    # Team B Series Differentials Histogram
    @render.plot
    def team_b_series_diffs():
        return team_series_diffs(series_score_diffs, input.team_b())

    # Player One Line
    @reactive.Calc
    def player_1_line():
        return player_props_df.get()[
                (player_props_df.get()['team'] == input.team_a()) &
                (player_props_df.get()['prop'] == map_num())] \
                    .iloc[0]['line']
    
    # Player Two Line
    @reactive.Calc
    def player_2_line():
        return player_props_df.get()[
                (player_props_df.get()['team'] == input.team_a()) &
                (player_props_df.get()['prop'] == map_num())] \
                    .iloc[1]['line']
    
    # Player Three Line
    @reactive.Calc
    def player_3_line():
        return player_props_df.get()[
                (player_props_df.get()['team'] == input.team_a()) &
                (player_props_df.get()['prop'] == map_num())] \
                    .iloc[2]['line']
    
    # Player Four Line
    @reactive.Calc
    def player_4_line():
        return player_props_df.get()[
                (player_props_df.get()['team'] == input.team_a()) &
                (player_props_df.get()['prop'] == map_num())] \
                    .iloc[3]['line']
    
    # Player Five Line
    @reactive.Calc
    def player_5_line():
        return player_props_df.get()[
                (player_props_df.get()['team'] == input.team_b()) &
                (player_props_df.get()['prop'] == map_num())] \
                    .iloc[0]['line']
    
    # Player Six Line
    @reactive.Calc
    def player_6_line():
        return player_props_df.get()[
                (player_props_df.get()['team'] == input.team_b()) &
                (player_props_df.get()['prop'] == map_num())] \
                    .iloc[1]['line']
    
    # Player Seven Line
    @reactive.Calc
    def player_7_line():
        return player_props_df.get()[
                (player_props_df.get()['team'] == input.team_b()) &
                (player_props_df.get()['prop'] == map_num())] \
                    .iloc[2]['line']
    
    # Player Eight Line
    @reactive.Calc
    def player_8_line():
        return player_props_df.get()[
                (player_props_df.get()['team'] == input.team_b()) &
                (player_props_df.get()['prop'] == map_num())] \
                    .iloc[3]['line']

    # Player One Boxplot
    @render.plot
    def player_1_box():
        return player_kills_overview(
            cdlDF, 
            rostersDF[rostersDF['team'] == input.team_a()].iloc[0]['player'],  
            gamemode(), 
            player_1_line(),
            input.map_name()
        )

    # Player One Scatterplot
    @render.plot
    def player_1_scatter():
        if input.x_axis() == "Time":
            return player_kills_vs_time(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.team_a()].iloc[0]['player'],  
                gamemode(), 
                player_1_line(),
                input.map_name()
            )
        else:
            return player_kills_vs_score_diff(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.team_a()].iloc[0]['player'],  
                gamemode(), 
                player_1_line(),
                input.map_name()
            )
    
    # Player Two Boxplot
    @render.plot
    def player_2_box():
        return player_kills_overview(
            cdlDF, 
            rostersDF[rostersDF['team'] == input.team_a()].iloc[1]['player'],  
            gamemode(), 
            player_2_line(),
            input.map_name()
        )

    # Player Two Scatterplot
    @render.plot
    def player_2_scatter():
        if input.x_axis() == "Time":
            return player_kills_vs_time(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.team_a()].iloc[1]['player'],  
                gamemode(), 
                player_2_line(),
                input.map_name()
            )
        else:
            return player_kills_vs_score_diff(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.team_a()].iloc[1]['player'],  
                gamemode(), 
                player_2_line(),
                input.map_name()
            )
        
    # Player Three Boxplot
    @render.plot
    def player_3_box():
        return player_kills_overview(
            cdlDF, 
            rostersDF[rostersDF['team'] == input.team_a()].iloc[2]['player'],  
            gamemode(), 
            player_3_line(),
            input.map_name()
        )

    # Player Three Scatterplot
    @render.plot
    def player_3_scatter():
        if input.x_axis() == "Time":
            return player_kills_vs_time(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.team_a()].iloc[2]['player'],  
                gamemode(), 
                player_3_line(),
                input.map_name()
            )
        else:
            return player_kills_vs_score_diff(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.team_a()].iloc[2]['player'],  
                gamemode(), 
                player_3_line(),
                input.map_name()
            )
        
    # Player Four Boxplot
    @render.plot
    def player_4_box():
        return player_kills_overview(
            cdlDF, 
            rostersDF[rostersDF['team'] == input.team_a()].iloc[3]['player'],  
            gamemode(), 
            player_4_line(),
            input.map_name()
        )

    # Player Four Scatterplot
    @render.plot
    def player_4_scatter():
        if input.x_axis() == "Time":
            return player_kills_vs_time(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.team_a()].iloc[3]['player'],  
                gamemode(), 
                player_4_line(),
                input.map_name()
            )
        else:
            return player_kills_vs_score_diff(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.team_a()].iloc[3]['player'], 
                gamemode(), 
                player_4_line(),
                input.map_name()
            )
    
    # Player Five Boxplot
    @render.plot
    def player_5_box():
        return player_kills_overview(
            cdlDF, 
            rostersDF[rostersDF['team'] == input.team_b()].iloc[0]['player'],  
            gamemode(), 
            player_5_line(),
            input.map_name()
        )

    # Player Five Scatterplot
    @render.plot
    def player_5_scatter():
        if input.x_axis() == "Time":
            return player_kills_vs_time(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.team_b()].iloc[0]['player'],  
                gamemode(), 
                player_5_line(),
                input.map_name()
            )
        else:
            return player_kills_vs_score_diff(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.team_b()].iloc[0]['player'], 
                gamemode(), 
                player_5_line(),
                input.map_name()
            )
        
    # Player Six Boxplot
    @render.plot
    def player_6_box():
        return player_kills_overview(
            cdlDF, 
            rostersDF[rostersDF['team'] == input.team_b()].iloc[1]['player'],  
            gamemode(), 
            player_6_line(),
            input.map_name()
        )

    # Player Six Scatterplot
    @render.plot
    def player_6_scatter():
        if input.x_axis() == "Time":
            return player_kills_vs_time(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.team_b()].iloc[1]['player'],  
                gamemode(), 
                player_6_line(),
                input.map_name()
            )
        else:
            return player_kills_vs_score_diff(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.team_b()].iloc[1]['player'], 
                gamemode(), 
                player_6_line(),
                input.map_name()
            )
        
    # Player Seven Boxplot
    @render.plot
    def player_7_box():
        return player_kills_overview(
            cdlDF, 
            rostersDF[rostersDF['team'] == input.team_b()].iloc[2]['player'],  
            gamemode(), 
            player_7_line(),
            input.map_name()
        )

    # Player Seven Scatterplot
    @render.plot
    def player_7_scatter():
        if input.x_axis() == "Time":
            return player_kills_vs_time(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.team_b()].iloc[2]['player'],  
                gamemode(), 
                player_7_line(),
                input.map_name()
            )
        else:
            return player_kills_vs_score_diff(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.team_b()].iloc[2]['player'], 
                gamemode(), 
                player_7_line(),
                input.map_name()
            )
        
    # Player Eight Boxplot
    @render.plot
    def player_8_box():
        return player_kills_overview(
            cdlDF, 
            rostersDF[rostersDF['team'] == input.team_b()].iloc[3]['player'],  
            gamemode(), 
            player_8_line(),
            input.map_name()
        )

    # Player Eight Scatterplot
    @render.plot
    def player_8_scatter():
        if input.x_axis() == "Time":
            return player_kills_vs_time(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.team_b()].iloc[3]['player'],  
                gamemode(), 
                player_8_line(),
                input.map_name()
            )
        else:
            return player_kills_vs_score_diff(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.team_b()].iloc[3]['player'], 
                gamemode(), 
                player_8_line(),
                input.map_name()
            )
    
    # Player One O/U 
    @render.ui
    def player_1_ou():
        over_under, percentage = player_over_under_percentage(
            cdlDF, 
            rostersDF[rostersDF['team'] == input.team_a()].iloc[0]['player'], 
            gamemode(), 
            player_1_line(), 
            input.map_name()
        )
        if over_under == "Never Played":
            return over_under
        return f"{over_under} {percentage}%"
    
    # Player Two O/U 
    @render.ui
    def player_2_ou():
        over_under, percentage = player_over_under_percentage(
            cdlDF, 
            rostersDF[rostersDF['team'] == input.team_a()].iloc[1]['player'], 
            gamemode(), 
            player_2_line(), 
            input.map_name()
        )
        if over_under == "Never Played":
            return over_under
        return f"{over_under} {percentage}%"

    # Player Three O/U 
    @render.ui
    def player_3_ou():
        over_under, percentage = player_over_under_percentage(
            cdlDF, 
            rostersDF[rostersDF['team'] == input.team_a()].iloc[2]['player'], 
            gamemode(), 
            player_3_line(), 
            input.map_name()
        )
        if over_under == "Never Played":
            return over_under
        return f"{over_under} {percentage}%"

    # Player Four O/U 
    @render.ui
    def player_4_ou():
        over_under, percentage = player_over_under_percentage(
            cdlDF, 
            rostersDF[rostersDF['team'] == input.team_a()].iloc[3]['player'], 
            gamemode(), 
            player_4_line(), 
            input.map_name()
        )
        if over_under == "Never Played":
            return over_under
        return f"{over_under} {percentage}%"

    # Player Five O/U 
    @render.ui
    def player_5_ou():
        over_under, percentage = player_over_under_percentage(
            cdlDF, 
            rostersDF[rostersDF['team'] == input.team_b()].iloc[0]['player'], 
            gamemode(), 
            player_5_line(), 
            input.map_name()
        )
        if over_under == "Never Played":
            return over_under
        return f"{over_under} {percentage}%"

    # Player Six O/U 
    @render.ui
    def player_6_ou():
        over_under, percentage = player_over_under_percentage(
            cdlDF, 
            rostersDF[rostersDF['team'] == input.team_b()].iloc[1]['player'], 
            gamemode(), 
            player_6_line(), 
            input.map_name()
        )
        if over_under == "Never Played":
            return over_under
        return f"{over_under} {percentage}%"

    # Player Seven O/U 
    @render.ui
    def player_7_ou():
        over_under, percentage = player_over_under_percentage(
            cdlDF, 
            rostersDF[rostersDF['team'] == input.team_b()].iloc[2]['player'], 
            gamemode(), 
            player_7_line(), 
            input.map_name()
        )
        if over_under == "Never Played":
            return over_under
        return f"{over_under} {percentage}%"

    # Player Eight O/U 
    @render.ui
    def player_8_ou():
        over_under, percentage = player_over_under_percentage(
            cdlDF, 
            rostersDF[rostersDF['team'] == input.team_b()].iloc[3]['player'], 
            gamemode(), 
            player_8_line(), 
            input.map_name()
        )
        if over_under == "Never Played":
            return over_under
        return f"{over_under} {percentage}%"
    
    # Player One O/U Icon
    @render.ui
    def player_1_ou_icon():
        over_under = player_over_under_percentage(
            cdlDF, 
            rostersDF[rostersDF['team'] == input.team_a()].iloc[0]['player'], 
            gamemode(), 
            player_1_line(), 
            input.map_name()
        )[0]
        if over_under == "Over":
            return ICONS["chevron_up"]
        else:
            return ICONS["chevron_down"]
        
    # Player Two O/U Icon
    @render.ui
    def player_2_ou_icon():
        over_under = player_over_under_percentage(
            cdlDF, 
            rostersDF[rostersDF['team'] == input.team_a()].iloc[1]['player'], 
            gamemode(), 
            player_2_line(), 
            input.map_name()
        )[0]
        if over_under == "Over":
            return ICONS["chevron_up"]
        else:
            return ICONS["chevron_down"]
        
    # Player Three O/U Icon
    @render.ui
    def player_3_ou_icon():
        over_under = player_over_under_percentage(
            cdlDF, 
            rostersDF[rostersDF['team'] == input.team_a()].iloc[2]['player'], 
            gamemode(), 
            player_3_line(), 
            input.map_name()
        )[0]
        if over_under == "Over":
            return ICONS["chevron_up"]
        else:
            return ICONS["chevron_down"]
        
    # Player Four O/U Icon
    @render.ui
    def player_4_ou_icon():
        over_under = player_over_under_percentage(
            cdlDF, 
            rostersDF[rostersDF['team'] == input.team_a()].iloc[3]['player'], 
            gamemode(), 
            player_4_line(), 
            input.map_name()
        )[0]
        if over_under == "Over":
            return ICONS["chevron_up"]
        else:
            return ICONS["chevron_down"]
        
    # Player Five O/U Icon
    @render.ui
    def player_5_ou_icon():
        over_under = player_over_under_percentage(
            cdlDF, 
            rostersDF[rostersDF['team'] == input.team_b()].iloc[0]['player'], 
            gamemode(), 
            player_5_line(), 
            input.map_name()
        )[0]
        if over_under == "Over":
            return ICONS["chevron_up"]
        else:
            return ICONS["chevron_down"]
        
    # Player Six O/U Icon
    @render.ui
    def player_6_ou_icon():
        over_under = player_over_under_percentage(
            cdlDF, 
            rostersDF[rostersDF['team'] == input.team_b()].iloc[1]['player'], 
            gamemode(), 
            player_6_line(), 
            input.map_name()
        )[0]
        if over_under == "Over":
            return ICONS["chevron_up"]
        else:
            return ICONS["chevron_down"]
        
    # Player Seven O/U Icon
    @render.ui
    def player_7_ou_icon():
        over_under = player_over_under_percentage(
            cdlDF, 
            rostersDF[rostersDF['team'] == input.team_b()].iloc[2]['player'], 
            gamemode(), 
            player_7_line(), 
            input.map_name()
        )[0]
        if over_under == "Over":
            return ICONS["chevron_up"]
        else:
            return ICONS["chevron_down"]
        
    # Player Eight O/U Icon
    @render.ui
    def player_8_ou_icon():
        over_under = player_over_under_percentage(
            cdlDF, 
            rostersDF[rostersDF['team'] == input.team_b()].iloc[3]['player'], 
            gamemode(), 
            player_8_line(), 
            input.map_name()
        )[0]
        if over_under == "Over":
            return ICONS["chevron_up"]
        else:
            return ICONS["chevron_down"]
        
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
        
    # Change O/U Streak Icon Based on recent O/U result
    @render.ui
    def change_player_1_ou_streak_icon():
        start = player_over_under_streak(
            cdlDF, 
            rostersDF[rostersDF['team'] == input.team_a()].iloc[0]['player'], 
            gamemode(), 
            player_1_line(), 
            input.map_name()
        )[0]
        return ICONS["red_crosshairs"] if start == "Under" else ICONS["green_crosshairs"]
    
    # Change O/U Streak Icon Based on recent O/U result
    @render.ui
    def change_player_2_ou_streak_icon():
        start = player_over_under_streak(
            cdlDF, 
            rostersDF[rostersDF['team'] == input.team_a()].iloc[1]['player'], 
            gamemode(), 
            player_2_line(), 
            input.map_name()
        )[0]
        return ICONS["red_crosshairs"] if start == "Under" else ICONS["green_crosshairs"]
    
    # Change O/U Streak Icon Based on recent O/U result
    @render.ui
    def change_player_3_ou_streak_icon():
        start = player_over_under_streak(
            cdlDF, 
            rostersDF[rostersDF['team'] == input.team_a()].iloc[2]['player'], 
            gamemode(), 
            player_3_line(), 
            input.map_name()
        )[0]
        return ICONS["red_crosshairs"] if start == "Under" else ICONS["green_crosshairs"]
    
    # Change O/U Streak Icon Based on recent O/U result
    @render.ui
    def change_player_4_ou_streak_icon():
        start = player_over_under_streak(
            cdlDF, 
            rostersDF[rostersDF['team'] == input.team_a()].iloc[3]['player'], 
            gamemode(), 
            player_4_line(), 
            input.map_name()
        )[0]
        return ICONS["red_crosshairs"] if start == "Under" else ICONS["green_crosshairs"]
    
    # Change O/U Streak Icon Based on recent O/U result
    @render.ui
    def change_player_5_ou_streak_icon():
        start = player_over_under_streak(
            cdlDF, 
            rostersDF[rostersDF['team'] == input.team_b()].iloc[0]['player'], 
            gamemode(), 
            player_5_line(), 
            input.map_name()
        )[0]
        return ICONS["red_crosshairs"] if start == "Under" else ICONS["green_crosshairs"]
    
    # Change O/U Streak Icon Based on recent O/U result
    @render.ui
    def change_player_6_ou_streak_icon():
        start = player_over_under_streak(
            cdlDF, 
            rostersDF[rostersDF['team'] == input.team_b()].iloc[1]['player'], 
            gamemode(), 
            player_6_line(), 
            input.map_name()
        )[0]
        return ICONS["red_crosshairs"] if start == "Under" else ICONS["green_crosshairs"]
    
    # Change O/U Streak Icon Based on recent O/U result
    @render.ui
    def change_player_7_ou_streak_icon():
        start = player_over_under_streak(
            cdlDF, 
            rostersDF[rostersDF['team'] == input.team_b()].iloc[2]['player'], 
            gamemode(), 
            player_7_line(), 
            input.map_name()
        )[0]
        return ICONS["red_crosshairs"] if start == "Under" else ICONS["green_crosshairs"]
    
    # Change O/U Streak Icon Based on recent O/U result
    @render.ui
    def change_player_8_ou_streak_icon():
        start = player_over_under_streak(
            cdlDF, 
            rostersDF[rostersDF['team'] == input.team_b()].iloc[3]['player'], 
            gamemode(), 
            player_8_line(), 
            input.map_name()
        )[0]
        return ICONS["red_crosshairs"] if start == "Under" else ICONS["green_crosshairs"]


# Run app
app = App(app_ui, server)