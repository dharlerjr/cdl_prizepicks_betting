
# Imports
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt
import math

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


# Team Distribution of Score Differentials by Map & Mode
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
    fig, ax = plt.subplots(figsize = (4, 2))

    # Histogram for Hardpoint
    if gamemode_input == "Hardpoint":
          
        # Plot the histogram
        sns.histplot(data = queried_df, x = "score_diff", binwidth = 50, binrange = (-250, 250))

        # Get max y
        queried_df['bin'] = pd.cut(queried_df['score_diff'], bins = range(-250, 300, 50))
        max_y = max(queried_df['bin'].value_counts())

    # Bar chart for SnD & Control
    else:
        
        # Plot the bar chart
        sns.histplot(data = queried_df, x = "score_diff", discrete = True, 
             binrange = gamemode_bin_ranges[gamemode_input])
        
        # Get max y
        max_y = 0 if queried_df.empty else max(queried_df["score_diff"].value_counts())
        
    # Set y-axis to integer values only
    y_axis_ticks = range(0, max_y + 1)
    plt.yticks(y_axis_ticks)
        
    # Styling
    ax.set_xlabel("Map Result")


# Team % of Maps Played by Mode
def team_percent_maps_played(
        team_summaries_input: pd.DataFrame, team_input: str, 
        gamemode_input: str
):
    
    # Create a copy of cdlDF_input
    queried_df = team_summaries_input.copy()

    # Filter team_summaries_input by team & mode
    queried_df = queried_df[
        (queried_df["team"] == team_input) &
        (queried_df["gamemode"] == gamemode_input) &
        (queried_df["map_name"] != "Overall") & 
        (queried_df["total"] != 0)
    ]

    # Create figure
    fig, ax = plt.subplots(figsize = (4, 2))

    # Pie Chart
    ax.pie(queried_df["total"], labels = queried_df["map_name"], 
           autopct = '%1.1f%%',  pctdistance = 0.65,
           colors = viridis_gamemode_color_scales["Hardpoint"])


# Team Distribution of Series Differentials
def team_series_diffs(series_score_diffs_input: pd.DataFrame, team_input: str):
    
    # Filter series_score_diffs by team
    queried_df = series_score_diffs_input[
        series_score_diffs_input["team"] == team_input
        ].copy()

    # Create figure
    fig, ax = plt.subplots(figsize = (4, 2))

    # Histogram
    sns.histplot(data = queried_df, x = "series_score_diff", discrete = True, color = "#2fa4e7")

    # Styling
    ax.set_xlabel("Series Result")


# Player Kills vs Time by Map & Mode
def player_kills_vs_time(        
        cdlDF_input: pd.DataFrame, player_input: str,
        gamemode_input: str, cur_line: float, map_input = "All"
):
    
    # Create a copy of cdlDF_input
    queried_df = cdlDF_input.copy()

    # If user selected all maps
    if map_input == "All":
        
        # Filter data based on user inputs
        queried_df = queried_df[
            (queried_df["player"] == player_input) &
            (queried_df["gamemode"] == gamemode_input)
            ]

    # If user selected only one map
    else:
        
        # Filter data based on user inputs, including map
        queried_df = queried_df[
            (queried_df["player"] == player_input) &
            (queried_df["gamemode"] == gamemode_input) & 
            (queried_df["map_name"] == map_input)
            ]
    
    # Create figure with gridspec
    f, axs = plt.subplots(1, 2, figsize = (6, 3), gridspec_kw = dict(width_ratios=[0.4, 2], wspace = 0.05), sharey = True)

    # Boxplot
    sns.boxplot(queried_df, y =  "kills", fill = False, ax=axs[0], color = "#2fa4e7", showfliers = False)
    sns.stripplot(queried_df, y = "kills", jitter = 0.05, ax=axs[0], color = "#2fa4e7")
    axs[0].axhline(y = cur_line, color = "purple", linestyle = '--')

    # Scatterplot
    sns.scatterplot(queried_df, x = "match_date", y = "kills", ax=axs[1], color = "#2fa4e7")
    axs[1].axhline(y = cur_line, color = "purple", linestyle = '--')

    # If necessary, scale y-axis due to lack of entries
    kills = queried_df["kills"].to_list()
    kills.append(math.floor(cur_line))
    min_y = min(kills)
    max_y = max(kills)
    if min_y == max_y:
        y_axis_ticks = range(min_y - 2, max_y + 3)
    elif max_y - min_y <= 5:
        y_axis_ticks = range(min_y - 1, max_y + 1)
        plt.yticks(y_axis_ticks)

    # X- & Y-Axis Labels
    axs[1].set_xlabel("Date")
    axs[0].set_ylabel("Kills")
    axs[0].get_xaxis().set_visible(False)
    axs[1].get_yaxis().set_visible(False)

    # Date Ticks
    formatter = mdates.DateFormatter('%b %d')
    axs[1].xaxis.set_major_formatter(formatter)
    axs[1].tick_params(axis = 'x', rotation = 35)

    # Label current line from PrizePicks if queried_df is not empty
    if not queried_df.empty:
        bbox = {'facecolor': 'purple', 'alpha': 0.5, 'pad': 0.4, 'boxstyle': 'round'}
        cur_line_x = min(queried_df["match_date"])
        plt.text(cur_line_x, cur_line + 1, "Line: " + str(cur_line), bbox = bbox, color = "white")

    # Add title
    plt.title(player_input, loc = "left")
    

