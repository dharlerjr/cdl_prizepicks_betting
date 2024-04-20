
# Import pandas, seaborn & matplotlib
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Import filter_maps from setup
from setup.setup import filter_maps

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

# Dictionary of bin ranges by gamemode
gamemode_bin_ranges = {
    "Search & Destroy": (-6, 6), 
    "Control": (-3, 3)
}

# Dictionary of ylims by gamemode 
gamemode_kill_lims = {
  "Hardpoint": [0, 45],
  "Search & Destroy": [0, 16],
  "Control": [0, 45]
}

# Set seaborn theme
sns.set_theme(style = "darkgrid")

# Distribution of Score Differentials by Team, Map & Mode
def team_score_diffs(
        cdlDF_input: pd.DataFrame, team_input: str, 
        gamemode_input: str, map_input = "All"
):
    
    # Create a copy of cdlDF_input
    queried_df = cdlDF_input.copy()

    # If user selected all maps    
    if map_input == "All":
    
        # Filter data based on user inputs
        queried_df = \
        queried_df[(queried_df['gamemode'] == gamemode_input) & \
                (queried_df['team'] == team_input)] \
                [['match_id', 'map_name', 'score_diff']].drop_duplicates()
        
        # Initialize facets
        p = sns.FacetGrid(queried_df, col = "map_name", col_wrap = 3)

        # Histogram for Hardpoint
        if gamemode_input == "Hardpoint":
          
          # Plot the faceted histograms
          p.map_dataframe(
              sns.histplot, x = "score_diff", 
              binwidth = 50, binrange = (-150, 150)
              )
          
        # Bar chart for SnD & Control
        else:

          # Plot the faceted bar charts
          p.map_dataframe(sns.histplot, x = "score_diff", discrete = True, 
                          binrange = gamemode_bin_ranges[gamemode_input])
        
        # Title
        p.figure.suptitle(f"{team_input} Score Differentials: {gamemode_input}")

        # Set facet titles
        p.set_titles("{col_name}")
    
    # User selected only one map 
    else:

        # Filter data based on user inputs, including map
        queried_df = \
        queried_df[(queried_df['gamemode'] == gamemode_input) & \
                (queried_df['team'] == team_input) & \
                (queried_df["map_name"] == map_input)] \
                [['match_id', 'map_name', 'score_diff']].drop_duplicates()
        
        # Histogram for Hardpoint
        if gamemode_input == "Hardpoint":

          # Plot the histogram
          p = sns.histplot(
              data = queried_df, x = "score_diff", 
              binwidth = 50, binrange = (-150, 150)
              )
        
        # Bar chart for SnD & Control
        else:
           
          # Plot the bar chart
          p = sns.histplot(data = queried_df, x = "score_diff", discrete = True, 
                           binrange = gamemode_bin_ranges[gamemode_input])
        
        # Title
        p.figure.suptitle(f"{team_input} Score Differentials: {map_input} {gamemode_input}")

    # Move title up
    p.figure.subplots_adjust(top = 0.9)
        
    return p


# Distribution of Series Differentials by Team
def team_series_diffs(series_score_diffs_input: pd.DataFrame, team_input: str):

    queried_df = \
        series_score_diffs_input[
            series_score_diffs_input["team"] == team_input
            ].copy()

    # Plot the histogram
    p = sns.histplot(
        data = queried_df, x = "series_score_diff", discrete = True
        )
        
    # Title
    p.figure.suptitle(f"{team_input} Series Differentials")

    # Move title up
    p.figure.subplots_adjust(top = 0.9)


# Player Kills Overview
def player_kills_overview(
        cdlDF_input: pd.DataFrame, player_input: str, gamemode_input: str, 
        cur_line: float, map_input = "All"
):
    
    # Create a copy of cdlDF_input
    queried_df = cdlDF_input.copy()

    # If user selected all maps
    if map_input == "All":

        # Filter data based on user inputs
        queried_df = \
            queried_df[(queried_df["gamemode"] == gamemode_input) & \
            (queried_df["player"] == player_input)]

    # User selected only one map
    else:

        # Filter data based on user inputs, including map
        queried_df = \
            queried_df[(queried_df["gamemode"] == gamemode_input) & \
            (queried_df["player"] == player_input) & \
            (queried_df["map_name"] == map_input)]
        
    # Plot the boxplot
    sns.boxplot(queried_df, y =  "kills", fill = False).set(title = f"{player_input}")
    
    # Add in points to show each observation
    sns.stripplot(queried_df, y = "kills", jitter = 0.05)

    # Add current PrizePicks lines
    plt.axhline(y = cur_line, color = "purple", linestyle = '--')


# Player Kills vs. Time
def player_kills_vs_time(
        cdlDF_input: pd.DataFrame, player_input: str,
          gamemode_input: str, cur_line: float, map_input = "All"
):
    
    # Create a copy of cdlDF_input
    queried_df = cdlDF_input.copy()

    # If user selects all maps
    if map_input == "All":
        
        queried_df = \
            queried_df[(queried_df["gamemode"] == gamemode_input) & \
                (queried_df["player"] == player_input)]

    # If user selects only one map
    else:

        queried_df = \
            queried_df[(queried_df["gamemode"] == gamemode_input) & \
                (queried_df["player"] == player_input) & \
                (queried_df["map_name"] == map_input)]
        
    
    # Create the line chart 
    sns.scatterplot(
        queried_df, x = "match_date", y = "kills"
        )
    
    # Add current PrizePicks lines
    plt.axhline(y = cur_line, color = "purple", linestyle = '--')


# Player Kills vs Score Diff
def player_kills_vs_score_diff(
        cdlDF_input: pd.DataFrame, player_input: str, 
        gamemode_input: str, cur_line: float, map_input = "All"
):
    
    # Create a copy of cdlDF_input
    queried_df = cdlDF_input.copy()
    
    # If user selects all maps
    if map_input == "All":
        
        queried_df = \
            queried_df[(queried_df["gamemode"] == gamemode_input) & \
                (queried_df["player"] == player_input)]

    # If user selects only one map
    else:

        queried_df = \
            queried_df[(queried_df["gamemode"] == gamemode_input) & \
                (queried_df["player"] == player_input) & \
                (queried_df["map_name"] == map_input)]
        
    
    # Create the scatterplot with lowess model
    sns.regplot(
        queried_df, x = "score_diff", y = "kills", lowess = True
        )
    
    # Add current PrizePicks lines
    plt.axhline(y = cur_line, color = "purple", linestyle = '--')

    # Add vertical line at x = 0
    plt.axvline(x = 0, color = "orange", linestyle = '--')