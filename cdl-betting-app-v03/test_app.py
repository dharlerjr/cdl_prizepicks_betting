
# Import shiny, shinyswatch, faicons, and asyncio
from shiny import App, reactive, render, ui
import shinyswatch

# Import setup
from setup.setup import *

# Import helpers
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

# Global color variables
theme_color_light = "#2fa4e7"
theme_color_dark = "#1b6ead"
team_a_color = theme_color_light
team_b_color = theme_color_dark


# Load in four instance of cdl data for testing
cdlDF = load_and_clean_cdl_data()

# Filter maps from cdlDF
cdlDF = filter_maps(cdlDF)

# Build rosters
rostersDF = build_rosters(cdlDF).copy()

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
                                #choices = ["All"] + sorted(filter_maps(cdlDF)['map_name'].unique())), 
                ui.input_select(id = "x_axis", label = "Player Card X-Axis", selected = "Time",
                                choices = ["Time", "Score Differential"]),

            ),

            # Test row
            ui.layout_columns(

                # Player cards
                ui.navset_card_pill(
                    ui.nav_panel("1", ui.output_plot("player_1_plot")),
                    ui.nav_panel("2", ui.output_plot("player_2_plot")), 
                    title = "Player Cards"
                ),

                # Column Widths
                col_widths = [-2, 8, -2]
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

    # Player One Line
    @reactive.Calc
    def player_1_line():
        return get_line(initial_player_props, input.team_a(), 1, map_num())
    
    # Player Two Line
    @reactive.Calc
    def player_2_line():
        return get_line(initial_player_props, input.team_a(), 2, map_num())
    
    # Player One Plot
    @render.plot
    def player_1_plot():
        if input.x_axis() == "Time":
            return player_kills_vs_time(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.team_a()].iloc[0]['player'],
                team_a_color,
                gamemode(), 
                player_1_line(),
                input.map_name()
            )
        else:
            return player_kills_vs_score_diff(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.team_a()].iloc[0]['player'],
                team_a_color,
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
                team_a_color,
                gamemode(), 
                player_2_line(),
                input.map_name()
            )
        else:
            return player_kills_vs_score_diff(
                cdlDF, 
                rostersDF[rostersDF['team'] == input.team_a()].iloc[1]['player'],
                team_a_color,
                gamemode(), 
                player_2_line(),
                input.map_name()
            )
        

# Run app
app = App(app_ui, server)