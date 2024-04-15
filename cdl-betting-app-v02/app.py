
# Import shiny and shinyswatch
from shiny import App, reactive, render, ui
import shinyswatch

# Import setup
from setup.setup import *

# Import webscraper & helpers
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

# Function to remove all removed map & mode combos from cdlDF, 
# after building series summaries
cdlDF = filter_cdldf(cdlDF)

# Build team rosters
rostersDF = build_rosters(cdlDF)


# Define ui
app_ui = ui.page_sidebar(   
    ui.sidebar(
        # Theme superhero
        shinyswatch.theme.superhero,
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
        ui.card(ui.output_plot("player_1_box")), 
        ui.card(ui.output_plot("player_1_scatter"))
    ),
    ui.layout_columns(
        ui.card(ui.output_plot("player_1_box")), 
        ui.card(ui.output_plot("player_1_scatter"))
    ),
    title = "CDL Bets on PrizePicks" 
)

# Define server logic
def server(input, output, session):

    # Reactive calc to translate map num to gamemode
    @reactive.calc
    def gamemode():
        return map_nums_to_gamemode[input.map_num()]
    
     # Player One Boxplot
    @render.plot
    def player_1_box():
        return player_kills_overview(
            cdlDF, 
            rostersDF[rostersDF['team'] == input.team_a()].iloc[0]['player'],  
            gamemode(), 
            21,
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
                21,
                input.map_name()
            )
        else:
            return player_kills_vs_score_diff(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.team_a()].iloc[0]['player'],  
                gamemode(), 
                21,
                input.map_name()
            )
        
app = App(app_ui, server)