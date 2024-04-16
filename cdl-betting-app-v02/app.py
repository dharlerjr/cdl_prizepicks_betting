

# Import shiny and shinyswatch
from shiny import App, reactive, render, ui
import shinyswatch

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

# Initialize player props dataframe
initial_player_props = build_intial_props(rostersDF)

# Define ui
app_ui = ui.page_sidebar(   
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
    ui.layout_columns(
        ui.card(ui.output_table("team_summaries")), 
        ui.card(ui.output_table("h2h_summary"))
    ),
    ui.layout_columns(
        ui.card(ui.output_plot("player_1_box")), 
        ui.card(ui.output_plot("player_1_scatter"))
    ),
    ui.layout_columns(
        ui.card(ui.output_plot("player_2_box")), 
        ui.card(ui.output_plot("player_2_scatter"))
    ),
    ui.layout_columns(
        ui.card(ui.output_plot("player_3_box")), 
        ui.card(ui.output_plot("player_3_scatter"))
    ),
    ui.layout_columns(
        ui.card(ui.output_plot("player_4_box")), 
        ui.card(ui.output_plot("player_4_scatter"))
    ),
    ui.layout_columns(
        ui.card(ui.output_plot("team_a_score_diffs")), 
        ui.card(ui.output_data_frame("team_a_kills_scoreboard"))
    ),
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
    
    # Team Summaries
    @render.table
    def team_summaries():
        return team_summaries_fn(team_summaries_DF, input.team_a(), input.team_b())
    
    # H2H Summary
    @render.table
    def h2h_summary():
        return h2h_summary_fn(cdlDF, input.team_a(), input.team_b())
    
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
        

app = App(app_ui, server)