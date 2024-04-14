
# Import setup
from setup.setup import *

# Import shiny and shinyswatch
from shiny import App, render, ui
import shinyswatch

# Import helpers
from seaborn_helpers import *

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
                        choices = [1, 2, 3]), 
        ui.input_select(id = "gamemode", label = "Gamemode", selected = "Hardpoint",
                        choices = cdlDF.sort_values(by = ['gamemode']).gamemode.unique().to_list()), 
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
        ui.card(), 
        ui.card()
    ),
    title = "CDL Bets on PrizePicks" 
)


# Define server logic
def server(input, output, session):

    ## Theme picker - start
    shinyswatch.theme_picker_server()

app = App(app_ui, server)

