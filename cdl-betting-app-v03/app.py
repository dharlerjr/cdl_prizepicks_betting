

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

# Dictionary of gamemode abbreviations for value box titles
gamemode_abbrs = {
    "Hardpoint": "HP", 
    "Search & Destroy": "SnD", 
    "Control": "Control"
}

# Dictionary of faicons for value boxes
ICONS = {
    "red_crosshairs": fa.icon_svg("crosshairs", height = "48px").add_class("text-danger"), 
    "green_crosshairs": fa.icon_svg("crosshairs", height = "48px").add_class("text-success"), 
    "crosshairs": fa.icon_svg("crosshairs", height = "48px"),
    "percent": fa.icon_svg("percent", height = "48px"), 
    "headset": fa.icon_svg("headset", height = "48px"), 
    "plus": fa.icon_svg("plus", height = "48px"), 
    "minus": fa.icon_svg("minus", height = "48px"), 
    "chevron_up": fa.icon_svg("chevron-up", height = "48px").add_class("text-purple"),
    "chevron_down": fa.icon_svg("chevron-down", height = "48px").add_class("text-purple")
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
        #shinyswatch.theme_picker_ui(),
        
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

    # Row 1 of 4
    ui.layout_columns(
        
        # Column 1 of 5: Team A Logo
        ui.output_image("team_a_logo", width = "120px", height = "120px"), 
            
        # Column 2 of 5: Team A Standing
        ui.value_box(
            title = "Series W-L (Major III Qualifiers)", 
            value = ui.output_ui("team_a_series_record"),
            showcase = ICONS["headset"]
        ),
        
        # Column 3 of 5: H2H Series Record
        ui.value_box(
            title = "Series H2H (Overall)",
            value = ui.output_ui("h2h_series_record"),
            showcase = ICONS["crosshairs"]
        ), 
        
        # Column 4 of 5: Team B Standing
        ui.value_box(
            title = "Series W-L (Major III Qualifiers)", 
            value = ui.output_ui("team_b_series_record"),
            showcase = ICONS["headset"]
        ), 
        
        # Column 5 of 5: Team B Logo
        ui.output_image("team_b_logo", width = "120px", height = "120px"), 

        # Row Height
        height = "140px"

    ),

    # Row 2 of 4
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
            showcase = ui.output_ui("team_a_percentage_icon")
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
            showcase = ui.output_ui("team_b_percentage_icon")
        ), 
        
        # Team B Win Streak
        ui.value_box(
            title = ui.output_ui("team_b_win_streak_title"),
            value = ui.output_ui("team_b_win_streak"),
            showcase = ui.output_ui("change_team_b_win_streak_icon")
        ),
        
        # Row Height
        height = "140px"
    ),

    # Row 3 of 4
    ui.layout_columns(

        # Column 1: Team A Stats
        ui.layout_column_wrap(
            
            ui.card(ui.output_plot("team_a_score_diffs", width = "280px", height = "240px")),
            ui.card(ui.output_plot("team_a_maps_played", width = "280px", height = "160px")),

            width = 1
        ),

        # Column 2: Card with Pill Tabset of Player O/U Stats
        ui.layout_columns(
            ui.navset_card_pill( 
                player_panel("1"), 
                player_panel("2"), 
                player_panel("3"), 
                player_panel("4"), 
                player_panel("5"), 
                player_panel("6"), 
                player_panel("7"), 
                player_panel("8"), 
            ),
        ),

        # Column 3: Team B Stats
        ui.layout_column_wrap(

            ui.card(ui.output_plot("team_b_score_diffs", width = "280px", height = "240px")),
            ui.card(ui.output_plot("team_b_maps_played", width = "280px", height = "160px")),

            width = 1, 
        ),

        # Row Height
        height = "680px",

        # Column Widths
        col_widths = [3, 6, 3]

    ),

    # Row 4 of 4: Series Score Differentials & Big Datagrid
    ui.layout_columns(

        # Column 1: Team A Score Diffs
        ui.card(ui.output_plot("team_a_series_diffs", width = "280px", height = "240px")),

        # Column 2: Big Datagrid
        ui.card(ui.output_data_frame("scoreboards")),

        # Column 3: Team B Score Diffs
        ui.card(ui.output_plot("team_b_series_diffs", width = "280px", height = "240px")),

        # Row Height
        height = "360px",
        
        # Column Widths
        col_widths = [3, 6, 3]

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
                        "width": "120px", "height": "120px"}
        return img
    
    # Team B Logo
    @render.image
    def team_b_logo():
        img: ImgData = {"src": os.path.dirname(__file__) + team_logos[input.team_b()], 
                        "width": "120px", "height": "120px"}
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
    
    # Title for Team A Map Record Value Box
    @render.ui
    def team_a_map_record_title():
        if input.map_name() == "All":
            return f"{gamemode_abbrs[gamemode()]} Win % (W - L)"
        else:
            return f"{input.map_name()} {gamemode_abbrs[gamemode()]} Win % (W - L)"
        
    # Title for Team B Map Record Value Box
    @render.ui
    def team_b_map_record_title():
        if input.map_name() == "All":
            return f"{gamemode_abbrs[gamemode()]} Win % (W - L)"
        else:
            return f"{input.map_name()} {gamemode_abbrs[gamemode()]} Win % (W - L)"
        
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
    def team_a_percentage_icon():
        map_to_search_for = "Overall" if input.map_name() == "All" else input.map_name()
        win_percentage = team_summaries_DF.loc[
            (team_summaries_DF['team'] == input.team_a()) &
            (team_summaries_DF['gamemode'] == gamemode()) & 
            (team_summaries_DF['map_name'] == map_to_search_for), 'win_percentage'].reset_index(drop=True)[0]
        icon = ICONS["percent"]
        return icon.add_class(f"text-{('success' if win_percentage >= 0.5 else 'danger')}")
                

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
    def team_b_percentage_icon():
        map_to_search_for = "Overall" if input.map_name() == "All" else input.map_name()
        win_percentage = team_summaries_DF.loc[
            (team_summaries_DF['team'] == input.team_b()) &
            (team_summaries_DF['gamemode'] == gamemode()) & 
            (team_summaries_DF['map_name'] == map_to_search_for), 'win_percentage'].reset_index(drop=True)[0]
        icon = ICONS["percent"]
        return icon.add_class(f"text-{('success' if win_percentage >= 0.5 else 'danger')}")

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
    
    # Team A Pie Chart of % Maps Played
    @render.plot
    def team_a_maps_played():
        return team_percent_maps_played(
            team_summaries_DF, input.team_a(), gamemode()
        )
    
    # Team B Pie Chart of % Maps Played
    @render.plot
    def team_b_maps_played():
        return team_percent_maps_played(
            team_summaries_DF, input.team_b(), gamemode()
        )
    
    # Team A Series Differentials Histogram
    @render.plot
    def team_a_series_diffs():
        return team_series_diffs(series_score_diffs, input.team_a())
    
    # Team B Series Differentials Histogram
    @render.plot
    def team_b_series_diffs():
        return team_series_diffs(series_score_diffs, input.team_b())
    
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
    
    
    # Player One Plot
    @render.plot
    def player_1_plot():
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
        
    # Player Two Plot
    @render.plot
    def player_2_plot():
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
        
    # Player Three Plot
    @render.plot
    def player_3_plot():
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
        
    # Player Four Plot
    @render.plot
    def player_4_plot():
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
        
    # Player Five Plot
    @render.plot
    def player_5_plot():
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
        
    # Player Six Plot
    @render.plot
    def player_6_plot():
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
        
    # Player Seven Plot
    @render.plot
    def player_7_plot():
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
        
    # Player Eight Plot
    @render.plot
    def player_8_plot():
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
    @render.ui
    def player_1_ou():
        over_under, percentage, overs, unders, hooks = player_1_ou_stats()
        if over_under == "Never Played":
            return over_under
        return f"{over_under} {percentage}% ({overs} - {unders} - {hooks})"
    
    # Player Two O/U %
    @render.ui
    def player_2_ou():
        over_under, percentage, overs, unders, hooks = player_2_ou_stats()
        if over_under == "Never Played":
            return over_under
        return f"{over_under} {percentage}% ({overs} - {unders} - {hooks})"

    # Player Three O/U %
    @render.ui
    def player_3_ou():
        over_under, percentage, overs, unders, hooks = player_3_ou_stats()
        if over_under == "Never Played":
            return over_under
        return f"{over_under} {percentage}% ({overs} - {unders} - {hooks})"

    # Player Four O/U %
    @render.ui
    def player_4_ou():
        over_under, percentage, overs, unders, hooks = player_4_ou_stats()
        if over_under == "Never Played":
            return over_under
        return f"{over_under} {percentage}% ({overs} - {unders} - {hooks})"

    # Player Five O/U %
    @render.ui
    def player_5_ou():
        over_under, percentage, overs, unders, hooks = player_5_ou_stats()
        if over_under == "Never Played":
            return over_under
        return f"{over_under} {percentage}% ({overs} - {unders} - {hooks})"

    # Player Six O/U %
    @render.ui
    def player_6_ou():
        over_under, percentage, overs, unders, hooks = player_6_ou_stats()
        if over_under == "Never Played":
            return over_under
        return f"{over_under} {percentage}% ({overs} - {unders} - {hooks})"

    # Player Seven O/U %
    @render.ui
    def player_7_ou():
        over_under, percentage, overs, unders, hooks = player_7_ou_stats()
        if over_under == "Never Played":
            return over_under
        return f"{over_under} {percentage}% ({overs} - {unders} - {hooks})"

    # Player Eight O/U %
    @render.ui
    def player_8_ou():
        over_under, percentage, overs, unders, hooks = player_8_ou_stats()
        if over_under == "Never Played":
            return over_under
        return f"{over_under} {percentage}% ({overs} - {unders} - {hooks})"
    
    # Player One O/U Icon
    @render.ui
    def player_1_ou_icon():
        over_under = player_1_ou_stats()[0]
        if over_under == "Over":
            return ICONS["chevron_up"]
        else:
            return ICONS["chevron_down"]
        
    # Player Two O/U Icon
    @render.ui
    def player_2_ou_icon():
        over_under = player_2_ou_stats()[0]
        if over_under == "Over":
            return ICONS["chevron_up"]
        else:
            return ICONS["chevron_down"]
        
    # Player Three O/U Icon
    @render.ui
    def player_3_ou_icon():
        over_under = player_3_ou_stats()[0]
        if over_under == "Over":
            return ICONS["chevron_up"]
        else:
            return ICONS["chevron_down"]
        
    # Player Four O/U Icon
    @render.ui
    def player_4_ou_icon():
        over_under = player_4_ou_stats()[0]
        if over_under == "Over":
            return ICONS["chevron_up"]
        else:
            return ICONS["chevron_down"]
        
    # Player Five O/U Icon
    @render.ui
    def player_5_ou_icon():
        over_under = player_5_ou_stats()[0]
        if over_under == "Over":
            return ICONS["chevron_up"]
        else:
            return ICONS["chevron_down"]
        
    # Player Six O/U Icon
    @render.ui
    def player_6_ou_icon():
        over_under = player_6_ou_stats()[0]
        if over_under == "Over":
            return ICONS["chevron_up"]
        else:
            return ICONS["chevron_down"]
        
    # Player Seven O/U Icon
    @render.ui
    def player_7_ou_icon():
        over_under = player_7_ou_stats()[0]
        if over_under == "Over":
            return ICONS["chevron_up"]
        else:
            return ICONS["chevron_down"]
        
    # Player Eight O/U Icon
    @render.ui
    def player_8_ou_icon():
        over_under = player_8_ou_stats()[0]
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
    def player_1_ou_streak_icon():
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
    def player_2_ou_streak_icon():
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
    def player_3_ou_streak_icon():
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
    def player_4_ou_streak_icon():
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
    def player_5_ou_streak_icon():
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
    def player_6_ou_streak_icon():
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
    def player_7_ou_streak_icon():
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
    def player_8_ou_streak_icon():
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