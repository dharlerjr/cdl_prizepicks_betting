

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
from pandas_stylers_helpers import *
from df_display_helpers import *

# Dictionary to map map_num to gamemode
map_nums_to_gamemode = {
    "1": "Hardpoint", 
    "2": "Search & Destroy", 
    "3": "Control", 
    "4": "Hardpoint", 
    "5": "Search & Destroy"
}

# Dictionary of paths to saved team logo images
team_logos = {
    "Atlanta FaZe": "\\team_logos\\ATL.webp",
    "Boston Breach": "\\team_logos\\BOS.webp",
    "Carolina Royal Ravens": "\\team_logos\\CAR.webp", 
    "Las Vegas Legion": "\\team_logos\\LV.webp",
    "Los Angeles Guerrillas": "\\team_logos\\LAG.webp", 
    "Los Angeles Thieves": "\\team_logos\\LAT.webp", 
    "Miami Hertics": "\\team_logos\\MIA.webp", 
    "Minnesota ROKKR": "\\team_logos\\MIN.webp", 
    "New York Subliners": "\\team_logos\\NYSL.webp",
    "OpTic Texas": "\\team_logos\\TX.webp", 
    "Seattle Surge": "\\team_logos\\SEA.webp", 
    "Toronto Ultra": "\\team_logos\\TOR.webp"
}

# Dictionary of faicons for value boxes
ICONS = {
    "crosshairs": fa.icon_svg("crosshairs"), 
    "percent": fa.icon_svg("percent"), 
    "headset": fa.icon_svg("headset")
}

# Load in data
cdlDF = load_and_clean_cdl_data()
cdlDF

# Build series summaries
series_score_diffs = build_series_summaries(cdlDF)

# Build team summaries
team_summaries_DF = build_team_summaries(cdlDF)
team_summaries_DF

# Filter players
cdlDF = filter_players(cdlDF)

# Build team rosters
rostersDF = build_rosters(cdlDF)

# Compute CDL Standings for Major III Qualifiers
current_standings = \
    cdlDF[(cdlDF["match_date"] >= '2024-04-12')] \
    [["match_id", "team", "series_result"]] \
    .drop_duplicates() \
    .groupby("team") \
    .agg(
        wins = ("series_result", lambda x: sum(x)), 
        losses = ("series_result", lambda x: len(x) - sum(x))
    ) \
    .reset_index()

# Initialize player props dataframe
initial_player_props = build_intial_props(rostersDF)