# Player Kills vs Score Differential by Map & Mode
def player_kills_vs_score_diff(
        cdlDF_input: pd.DataFrame, player_input: str,
        gamemode_input: str, cur_line: float, map_input = "All"
):
    
    # Create a copy of cdlDF_input
    queried_df = cdlDF_input.copy()

    # If user selected all maps
    if map_input == "All":
        
        # Filter data based on user inputs
        queried_df = queried_df[
            (queried_df["player"] == player_input) &
            (queried_df["gamemode"] == gamemode_input)
            ]

    # If user selected only one map
    else:
        
        # Filter data based on user inputs, including map
        queried_df = queried_df[
            (queried_df["player"] == player_input) &
            (queried_df["gamemode"] == gamemode_input) & 
            (queried_df["map_name"] == map_input)
            ]
        
    # Create figure with gridspec
    f, axs = plt.subplots(1, 2, figsize = (6, 3), gridspec_kw = dict(width_ratios=[0.4, 2], wspace = 0.05), sharey = True)

    # Boxplot
    sns.boxplot(queried_df, y =  "kills", fill = False, ax=axs[0], color = "#2fa4e7", showfliers = False)
    sns.stripplot(queried_df, y = "kills", jitter = 0.05, ax=axs[0], color = "#2fa4e7")
    axs[0].axhline(y = cur_line, color = "purple", linestyle = '--')

    # Scatterplot
    sns.scatterplot(queried_df, x = "score_diff", y = "kills", ax=axs[1])
    sns.regplot(queried_df, x = "score_diff", y = "kills", lowess = True, color = "#2fa4e7")
    axs[1].axhline(y = cur_line, color = "purple", linestyle = '--')
    axs[1].axvline(x = 0, color = "orange", linestyle = '--')

    # If necessary, scale y-axis due to lack of entries
    kills = queried_df["kills"].to_list()
    kills.append(math.floor(cur_line))
    min_y = min(kills)
    max_y = max(kills)
    if min_y == max_y:
        y_axis_ticks = range(min_y - 2, max_y + 3)
    elif max_y - min_y <= 5:
        y_axis_ticks = range(min_y, max_y + 1)
        plt.yticks(y_axis_ticks)

    # Styling
    axs[1].set_xlabel("Map Result")
    axs[0].set_ylabel("Kills")
    axs[0].get_xaxis().set_visible(False)
    axs[1].get_yaxis().set_visible(False)

    # Label current line from PrizePicks if queried_df is not empty
    if not queried_df.empty:
        bbox = {'facecolor': 'purple', 'alpha': 0.5, 'pad': 0.4, 'boxstyle': 'round'}
        min_score_diff = min(queried_df["score_diff"])
        text = [plt.text(min_score_diff, cur_line + 1, "Line: " + str(cur_line), bbox = bbox, color = "white")]

    # Add title
    plt.title(player_input, loc = "left")