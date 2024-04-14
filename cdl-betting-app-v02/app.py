

# Import shiny and shinyswatch
from shiny import App, reactive, render, ui
import shinyswatch

# Import setup
from setup.setup import *

# Import webscraper & helpers
from webscraper import *
from seaborn_helpers import *

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

# Function to remove all removed map & mode combos from cdlDF, 
# after building series summaries
cdlDF = filter_cdldf(cdlDF)

# Build team summaries
team_summaries_DF = build_team_summaries(cdlDF)
team_summaries_DF

# Initialize dataframe of PrizePicks player props
player_props = pd.DataFrame()

# Define ui
app_ui = ui.page_sidebar(   
    ui.sidebar(
        # Theme picker - start
        shinyswatch.theme_picker_ui(),

        ui.input_action_button(id = "scrape", label = "Get PrizePicks Lines"), 
        ui.input_select(id = "team_a", label = "Team", selected = "OpTic Texas",
                        choices = sorted(cdlDF['team'].unique())), 
        ui.input_select(id = "team_b", label = "Team", selected = "Atlanta FaZe",
                        choices = sorted(cdlDF['team'].unique())), 
        ui.input_select(id = "map_num", label = "Map Number", selected = 1,
                        choices = [1, 2, 3, 4, 5]), 
        ui.input_select(id = "map_name", label = "Map", selected = "All",
                        choices = ["All"] + \
                            sorted([map_name for map_name in cdlDF['map_name'].unique() if map_name != "Skidrow"])), 
        ui.input_select(id = "x_axis", label = "X-Axis", selected = "Time",
                        choices = ["Time", "Score Differential"])
    ), 
    ui.layout_columns(
        ui.card(), 
        ui.card()
    ),
        ui.layout_columns(
        ui.card(ui.output_plot("player_1_box"),), 
        ui.card(ui.output_plot("player_1_scatter"),)
    ),
    ui.layout_columns(
        ui.card(ui.output_plot("player_2_box"),), 
        ui.card(ui.output_plot("player_2_scatter"),)
    ),
    ui.layout_columns(
        ui.card(ui.output_plot("player_3_box"),), 
        ui.card(ui.output_plot("player_3_scatter"),)
    ),
    ui.layout_columns(
        ui.card(ui.output_plot("player_4_box"),), 
        ui.card(ui.output_plot("player_4_scatter"),)
    ),
    title = "CDL Bets on PrizePicks" 
)


# Define server logic
def server(input, output, session):

    # Theme picker
    shinyswatch.theme_picker_server()

    # Reactive calc to translate map num to gamemode
    @reactive.calc
    def gamemode():
        return map_nums_to_gamemode[input.map_num()]

    # Player One Boxplot
    @render.plot
    def player_1_box():
        return player_kills_overview(
            cdlDF, "Kenny", gamemode(), 20, input.map_name()
        )

    # Player One Scatterplot
    @render.plot
    def player_1_scatter():
        if input.x_axis() == "Time":
            return player_kills_vs_time(
                cdlDF, "Kenny", gamemode(), 20, input.map_name()
            )
        else:
            return player_kills_vs_score_diff(
                cdlDF, "Kenny", gamemode(), 20, input.map_name()
            )
    # Player Two Boxplot
    @render.plot
    def player_2_box():
        return player_kills_overview(
            cdlDF, "Kenny", gamemode(), 20, input.map_name()
        )

    # Player Two Scatterplot
    @render.plot
    def player_2_scatter():
        if input.x_axis() == "Time":
            return player_kills_vs_time(
                cdlDF, "Kenny", gamemode(), 20, input.map_name()
            )
        else:
            return player_kills_vs_score_diff(
                cdlDF, "Kenny", gamemode(), 20, input.map_name()
            )
        
    # Player Three Boxplot
    @render.plot
    def player_3_box():
        return player_kills_overview(
            cdlDF, "Kenny", gamemode(), 20, input.map_name()
        )

    # Player Three Scatterplot
    @render.plot
    def player_3_scatter():
        if input.x_axis() == "Time":
            return player_kills_vs_time(
                cdlDF, "Kenny", gamemode(), 20, input.map_name()
            )
        else:
            return player_kills_vs_score_diff(
                cdlDF, "Kenny", gamemode(), 20, input.map_name()
            )
        
    # Player Four Boxplot
    @render.plot
    def player_4_box():
        return player_kills_overview(
            cdlDF, "Kenny", gamemode(), 20, input.map_name()
        )

    # Player Four Scatterplot
    @render.plot
    def player_4_scatter():
        if input.x_axis() == "Time":
            return player_kills_vs_time(
                cdlDF, "Kenny", gamemode(), 20, input.map_name()
            )
        else:
            return player_kills_vs_score_diff(
                cdlDF, "Kenny", gamemode(), 20, input.map_name()
            )


app = App(app_ui, server)

