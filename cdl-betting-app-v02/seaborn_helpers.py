
# Import seaborn
import seaborn as sns

# Import setup
from setup.setup import *

# Dictionary of color scales by gamemode 
gamemode_color_scales = {
  "Hardpoint": ["red", "orange", "green", "blue", "purple"],
  "Search & Destroy": ["red", "orange", "green", "blue", "purple"],
  "Control": ["red", "green", "blue"]
}

# Dictionary of colors by map & mode 
map_and_mode_colors = {
  "Hardpoint" : {
    "6 Star" : "red", 
    "Karachi" : "orange",
    "Rio" : "green",
    "Sub Base" : "blue",
    "Vista" : "purple"
  } ,
  "Search & Destroy" : {
    "6 Star" : "red", 
    "Highrise" : "orange",
    "Invasion" : "green", 
    "Karachi" : "blue",
    "Rio" : "purple"
  },
  "Control" : {
    "Highrise" : "red", 
    "Invasion" : "green", 
    "Karachi" : "blue"
  }
}

# Dictionary of viridis color scales by gamemode
viridis_gamemode_color_scales = {
  "Hardpoint":
    ["#FDE725FF", "#56c667ff", "#21908CFF", "#3B528BFF", "#440154FF"],
  "Search & Destroy":
    ["#FDE725FF", "#56c667ff", "#21908CFF", "#3B528BFF", "#440154FF"], 
  "Control": ["#FDE725FF", "#56c667ff", "#21908CFF"]
}

# Dictionary of viridis colors by map & mode
viridis_map_and_mode_colors = {
  "Hardpoint": {
    "6 Star" : "#FDE725FF", 
    "Karachi" : "#56c667ff",
    "Rio" : "#21908CFF",
    "Sub Base" : "#3B528BFF",
    "Vista" : "#440154FF"
  }, 
  "Search & Destroy": {
    "6 Star" : "#FDE725FF", 
    "Highrise" : "#56c667ff",
    "Invasion" : "#21908CFF", 
    "Karachi" : "#3B528BFF",
    "Rio" : "#440154FF"
  }, 
  "Control": {
    "Highrise" : "#FDE725FF", 
    "Invasion" : "#56c667ff", 
    "Karachi" : "#21908CFF"
  }
}

# Dictionary of binwidths by gamemode
gamemode_binwidths = {
  "Hardpoint": 50, 
  "Search & Destroy": 1, 
  "Control": 1
}

# Dictionary of ylims by gamemode 
gamemode_kill_lims = {
  "Hardpoint": [0, 45],
  "Search & Destroy": [0, 16],
  "Control": [0, 45]
}

# Set seaborn theme
sns.set_theme(style = "darkgrid")

# Load in data
cdlDF = load_and_clean_cdl_data()
cdlDF

# Distribution of Score Differentials by Team, Map & Mode
def team_score_diffs(team_input: str, gamemode_input: str, map_input = "All"):

    # If user selected all maps    
    if map_input == "All":
    
        # Filter data based on user inputs
        filtered_df = \
        cdlDF[(cdlDF['gamemode'] == gamemode_input) & \
                (cdlDF['team'] == team_input)] \
                [['match_id', 'map_name', 'score_diff']].drop_duplicates()

        # Plot the faceted histogram
        p = sns.displot(
            data = filtered_df,  x = "score_diff", col = "map_name", col_wrap = 3,
            binwidth = gamemode_binwidths[gamemode_input], height = 3, facet_kws = dict(margin_titles=True),
            )
        
        # Title
        p.figure.suptitle(f"{team_input} Score Differentials: {gamemode_input}")

        # Set facet titles
        p.set_titles("{col_name}")
    
    # User selected only one map 
    else:

        # Filter data based on user inputs, including map
        filtered_df = \
        cdlDF[(cdlDF['gamemode'] == gamemode_input) & \
                (cdlDF['team'] == team_input) & \
                (cdlDF["map_name"] == map_input)] \
                [['match_id', 'map_name', 'score_diff']].drop_duplicates()

        # Plot the histogram
        p = sns.displot(
            data = filtered_df, x = "score_diff", 
            binwidth = gamemode_binwidths[gamemode_input]
            )
        
        # Title
        p.figure.suptitle(f"{team_input} Score Differentials: {map_input} {gamemode_input}")
        
    # Set axis labels 
    p.set_axis_labels("Score Differential", "Count")

    # Move title up
    p.figure.subplots_adjust(top = 0.9)
        
    return p

# Distribution of Series Differentials by Team
def team_series_diffs(team_input: str):
    pass
    

    

# Player Kills Overview
def player_kills_overview(
        player_input: str, gamemode_input: str, cur_line: float, map_input = "All"
):
    # If user selected all maps
    if map_input == "All":

        # Filter data based on user inputs
        filtered_df = \
            cdlDF[(cdlDF["gamemode"] == gamemode_input) & \
            (cdlDF["player"] == player_input)]

    # User selected only one map
    else:

        # Filter data based on user inputs, including map
        filtered_df = \
            cdlDF[(cdlDF["gamemode"] == gamemode_input) & \
            (cdlDF["player"] == player_input) & \
            (cdlDF["map_name"] == map_input)]
        
    # Plot the boxplot
    sns.boxplot(filtered_df, y =  "kills", fill = False)
    
    # Add in points to show each observation
    sns.stripplot(filtered_df, y = "kills")


