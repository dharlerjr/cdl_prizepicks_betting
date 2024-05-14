
# Imports
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt
import math

# Dictionary of viridis color scales by gamemode
viridis_gamemode_color_scales = {
  "Hardpoint":
    ["#FDE725FF", "#56c667ff", "#21908CFF", "#3B528BFF", "#440154FF"],
  "Search & Destroy":
    ["#FDE725FF", "#56c667ff", "#21908CFF", "#3B528BFF", "#440154FF"], 
  "Control": ["#FDE725FF", "#56c667ff", "#21908CFF"]
}

# Dictionary of bin ranges by gamemode
gamemode_bin_ranges = {
    "Search & Destroy": (-6, 6), 
    "Control": (-3, 3)
}

# Dictionary of team colors for plotting
team_colors = {
    "Atlanta FaZe": "#e43d30", 
    "Boston Breach": "#02ff5b",
    "Carolina Royal Ravens": "#0083c1",
    "Los Angeles Guerrillas": "#60269e",
    "Los Angeles Thieves": "#ff0000",
    "Las Vegas Legion": "#ee7623",
    "Miami Heretics": "#216d6b",
    "Minnesota ROKKR": "#351f65",
    "New York Subliners": "#fff000", #"#171C38", 
    "Seattle Surge": "#00ffcc", 
    "Toronto Ultra": "#780df2",
    "OpTic Texas": "#92c951" # "#000000"

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
        sns.histplot(data = queried_df, x = "score_diff", binwidth = 50, 
                     binrange = (-250, 250), color = team_colors[team_input])

        # Get max y
        queried_df['bin'] = pd.cut(queried_df['score_diff'], bins = range(-250, 300, 50))
        max_y = max(queried_df['bin'].value_counts())

    # Bar chart for SnD & Control
    else:
        
        # Plot the bar chart
        sns.histplot(data = queried_df, x = "score_diff", discrete = True, 
             binrange = gamemode_bin_ranges[gamemode_input], 
             color = team_colors[team_input])
        
        # Get max y
        max_y = 0 if queried_df.empty else max(queried_df["score_diff"].value_counts())
        
    # Set y-axis to integer values only
    step_y = 1 if max_y < 6 else 2
    y_axis_ticks = range(0, max_y + 1, step_y)
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
    
    # Margins
    plt.margins(0.05)


# Team Distribution of Series Differentials
def team_series_diffs(series_score_diffs_input: pd.DataFrame, team_input: str):
    
    # Filter series_score_diffs by team
    queried_df = series_score_diffs_input[
        series_score_diffs_input["team"] == team_input
        ].copy()

    # Create figure
    fig, ax = plt.subplots(figsize = (4, 2))

    # Histogram
    sns.histplot(data = queried_df, x = "series_score_diff", 
                 discrete = True, color = team_colors[team_input])

    # Styling
    ax.set_xlabel("Series Result")

    # Set margins
    plt.margins(0.05)


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
        
    # Set match_date column to dt.date type
    queried_df.loc[:, 'match_date'] = pd.to_datetime(queried_df['match_date']).dt.date

    # Get team for for team_colors dictionary
    team = queried_df.iloc[0, 4]
    
    # Create figure with gridspec
    f, axs = plt.subplots(1, 2, figsize = (6, 3), sharey = True, gridspec_kw = 
                          dict(width_ratios=[2, 0.4], wspace = 0.05))

    # Scatterplot
    sns.scatterplot(queried_df, x = "match_date", y = "kills", ax=axs[0], 
                    color = team_colors[team])
    axs[0].axhline(y = cur_line, color = "purple", linestyle = '--')

    # Boxplot
    sns.boxplot(queried_df, y =  "kills", fill = False, ax=axs[1], 
                color = team_colors[team], showfliers = False)
    sns.stripplot(queried_df, y = "kills", jitter = 0.05, ax=axs[1], color = team_colors[team])
    axs[1].axhline(y = cur_line, color = "purple", linestyle = '--')

    # Add title
    axs[0].set_title(player_input, fontsize = 18, family = "sans serif", loc = "left")

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
    axs[0].set_xlabel("")
    axs[0].set_ylabel("Kills")
    axs[1].set_xticks([])
    axs[1].set_ylabel("")

    # Date Ticks
    formatter = mdates.DateFormatter('%b %d')
    axs[0].xaxis.set_major_formatter(formatter)
    axs[0].tick_params(axis = 'x', rotation = 30)


    # Label current line from PrizePicks if queried_df is not empty
    plt.sca(axs[0])
    if not queried_df.empty:
        bbox = {'facecolor': 'purple', 'alpha': 0.5, 'pad': 0.4, 'boxstyle': 'round'}
        cur_line_x = min(queried_df["match_date"])
        plt.text(cur_line_x, cur_line + 1, "Line: " + str(cur_line), bbox = bbox, color = "white")

    # Set margins
    plt.margins(0.05)
    

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
        
    # Get team for for team_colors dictionary
    team = queried_df.iloc[0, 4]
        
    # Create figure with gridspec
    f, axs = plt.subplots(1, 2, figsize = (6, 3), gridspec_kw = dict(width_ratios=[2, 0.4], wspace = 0.05), sharey = True)

    # Scatterplot
    sns.scatterplot(queried_df, x = "score_diff", y = "kills", ax=axs[0], 
                    color = team_colors[team])
    sns.regplot(queried_df, x = "score_diff", y = "kills", lowess = True, ax=axs[0], 
                color = team_colors[team])
    axs[0].axhline(y = cur_line, color = "purple", linestyle = '--')
    # axs[0].axvline(x = 0, color = "orange", linestyle = '--')

    # Boxplot
    sns.boxplot(queried_df, y =  "kills", fill = False, ax=axs[1], 
                color = team_colors[team], showfliers = False)
    sns.stripplot(queried_df, y = "kills", jitter = 0.05, ax=axs[1], 
                  color = team_colors[team])
    axs[1].axhline(y = cur_line, color = "purple", linestyle = '--')

    # Add title
    axs[0].set_title(player_input, fontsize = 18, family = "sans serif", loc = "left")

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

    # X- & Y-Axis Labels
    axs[0].set_xlabel("")
    axs[0].set_ylabel("Kills")
    axs[1].set_xticks([])
    axs[1].set_ylabel("")


    # Label current line from PrizePicks if queried_df is not empty
    plt.sca(axs[0])
    if not queried_df.empty:
        bbox = {'facecolor': 'purple', 'alpha': 0.5, 'pad': 0.4, 'boxstyle': 'round'}
        min_score_diff = min(queried_df["score_diff"])
        text = [plt.text(min_score_diff, cur_line + 1, "Line: " + str(cur_line), bbox = bbox, color = "white")]

    # Set margins
    plt.margins(0.05)