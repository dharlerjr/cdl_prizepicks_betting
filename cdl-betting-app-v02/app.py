
# Imports
from setup.setup import *

# Import shiny
from shiny import App, render, ui

# Load and clean cdl dataset
cdlDF = load_and_clean_cdl_data()

# Build team summaries 
team_summaries_DF = build_team_summaries(cdlDF_input = cdlDF)

# Define ui
app_ui = ui.page_sidebar(   
    
    ui.sidebar(
        ui.input_select(id = "team_a_input", label = "Team", selected = "OpTic Texas",
                        choices = sorted(cdlDF['team'].unique())), 
        ui.input_select(id = "team_b_input", label = "Team", selected = "Atlanta FaZe",
                        choices = sorted(cdlDF['team'].unique())), 
        ui.input_action_button(id = "scrape", label = "Get PrizePicks Lines"), 
        ui.input_select(id = "gamemode_input", label = "Gamemode", selected = "Hardpoint",
                        choices = cdlDF.sort_values(by = ['gamemode']).gamemode.unique().to_list()), 
        ui.input_select(id = "map_name_input", label = "Map", selected = "All",
                        choices = ["All"] + \
                            sorted([map_name for map_name in cdlDF['map_name'].unique() if map_name != "Skidrow"])), 
        ui.input_select(id = "x_axis_input", label = "X-Axis", selected = "Time",
                        choices = ["Time", "Total Score", "Score Differential"]), 
        title = "CDL Bets on PrizePicks" 
    )
)


# Define server logic
def server(input, output, session):

    @render.code
    def result():
        return f"You entered '{input.txt_in()}'."


app = App(app_ui, server)