# Define ui
app_ui = ui.page_sidebar(   

    # Sidebar
    ui.sidebar(

        # Theme picker
        # shinyswatch.theme_picker_ui(),

        # Set theme
        shinyswatch.theme.cerulean,

        # Inputs
        ui.input_action_button(id = "scrape", label = "Get PrizePicks Lines"), 
        ui.input_select(id = "team_a", label = "Team A", selected = "OpTic Texas",
                        choices = sorted(cdlDF['team'].unique())), 
        ui.input_select(id = "team_b", label = "Team B", selected = "Atlanta FaZe",
                        choices = sorted(cdlDF['team'].unique())), 
        ui.input_select(id = "map_num", label = "Map Number", selected = 1,
                        choices = [1, 2, 3, 4, 5]), 
        ui.input_select(id = "map_name", label = "Map", selected = "All",
                        choices = ["All"] + sorted(filter_maps(cdlDF)['map_name'].unique())), 
        ui.input_select(id = "x_axis", label = "X-Axis", selected = "Time",
                        choices = ["Time", "Score Differential"])
    ), 
    
    # Team Logos
    ui.layout_columns(
        ui.card(
            ui.output_image("team_a_logo", width = "80px", height = "100px"), 
            max_height = "160px"
            ),
        ui.markdown("**vs**"),
        ui.card(
            ui.output_image("team_b_logo", width = "80px", height = "100px"), 
            max_height = "160px"
            ), 
        col_widths = [2, 8, 2]
    ),

    # Value boxes of Win-Loss Records & Win %s for Selected Teams
    ui.layout_columns(
        ui.value_box(
            title = "Major III Series W-L", 
            value = ui.output_ui("team_a_series_record"),
            showcase = ICONS["headset"]
        ), 
        ui.value_box(
            title = "Map Win % (W-L)", 
            value = ui.output_ui("team_b_map_record"),
            showcase = ICONS["percent"]
        ), 
        ui.value_box(
            title = "H2H Map Record", 
            value = ui.output_ui("h2h_map_record"),
            showcase = ICONS["crosshairs"]
        ), 
        ui.value_box(
            title = "Map Win % (W-L)", 
            value = ui.output_ui("team_b_map_record"),
            showcase = ICONS["percent"]
        ),
        ui.value_box(
            title = "Major III Series W-L", 
            value = ui.output_ui("team_b_series_record"),
            showcase = ICONS["headset"]
        )
    ),

    # Plots of Player Kills
    ui.layout_columns(
        # Team A Card & Tabs
        ui.navset_card_pill(
            ui.nav_panel(
                "1", 
                ui.layout_columns(
                    ui.output_plot("player_1_box", width = "200px"), 
                    ui.output_plot("player_1_scatter", width = "800px")
                )
            ), 
            ui.nav_panel(                
                "2", 
                ui.layout_columns(
                    ui.output_plot("player_2_box", width = "200px"), 
                    ui.output_plot("player_2_scatter", width = "800px")
                )), 
            ui.nav_panel(                
                "3", 
                ui.layout_columns(
                    ui.output_plot("player_3_box", width = "200px"), 
                    ui.output_plot("player_3_scatter", width = "800px")
                )), 
            ui.nav_panel(                
                "4", 
                ui.layout_columns(
                    ui.output_plot("player_4_box", width = "200px"), 
                    ui.output_plot("player_4_scatter", width = "800px")
                ))
        ),
        # Team B Card & Tabs
        ui.navset_card_pill(
            ui.nav_panel(
                "1", 
                ui.layout_columns(
                    ui.output_plot("player_5_box", width = "200px"), 
                    ui.output_plot("player_5_scatter", width = "800px")
                )
            ), 
            ui.nav_panel(                
                "2", 
                ui.layout_columns(
                    ui.output_plot("player_6_box", width = "200px"), 
                    ui.output_plot("player_6_scatter", width = "800px")
                )), 
            ui.nav_panel(                
                "3", 
                ui.layout_columns(
                    ui.output_plot("player_7_box", width = "200px"), 
                    ui.output_plot("player_7_scatter", width = "800px")
                )), 
            ui.nav_panel(                
                "4", 
                ui.layout_columns(
                    ui.output_plot("player_8_box", width = "200px"), 
                    ui.output_plot("player_8_scatter", width = "800px")
                ))
        ),
    ),
    # Map Score Differentials & Results
    ui.layout_columns(
        ui.card(ui.output_plot("team_a_score_diffs")), 
        ui.card(ui.output_data_frame("team_a_kills_scoreboard"))
    ),
    # Series Score Differentials & Results
    ui.layout_columns(
        ui.card(ui.output_plot("team_a_series_diffs")), 
        ui.card(ui.output_data_frame("team_a_series_scoreboard"))
    ),
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
        player_props_df.set(
            pd.merge(
                scrape_prizepicks(),
                rostersDF.drop(['proptype', 'player_line'], axis=1),
                on = 'player', how =  'left'
            )
        )

    # Reactive calc to translate map num to gamemode
    @reactive.calc
    def gamemode():
        return map_nums_to_gamemode[input.map_num()]
    
    # Team A Logo
    @render.image
    def team_a_logo():
        img: ImgData = {"src": os.path.dirname(__file__) + team_logos[input.team_a()], 
                        "width": "100px", "width": "100px", "image-align": "left"}
        return img
    
    # Team B Logo
    @render.image
    def team_b_logo():
        img: ImgData = {"src": os.path.dirname(__file__) + team_logos[input.team_b()], 
                        "width": "100px", "width": "100px", "image-align": "right"}
        return img
    
    # Team A Series Record for Major 3 Quals
    @render.ui
    def team_a_series_record():
        queried_df = current_standings[current_standings["team"] == input.team_a()] \
            .reset_index(drop = True)
        wins = queried_df.loc[0, "wins"]
        losses = queried_df.loc[0, "losses"]
        return f"{wins} - {losses}"

    # Team B Series Record for Major 3 Quals
    @render.ui
    def team_b_series_record():
        queried_df = current_standings[current_standings["team"] == input.team_b()] \
            .reset_index(drop = True)
        wins = queried_df.loc[0, "wins"]
        losses = queried_df.loc[0, "losses"]
        return f"{wins} - {losses}"
    
    # Team A Map Record for User-Selected Map & Mode Combination
    @render.ui
    def team_a_map_record():
        if input.map_name() == "All":
            queried_df = team_summaries_DF[
                (team_summaries_DF["team"] == input.team_a()) & 
                (team_summaries_DF["gamemode"] == gamemode()) & 
                (team_summaries_DF["map_name"] == "Overall")
            ].reset_index(drop = True)
        else:
            queried_df = team_summaries_DF[
                (team_summaries_DF["team"] == input.team_a()) & 
                (team_summaries_DF["gamemode"] == gamemode()) & 
                (team_summaries_DF["map_name"] == input.map_name())
            ].reset_index(drop = True)
        wins = queried_df.loc[0, "wins"]
        losses = queried_df.loc[0, "losses"]
        win_percentage = queried_df.loc[0, "win_percentage"]
        return f"{win_percentage:.0%} ({wins} - {losses})"

    # Team B Map Record for User-Selected Map & Mode Combination
    @render.ui
    def team_b_map_record():
        if input.map_name() == "All":
            queried_df = team_summaries_DF[
                (team_summaries_DF["team"] == input.team_b()) & 
                (team_summaries_DF["gamemode"] == gamemode()) & 
                (team_summaries_DF["map_name"] == "Overall")
            ].reset_index(drop = True)
        else:
            queried_df = team_summaries_DF[
                (team_summaries_DF["team"] == input.team_b()) & 
                (team_summaries_DF["gamemode"] == gamemode()) & 
                (team_summaries_DF["map_name"] == input.map_name())
            ].reset_index(drop = True)
        wins = queried_df.loc[0, "wins"]
        losses = queried_df.loc[0, "losses"]
        win_percentage = queried_df.loc[0, "win_percentage"]
        return f"{win_percentage:.0%} ({wins} - {losses})"

    # H2H Map Record for User-Selected Map & Mode Combination
    @render.ui
    def h2h_map_record():
        if input.map_name() == "All":
            queried_df = cdlDF \
                [["match_id", "team", "map_name", "gamemode", "map_result", "opp"]] \
                [(cdlDF["team"] == "OpTic Texas") & \
                    (cdlDF["opp"] == "Atlanta FaZe") &
                    (cdlDF["gamemode"] == "Hardpoint")] \
                .drop_duplicates() \
                .groupby("gamemode", observed = True) \
                .agg(
                    wins = ("map_result", lambda x: sum(x)), 
                    losses = ("map_result", lambda x: len(x) - sum(x))
                    ) \
                .reset_index()
        else:
            queried_df = filter_maps(cdlDF) \
                [["match_id", "team", "map_name", "gamemode", "map_result", "opp"]] \
                [(cdlDF["team"] == "Atlanta FaZe") & \
                    (cdlDF["opp"] == "OpTic Texas") & 
                    (cdlDF["gamemode"] == "Hardpoint") & 
                    (cdlDF["map_name"] == "Karachi")] \
                .drop_duplicates() \
                .groupby(["gamemode", "map_name"], observed = True) \
                .agg(
                    wins = ("map_result", lambda x: sum(x)), 
                    losses = ("map_result", lambda x: len(x) - sum(x))
                ) \
                .reset_index()
        wins = queried_df.loc[0, "wins"]
        losses = queried_df.loc[0, "losses"]
        return f"{wins} - {losses}"

    # Not implemented
    # # Team Summaries
    # @render.table
    # def team_summaries():
    #     return team_summaries_fn(team_summaries_DF, input.team_a(), input.team_b())
    
    # # H2H Summary
    # @render.table
    # def h2h_summary():
    #     return h2h_summary_fn(cdlDF, input.team_a(), input.team_b())
    
    # Team A Series Scoreboard
    @render.data_frame
    def team_a_series_scoreboard():
        return render.DataGrid(
            build_series_scoreboards(
                series_score_diffs, 
                input.team_a()
                ), 
            filters = True, 
            summary = False
            )
    
    # Team A Kills Scoreboard
    @render.data_frame
    def team_a_kills_scoreboard():
        return render.DataGrid(
            build_map_scoreboards(
                filter_maps(cdlDF), 
                input.team_a(),
                gamemode()
                ), 
            filters = True, 
            summary = False
            )
    
    # Team A Score Differentials
    @render.plot
    def team_a_score_diffs():
        return team_score_diffs(
            cdlDF, input.team_a(), gamemode(), input.map_name()
        )
    
    # Team A Series Differentials
    @render.plot
    def team_a_series_diffs():
        return team_series_diffs(series_score_diffs, input.team_a())

    # Player One Boxplot
    @render.plot
    def player_1_box():
        return player_kills_overview(
            cdlDF, 
            rostersDF[rostersDF['team'] == input.team_a()].iloc[0]['player'],  
            gamemode(), 
            player_props_df.get()[
                (player_props_df.get()['team'] == input.team_a()) &
                (player_props_df.get()['proptype'] == int(input.map_num()))] \
                    .iloc[0]['player_line'],
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
                player_props_df.get()[
                    (player_props_df.get()['team'] == input.team_a()) &
                    (player_props_df.get()['proptype'] == int(input.map_num()))] \
                        .iloc[0]['player_line'],
                input.map_name()
            )
        else:
            return player_kills_vs_score_diff(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.team_a()].iloc[0]['player'],  
                gamemode(), 
                player_props_df.get()[
                    (player_props_df.get()['team'] == input.team_a()) &
                    (player_props_df.get()['proptype'] == int(input.map_num()))] \
                        .iloc[0]['player_line'],
                input.map_name()
            )
    
    # Player Two Boxplot
    @render.plot
    def player_2_box():
        return player_kills_overview(
            cdlDF, 
            rostersDF[rostersDF['team'] == input.team_a()].iloc[1]['player'],  
            gamemode(), 
            player_props_df.get()[
                (player_props_df.get()['team'] == input.team_a()) &
                (player_props_df.get()['proptype'] == int(input.map_num()))] \
                    .iloc[1]['player_line'],
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
                player_props_df.get()[
                    (player_props_df.get()['team'] == input.team_a()) &
                    (player_props_df.get()['proptype'] == int(input.map_num()))] \
                        .iloc[1]['player_line'],
                input.map_name()
            )
        else:
            return player_kills_vs_score_diff(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.team_a()].iloc[1]['player'],  
                gamemode(), 
                player_props_df.get()[
                    (player_props_df.get()['team'] == input.team_a()) &
                    (player_props_df.get()['proptype'] == int(input.map_num()))] \
                        .iloc[1]['player_line'],
                input.map_name()
            )
        
    # Player Three Boxplot
    @render.plot
    def player_3_box():
        return player_kills_overview(
            cdlDF, 
            rostersDF[rostersDF['team'] == input.team_a()].iloc[2]['player'],  
            gamemode(), 
            player_props_df.get()[
                (player_props_df.get()['team'] == input.team_a()) &
                (player_props_df.get()['proptype'] == int(input.map_num()))] \
                    .iloc[2]['player_line'],
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
                player_props_df.get()[
                    (player_props_df.get()['team'] == input.team_a()) &
                    (player_props_df.get()['proptype'] == int(input.map_num()))] \
                        .iloc[2]['player_line'],
                input.map_name()
            )
        else:
            return player_kills_vs_score_diff(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.team_a()].iloc[2]['player'],  
                gamemode(), 
                player_props_df.get()[
                    (player_props_df.get()['team'] == input.team_a()) &
                    (player_props_df.get()['proptype'] == int(input.map_num()))] \
                        .iloc[2]['player_line'],
                input.map_name()
            )
        
    # Player Four Boxplot
    @render.plot
    def player_4_box():
        return player_kills_overview(
            cdlDF, 
            rostersDF[rostersDF['team'] == input.team_a()].iloc[3]['player'],  
            gamemode(), 
            player_props_df.get()[
                (player_props_df.get()['team'] == input.team_a()) &
                (player_props_df.get()['proptype'] == int(input.map_num()))] \
                    .iloc[3]['player_line'],
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
                player_props_df.get()[
                    (player_props_df.get()['team'] == input.team_a()) &
                    (player_props_df.get()['proptype'] == int(input.map_num()))] \
                        .iloc[3]['player_line'],
                input.map_name()
            )
        else:
            return player_kills_vs_score_diff(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.team_a()].iloc[3]['player'], 
                gamemode(), 
                player_props_df.get()[
                    (player_props_df.get()['team'] == input.team_a()) &
                    (player_props_df.get()['proptype'] == int(input.map_num()))] \
                        .iloc[3]['player_line'],
                input.map_name()
            )
    
    # Player Five Boxplot
    @render.plot
    def player_5_box():
        return player_kills_overview(
            cdlDF, 
            rostersDF[rostersDF['team'] == input.team_b()].iloc[0]['player'],  
            gamemode(), 
            player_props_df.get()[
                (player_props_df.get()['team'] == input.team_b()) &
                (player_props_df.get()['proptype'] == int(input.map_num()))] \
                    .iloc[0]['player_line'],
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
                player_props_df.get()[
                    (player_props_df.get()['team'] == input.team_b()) &
                    (player_props_df.get()['proptype'] == int(input.map_num()))] \
                        .iloc[0]['player_line'],
                input.map_name()
            )
        else:
            return player_kills_vs_score_diff(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.team_a()].iloc[0]['player'], 
                gamemode(), 
                player_props_df.get()[
                    (player_props_df.get()['team'] == input.team_b()) &
                    (player_props_df.get()['proptype'] == int(input.map_num()))] \
                        .iloc[0]['player_line'],
                input.map_name()
            )
        
    # Player Six Boxplot
    @render.plot
    def player_6_box():
        return player_kills_overview(
            cdlDF, 
            rostersDF[rostersDF['team'] == input.team_b()].iloc[1]['player'],  
            gamemode(), 
            player_props_df.get()[
                (player_props_df.get()['team'] == input.team_b()) &
                (player_props_df.get()['proptype'] == int(input.map_num()))] \
                    .iloc[1]['player_line'],
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
                player_props_df.get()[
                    (player_props_df.get()['team'] == input.team_b()) &
                    (player_props_df.get()['proptype'] == int(input.map_num()))] \
                        .iloc[1]['player_line'],
                input.map_name()
            )
        else:
            return player_kills_vs_score_diff(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.team_b()].iloc[1]['player'], 
                gamemode(), 
                player_props_df.get()[
                    (player_props_df.get()['team'] == input.team_b()) &
                    (player_props_df.get()['proptype'] == int(input.map_num()))] \
                        .iloc[1]['player_line'],
                input.map_name()
            )
        
    # Player Seven Boxplot
    @render.plot
    def player_7_box():
        return player_kills_overview(
            cdlDF, 
            rostersDF[rostersDF['team'] == input.team_b()].iloc[2]['player'],  
            gamemode(), 
            player_props_df.get()[
                (player_props_df.get()['team'] == input.team_b()) &
                (player_props_df.get()['proptype'] == int(input.map_num()))] \
                    .iloc[2]['player_line'],
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
                player_props_df.get()[
                    (player_props_df.get()['team'] == input.team_b()) &
                    (player_props_df.get()['proptype'] == int(input.map_num()))] \
                        .iloc[2]['player_line'],
                input.map_name()
            )
        else:
            return player_kills_vs_score_diff(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.team_b()].iloc[2]['player'], 
                gamemode(), 
                player_props_df.get()[
                    (player_props_df.get()['team'] == input.team_b()) &
                    (player_props_df.get()['proptype'] == int(input.map_num()))] \
                        .iloc[2]['player_line'],
                input.map_name()
            )
        
    # Player Eight Boxplot
    @render.plot
    def player_8_box():
        return player_kills_overview(
            cdlDF, 
            rostersDF[rostersDF['team'] == input.team_b()].iloc[3]['player'],  
            gamemode(), 
            player_props_df.get()[
                (player_props_df.get()['team'] == input.team_b()) &
                (player_props_df.get()['proptype'] == int(input.map_num()))] \
                    .iloc[3]['player_line'],
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
                player_props_df.get()[
                    (player_props_df.get()['team'] == input.team_b()) &
                    (player_props_df.get()['proptype'] == int(input.map_num()))] \
                        .iloc[3]['player_line'],
                input.map_name()
            )
        else:
            return player_kills_vs_score_diff(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.team_b()].iloc[3]['player'], 
                gamemode(), 
                player_props_df.get()[
                    (player_props_df.get()['team'] == input.team_b()) &
                    (player_props_df.get()['proptype'] == int(input.map_num()))] \
                        .iloc[3]['player_line'],
                input.map_name()
            )
        

app = App(app_ui, server)