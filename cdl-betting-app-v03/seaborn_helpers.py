
# Import pandas, seaborn & matplotlib
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

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


# Team Score Diffs by Map & Mode
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
    
    # User selected only one map 
    else:

        # Filter data based on user inputs, including map
        queried_df = \
        queried_df[(queried_df['gamemode'] == gamemode_input) & \
                (queried_df['team'] == team_input) & \
                (queried_df["map_name"] == map_input)] \
                [['match_id', 'map_name', 'score_diff']].drop_duplicates()
        

    # Create the figure
    fig, ax = plt.subplots(figsize = (8, 4))

    # Histogram for Hardpoint
    if gamemode_input == "Hardpoint":
          
          # Plot the histogram
          sns.histplot(data = queried_df, x = "score_diff", binwidth = 50, binrange = (-200, 200))

    # Bar chart for SnD & Control
    else:
        
        # Plot the bar chart
        sns.histplot(data = queried_df, x = "score_diff", discrete = True, 
             binrange = gamemode_bin_ranges["Control"])
        
    # Styling
    ax.set_xlabel("Map Result")